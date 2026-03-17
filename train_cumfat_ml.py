import pandas as pd
import json
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

def main():
    print("Loading data...")
    df = pd.read_csv('data/historical_fatigue.csv')

    # Drop any missing values in features or target
    features = ['MILES_FLOWN_7D', 'TZ_CROSSED_7D', 'GAMES_IN_7D', 'B2B_IN_7D', 'RECENT_WORKLOAD_MIN']
    target = 'MISSED_NEXT_GAME'
    
    df = df.dropna(subset=features + [target])

    X = df[features]
    y = df[target].astype(int)

    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Train
    print("Training Logistic Regression model...")
    model = LogisticRegression(random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))

    # Extract coefficients
    coeffs = model.coef_[0]
    
    # Let's map coefficients to feature names
    # And rescale them slightly if we want to build a simple formula.
    # We will save the unscaled or scaled coefficients.
    # To use them in fetcher.py without a standard scaler, we need the raw weights:
    # y = bias + x_raw * (coef / scale)
    # where scale is standard deviation from scaler.
    
    weights = {}
    total_abs_weight = 0
    raw_weights = {}
    
    print("\nFeature Importances (Standardized):")
    for feat, coef, scale in zip(features, coeffs, scaler.scale_):
        print(f"{feat}: {coef:.4f}")
        # To apply directly to raw data: weight = coef / scale
        raw_wt = float(coef / scale)
        raw_weights[feat] = raw_wt
        total_abs_weight += abs(coef)

    bias = float(model.intercept_[0])

    # Let's save the standardized coefficients to calculate relative impact/correlations
    correlations = {}
    for feat, coef in zip(features, coeffs):
        correlations[feat] = float(coef)

    model_data = {
        'weights': raw_weights,
        'bias': bias,
        'standardized_coefficients': correlations,
        'accuracy': float(acc),
        'intercept': bias,
        'means': {feat: float(mean) for feat, mean in zip(features, scaler.mean_)},
        'scales': {feat: float(scale) for feat, scale in zip(features, scaler.scale_)},
        'model_type': 'LogisticRegression'
    }

    # Save to JSON
    with open('data/cumfat_ml_weights.json', 'w') as f:
        json.dump(model_data, f, indent=4)
    print("\nSaved weights to data/cumfat_ml_weights.json")

if __name__ == '__main__':
    main()
