import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Page Config & CSS Theme
st.set_page_config(page_title="NBA Player Analytics", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #1D428A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1rem; color: #555555; margin-bottom: 1.5rem; }
    .stApp { background-color: #F8F9FA; }
    /* Style the metric boxes to look like a sports card */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏀 NBA Player Stats & Historical Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interactively filter, compare metrics, and inspect player performance across eras.</div>', unsafe_allow_html=True)

# 2. Data Loader
@st.cache_data
def load_data():
    for path in ['nba_master_stats.csv', 'data/nba_master_stats.csv']:
        try:
            return pd.read_csv(path)
        except FileNotFoundError:
            continue
    return None

df = load_data()

if df is None:
    st.error("⚠️ `nba_master_stats.csv` not found. Please verify it is uploaded to your repository.")
else:
    # Standardize Column Identifiers
    season_col = 'SEASON' if 'SEASON' in df.columns else ('season' if 'season' in df.columns else None)
    player_col = 'PLAYER_NAME' if 'PLAYER_NAME' in df.columns else ('player' if 'player' in df.columns else None)
    team_col = 'team' if 'team' in df.columns else ('TEAM' if 'TEAM' in df.columns else None)
    id_col = 'player_id' if 'player_id' in df.columns else None
    games_col = 'g' if 'g' in df.columns else ('G' if 'G' in df.columns else None)

    # Clean Name Helper for Dropdowns
    def format_col_name(col):
        return col.replace('_', ' ').title().replace('Pts', 'Points').replace('Ast', 'Assists').replace('Trb', 'Rebounds')

    # 3. Sidebar Configuration
    st.sidebar.header("🎯 Dashboard Filters")
    
    # Season Filter
    if season_col:
        seasons_list = sorted(df[season_col].dropna().unique(), reverse=True)
        selected_season = st.sidebar.selectbox("Select Season", seasons_list)
        df_filtered = df[df[season_col] == selected_season].copy()
    else:
        df_filtered = df.copy()

    # Games Played Filter 
    if games_col and games_col in df_filtered.columns:
        max_g = int(df_filtered[games_col].max()) if not df_filtered[games_col].empty else 82
        min_games = st.sidebar.slider("Minimum Games Played", min_value=1, max_value=max_g, value=15)
        df_filtered = df_filtered[df_filtered[games_col] >= min_games]

    # Metric Extraction
    numeric_cols = df_filtered.select_dtypes(include=['float64', 'int64']).columns.tolist()
    ignore_cols = [season_col, 'player_id', 'hof', 'ht_in_in', 'wt']
    metric_options = [c for c in numeric_cols if c not in ignore_cols]

    default_x = 'pts_per_game' if 'pts_per_game' in metric_options else metric_options[0]
    default_y = 'ast_per_game' if 'ast_per_game' in metric_options else (metric_options[1] if len(metric_options) > 1 else metric_options[0])

    st.sidebar.markdown("---")
    st.sidebar.subheader("🏆 Leaderboard Cutoff")
    top_n_choice = st.sidebar.selectbox("Show Top N Players", ["Show All", 10, 15, 20, 30, 50, 100], index=4)

    if top_n_choice != "Show All":
        rank_by = st.sidebar.radio("Rank Top Players By:", ["Y-Axis Metric", "X-Axis Metric"])
    else:
        rank_by = None

    # 4. Metric Selectors
    col_x, col_y = st.columns(2)
    with col_x:
        x_axis = st.selectbox("Select X-Axis Metric", metric_options, index=metric_options.index(default_x) if default_x in metric_options else 0, format_func=format_col_name)
    with col_y:
        y_axis = st.selectbox("Select Y-Axis Metric", metric_options, index=metric_options.index(default_y) if default_y in metric_options else 1, format_func=format_col_name)

    # Filter Top N
    if top_n_choice != "Show All":
        sort_col = y_axis if rank_by == "Y-Axis Metric" else x_axis
        df_filtered = df_filtered.nlargest(int(top_n_choice), sort_col)

    # 5. Build Clean Plotly Scatter Plot
    if not df_filtered.empty:
        show_labels = True if (top_n_choice != "Show All" and int(top_n_choice) <= 25) else False

        fig = px.scatter(
            df_filtered,
            x=x_axis,
            y=y_axis,
            text=player_col if show_labels else None,
            color=team_col if team_col else None,
            hover_name=player_col,
            custom_data=[player_col], 
            hover_data={
                x_axis: ':.2f',
                y_axis: ':.2f',
                team_col: True,
                season_col: True,
                games_col: True if games_col else False
            },
            title=f"<b>{format_col_name(y_axis)}</b> vs <b>{format_col_name(x_axis)}</b> ({selected_season})"
        )

        fig.update_traces(
            textposition='top center',
            marker=dict(size=11, opacity=0.85, line=dict(width=1, color='white'))
        )

        fig.update_layout(
            height=650,
            template="plotly_white",
            xaxis_title=format_col_name(x_axis),
            yaxis_title=format_col_name(y_axis),
            hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial"),
            margin=dict(l=20, r=20, t=50, b=20)
        )

        st.markdown("💡 **Click on any dot in the chart to load that player's specific headshot and bio!**")
        
        # Catch the click event from the user
        chart_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

        # 6. Interactive Player Spotlight Card with Headshots & Full Stat Line
        st.markdown("---")
        st.subheader("👤 Player Spotlight")
        
        selected_player = None
        if chart_event and len(chart_event.selection["points"]) > 0:
            selected_player = chart_event.selection["points"][0]["customdata"][0]
        else:
            selected_player = df_filtered[player_col].iloc[0]

        if selected_player:
            player_data = df_filtered[df_filtered[player_col] == selected_player].iloc[0]
            
            # Layout: Image on left, Bio on right
            p_col1, p_
