import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# Page & Custom CSS Setup (Hoopology Theme)
# ---------------------------------------------------------
st.set_page_config(page_title="NBA Metric Explorer", page_icon="🏀", layout="wide")

# Custom Dark Mode & Orange Accent Styles
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
    }
    .stSelectbox label, .stSlider label {
        color: #FFA500 !important;
        font-weight: bold;
    }
    div[data-baseweb="select"] > div {
        background-color: #1E1E1E;
        color: white;
        border-radius: 8px;
        border: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏀 NBA Metric Explorer")
st.markdown("<p style='color: #888;'>Compare player efficiency, volume, and advanced analytics across seasons.</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Datasets (Expanded Mock Data with Accolades)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    data = [
        {"PLAYER_NAME": "Nikola Jokić", "SEASON": "2023-24", "GP": 79, "MIN": 34.6, "PTS": 26.4, "AST": 9.0, "REB": 12.4, "True_Shooting_Pct": 65.0, "PTS_REB_AST": 47.8, "ACCOLADE": "MVP / All-NBA 1st"},
        {"PLAYER_NAME": "Luka Dončić", "SEASON": "2023-24", "GP": 70, "MIN": 37.5, "PTS": 33.9, "AST": 9.8, "REB": 9.2, "True_Shooting_Pct": 61.7, "PTS_REB_AST": 52.9, "ACCOLADE": "All-NBA 1st"},
        {"PLAYER_NAME": "Giannis Antetokounmpo", "SEASON": "2023-24", "GP": 73, "MIN": 35.2, "PTS": 30.4, "AST": 6.5, "REB": 11.5, "True_Shooting_Pct": 64.9, "PTS_REB_AST": 48.4, "ACCOLADE": "All-NBA 1st"},
        {"PLAYER_NAME": "Shai Gilgeous-Alexander", "SEASON": "2023-24", "GP": 75, "MIN": 34.0, "PTS": 30.1, "AST": 6.2, "REB": 5.5, "True_Shooting_Pct": 63.6, "PTS_REB_AST": 41.8, "ACCOLADE": "All-NBA 1st"},
        {"PLAYER_NAME": "Jayson Tatum", "SEASON": "2023-24", "GP": 74, "MIN": 35.7, "PTS": 26.9, "AST": 4.9, "REB": 8.1, "True_Shooting_Pct": 60.4, "PTS_REB_AST": 39.9, "ACCOLADE": "All-NBA 1st / Champion"},
        {"PLAYER_NAME": "Anthony Davis", "SEASON": "2023-24", "GP": 76, "MIN": 35.5, "PTS": 24.7, "AST": 3.5, "REB": 12.6, "True_Shooting_Pct": 62.1, "PTS_REB_AST": 40.8, "ACCOLADE": "All-Defensive 1st"},
        {"PLAYER_NAME": "LeBron James", "SEASON": "2023-24", "GP": 71, "MIN": 35.3, "PTS": 25.7, "AST": 8.3, "REB": 7.3, "True_Shooting_Pct": 63.0, "PTS_REB_AST": 41.3, "ACCOLADE": "All-NBA 3rd"},
        {"PLAYER_NAME": "Jimmy Butler", "SEASON": "2023-24", "GP": 60, "MIN": 34.0, "PTS": 20.8, "AST": 5.0, "REB": 5.3, "True_Shooting_Pct": 62.6, "PTS_REB_AST": 31.1, "ACCOLADE": "None"},
        {"PLAYER_NAME": "Kawhi Leonard", "SEASON": "2023-24", "GP": 68, "MIN": 34.3, "PTS": 23.7, "AST": 3.6, "REB": 6.1, "True_Shooting_Pct": 62.6, "PTS_REB_AST": 33.4, "ACCOLADE": "All-NBA 2nd"}
    ]
    return pd.DataFrame(data)

df = load_data()

# ---------------------------------------------------------
# Control Panels (Top Bar Layout)
# ---------------------------------------------------------
c1, c2, c3 = st.columns(3)

with c1:
    season = st.selectbox("SEASON", ["2023-24", "2022-23", "2021-22"])

with c2:
    x_axis = st.selectbox("X-AXIS METRIC", ["PTS_REB_AST", "PTS", "AST", "REB"], index=0)

with c3:
    y_axis = st.selectbox("Y-
