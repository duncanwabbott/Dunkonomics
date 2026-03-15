import re

with open('app.py', 'r') as f:
    content = f.read()

replacement = """
    st.markdown("---")
    st.markdown("### Interactive DUNK Score Explorer")
    
    import plotly.express as px
    import os
    
    advanced_path = os.path.join(DATA_DIR, 'advanced_players.csv')
    if os.path.exists(advanced_path):
        df_advanced = pd.read_csv(advanced_path)
        
        # Display the highly polished dataframe
        st.dataframe(
            df_advanced.style.background_gradient(subset=['DUNK_SCORE'], cmap='Purples')
            .background_gradient(subset=['TS_PCT'], cmap='Greens')
            .format({
                'TS_PCT': '{:.3f}', 
                'AST_PCT': '{:.3f}', 
                'USG_PCT': '{:.3f}', 
                'PIE': '{:.3f}', 
                'TM_TOV_PCT': '{:.3f}', 
                'DUNK_SCORE': '{:.2f}'
            }),
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        st.markdown("### Offensive Efficiency: Usage vs True Shooting")
        
        # Filter for players with decent minutes to avoid noise
        df_plot = df_advanced[df_advanced['MIN'] > 15].copy()
        
        fig = px.scatter(
            df_plot,
            x='TS_PCT',
            y='USG_PCT',
            hover_name='PLAYER_NAME',
            hover_data=['TEAM_ABBREVIATION', 'DUNK_SCORE'],
            color='DUNK_SCORE',
            color_continuous_scale='Purples',
            title='Usage Rate vs True Shooting Percentage (Min > 15 MPG)',
            labels={'TS_PCT': 'True Shooting %', 'USG_PCT': 'Usage Rate %'}
        )
        fig.update_layout(template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Advanced player data is syncing in the background. Please check back shortly.")
"""

pattern = r'    st\.markdown\("---"\)\n    st\.markdown\("### Interactive DUNK Score Explorer"\)\n    st\.info\("🔒 The live proprietary database recalculates nightly at 3:00 AM EST\. \*\*Upgrade to the Nerd Tier \(\$10/mo\)\*\* to access the full sortable table and API endpoints\."\)\n    mock_dunk = pd\.DataFrame\(\{"Player": \["Nikola Jokic", "Shai Gilgeous-Alexander", "Luka Doncic", "Giannis Antetokounmpo", "Jayson Tatum"\], "Team": \["DEN", "OKC", "DAL", "MIL", "BOS"\], "TS%": \[64\.2, 63\.8, 61\.5, 65\.1, 60\.2\], "AST%": \[38\.5, 32\.1, 41\.2, 31\.0, 22\.4\], "USG%": \[29\.1, 32\.5, 36\.0, 32\.8, 29\.5\], "DUNK Score": \[84\.2, 81\.5, 79\.8, 77\.4, 72\.1\]\}\)\n    st\.dataframe\(mock_dunk\.style\.background_gradient\(subset=\[\'DUNK Score\'\], cmap=\'Purples\'\), hide_index=True, use_container_width=True\)'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('app.py', 'w') as f:
    f.write(content)
