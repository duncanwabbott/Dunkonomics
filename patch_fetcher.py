import re

with open('fetcher.py', 'r') as f:
    content = f.read()

new_func = """
from nba_api.stats.endpoints import leaguedashplayerstats

def fetch_advanced_players():
    try:
        logging.info("Fetching Advanced Player Stats...")
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(measure_type_detailed_defense='Advanced', timeout=30)
        df = player_stats.get_data_frames()[0]
        # Calculate DUNK Score: (TS_PCT * 0.4) + (AST_PCT * 0.3) + (USG_PCT * 0.2) + PIE - (TM_TOV_PCT * 1.5)
        # Assuming missing STL_PCT and BLK_PCT are mapped to PIE (Player Impact Estimate)
        df['DUNK_SCORE'] = (df['TS_PCT'] * 0.4) + (df['AST_PCT'] * 0.3) + (df['USG_PCT'] * 0.2) + df['PIE'] - (df['TM_TOV_PCT'] * 1.5)
        
        cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'TS_PCT', 'AST_PCT', 'USG_PCT', 'PIE', 'TM_TOV_PCT', 'DUNK_SCORE']
        df = df[[c for c in cols if c in df.columns]].sort_values('DUNK_SCORE', ascending=False)
        df.to_csv(os.path.join(DATA_DIR, "advanced_players.csv"), index=False)
        logging.info("Advanced players saved.")
        return True
    except Exception as e:
        logging.error(f"Failed to fetch advanced players: {e}")
        return False
"""

# Insert new_func before def run_fetch_cycle():
content = content.replace('def run_fetch_cycle():', new_func + '\ndef run_fetch_cycle():')
content = content.replace('fetch_players()', 'fetch_players()\n    time.sleep(2)\n    fetch_advanced_players()')

with open('fetcher.py', 'w') as f:
    f.write(content)
