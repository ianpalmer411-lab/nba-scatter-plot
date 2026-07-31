import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration & Modern App Styling (Spotify/Twitter Dark Theme Aesthetic)
st.set_page_config(
    page_title="NBA Pulse • Analytics & Player Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Main App Background & Typography */
    .stApp {
        background-color: #000000;
        color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Modern Header Styling */
    .app-header {
        display: flex;
        flex-direction: column;
        gap: 4px;
        margin-bottom: 1.5rem;
        padding-top: 0.5rem;
    }
    .app-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        font-weight: 400;
    }

    /* Sleek Card Containers (Spotify/Twitter Card Style) */
    .main-card {
        background: #121214;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        margin-bottom: 20px;
    }
    .spotlight-card {
        background: linear-gradient(145deg, #121216 0%, #1a1a22 100%);
        border: 1px solid rgba(56, 189, 248, 0.15);
        padding: 28px;
        border-radius: 20px;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7);
        margin-bottom: 24px;
    }

    /* Pill Badges & Tags */
    .badge-pill {
        display: inline-block;
        background: rgba(56, 189, 248, 0.1);
        color: #38BDF8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(56, 189, 248, 0.2);
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Metric Grid Boxes (Modern App Style) */
    div[data-testid="metric-container"] {
        background: #18181C;
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 14px;
        border-radius: 14px;
        text-align: center;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="metric-container"]:hover {
        border-color: rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }
    div[data-testid="metric-container"] label {
        color: #94A3B8 !important;
        font-weight: 600;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 1.4rem !important;
        letter-spacing: -0.02em;
    }

    /* Sidebar Streamlining */
    [data-testid="stSidebar"] {
        background-color: #08080A;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* Input styling */
    .stSelectbox div[data-baseweb="select"], .stSlider {
        background-color: #141418;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
    <div class="app-header">
        <div class="app-title">🏀 NBA Pulse <span style="font-size: 1rem; background: #38BDF8; color: #000; padding: 2px 8px; border-radius: 6px; font-weight: 700;">PRO</span></div>
        <div class="app-subtitle">Streamlined historical analytics, interactive scatter matrices, and scouting dossiers.</div>
    </div>
""", unsafe_allow_html=True)

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
    st.error("⚠️ `nba_master_stats.csv` not found in repository. Please ensure the dataset file is present.")
else:
    season_col = 'SEASON' if 'SEASON' in df.columns else ('season' if 'season' in df.columns else None)
    player_col = 'PLAYER_NAME' if 'PLAYER_NAME' in df.columns else ('player' if 'player' in df.columns else None)
    team_col = 'team' if 'team' in df.columns else ('TEAM' if 'TEAM' in df.columns else None)
    id_col = 'player_id' if 'player_id' in df.columns else None
    games_col = 'g' if 'g' in df.columns else ('G' if 'G' in df.columns else None)

    def format_col_name(col):
        return col.replace('_', ' ').title().replace('Pts', 'Points').replace('Ast', 'Assists').replace('Trb', 'Rebounds')

    # 3. Sidebar Controls
    st.sidebar.markdown("### 🎛️ Dashboard Controls")
    
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
    st.sidebar.markdown("### 🏆 Leaderboard Filter")
    top_n_choice = st.sidebar.selectbox("Show Top N Players", ["Show All", 10, 15, 20, 30, 50, 100], index=3)

    rank_by = st.sidebar.radio("Rank Top Players By:", ["Y-Axis Metric", "X-Axis Metric"]) if top_n_choice != "Show All" else None

    # 4. Metric Selection Card
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Metric Matrix Selection")
    col_x, col_y = st.columns(2, gap="medium")
    with col_x:
        x_axis = st.selectbox("X-Axis Parameter", metric_options, index=metric_options.index(default_x) if default_x in metric_options else 0, format_func=format_col_name)
    with col_y:
        y_axis = st.selectbox("Y-Axis Parameter", metric_options, index=metric_options.index(default_y) if default_y in metric_options else 1, format_func=format_col_name)
    st.markdown('</div>', unsafe_allow_html=True)

    if top_n_choice != "Show All":
        sort_col = y_axis if rank_by == "Y-Axis Metric" else x_axis
        df_filtered = df_filtered.nlargest(int(top_n_choice), sort_col)

    # 5. Build Scatter Plot with Modern Polish
    if not df_filtered.empty:
        p_series = df_filtered[player_col] if player_col in df_filtered.columns else pd.Series(['Unknown'] * len(df_filtered))
        t_series = df_filtered[team_col] if team_col in df_filtered.columns else pd.Series(['N/A'] * len(df_filtered))
        g_series = df_filtered[games_col] if games_col and games_col in df_filtered.columns else pd.Series([0] * len(df_filtered))
        s_series = df_filtered[season_col] if season_col in df_filtered.columns else pd.Series([selected_season] * len(df_filtered))

        fig = px.scatter(
            df_filtered,
            x=x_axis,
            y=y_axis,
            color=team_col if team_col else None,
            custom_data=[p_series, t_series, g_series, s_series],
            title=f"<b>{format_col_name(y_axis)}</b> vs <b>{format_col_name(x_axis)}</b> ({selected_season})"
        )

        # Crisp, modern circular points with refined hover cards (Spotify/Twitter dark popup style)
        fig.update_traces(
            marker=dict(size=12, opacity=0.9, line=dict(width=1.5, color='rgba(255,255,255,0.6)')),
            hovertemplate=(
                "<b style='font-size: 16px; color: #38BDF8;'>%{customdata[0]}</b><br>"
                "<span style='color: #94A3B8; font-size: 12px;'>TEAM: <b>%{customdata[1]}</b> &bull; SEASON: %{customdata[3]}</span><br>"
                "──────────────────────────────<br>"
                f"<b>{format_col_name(y_axis)}:</b> %{{y:.2f}}<br>"
                f"<b>{format_col_name(x_axis)}:</b> %{{x:.2f}}<br>"
                "<b>Games Played:</b> %{customdata[2]}<br>"
                "<extra></extra>"
            )
        )

        # League Average Benchmark Crosshairs
        x_mean = df_filtered[x_axis].mean()
        y_mean = df_filtered[y_axis].mean()

        fig.add_vline(
            x=x_mean, 
            line_dash="dot", 
            line_color="rgba(255, 255, 255, 0.25)", 
            annotation_text="League Avg", 
            annotation_position="top",
            annotation_font_color="#94A3B8",
            annotation_font_size=11
        )
        fig.add_hline(
            y=y_mean, 
            line_dash="dot", 
            line_color="rgba(255, 255, 255, 0.25)", 
            annotation_text="League Avg", 
            annotation_position="right",
            annotation_font_color="#94A3B8",
            annotation_font_size=11
        )

        fig.update_layout(
            height=680,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(10, 10, 14, 0.8)",
            xaxis_title=format_col_name(x_axis),
            yaxis_title=format_col_name(y_axis),
            hoverlabel=dict(
                bgcolor="#18181C",
                bordercolor="#38BDF8",
                font_size=13,
                font_family="sans-serif",
                font_color="#F8FAFC"
            ),
            margin=dict(l=20, r=20, t=50, b=20),
            font=dict(color="#F8FAFC", family="sans-serif"),
            showlegend=True,
            legend=dict(
                bgcolor="rgba(18, 18, 22, 0.8)",
                bordercolor="rgba(255, 255, 255, 0.1)",
                borderwidth=1
            )
        )

        st.markdown("💡 *Quick Tip: Click on any player node in the interactive scatter plot to instantly load their detailed scouting profile below.*")
        
        chart_event = st.plotly_chart(fig, width="stretch", on_select="rerun")

        # 6. Modern Player Spotlight Dossier (Spotify/YouTube Profile Card Style)
        st.markdown("---")
        st.markdown("### 👤 Player Scouting Dossier")
        
        selected_player = None
        if chart_event and len(chart_event.selection["points"]) > 0:
            selected_player = chart_event.selection["points"][0]["customdata"][0]
        else:
            selected_player = df_filtered[player_col].iloc[0]

        if selected_player:
            player_data = df_filtered[df_filtered[player_col] == selected_player].iloc[0]
            
            st.markdown('<div class="spotlight-card">', unsafe_allow_html=True)
            
            col_img, col_bio = st.columns([1, 4.5], gap="large")
            
            with col_img:
                if id_col and pd.notna(player_data[id_col]):
                    pid = str(player_data[id_col])
                    img_url = f"https://www.basketball-reference.com/req/202106291/images/headshots/{pid}.jpg"
                    st.markdown(f"""
                        <div style="display: flex; justify-content: center; align-items: center;">
                            <img src="{img_url}" style="width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: 3px solid #38BDF8; box-shadow: 0 8px 24px rgba(56, 189, 248, 0.3);">
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No Photo Available")

            with col_bio:
                st.markdown(f"""
                    <div style="font-size: 1.8rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em; margin-bottom: 8px;">
                        {selected_player}
                    </div>
                """, unsafe_allow_html=True)
                
                ht_in = player_data.get('ht_in_in', None)
                height_str = f"{int(ht_in // 12)}'{int(ht_in % 12)}\"" if pd.notna(ht_in) else "N/A"
                wt_lbs = player_data.get('wt', None)
                weight_str = f"{int(wt_lbs)} lbs" if pd.notna(wt_lbs) else "N/A"
                
                team_str = player_data.get(team_col, 'N/A')
                szn_str = player_data.get(season_col, 'N/A')
                gm_str = int(player_data.get(games_col, 0)) if pd.notna(player_data.get(games_col)) else 'N/A'

                st.markdown(f"""
                    <div>
                        <span class="badge-pill">TEAM: {team_str}</span>
                        <span class="badge-pill">SEASON: {szn_str}</span>
                        <span class="badge-pill">GAMES: {gm_str}</span>
                        <span class="badge-pill">PHYSICAL: {height_str} / {weight_str}</span>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 1.05rem; font-weight: 700; color: #E2E8F0; margin-bottom: 12px;'>📈 Per-Game Box Score & Efficiency Splits</div>", unsafe_allow_html=True)

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

        with st.expander("📊 View Complete Filtered Dataset"):
            st.dataframe(df_filtered, width="stretch")

    else:
        st.warning("No players matched your active filters. Try decreasing the minimum games played threshold.")
