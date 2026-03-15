import pandas as pd
import time
import os
import logging
from nba_api.stats.endpoints import leaguestandingsv3, leaguedashteamstats, leaguedashplayerstats
from nba_api.stats.static import players
from urllib3.exceptions import NotOpenSSLWarning
import warnings

# Silence warnings
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

NBA_HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true',
    'Referer': 'https://stats.nba.com/'
}

def fetch_standings():
    try:
        logging.info("Fetching Standings...")
        standings = leaguestandingsv3.LeagueStandingsV3(timeout=30)
        df = standings.get_data_frames()[0]
        df.rename(columns={'PlayoffRank': 'Rank', 'WinPCT': 'Win %', 'PointsPG': 'PPG', 'OppPointsPG': 'OPP PPG', 'strCurrentStreak': 'Streak', 'DiffPointsPG': 'Diff'}, inplace=True)
        cols = ['TeamName', 'Conference', 'Rank', 'WINS', 'LOSSES', 'Win %', 'HOME', 'ROAD', 'L10', 'Streak', 'PPG', 'OPP PPG', 'Diff']
        df = df[[c for c in cols if c in df.columns]]
        df.to_csv(os.path.join(DATA_DIR, "standings.csv"), index=False)
        logging.info("Standings saved.")
        return True
    except Exception as e:
        logging.error(f"Failed to fetch standings: {e}")
        return False

def fetch_team_stats():
    try:
        logging.info("Fetching Advanced Team Stats...")
        team_stats = leaguedashteamstats.LeagueDashTeamStats(measure_type_detailed_defense='Advanced', timeout=30)
        df = team_stats.get_data_frames()[0]
        cols = ['TEAM_NAME', 'GP', 'W', 'L', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'AST_PCT', 'TS_PCT', 'PACE']
        df = df[cols].sort_values('NET_RATING', ascending=False)
        df.to_csv(os.path.join(DATA_DIR, "team_stats.csv"), index=False)
        logging.info("Team stats saved.")
        return True
    except Exception as e:
        logging.error(f"Failed to fetch team stats: {e}")
        return False

def fetch_players():
    try:
        logging.info("Fetching Player Directory...")
        all_p = players.get_active_players()
        df = pd.DataFrame(all_p)
        df.to_csv(os.path.join(DATA_DIR, "players.csv"), index=False)
        logging.info("Players saved.")
        return True
    except Exception as e:
        logging.error(f"Failed to fetch players: {e}")
        return False

def fetch_advanced_players():
    try:
        logging.info("Fetching Advanced Player Stats...")
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(measure_type_detailed_defense='Advanced', timeout=30)
        df = player_stats.get_data_frames()[0]
        # Calculate DUNK Score: (TS_PCT * 0.4) + (AST_PCT * 0.3) + (USG_PCT * 0.2) + PIE - (TM_TOV_PCT * 1.5)
        # Using PIE as a proxy for STL/BLK defensive impact
        df['DUNK_SCORE'] = (df['TS_PCT'] * 0.4) + (df['AST_PCT'] * 0.3) + (df['USG_PCT'] * 0.2) + df['PIE'] - (df['TM_TOV_PCT'] * 1.5)
        
        cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'TS_PCT', 'AST_PCT', 'USG_PCT', 'PIE', 'TM_TOV_PCT', 'DUNK_SCORE']
        df = df[[c for c in cols if c in df.columns]].sort_values('DUNK_SCORE', ascending=False)
        df.to_csv(os.path.join(DATA_DIR, "advanced_players.csv"), index=False)
        logging.info("Advanced players saved.")
        return True
    except Exception as e:
        logging.error(f"Failed to fetch advanced players: {e}")
        return False

def run_fetch_cycle():
    logging.info("--- Starting Fetch Cycle ---")
    fetch_standings()
    time.sleep(2) # Be polite to the API
    fetch_team_stats()
    time.sleep(2)
    fetch_players()
    time.sleep(2)
    fetch_advanced_players()
    logging.info("--- Fetch Cycle Complete ---")

if __name__ == "__main__":
    # If run directly, execute one cycle
    run_fetch_cycle()
