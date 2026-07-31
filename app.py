import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="NBA Player Analytics", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a sleek dark sports analytics theme with high contrast visible text
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .main-header {
        font-size: 2.4rem;
        font-weight: 800;
        color: #60A5FA;
        margin-bottom: 0.1rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1rem;
        color: #9CA3AF;
        margin-bottom: 1.5rem;
    }
    /* Style metric cards for dark mode */
    div[data-testid="metric-container"] {
        background-color: #1F2937;
        border: 1px solid #374151;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="metric-container"] label {
        color: #9CA3AF !important;
        font-weight: 600;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #F9FAFB !important;
        font-weight: 700;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1F2937;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
        color: #E5E7EB !important;
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

    def format_col_name(col):
        return col.replace('_', ' ').title().replace('Pts', 'Points').replace('Ast', 'Assists').replace('Trb', 'Rebounds')

    # 3. Sidebar Configuration
    st.sidebar.header("🎯 Dashboard Filters")
    
    if season_col:
        seasons_list = sorted(df[season_col].dropna().unique(), reverse=True)
        selected_season = st.sidebar.selectbox("Select Season", seasons_list)
        df_filtered = df[df[season_col] == selected_season].copy()
    else:
        df_filtered = df.copy()

    if games_col and games_col in df_filtered.columns:
        max_g = int(df_filtered[games_col].max()) if not df_filtered[games_col].empty else 82
        min_games = st.sidebar.slider("Minimum Games Played", min_value=1, max_value=max_g, value=15)
        df_filtered = df_filtered[df_filtered[games_col] >= min_games]

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

    if top_n_choice != "Show All":
        sort_col = y_axis if rank_by == "Y-Axis Metric" else x_axis
        df_filtered = df_filtered.nlargest(int(top_n_choice), sort_col)

    # 5. Build Clean Plotly Scatter Plot (Dark Theme Template)
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
            marker=dict(size=12, opacity=0.9, line=dict(width=1, color='#1F2937'))
        )

        fig.update_layout(
            height=650,
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#111827",
            xaxis_title=format_col_name(x_axis),
            yaxis_title=format_col_name(y_axis),
            hoverlabel=dict(bgcolor="#1F2937", font_size=13, font_family="Arial", font_color="white"),
            margin=dict(l=20, r=20, t=50, b=20),
            font=dict(color="#F3F4F6")
        )

        st.markdown("💡 **Click on any dot in the chart to load that player's specific headshot and bio!**")
        
        chart_event = st.plotly_chart(fig, width="stretch", on_select="rerun")

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
            
            p_col1, p_col2 = st.columns([1, 6])
            
            with p_col1:
                if id_col and pd.notna(player_data[id_col]):
                    pid = str(player_data[id_col])
                    img_url = f"https://www.basketball-reference.com/req/202106291/images/headshots/{pid}.jpg"
                    st.image(img_url, width=130)
                else:
                    st.info("No Photo")

            with p_col2:
                st.markdown(f"## {selected_player}")
                
                ht_in = player_data.get('ht_in_in', None)
                height_str = f"{int(ht_in // 12)}'{int(ht_in % 12)}\"" if pd.notna(ht_in) else "N/A"
                
                wt_lbs = player_data.get('wt', None)
                weight_str = f"{int(wt_lbs)} lbs" if pd.notna(wt_lbs) else "N/A"
                
                team_str = player_data.get(team_col, 'N/A')
                szn_str = player_data.get(season_col, 'N/A')
                gm_str = int(player_data.get(games_col, 0)) if pd.notna(player_data.get(games_col)) else 'N/A'

                st.markdown(f"**Team:** {team_str} &nbsp;|&nbsp; **Season:** {szn_str} &nbsp;|&nbsp; **Games:** {gm_str}")
                st.markdown(f"**Height:** {height_str} &nbsp;|&nbsp; **Weight:** {weight_str}")

            st.markdown("<br>", unsafe_allow_html=True)

            def safe_stat(col, is_pct=False):
                val = player_data.get(col, None)
                if pd.isna(val): return "-"
                if is_pct: return f"{val * 100:.1f}%"
                return f"{val:.1f}"

            m1, m2, m3, m4, m5, m6, m7, m8, m9 = st.columns(9)
            m1.metric("PPG", safe_stat('pts_per_game'))
            m2.metric("RPG", safe_stat('trb_per_game'))
            m3.metric("APG", safe_stat('ast_per_game'))
            m4.metric("SPG", safe_stat('stl_per_game'))
            m5.metric("BPG", safe_stat('blk_per_game'))
            m6.metric("MPG", safe_stat('mp_per_game'))
            m7.metric("FG%", safe_stat('fg_percent', is_pct=True))
            m8.metric("3P%", safe_stat('x3p_percent', is_pct=True))
            m9.metric("FT%", safe_stat('ft_percent', is_pct=True))

        with st.expander("📊 View Complete Data Table"):
            st.dataframe(df_filtered, width="stretch")

    else:
        st.warning("No players found matching the current filters. Try lowering the Minimum Games Played filter.")
