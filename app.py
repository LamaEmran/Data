import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ==========================================
# 1. APP CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Ontario Wildfire Intelligence",
    page_icon="🔥",
    layout="wide"
)

# ==========================================
# 2. DATA LOADING
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_dashboard_data.csv")

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

        for c in ['lat', 'lon', 'pm25', 'temperature', 'wind_speed', 'FIRE_FINAL_SIZE']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')

        return df.dropna(subset=['date'])
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return pd.DataFrame()

df = load_data()

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
st.sidebar.header("🔍 Filters")

if df.empty:
    st.warning("No data available")
    st.stop()

min_date = df['date'].min().date()
max_date = df['date'].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    (min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if 'city' in df.columns:
    cities = sorted(df['city'].dropna().unique())
    selected_cities = st.sidebar.multiselect(
        "Regions",
        cities,
        default=cities[:3] if len(cities) >= 3 else cities
    )
else:
    selected_cities = []

mask = (
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1]))
)

if selected_cities:
    mask &= df['city'].isin(selected_cities)

filtered_df = df[mask]

fire_days = (
    filtered_df[filtered_df['FIRE_FINAL_SIZE'] > 0]
    if 'FIRE_FINAL_SIZE' in filtered_df.columns
    else pd.DataFrame()
)

# ==========================================
# 4. DASHBOARD
# ==========================================
st.title("🔥 Ontario Wildfire Intelligence Dashboard")

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    if 'pm25' in filtered_df.columns:
        st.metric("Avg PM2.5", f"{filtered_df['pm25'].mean():.1f}")
    else:
        st.metric("Avg PM2.5", "N/A")

with col2:
    if 'pm25' in filtered_df.columns:
        st.metric("Peak PM2.5", f"{filtered_df['pm25'].max():.1f}")
    else:
        st.metric("Peak PM2.5", "N/A")

with col3:
    st.metric("Active Fire Days", len(fire_days))

with col4:
    if 'temperature' in filtered_df.columns:
        st.metric("Avg Temp", f"{filtered_df['temperature'].mean():.1f} °C")
    else:
        st.metric("Avg Temp", "N/A")

# --- TIME SERIES ---
st.subheader("📈 PM2.5 Over Time")

if 'pm25' in filtered_df.columns:
    daily = filtered_df.groupby('date')['pm25'].mean().reset_index()
    fig = px.area(daily, x='date', y='pm25')
    st.plotly_chart(fig, use_container_width=True)

# --- MAP ---
st.subheader("🗺️ Pollution Map")

if {'lat', 'lon', 'pm25'}.issubset(filtered_df.columns):
    map_df = filtered_df.dropna(subset=['lat', 'lon'])
    if not map_df.empty:
        fig = px.scatter_mapbox(
            map_df,
            lat='lat',
            lon='lon',
            size='pm25',
            color='pm25',
            zoom=4,
            mapbox_style="carto-darkmatter"
        )
        st.plotly_chart(fig, use_container_width=True)

# --- FIRE ANALYSIS ---
st.subheader("🔥 Fire Size Distribution")

if not fire_days.empty and 'FIRE_GENERAL_CAUSE_CODE' in fire_days.columns:
    fig = px.violin(
        fire_days,
        y='FIRE_FINAL_SIZE',
        x='FIRE_GENERAL_CAUSE_CODE',
        box=True,
        log_y=True
    )
    st.plotly_chart(fig, use_container_width=True)

# --- RAW DATA ---
with st.expander("🔍 Raw Data"):
    st.dataframe(filtered_df.sort_values('date', ascending=False))
