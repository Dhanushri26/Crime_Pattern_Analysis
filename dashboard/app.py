import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.express as px


from data_loader import load_crime_data
from utils import (
    apply_time_filter,
    get_overview_metrics,
    filter_by_cluster,
    hourly_distribution,
    top_crime_types,
    arrest_rate
)

# ----------------------------------
# Page config
# ----------------------------------
st.set_page_config(
    page_title="Crime Hotspot Dashboard",
    layout="wide"
)

st.title("🚔 Crime Hotspot Analysis Dashboard")
st.caption("Spatio-temporal DBSCAN based analysis (Chicago)")

# ----------------------------------
# Load data
# ----------------------------------
df = load_crime_data()

# ----------------------------------
# Sidebar filters
# ----------------------------------

import pandas as pd
custom_scale = [
    [0.0, "blue"],
    [0.25, "green"],
    [0.5, "yellow"],
    [0.75, "orange"],
    [1.0, "red"]
]

st.sidebar.subheader("Time Range")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

# Ensure default range is valid
default_start = max(min_date, max_date - pd.Timedelta(days=30))
default_end = max_date

start_date, end_date = st.sidebar.date_input(
    "Select date range",
    value=(default_start, default_end),
    min_value=min_date,
    max_value=max_date
)

df_time = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
]

def time_bucket(hour):
    if 5 <= hour < 9:
        return "Early Morning"
    elif 9 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"
df_time["time_bucket"] = df_time["hour"].apply(time_bucket)

use_time_buckets = st.sidebar.checkbox(
    "Use time buckets (Morning / Night etc.)",
    value=False
)
df_time["day_name"] = df_time["date"].dt.day_name()

if use_time_buckets:
    heatmap_df = (
        df_time
        .groupby(["day_name", "time_bucket"])
        .size()
        .reset_index(name="count")
    )

    x_axis = "time_bucket"
else:
    heatmap_df = (
        df_time
        .groupby(["day_name", "hour"])
        .size()
        .reset_index(name="count")
    )

    x_axis = "hour"

st.subheader("🕒 Crime Time Heatmap")

fig_heatmap = px.density_heatmap(
    heatmap_df,
    x=x_axis,
    y="day_name",
    z="count",
    color_continuous_scale="Plasma"
)

st.plotly_chart(fig_heatmap, width="stretch")

st.sidebar.header("Filters")

time_window = st.sidebar.selectbox(
    "Time Window",
    [7, 14, 30, 90, 180, 365, 730],
    format_func=lambda x: f"Last {x} days"
)

df_time = apply_time_filter(df, time_window)

clusters = sorted(c for c in df_time["st_cluster"].unique() if c != -1)
cluster_choice = st.sidebar.selectbox(
    "Select Hotspot",
    ["All"] + clusters
)

df_filtered = filter_by_cluster(df_time, cluster_choice)

# ----------------------------------
# Overview metrics
# ----------------------------------
total, hotspots, noise_pct = get_overview_metrics(df_filtered)

col1, col2, col3 = st.columns(3)
col1.metric("Total Crimes", total)
col2.metric("Active Hotspots", hotspots)
col3.metric("Noise (%)", f"{noise_pct:.1f}")

# ----------------------------------
# Map
# ----------------------------------
st.subheader("📍 Crime Hotspot Map")



heatmap = px.density_mapbox(
    df_filtered,
    lat="latitude",
    lon="longitude",
    radius=20,
    zoom=9,
    color_continuous_scale="Viridis",
    opacity=0.6
)


if total == 0:
    st.warning("No data available for selected time window.")
else:
    fig_map = px.scatter_mapbox(
        df_filtered,
        lat="latitude",
        lon="longitude",
        color="st_cluster",
        hover_data=["primary_type", "hour"],
        zoom=9,
        height=500,
        color_continuous_scale=custom_scale
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig_map, use_container_width=True)

# ----------------------------------
# Remove noise for analysis
# ----------------------------------
analysis_df = df_filtered[df_filtered["st_cluster"] != -1]

if len(analysis_df) == 0:
    st.info("No hotspot data available for analysis.")
    st.stop()

# ----------------------------------
# Time analysis
# ----------------------------------
st.subheader("⏰ Time of Crime")

hour_df = hourly_distribution(analysis_df)
fig_time = px.bar(hour_df, x="hour", y="count")
st.plotly_chart(fig_time, use_container_width=True)

# ----------------------------------
# Crime types
# ----------------------------------
st.subheader("🏷️ Crime Type Distribution")

crime_df = top_crime_types(analysis_df)
fig_crime = px.bar(crime_df, x="crime_type", y="crime_count")
st.plotly_chart(fig_crime, use_container_width=True)

# ----------------------------------
# Arrest rate
# ----------------------------------
st.subheader("🚓 Observed Arrest Rate")

rate = arrest_rate(analysis_df)
st.metric("Arrest Rate (%)", f"{rate:.1f}")

# ----------------------------------
# Footer
# ----------------------------------
st.caption(
    "For analytical and educational use only. "
    "Uses publicly available Chicago crime data."
)
