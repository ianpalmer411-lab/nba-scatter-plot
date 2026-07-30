import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NBA Metric Explorer", page_icon="🏀", layout="wide")

st.title("🏀 NBA Player Metric Scatter Plot")
st.markdown("Select metrics to compare player performance across seasons.")

# Sample baseline dataset for instant rendering
@st.cache_data
def load_data():
    data = {
        'PLAYER_NAME': ['Nikola Jokic', 'Luka Doncic', 'Giannis Antetokounmpo', 'Shai Gilgeous-Alexander', 'Jayson Tatum', 'Anthony Davis', 'LeBron James', 'Stephen Curry'],
        'SEASON': ['2023-24'] * 8,
        'GP': [79, 70, 73, 75, 74, 76, 71, 74],
        'PTS': [26.4, 33.9, 30.4, 30.1, 26.9, 24.7, 25.7, 26.4],
        'AST': [9.0, 9.8, 6.5, 6.2, 4.9, 3.5, 8.3, 5.1],
        'REB': [12.4, 9.2, 11.5, 5.5, 8.1, 12.6, 7.3, 4.5],
        'True_Shooting_Pct': [65.0, 61.7, 64.9, 63.6, 60.4, 62.1, 63.0, 62.6],
        'PTS_REB_AST': [47.8, 52.9, 48.4, 41.8, 39.9, 40.8, 41.3, 36.0]
    }
    return pd.DataFrame(data)

df = load_data()

numeric_cols = ['PTS', 'AST', 'REB', 'True_Shooting_Pct', 'PTS_REB_AST']

st.sidebar.header("⚙️ Plot Options")
x_axis = st.sidebar.selectbox("X-Axis Metric", numeric_cols, index=4)
y_axis = st.sidebar.selectbox("Y-Axis Metric", numeric_cols, index=3)

fig = px.scatter(
    df,
    x=x_axis,
    y=y_axis,
    hover_name='PLAYER_NAME',
    hover_data=['GP'],
    title=f"<b>{x_axis}</b> vs <b>{y_axis}</b>",
    template="plotly_dark"
)

fig.update_traces(marker=dict(size=14, opacity=0.85, line=dict(width=1, color='white')))
fig.update_layout(height=650)

st.plotly_chart(fig, use_container_width=True)
