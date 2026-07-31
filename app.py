import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration & Professional Sports Theme
st.set_page_config(
    page_title="Pro NBA Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Global Theme */
    .stApp {
        background-color: #12141C;
        color: #F3F4F6;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Styling */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 50%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #9CA3AF;
        margin-bottom: 1.5rem;
    }

    /* Glassmorphism Containers */
    .glass-card {
        background: rgba(20, 24, 33, 0.85);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }

    /* Metric Box Styling */
    div[data-testid="metric-container"] {
        background: rgba(28, 35, 49, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 14px;
        border-radius: 12px;
        text-align: center;
    }
    div[data-testid="metric-container"] label {
        color: #9CA3AF !important;
        font-weight: 600;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #F9FAFB !important;
        font-weight: 800;
        font-size: 1.35rem !important;
    }

    /* Sidebar Tweaks */
    [data-testid="stSidebar"] {
        background-color: #0A0C10;
        border-right: 1px solid rgba(255, 255, 255, 0.04);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏀 Pro NBA Analytics Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Advanced player performance mapping with visual reference benchmarks and deep metrics.</div>', unsafe_allow_html=True)

# 2. Data Loader with Caching
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
    st.error("⚠️ `nba_master_stats.csv` not found. Please ensure your dataset is properly uploaded.")
else:
    season_col = 'SEASON' if 'SEASON' in df.columns else ('season' if 'season' in df.columns else None)
    player_col = 'PLAYER_NAME' if 'PLAYER_NAME' in df.columns else ('player' if 'player' in df.columns else None)
    team_col = 'team' if 'team' in df.columns else ('TEAM' if 'TEAM' in df.columns else None)
    id_col = 'player_id' if 'player_id' in df.columns else None
    games_col = 'g' if 'g' in df.columns else ('G' if 'G' in df.columns else None)

    def format_col_name(col):
        return col.replace('_', ' ').title().replace('Pts', 'Points').replace('Ast', 'Assists').replace('Trb', 'Rebounds')

    # 3. Sidebar Configuration Controls
    st.sidebar.header("🎯 Dashboard Controls")
    
    if season_col:
        seasons_list = sorted(df[season_col].dropna().unique(), reverse=True)
        selected_season = st.sidebar.selectbox("📅 Select Season", seasons_list)
        df_filtered = df[df[season_col] == selected_season].copy()
    else:
        df_filtered = df.copy()

    if games_col and games_col in df_filtered.columns:
        max_g = int(df_filtered[games_col].max()) if not df_filtered[games_col].empty else 82
        min_games = st.sidebar.slider("🛡️ Minimum Games Played", min_value=1, max_value=max_g, value=20)
        df_filtered = df_filtered[df_filtered[games_col] >= min_games]

    numeric_cols = df_filtered.select_dtypes(include=['float64', 'int64']).columns.tolist()
    ignore_cols = [season_col, 'player_id', 'hof', 'ht_in_in', 'wt']
    metric_options = [c for c in numeric_cols if c not in ignore_cols]

    default_x = 'pts_per_game' if 'pts_per_game' in metric_options else metric_options[0]
    default_y = 'ast_per_game' if 'ast_per_game' in metric_options else (metric_options[1] if len(metric_options) > 1 else metric_options[0])

    st.sidebar.markdown("---")
    st.sidebar.subheader("🏆 Leaderboard Cutoff")
    top_n_choice = st.sidebar.selectbox("Show Top N Players", ["Show All", 10, 15, 20, 30, 50, 100], index=3)

    rank_by = st.sidebar.radio("Rank Top Players By:", ["Y-Axis Metric", "X-Axis Metric"]) if top_n_choice != "Show All" else None

    # 4. Metric Selection Panel
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎛️ Chart Metric Selection")
    col_x, col_y = st.columns(2)
    with col_x:
        x_axis = st.selectbox("X-Axis Metric", metric_options, index=metric_options.index(default_x) if default_x in metric_options else 0, format_func=format_col_name)
    with col_y:
        y_axis = st.selectbox("Y-Axis Metric", metric_options, index=metric_options.index(default_y) if default_y in metric_options else 1, format_func=format_col_name)
    st.markdown('</div>', unsafe_allow_html=True)

    if top_n_choice != "Show All":
        sort_col = y_axis if rank_by == "Y-Axis Metric" else x_axis
        df_filtered = df_filtered.nlargest(int(top_n_choice), sort_col)

    # 5. Build Scatter Plot with Benchmark Lines & Vibrant Colored Circles
    if not df_filtered.empty:
        fig = px.scatter(
            df_filtered,
            x=x_axis,
            y=y_axis,
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

        # Style markers as vibrant colored circles
        fig.update_traces(marker=dict(size=12, opacity=0.85, line=dict(width=1, color='rgba(255,255,255,0.4)')))

        # Calculate League Averages for Crosshair Benchmark Lines
        x_mean = df_filtered[x_axis].mean()
        y_mean = df_filtered[y_axis].mean()

        fig.add_vline(
            x=x_mean, 
            line_dash="dash", 
            line_color="rgba(255, 255, 255, 0.3)", 
            annotation_text="Avg", 
            annotation_position="top",
            annotation_font_color="#9CA3AF"
        )
        fig.add_hline(
            y=y_mean, 
            line_dash="dash", 
            line_color="rgba(255, 255, 255, 0.3)", 
            annotation_text="Avg", 
            annotation_position="right",
            annotation_font_color="#9CA3AF"
        )

        fig.update_layout(
            height=720,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 18, 25, 0.75)",
            xaxis_title=format_col_name(x_axis),
            yaxis_title=format_col_name(y_axis),
            hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Inter", font_color="white"),
            margin=dict(l=30, r=30, t=60, b=30),
            font=dict(color="#F3F4F6", family="Inter"),
            showlegend=True
        )

        st.markdown("💡 *Interactive Tip: Click on any player point on the scatter plot to inspect their comprehensive scouting profile below!*")
        
        chart_event = st.plotly_chart(fig, width="stretch", on_select="rerun")

        # 6. Premium Player Spotlight Card
        st.markdown("---")
        st.markdown("### 👤 Player Scouting Spotlight Card")
        
        selected_player = None
        if chart_event and len(chart_event.selection["points"]) > 0:
            selected_player = chart_event.selection["points"][0]["customdata"][0]
        else:
            selected_player = df_filtered[player_col].iloc[0]

        if selected_player:
            player_data = df_filtered[df_filtered[player_col] == selected_player].iloc[0]
            
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            p_col1, p_col2 = st.columns([1, 5], gap="large")
            
            with p_col1:
                if id_col and pd.notna(player_data[id_col]):
                    pid = str(player_data[id_col])
                    img_url = f"https://www.basketball-reference.com/req/202106291/images/headshots/{pid}.jpg"
                    st.image(img_url, width=150)
                else:
                    st.info("No Photo Available")

            with p_col2:
                st.markdown(f"## **{selected_player}**")
                
                ht_in = player_data.get('ht_in_in', None)
                height_str = f"{int(ht_in // 12)}'{int(ht_in % 12)}\"" if pd.notna(ht_in) else "N/A"
                wt_lbs = player_data.get('wt', None)
                weight_str = f"{int(wt_lbs)} lbs" if pd.notna(wt_lbs) else "N/A"
                
                team_str = player_data.get(team_col, 'N/A')
                szn_str = player_data.get(season_col, 'N/A')
                gm_str = int(player_data.get(games_col, 0)) if pd.notna(player_data.get(games_col)) else 'N/A'

                b1, b2, b3, b4 = st.columns(4)
                b1.markdown(f"**Team:** `{team_str}`")
                b2.markdown(f"**Season:** `{szn_str}`")
                b3.markdown(f"**Games Played:** `{gm_str}`")
                b4.markdown(f"**Height / Weight:** `{height_str} / {weight_str}`")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📊 Per-Game Box Score & Shooting Efficiency")

            def safe_stat(col, is_pct=False):
                val = player_data.get(col, None)
                if pd.isna(val): return "-"
                if is_pct: return f"{val * 100:.1f}%"
                return f"{val:.1f}"

            s1, s2, s3, s4, s5, s6, s7, s8, s9 = st.columns(9)
            s1.metric("PPG", safe_stat('pts_per_game'))
            s2.metric("RPG", safe_stat('trb_per_game'))
            s3.metric("APG", safe_stat('ast_per_game'))
            s4.metric("SPG", safe_stat('stl_per_game'))
            s5.metric("BPG", safe_stat('blk_per_game'))
            s6.metric("MPG", safe_stat('mp_per_game'))
            s7.metric("FG%", safe_stat('fg_percent', is_pct=True))
            s8.metric("3P%", safe_stat('x3p_percent', is_pct=True))
            s9.metric("FT%", safe_stat('ft_percent', is_pct=True))

            st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("📊 View Complete Filtered Data Table"):
            st.dataframe(df_filtered, width="stretch")

    else:
        st.warning("No players found matching the current filters. Try lowering the Minimum Games Played threshold.")
