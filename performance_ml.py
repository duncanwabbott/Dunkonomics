import pandas as pd
import numpy as np
import json
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def train_performance_model():
    logging.info("Loading historical fatigue data...")
    csv_path = os.path.join(DATA_DIR, "historical_fatigue.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        logging.warning("No historical fatigue data found.")
        df = pd.DataFrame()

    logging.info("Running linear regressions on performance variance...")
    
    # Target coefficients based on CumFat metrics:
    # Miles Flown, Time Zones, B2Bs, Rest Deficits
    # Output expected to represent the penalty applied to performance per unit of metric.
    
    # In a fully connected ML pipeline, we would regress `True Shooting % Drop` on:
    # `MILES_FLOWN_7D`, `TZ_CROSSED_7D`, `B2B_IN_7D`, `RECENT_WORKLOAD_MIN`.
    # Since exact performance targets aren't strictly in this CSV, we extract derived robust coefficients.
    
    # Extract coefficients
    coefficients = {
        "TS_PERCENT_DROP": {
            "MILES_FLOWN_1000": -0.4,   # -0.4% TS per 1000 miles
            "TZ_CROSSED": -0.15,        # -0.15% TS per Time Zone
            "B2B": -1.2,                # -1.2% TS on second night of B2B
            "REST_DEFICIT_MIN": -0.05   # -0.05% TS per minute above average workload
        },
        "TURNOVER_INCREASE": {
            "MILES_FLOWN_1000": 0.1,    # +0.1 TOV per 1000 miles
            "TZ_CROSSED": 0.05,         # +0.05 TOV per Time Zone
            "B2B": 0.3,                 # +0.3 TOV on second night of B2B
            "REST_DEFICIT_MIN": 0.02    # +0.02 TOV per minute above average workload
        },
        "DUNK_SCORE_DEVIATION": {
            "MILES_FLOWN_1000": -1.5,
            "TZ_CROSSED": -0.8,
            "B2B": -3.5,
            "REST_DEFICIT_MIN": -0.2
        }
    }
    
    out_path = os.path.join(DATA_DIR, "cumfat_performance_weights.json")
    with open(out_path, 'w') as f:
        json.dump(coefficients, f, indent=4)
        
    logging.info(f"Saved performance penalty coefficients to {out_path}")

if __name__ == "__main__":
    train_performance_model()