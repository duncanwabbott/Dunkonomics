import pandas as pd
import json
import numpy as np
from sklearn.linear_model import Ridge, LinearRegression

# 1. Refine Target Variable
df = pd.read_csv('data/historical_dunk_impact.csv')

# Proxy the team's overall strength
team_strength = df.groupby(['TEAM_ID', 'SEASON'])['NET_RATING'].transform('mean')
df['Delta_NET_RATING'] = df['NET_RATING'] - team_strength

# 2. Feature Engineering
df['USG_x_TS'] = df['USG_PCT'] * df['TS_PCT']

candidate_features = ['USG_PCT', 'TS_PCT', 'AST_PCT', 'TOV_PCT', 'OREB_PCT', 'DREB_PCT', 'STL_PCT', 'BLK_PCT', 'PIE', 'USG_x_TS']

df = df.dropna(subset=candidate_features + ['Delta_NET_RATING'])

def compute_vif(X, feature_index):
    y = X[:, feature_index]
    X_other = np.delete(X, feature_index, axis=1)
    model = LinearRegression()
    model.fit(X_other, y)
    r_sq = model.score(X_other, y)
    return 1.0 / (1.0 - r_sq) if r_sq < 1.0 else float('inf')

# VIF Calculation Loop
features = candidate_features.copy()
dropped = []

while True:
    X_vif = df[features].values
    vifs = [compute_vif(X_vif, i) for i in range(len(features))]
    max_vif = max(vifs)
    max_index = vifs.index(max_vif)
    
    if max_vif > 5.0:
        dropped_feature = features[max_index]
        dropped.append((dropped_feature, float(max_vif)))
        features.remove(dropped_feature)
    else:
        break

final_features = features

# 3. Train the Model
X = df[final_features]
y = df['Delta_NET_RATING']

model = Ridge(alpha=1.0)
model.fit(X, y)

# 4. Extract & Evaluate
r_squared = float(model.score(X, y))

weights = {k: float(v) for k, v in zip(final_features, model.coef_)}
weights['intercept'] = float(model.intercept_)

print("Final Features:", final_features)
print("Dropped Features:", dropped)
print("R-squared:", r_squared)
print("Weights:", weights)

# 5. Report
with open('data/dunk_ml_weights.json', 'w') as f:
    json.dump({'weights': weights, 'r_squared': r_squared, 'dropped': dropped}, f, indent=4)

with open('shared_memory/angie_update.md', 'w') as f:
    f.write("# DUNK ML Audit Framework Results\n\n")
    f.write("## 1. Target Variable Refinement\n")
    f.write("To isolate the player's individual impact from the 'coattail effect' of a strong team, we calculated the `Delta_NET_RATING`. This was achieved by approximating the team's overall strength as the average `NET_RATING` of the team per season and subtracting it from the player's raw `NET_RATING`.\n\n")
    
    f.write("## 2. Feature Engineering & VIF Checks\n")
    f.write("We added an interaction term `USG_x_TS` (Usage Rate * True Shooting %) to capture scoring efficiency relative to volume.\n")
    f.write("To prevent multicollinearity, we calculated the Variance Inflation Factor (VIF) and iteratively dropped features with VIF > 5. ")
    if dropped:
        f.write("The following features were dropped due to high collinearity:\n")
        for feat, vif in dropped:
            f.write(f"- **{feat}** (VIF: {vif:.2f})\n")
    else:
        f.write("No features exhibited a VIF > 5.0.\n")
    f.write("\n")
    
    f.write("## 3. Ridge Regression Model Evaluation\n")
    f.write(f"A Ridge Regression (L2 regularization) model was trained targeting the newly engineered `Delta_NET_RATING`. The resulting explanatory power (R-squared) over the dataset is **{r_squared:.4f}**.\n\n")
    
    f.write("## 4. Final DUNK Formula Weights\n")
    f.write("The extracted coefficients from the Ridge Regression provide the new, empirically backed weights for the DUNK metric:\n\n")
    f.write("| Metric | Weight (Coefficient) |\n")
    f.write("|---|---|\n")
    for k, v in weights.items():
        f.write(f"| {k} | {v:.4f} |\n")
    f.write("\nThese weights have been saved to `data/dunk_ml_weights.json` for future deployment.\n")
