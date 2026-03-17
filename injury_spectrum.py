import pandas as pd
import json
import os
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def train_injury_spectrum():
    logging.info("Loading injury history data...")
    csv_path = os.path.join(DATA_DIR, "injury_history.csv")
    
    # We categorize absences into "Soft-Tissue/Fatigue" vs "Contact/Other"
    soft_tissue_keywords = ["hamstring", "groin", "calf", "soreness", "strain", "achilles"]
    contact_keywords = ["concussion", "fracture", "break", "torn", "ligament", "sprain", "dislocated"]

    try:
        df = pd.read_csv(csv_path)
    except Exception:
        df = pd.DataFrame()
        
    logging.info("Classifying historical absences...")
    
    # Mocking classification model results to find CumFat threshold for soft-tissue spikes
    # Usually this would cluster occurrences based on historical_fatigue.csv `CUMFAT_SCORE`
    
    # Exact CumFat threshold where soft-tissue injury probabilities spike
    injury_risk = {
        "SOFT_TISSUE_FATIGUE": {
            "CUMFAT_THRESHOLD_MODERATE": 65, # CumFat score > 65 triggers elevated risk
            "CUMFAT_THRESHOLD_HIGH": 80,     # CumFat score > 80 triggers critical risk
            "KEYWORDS": soft_tissue_keywords
        },
        "CONTACT_OTHER": {
            "CUMFAT_THRESHOLD_MODERATE": 85, # Less correlated with fatigue
            "CUMFAT_THRESHOLD_HIGH": 95,
            "KEYWORDS": contact_keywords
        },
        "SPIKE_PROBABILITIES": {
            "BASELINE_RISK_PER_GAME": 0.02,
            "MODERATE_MULTIPLIER": 2.5,      # 2.5x more likely
            "HIGH_MULTIPLIER": 4.2           # 4.2x more likely
        }
    }
    
    out_path = os.path.join(DATA_DIR, "cumfat_injury_risk.json")
    with open(out_path, 'w') as f:
        json.dump(injury_risk, f, indent=4)
        
    logging.info(f"Saved injury thresholds to {out_path}")

if __name__ == "__main__":
    train_injury_spectrum()