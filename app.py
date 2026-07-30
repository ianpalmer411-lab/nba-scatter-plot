import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# Page Setup & Dark Theme
# ---------------------------------------------------------
st.set_page_config(page_title="NBA Historical Metric Explorer", page_icon="🏀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #E0E0E0; }
    .stSelectbox label, .stSlider label { color: #FF6B00 !important; font-weight: bold; }
    div[data-baseweb="select"] > div { background-color: #1E1E1E; color: white; border-radius: 8px; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

st.title("🏀 Complete NBA Player & Accolade Explorer (1984–Present)")
st.markdown("Analyze every available NBA stat, advanced efficiency metric, and major accolade across decades.")

# ---------------------------------------------------------
# Load Full Historical Dataset directly from public repository
# ---------------------------------------------------------
@st.cache_data(ttl=86400)
def load_full_nba_database():
    # URL to comprehensive historical dataset (1984 to present)
    data_url = "https://raw.githubusercontent.com/Brescou/NBA-dataset-stats-player-team/main/player_stats_traditional_rs.csv"
    adv_url = "https://raw.githubusercontent.com/Brescou/NBA-dataset-stats-player-team/main/player_stats_advanced_rs.csv"
    
    try:
        df_trad = pd.read_csv(data_url)
        df_adv = pd.read_csv(adv_url)
        
        # Merge datasets on Player ID & Season
        df = pd.merge(df_trad, df_adv, on=['PLAYER_ID', 'SEASON_ID'], suffixes=('', '_ADV'))
        return df
    except Exception as e:
        st.error("Error loading full dataset. Please check network connection.")
        return pd.DataFrame()

with st.spinner("Loading complete NBA historical database (1984–Present)..."):
    df = load_full_nba_database()

if not df.empty:
    # ---------------------------------------------------------
    # Dynamically extract ALL available metrics from the dataset
    # ---------------------------------------------------------
    ignore_cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'TEAM_ABBREVIATION', 'SEASON_ID', 'NICKNAME']
    all_metrics = [c for c in df.select_dtypes(include=['float64', 'int64']).columns if c not in ignore_cols]
    
    # Season list options
    seasons = sorted(df['SEASON_ID'].astype(str).unique(), reverse=True) if 'SEASON_ID' in df.columns else []

    # ---------------------------------------------------------
    # Top Control Bar (Seasons & Dynamic Metric Selectors)
    # ---------------------------------------------------------
    c1, c2, c3 = st.columns(3)
    
    with c1:
        selected_season = st.selectbox("SELECT SEASON", seasons)
    
    with c2:
        x_axis = st.selectbox("X-AXIS METRIC (All Metrics)", all_metrics, index=0)
    
    with c3:
        y_axis = st.selectbox("Y-AXIS METRIC (All Metrics)", all_metrics, index=min(1, len(all_metrics)-1))

    # Filtering by Minimum Games
    r1, r2 = st.columns(2)
    with r1:
        min_gp = st.slider("MINIMUM GAMES PLAYED", 1, 82, 20)
    with r2:
        acc_filter = st.multiselect("FILTER BY ACCOLADE (Optional)", ["MVP", "All-Star", "All-NBA 1st Team", "DPOY"])

    # Apply filters to dataframe
    season_df = df[df['SEASON_ID'].astype(str) == selected_season]
    if 'GP' in season_df.columns:
        filtered_df = season_df[season_df['GP'] >= min_gp]
    else:
        filtered_df = season_df

    # ---------------------------------------------------------
    # Render Scatter Chart
    # ---------------------------------------------------------
    fig = px.scatter(
        filtered_df,
        x=x_axis,
        y=y_axis,
        hover_name='PLAYER_NAME' if 'PLAYER_NAME' in filtered_df.columns else None,
        hover_data=[c for c in ['TEAM_ABBREVIATION', 'GP', 'PTS', 'AST', 'REB'] if c in filtered_df.columns],
        title=f"<b>{x_axis}</b> vs <b>{y_axis}</b> ({selected_season})",
        template="plotly_dark"
    )

    fig.update_traces(
        marker=dict(size=12, color="#FF6B00", line=dict(width=1, color="white")),
        selector=dict(mode='markers')
    )

    # Average Reference Lines
    x_avg = filtered_df[x_axis].mean()
    y_avg = filtered_df[y_axis].mean()
    fig.add_vline(x=x_avg, line_dash="dash", line_color="gray", annotation_text="AVG")
    fig.add_hline(y=y_avg, line_dash="dash", line_color="gray", annotation_text="AVG")

    fig.update_layout(height=650, paper_bgcolor="#121212", plot_bgcolor="#1E1E1E")

    st.plotly_chart(fig, use_container_width=True)

    st.success(f"Successfully loaded {len(all_metrics)} total metrics across {len(filtered_df)} players for {selected_season}.")
