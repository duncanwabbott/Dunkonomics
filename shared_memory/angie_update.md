# Dunkonomics Deployment Preparation Updates

Date: 2026-03-15

## Overview
Dunkonomics has been updated to support ephemeral deployment on Streamlit Community Cloud. Because Streamlit Cloud instances spin down, local CSV databases stored in `data/` are lost. The following updates were made to ensure a seamless experience for the first user accessing the app after a reboot.

## Summary of Changes
1. **Automated Ephemeral Data Fetching:** 
   - Implemented an automated freshness check in `app.py` (`check_and_fetch_data()`).
   - If the `data/*.csv` files (e.g., `standings.csv`, `team_stats.csv`, `players.csv`, `advanced_players.csv`) are missing or older than 12 hours, the app automatically runs `fetcher.run_fetch_cycle()` with a user-friendly Streamlit spinner to populate the data.
2. **Optimized Caching Strategies:**
   - Modified the data loading functions (`load_standings`, `load_team_stats`, `load_players`) to use `@st.cache_data(ttl=3600)`.
   - Created a new cached loader for advanced player stats (`load_advanced_players`) to prevent repeated disk I/O reads during UI interaction.
3. **Dependency Tracking:**
   - Created a `requirements.txt` file in the root directory mapping out all core packages required for Streamlit Cloud deployment:
     - `streamlit`
     - `pandas`
     - `numpy`
     - `nba_api`
     - `plotly`
     - `matplotlib`
     - `urllib3`

The application is now resilient to server restarts and will dynamically spin up its own data warehouse on the fly!
