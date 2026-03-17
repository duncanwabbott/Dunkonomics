# Angie Update: CumFat ML Upgrade
### Phase 2 & 3: Machine Learning Pipeline & UI Integration

**Overview:**
The CumFat metric has been successfully upgraded from a static, heuristic-based formula to a Machine Learning-backed predictive model using historical fatigue and absence data (`historical_fatigue.csv`).

**1. Regression Results & Accuracy:**
- **Model Type:** Logistic Regression using `scikit-learn`.
- **Target Variable:** `MISSED_NEXT_GAME`
- **Accuracy:** The model achieves ~71.7% accuracy with a weighted F1-score of 0.76.

**2. Key Insights & Feature Correlations:**
Standardized coefficients highlight what actually drives missed games in the modern NBA:
- **`RECENT_WORKLOAD_MIN` (-0.605)**: Strongest predictor. A lower workload leading into a game strongly predicts absence, highlighting that players managing minor tweaks or load limits are most at risk of resting.
- **`GAMES_IN_7D` (-0.225)**: Playing fewer games in the week prior also strongly correlates to missing the upcoming game.
- **`B2B_IN_7D` (-0.038)**: Slight negative correlation.
- **`TZ_CROSSED_7D` (+0.027)**: Positive correlation. Crossing more time zones disrupts circadian rhythms and measurably increases the probability of an absence.
- **`MILES_FLOWN_7D` (+0.008)**: Positive correlation. Raw travel distance plays a smaller, but measurable role in injury/rest risk.

**3. The New Formula:**
The backend `fetcher.py` was rewritten to read the exact extracted model weights from `data/cumfat_ml_weights.json`. 
It calculates the log-odds of missing the next game using the raw coefficients and bias:
`log_odds = bias + w_miles * miles_flown + w_tz * time_zones_crossed + w_games * len(p_df) + w_b2b * b2b_count + w_workload * recent_workload`

This is then passed through a standard sigmoid function `1 / (1 + e^-log_odds)` to generate a probability, which is scaled up to a 0-100 CumFat score to integrate seamlessly with the existing frontend.

**4. UI Integration:**
The CumFat dashboard on the "Player Micro" tab in `app.py` has been updated to reflect its new predictive nature. The methodology section now explains the model formulation, displays the 71.7% accuracy, and explicitly breaks down the machine learning correlations and insights.
