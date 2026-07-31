import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Page Configuration & Custom CSS for a beautiful UI
st.set_page_config(page_title="NBA Stat Explorer", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Make the title look modern */
    .main h1 { font-family: 'Arial Black', sans-serif; color: #1D428A; }
    /* Soften the background */
    .stApp { background-color: #F8F9FA; }
    /* Style the sidebar */
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E0E0E0; }
    </style>
""", unsafe_allow_html=True)

st.title("🏀 NBA Player Stats Explorer")
st.markdown("Explore historical data, discover trends, and compare legends.")

# 2. Load Data
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
    st.error("⚠️ Could not find `nba_master_stats.csv`. Please upload it to your repository!")
else:
    # Identify standard identifier columns
    season_col = 'SEASON' if 'SEASON' in df.columns else ('season' if 'season' in df.columns else None)
    player_col = 'PLAYER_NAME' if 'PLAYER_NAME' in df.columns else ('player' if 'player' in df.columns else None)
    team_col = 'team' if 'team' in df.columns else ('TEAM' if 'TEAM' in df.columns else None)
    id_col = 'player_id' if 'player_id' in df.columns else None

    # 3. Premium UI: Sidebar Controls
    st.sidebar.image("https://cdn.nba.com/logos/nba/nba-logoman-word-white.svg", width=150)
    st.sidebar.title("Dashboard Filters")
    
    # Season Filter
    if season_col:
        all_seasons = sorted(df[season_col].dropna().unique(), reverse=True)
        all_seasons.insert(0, "All History")
        selected_season = st.sidebar.selectbox("📅 Select Season", all_seasons)
        if selected_season != "All History":
            df_filtered = df[df[season_col] == selected_season]
        else:
            df_filtered = df
    else:
        df_filtered = df

    # Metric Selection for Scatter Plot
    numeric_cols = df_filtered.select_dtypes(include=['float64', 'int64']).columns.tolist()
    default_x = 'pts_per_game' if 'pts_per_game' in numeric_cols else (numeric_cols[0] if numeric_cols else '')
    default_y = 'ast_per_game' if 'ast_per_game' in numeric_cols else (numeric_cols[1] if len(numeric_cols) > 1 else default_x)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🏆 Top Performers Filter")
    
    # NEW: Top N Filter
    top_n_options = ["Show All", 10, 15, 20, 30, 50, 100]
    top_n = st.sidebar.selectbox("Filter Number of Players", top_n_options, index=0)

    if top_n != "Show All":
        filter_axis = st.sidebar.radio("Determine 'Top' players based on:", ["Y-Axis Metric", "X-Axis Metric"])
    else:
        filter_axis = None

    if not numeric_cols:
        st.warning("No numeric columns found in the dataset to plot.")
    else:
        # Main area metric selection
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("📊 Select X-axis Metric", numeric_cols, index=numeric_cols.index(default_x) if default_x in numeric_cols else 0)
        with col2:
            y_axis = st.selectbox("📈 Select Y-axis Metric", numeric_cols, index=numeric_cols.index(default_y) if default_y in numeric_cols else (1 if len(numeric_cols) > 1 else 0))

        # Apply Top N Filter mathematically
        if top_n != "Show All":
            sort_metric = y_axis if filter_axis == "Y-Axis Metric" else x_axis
            df_filtered = df_filtered.nlargest(top_n, sort_metric)

        # 4. Build the Scatter Plot
        if not df_filtered.empty:
            
            # Create dynamic image URLs for the hover tooltip using Basketball-Reference formatting
            if id_col:
                df_filtered['image_url'] = df_filtered[id_col].apply(lambda x: f"https://www.basketball-reference.com/req/202106291/images/players/{x}.jpg")
            else:
                df_filtered['image_url'] = ""

            # Only show permanent text labels if the graph isn't crowded (e.g. 30 players or fewer)
            show_text_labels = True if (top_n != "Show All" and top_n <= 30) else False

            # Build the custom data array that Plotly will use for tooltips
            custom_data_cols = [player_col, season_col, team_col, 'image_url'] if id_col else [player_col, season_col, team_col]
            
            fig = px.scatter(
                df_filtered,
                x=x_axis,
                y=y_axis,
                text=player_col if show_text_labels else None, # Removes the text mess!
                custom_data=custom_data_cols,
                color=team_col if team_col else None,          # Automatically colors dots by team
                title=f"<b>{y_axis.upper().replace('_', ' ')} vs {x_axis.upper().replace('_', ' ')}</b>",
            )
            
            # Format the visual markers
            fig.update_traces(
                textposition='top center', 
                textfont=dict(color='#333333', size=11, family="Arial"),
                marker=dict(size=12, opacity=0.85, line=dict(width=1, color='DarkSlateGrey'))
            )
            
            # Build the gorgeous custom tooltip with images
            if id_col:
                hovertemplate = (
                    "<div style='font-family: Arial;'>"
                    "<b><span style='font-size: 16px;'>%{customdata[0]}</span></b><br>"
                    "<span style='color: #888;'>%{customdata[1]} | Team: %{customdata[2]}</span><br><br>"
                    "<b>X:</b> %{x:,.2f}<br>"
                    "<b>Y:</b> %{y:,.2f}<br><br>"
                    "<img src='%{customdata[3]}' width='120' style='border-radius: 8px;'>"
                    "</div><extra></extra>"
                )
            else:
                hovertemplate = (
                    "<b>%{customdata[0]}</b><br>"
                    "Season: %{customdata[1]} | Team: %{customdata[2]}<br>"
                    "X: %{x:,.2f}<br>"
                    "Y: %{y:,.2f}<extra></extra>"
                )

            fig.update_traces(hovertemplate=hovertemplate)
            
            # Clean up the chart's grid and layout
            fig.update_layout(
                height=750, 
                template="plotly_white",
                hoverlabel=dict(bgcolor="white", font_size=14),
                margin=dict(l=40, r=40, t=60, b=40),
                legend_title_text='Team'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Clean data table
            with st.expander("🔍 View Raw Data Table"):
                display_df = df_filtered.drop(columns=['image_url'], errors='ignore')
                st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("No data available for the selected filters.")
