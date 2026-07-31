import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="NBA Interactive Scatter Plot", layout="wide")

st.title("🏀 NBA Player Stats Explorer")
st.markdown("Compare any metrics across NBA history using your unified master dataset.")

# 2. Load Data Safely
@st.cache_data
def load_data():
    # Looks for your file in the root folder or a 'data' folder
    for path in ['nba_master_stats.csv', 'data/nba_master_stats.csv']:
        try:
            return pd.read_csv(path)
        except FileNotFoundError:
            continue
    return None

df = load_data()

if df is None:
    st.error("⚠️ Could not find `nba_master_stats.csv`. Please make sure it is uploaded to your repository!")
else:
    # Identify standard identifier columns
    season_col = 'SEASON' if 'SEASON' in df.columns else ('season' if 'season' in df.columns else None)
    player_col = 'PLAYER_NAME' if 'PLAYER_NAME' in df.columns else ('player' if 'player' in df.columns else None)
    team_col = 'team' if 'team' in df.columns else ('TEAM' if 'TEAM' in df.columns else None)

    # 3. Sidebar Filters
    st.sidebar.header("Filter Options")
    
    # Season Filter
    if season_col:
        all_seasons = sorted(df[season_col].dropna().unique(), reverse=True)
        selected_season = st.sidebar.selectbox("Select Season / Year", all_seasons)
        df_filtered = df[df[season_col] == selected_season]
    else:
        df_filtered = df

    # 4. Metric Selection for Scatter Plot
    # Automatically extracts all numeric columns (Points, PER, VORP, TS%, Shot Distances, etc.)
    numeric_cols = df_filtered.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    # Clean up column names for display purposes if desired
    default_x = 'pts_per_game' if 'pts_per_game' in numeric_cols else numeric_cols[0]
    default_y = 'ast_per_game' if 'ast_per_game' in numeric_cols else (numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0])

    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("Select X-axis Metric", numeric_cols, index=numeric_cols.index(default_x) if default_x in numeric_cols else 0)
    with col2:
        y_axis = st.selectbox("Select Y-axis Metric", numeric_cols, index=numeric_cols.index(default_y) if default_y in numeric_cols else 1)

    # 5. Build and Display Scatter Plot
    if not df_filtered.empty:
        fig = px.scatter(
            df_filtered,
            x=x_axis,
            y=y_axis,
            text
