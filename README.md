# Dunkonomics

Advanced NBA statistics dashboard built with Streamlit and the `nba_api`. Features proprietary metrics like the DUNK Score.

## Architecture
- **Frontend:** Streamlit (`app.py`)
- **Backend/Data:** Python fetcher (`fetcher.py`) pulling live stats from `stats.nba.com`.
- **Storage:** Local `.csv` caching layer (`data/`).

## Local Development
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```