import math
from datetime import datetime, timedelta
import pandas as pd
import time
import os
import logging
from nba_api.stats.endpoints import leaguestandingsv3, leaguedashteamstats, leaguedashplayerstats, leaguegamelog
from nba_api.stats.static import players
from urllib3.exceptions import NotOpenSSLWarning
import warnings

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

NBA_HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true',
    'Referer': 'https://stats.nba.com/'
}


NBA_ARENAS = {
    "ATL": {"lat": 33.7573, "lon": -84.3963, "tz": -5},
    "BOS": {"lat": 42.3662, "lon": -71.0621, "tz": -5},
    "BKN": {"lat": 40.6826, "lon": -73.9754, "tz": -5},
    "CHA": {"lat": 35.2251, "lon": -80.8392, "tz": -5},
    "CHI": {"lat": 41.8807, "lon": -87.6742, "tz": -6},
    "CLE": {"lat": 41.4965, "lon": -81.6881, "tz": -5},
    "DAL": {"lat": 32.7905, "lon": -96.8103, "tz": -6},
    "DEN": {"lat": 39.7486, "lon": -105.0075, "tz": -7},
    "DET": {"lat": 42.3411, "lon": -83.0550, "tz": -5},
    "GSW": {"lat": 37.7680, "lon": -122.3877, "tz": -8},
    "HOU": {"lat": 29.7508, "lon": -95.3621, "tz": -6},
    "IND": {"lat": 39.7641, "lon": -86.1555, "tz": -5},
    "LAC": {"lat": 34.0430, "lon": -118.2673, "tz": -8},
    "LAL": {"lat": 34.0430, "lon": -118.2673, "tz": -8},
    "MEM": {"lat": 35.1381, "lon": -90.0506, "tz": -6},
    "MIA": {"lat": 25.7814, "lon": -80.1870, "tz": -5},
    "MIL": {"lat": 43.0451, "lon": -87.9172, "tz": -6},
    "MIN": {"lat": 44.9795, "lon": -93.2761, "tz": -6},
    "NOP": {"lat": 29.9490, "lon": -90.0821, "tz": -6},
    "NYK": {"lat": 40.7505, "lon": -73.9934, "tz": -5},
    "OKC": {"lat": 35.4634, "lon": -97.5151, "tz": -6},
    "ORL": {"lat": 28.5392, "lon": -81.3839, "tz": -5},
    "PHI": {"lat": 39.9012, "lon": -75.1719, "tz": -5},
    "PHX": {"lat": 33.4457, "lon": -112.0712, "tz": -7},
    "POR": {"lat": 45.5316, "lon": -122.6668, "tz": -8},
    "SAC": {"lat": 38.5802, "lon": -121.4997, "tz": -8},
    "SAS": {"lat": 29.4270, "lon": -98.4375, "tz": -6},
    "TOR": {"lat": 43.6435, "lon": -79.3791, "tz": -5},
    "UTA": {"lat": 40.7683, "lon": -111.9011, "tz": -7},
    "WAS": {"lat": 38.8982, "lon": -77.0209, "tz": -5}
}

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dLat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def fetch_standings():
    try:
        logging.info("Fetching Standings...")
        standings = leaguestandingsv3.LeagueStandingsV3(timeout=30, headers=NBA_HEADERS)
        df = standings.get_data_frames()[0]
        df.rename(columns={'PlayoffRank': 'Rank', 'WinPCT': 'Win %', 'PointsPG': 'PPG', 'OppPointsPG': 'OPP PPG', 'strCurrentStreak': 'Streak', 'DiffPointsPG': 'Diff'}, inplace=True)
        cols = ['TeamName', 'Conference', 'Rank', 'WINS', 'LOSSES', 'Win %', 'HOME', 'ROAD', 'L10', 'Streak', 'PPG', 'OPP PPG', 'Diff']
        df = df[[c for c in cols if c in df.columns]]
        df.to_csv(os.path.join(DATA_DIR, "standings.csv"), index=False)
        logging.info("Standings saved.")
        return True
    except Exception as e:
        logging.error(f"Failed to fetch standings: {e}")
        cols = ['TeamName', 'Conference', 'Rank', 'WINS', 'LOSSES', 'Win %', 'HOME', 'ROAD', 'L10', 'Streak', 'PPG', 'OPP PPG', 'Diff']
        pd.DataFrame(columns=cols).to_csv(os.path.join(DATA_DIR, "standings.csv"), index=False)
        return False

def fetch_team_stats():
    try:
        logging.info("Fetching Advanced Team Stats...")
        team_stats = leaguedashteamstats.LeagueDashTeamStats(measure_type_detailed_defense='Advanced', timeout=30, headers=NBA_HEADERS)
        df = team_stats.get_data_frames()[0]
        cols = ['TEAM_NAME', 'GP', 'W', 'L', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'AST_PCT', 'TS_PCT', 'PACE']
        df = df[cols].sort_values('NET_RATING', ascending=False)
        df.to_csv(os.path.join(DATA_DIR, "team_stats.csv"), index=False)
        logging.info("Team stats saved.")
        return True
    except Exception as e:
        logging.error(f"Failed to fetch team stats: {e}")
        cols = ['TEAM_NAME', 'GP', 'W', 'L', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'AST_PCT', 'TS_PCT', 'PACE']
        pd.DataFrame(columns=cols).to_csv(os.path.join(DATA_DIR, "team_stats.csv"), index=False)
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
        pd.DataFrame([{'id': -1, 'full_name': 'Sync Failed', 'first_name': '', 'last_name': '', 'is_active': False}]).to_csv(os.path.join(DATA_DIR, "players.csv"), index=False)
        return False

def fetch_advanced_players():
    try:
        logging.info("Fetching Advanced Player Stats...")
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(measure_type_detailed_defense='Advanced', timeout=30, headers=NBA_HEADERS)
        df = player_stats.get_data_frames()[0]
        df['DUNK_SCORE'] = (df['TS_PCT'] * 0.4) + (df['AST_PCT'] * 0.3) + (df['USG_PCT'] * 0.2) + df['PIE'] - (df['TM_TOV_PCT'] * 1.5)
        
        cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'TS_PCT', 'AST_PCT', 'USG_PCT', 'PIE', 'TM_TOV_PCT', 'DUNK_SCORE']
        df = df[[c for c in cols if c in df.columns]].sort_values('DUNK_SCORE', ascending=False)
        df.to_csv(os.path.join(DATA_DIR, "advanced_players.csv"), index=False)
        logging.info("Advanced players saved.")
        return True
    except Exception as e:
        logging.error(f"Failed to fetch advanced players: {e}")
        cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'TS_PCT', 'AST_PCT', 'USG_PCT', 'PIE', 'TM_TOV_PCT', 'DUNK_SCORE']
        pd.DataFrame(columns=cols).to_csv(os.path.join(DATA_DIR, "advanced_players.csv"), index=False)
        return False

def fetch_cumfat():
    try:
        logging.info("Fetching CumFat Data...")
        ten_days_ago = (datetime.now() - timedelta(days=10)).strftime('%m/%d/%Y')
        lg = leaguegamelog.LeagueGameLog(player_or_team_abbreviation='P', date_from_nullable=ten_days_ago, headers=NBA_HEADERS)
        df = lg.get_data_frames()[0]

        def parse_location(matchup, home_team):
            if ' @ ' in matchup:
                return matchup.split(' @ ')[1]
            else:
                return home_team
        
        df['GAME_LOCATION'] = df.apply(lambda row: parse_location(row['MATCHUP'], row['TEAM_ABBREVIATION']), axis=1)
        df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
        
        results = []
        for player_id, p_df in df.groupby('PLAYER_ID'):
            p_df = p_df.sort_values('GAME_DATE').reset_index(drop=True)
            if len(p_df) == 0: continue
            
            p_name = p_df['PLAYER_NAME'].iloc[0]
            
            miles_flown = 0
            time_zones_crossed = 0
            
            for i in range(1, len(p_df)):
                loc1 = p_df['GAME_LOCATION'].iloc[i-1]
                loc2 = p_df['GAME_LOCATION'].iloc[i]
                
                if loc1 in NBA_ARENAS and loc2 in NBA_ARENAS:
                    a1 = NBA_ARENAS[loc1]
                    a2 = NBA_ARENAS[loc2]
                    dist = haversine(a1['lat'], a1['lon'], a2['lat'], a2['lon'])
                    miles_flown += dist
                    tz_diff = a2['tz'] - a1['tz']
                    if tz_diff > 0:
                        tz_diff *= 1.5
                    time_zones_crossed += abs(tz_diff)

            recent_workload = p_df['MIN'].iloc[-3:].mean() if len(p_df) >= 3 else p_df['MIN'].mean()
            
            schedule_density = 0
            b2b_count = 0
            for i in range(1, len(p_df)):
                if (p_df['GAME_DATE'].iloc[i] - p_df['GAME_DATE'].iloc[i-1]).days == 1:
                    b2b_count += 1
                    schedule_density += 10
            
            rest_deficit = b2b_count
            
            tt = (miles_flown / 5000) * 45
            sd = (schedule_density / 30) * 35
            wl = (recent_workload / 40) * 20
            
            cumfat = min(100, tt + sd + wl)
            
            results.append({
                "PlayerID": player_id,
                "PlayerName": p_name,
                "CumFatScore": round(cumfat, 1),
                "MilesFlown": round(miles_flown, 1),
                "TimeZones": round(time_zones_crossed, 1),
                "ScheduleContext": f"{b2b_count} B2Bs",
                "RestDeficit": rest_deficit,
                "RecentWorkload": round(recent_workload, 1)
            })
            
        final_df = pd.DataFrame(results)
        final_df.to_csv(os.path.join(DATA_DIR, "cumfat.csv"), index=False)
        logging.info("CumFat data saved.")
        return True
    except Exception as e:
        logging.error(f"Failed to fetch CumFat: {e}")
        cols = ['PlayerID', 'PlayerName', 'CumFatScore', 'MilesFlown', 'TimeZones', 'ScheduleContext', 'RestDeficit', 'RecentWorkload']
        pd.DataFrame(columns=cols).to_csv(os.path.join(DATA_DIR, "cumfat.csv"), index=False)
        return False


def fetch_foul_data():
    try:
        logging.info("Fetching Foul Data (Players & Teams)...")
        # Players
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(timeout=30, headers=NBA_HEADERS)
        p_df = player_stats.get_data_frames()[0]
        p_df['FTr'] = p_df['FTA'] / p_df['FGA'].replace(0, 1)
        p_df['Net_Fouls'] = p_df['PFD'] - p_df['PF']
        p_cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'PF', 'PFD', 'FTA', 'FGA', 'FTr', 'Net_Fouls']
        p_df = p_df[[c for c in p_cols if c in p_df.columns]].sort_values('Net_Fouls', ascending=False)
        p_df.to_csv(os.path.join(DATA_DIR, "player_fouls.csv"), index=False)

        # Teams
        team_stats = leaguedashteamstats.LeagueDashTeamStats(timeout=30, headers=NBA_HEADERS)
        t_df = team_stats.get_data_frames()[0]
        t_df['FTr'] = t_df['FTA'] / t_df['FGA'].replace(0, 1)
        t_df['Net_Fouls'] = t_df['PFD'] - t_df['PF']
        t_cols = ['TEAM_ID', 'TEAM_NAME', 'GP', 'MIN', 'PF', 'PFD', 'FTA', 'FGA', 'FTr', 'Net_Fouls']
        t_df = t_df[[c for c in t_cols if c in t_df.columns]].sort_values('Net_Fouls', ascending=False)
        t_df.to_csv(os.path.join(DATA_DIR, "team_fouls.csv"), index=False)
        
        logging.info("Foul data saved.")
        return True
    except Exception as e:
        logging.error(f"Failed to fetch foul data: {e}")
        p_cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'PF', 'PFD', 'FTA', 'FGA', 'FTr', 'Net_Fouls']
        pd.DataFrame(columns=p_cols).to_csv(os.path.join(DATA_DIR, "player_fouls.csv"), index=False)
        t_cols = ['TEAM_ID', 'TEAM_NAME', 'GP', 'MIN', 'PF', 'PFD', 'FTA', 'FGA', 'FTr', 'Net_Fouls']
        pd.DataFrame(columns=t_cols).to_csv(os.path.join(DATA_DIR, "team_fouls.csv"), index=False)
        return False

def run_fetch_cycle():
    logging.info("--- Starting Fetch Cycle ---")
    fetch_standings()
    time.sleep(2)
    fetch_team_stats()
    time.sleep(2)
    fetch_players()
    time.sleep(2)
    fetch_advanced_players()
    time.sleep(2)
    fetch_cumfat()
    time.sleep(2)
    fetch_foul_data()
    logging.info("--- Fetch Cycle Complete ---")

if __name__ == "__main__":
    run_fetch_cycle()
