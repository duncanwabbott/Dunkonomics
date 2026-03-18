from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import os
import fetcher
import time

fetcher.NBA_HEADERS['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
fetcher.NBA_HEADERS['Referer'] = 'https://www.nba.com/'
fetcher.NBA_HEADERS['Origin'] = 'https://www.nba.com'

max_retries = 3
for attempt in range(max_retries):
    try:
        print(f"Fetching player fouls... attempt {attempt + 1}")
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(timeout=120, headers=fetcher.NBA_HEADERS)
        p_df = player_stats.get_data_frames()[0]
        p_df['FTr'] = p_df['FTA'] / p_df['FGA'].replace(0, 1)
        p_df['Net_Fouls'] = p_df['PFD'] - p_df['PF']
        p_cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'PF', 'PFD', 'FTA', 'FGA', 'FTr', 'Net_Fouls']
        p_df = p_df[[c for c in p_cols if c in p_df.columns]].sort_values('Net_Fouls', ascending=False)
        p_df.to_csv(os.path.join(fetcher.DATA_DIR, "player_fouls.csv"), index=False)
        print(f"Player fouls saved to {os.path.join(fetcher.DATA_DIR, 'player_fouls.csv')}, rows: {len(p_df)}")
        break
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(5)
