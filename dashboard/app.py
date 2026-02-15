import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from data_loader import load_crime_data
from utils import (
    apply_time_filter,
    get_overview_metrics,
    filter_by_cluster,
    top_crime_types,
    arrest_rate,
    get_cluster_hotspots,
    get_daily_crime_trend,
    get_hour_crime_distribution,
    get_day_week_distribution,
    get_arrest_statistics,
    get_location_stats
)


def _safe_int(x, default=0):
    """Coerce to native int for display; avoid ? from numpy types in Streamlit."""
    if pd.isna(x):
        return default
    return int(x)


def _safe_float(x, default=0.0):
    """Coerce to native float for display; avoid NaN/? in metrics."""
    if pd.isna(x):
        return default
    return float(x)


# ============================================================================
# PAGE CONFIGURATION & STYLING
# ============================================================================

st.set_page_config(
    page_title="Crime Pattern Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Chicago Crime Pattern Analysis - Spatio-Temporal DBSCAN Hotspot Detection"
    }
)

# Custom CSS for enhanced styling
st.markdown("""
    <style>
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #ff7f0e;
            --danger-color: #d62728;
            --success-color: #2ca02c;
            --neutral-color: #FFE5B4;
            --heading-color: #191970;
            padding : 10px;
        }
        
        * {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            
        }
        
        .main {
            background-color: #f8f9f9;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #FFE5B4;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #1f3a93;
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        h2 {
            color: #2d5a8c;
            font-size: 1.8em;
            font-weight: 600;
            margin-top: 15px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        
        h3 {
            color: #404040;
            font-size: 1.3em;
            font-weight: 600;
        }
        
        .section-divider {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 2px;
            margin: 15px 0;
            border-radius: 2px;
            color: #FFE5B4;

        }
        
        [data-testid="stMetricValue"] {
            color: #FFAA94;
            font-size: 2.2em;
            font-weight: 700;
        }
        
        [data-testid="stMetricLabel"] {
            color: #2d5a8c;
            font-size: 14px !important;
            font-weight: 600;
        }
        
        [data-testid="stMetricDelta"] {
            color: #404040;
        }
        
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 1.1em;
            font-weight: 600;
        }

        /* Reduce metric label size */
div[data-testid="stMetricLabel"] {
    font-size: 18px !important;
}

/* Reduce metric value size */
div[data-testid="stMetricValue"] {
    font-size: 25px !important;
    font-weight: 600;
}

/* Optional: color crime count differently */
.crime-metric div[data-testid="stMetricValue"] {
    color: #ff4b4b !important;   /* red */
}

/* Optional: color arrest rate differently */
.arrest-metric div[data-testid="stMetricValue"] {
    color: #00c853 !important;   /* green */
}
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_data
def cached_load_data():
    return load_crime_data()

try:
    df = cached_load_data()
except FileNotFoundError as e:
    st.error(f"**Data file not found.** {e}")
    st.stop()
except ValueError as e:
    st.error(f"**Invalid data:** {e}")
    st.stop()
except Exception as e:
    st.error(f"**Failed to load crime data:** {e}")
    st.stop()

# ============================================================================
# HEADER SECTION
# ============================================================================

# col1, col2 = st.columns([3, 1])
# with col1:
#     st.markdown("# 🔍 Crime Pattern Analysis Dashboard")
#     st.markdown("### Advanced Spatio-Temporal Hotspot Detection")
#     st.markdown("**Data Source:** Chicago Crime Dataset | **Method:** DBSCAN Clustering")

# with col2:
#     st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

with st.container():
    st.markdown("# 🔍 Crime Pattern Analysis Dashboard")
    st.markdown("### Advanced Spatio-Temporal Hotspot Detection")
    # st.markdown("**Data Source:** Chicago Crime Dataset | **Method:** DBSCAN Clustering")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

st.sidebar.markdown("## Analysis Filters")
st.sidebar.markdown("Configure the dashboard parameters below")

with st.sidebar:
    # Time window filter
    st.markdown("### ⏰ Time Period")
    time_window = st.selectbox(
        "Analysis Window",
        [7, 14, 30, 90, 180, 365],
        index=2,
        format_func=lambda x: f"Last {x} days"
    )
    
    st.markdown("---")
    
    # Hotspot selection
    st.markdown("### 🎯 Hotspot Selection")
    df_time = apply_time_filter(df, time_window)
    clusters = sorted([c for c in df_time["st_cluster"].unique() if c != -1])
    
    cluster_choice = st.selectbox(
        "Select Hotspot",
        ["All"] + clusters,
        format_func=lambda x: f"Hotspot {x}" if x != "All" else "All Hotspots"
    )
    
    df_filtered = filter_by_cluster(df_time, cluster_choice)
    
    st.markdown("---")
    
    # Display filter summary
    st.markdown("### 📊 Filter Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Records Selected", f"{len(df_filtered):,}")
    with col2:
        st.metric("Time Window", f"{time_window}d")

# ============================================================================
# KEY METRICS SECTION
# ============================================================================

st.markdown(
    """
    <h1 style='color: #191970; text-align: left; font-size: 2.5em; font-weight: 700;'>
        Key Metrics 
    </h1>
    """,
    unsafe_allow_html=True
)




total, hotspots, noise_pct = get_overview_metrics(df_filtered)
arrests_stats = get_arrest_statistics(df_filtered)

metric_cols = st.columns(5)

with metric_cols[0]:
    st.metric(
        label="Total Crimes",
        value=f"{total:,}",
        delta=f"in {time_window}d",
        help="Total crime incidents in selected period"
    )

with metric_cols[1]:
    st.metric(
        label="Active Hotspots",
        value=_safe_int(hotspots),
        help="Number of spatial clusters detected"
    )

with metric_cols[2]:
    st.metric(
        label="Arrests Made",
        value=_safe_int(arrests_stats["total_arrests"]),
        delta=f"{_safe_float(arrests_stats['arrest_rate']):.1f}%",
        help="Total arrests and arrest rate"
    )

with metric_cols[3]:
    st.metric(
        label="Noise Ratio",
        value=f"{_safe_float(noise_pct):.1f}%",
        help="Crimes not belonging to any hotspot"
    )

with metric_cols[4]:
    avg_crimes_per_cluster = total / hotspots if hotspots > 0 else 0
    st.metric(
        label="Avg per Hotspot",
        value=f"{_safe_float(avg_crimes_per_cluster):.0f}",
        help="Average crimes per hotspot"
    )

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ============================================================================
# MAIN ANALYTICS SECTION
# ============================================================================

if total == 0:
    st.warning("⚠️ No crime data available for the selected filters.")
    st.stop()

# Create tabs for better organization
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Spatial Analysis",
    "📊 Temporal Patterns",
    "📋 Crime Types",
    "🔍 Detailed Analytics"
])

# ============================================================================
# TAB 1: SPATIAL ANALYSIS
# ============================================================================

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Hotspot Locations Map")
        
        # Create enhanced map with clusters highlighted
        fig_map = px.scatter_mapbox(
            df_filtered,
            lat="latitude",
            lon="longitude",
            color="st_cluster",
            hover_data={
                "primary_type": True,
                "hour": True,
                "arrest": True,
                "st_cluster": True
            },
            hover_name="primary_type",
            zoom=9,
            height=600,
            color_continuous_scale="plasma",
            title="Crime Hotspots Distribution"
        )
        
        fig_map.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Latitude: %{lat:.4f}<br>"
                "Longitude: %{lon:.4f}<br>"
                "Hour: %{customdata[1]}<br>"
                "Arrested: %{customdata[2]}<br>"
                "Cluster: %{customdata[3]}<extra></extra>"
            )
        )
        
        fig_map.update_layout(
            mapbox_style="carto-positron",
            margin=dict(l=0, r=0, t=30, b=0),
            font=dict(family="Segoe UI", size=12),
            plot_bgcolor="white"
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
    
    with col2:
        st.markdown("### Hotspot Details")
        
        hotspot_data = get_cluster_hotspots(df_filtered)
        
        if not hotspot_data.empty:
            for idx, row in hotspot_data.head(4).iterrows():
                with st.container():
                    col_a, col_b = st.columns([1, 1])
                    with col_a:
                        st.metric(
                            f"Hotspot {_safe_int(row['st_cluster'])}",
                            f"{_safe_int(row['count'])} crimes",
                            help=f"Lat: {_safe_float(row['latitude'], 0):.4f}, Lon: {_safe_float(row['longitude'], 0):.4f}"
                        )
                    with col_b:
                        st.metric(
                            "Arrest Rate",
                            f"{_safe_float(row['arrest_rate']):.1f}%"
                        )
                    st.divider()

# ============================================================================
# TAB 2: TEMPORAL PATTERNS
# ============================================================================

with tab2:
    st.markdown("### Crime Intensity by Time of Day and Day of Week")
    
    # Prepare data for heatmap
    df_filtered["day_name"] = df_filtered["date"].dt.day_name()
    
    heatmap_df = (
        df_filtered
        .groupby(["day_name", "hour"])
        .size()
        .reset_index(name="count")
    )
    
    # Reorder days and build pivot for correct heatmap from aggregated data
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_df["day_name"] = pd.Categorical(
        heatmap_df["day_name"],
        categories=day_order,
        ordered=True
    )
    heatmap_pivot = heatmap_df.pivot(index="day_name", columns="hour", values="count").fillna(0).reindex(day_order)
    # Ensure all hours 0-23 exist
    for h in range(24):
        if h not in heatmap_pivot.columns:
            heatmap_pivot[h] = 0
    heatmap_pivot = heatmap_pivot[[h for h in range(24)]]
    
    fig_heatmap = px.imshow(
        heatmap_pivot,
        labels=dict(x="Hour of Day", y="Day of Week", color="Crime Count"),
        x=heatmap_pivot.columns.tolist(),
        y=heatmap_pivot.index.tolist(),
        color_continuous_scale="RdYlBu_r",
        aspect="auto",
        height=450,
        title="Crime Activity Heatmap"
    )
    fig_heatmap.update_layout(
        xaxis_title="Hour of Day (24h format)",
        yaxis_title="Day of Week",
        font=dict(family="Segoe UI", size=11)
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Hourly Distribution")
        
        hour_dist = get_hour_crime_distribution(df_filtered)
        
        fig_hour = px.bar(
            hour_dist,
            x="hour",
            y="count",
            labels={"hour": "Hour of Day", "count": "Number of Crimes"},
            color="count",
            color_continuous_scale="Blues",
            height=400,
            title="Crimes by Hour"
        )
        
        fig_hour.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Crime Count",
            hovermode="x unified",
            showlegend=False,
            font=dict(family="Segoe UI", size=11)
        )
        
        st.plotly_chart(fig_hour, use_container_width=True)
    
    with col2:
        st.markdown("### Day of Week Distribution")
        
        day_dist = get_day_week_distribution(df_filtered)
        
        fig_day = px.bar(
            day_dist,
            x="day_name",
            y="count",
            labels={"day_name": "Day of Week", "count": "Number of Crimes"},
            color="count",
            color_continuous_scale="Greens",
            height=400,
            title="Crimes by Day of Week"
        )
        
        fig_day.update_layout(
            xaxis_title="Day of Week",
            yaxis_title="Crime Count",
            hovermode="x unified",
            showlegend=False,
            font=dict(family="Segoe UI", size=11)
        )
        
        st.plotly_chart(fig_day, use_container_width=True)
    
    st.markdown("### Daily Crime Trend")
    
    daily_trend = get_daily_crime_trend(df_filtered)
    
    fig_trend = px.line(
        daily_trend,
        x="date",
        y="crimes",
        markers=True,
        labels={"date": "Date", "crimes": "Number of Crimes"},
        height=400,
        title="Crime Trend Over Time"
    )
    
    fig_trend.update_layout(
        xaxis_title="Date",
        yaxis_title="Crime Count",
        hovermode="x unified",
        font=dict(family="Segoe UI", size=11),
        plot_bgcolor="rgba(240,240,240,0.5)"
    )
    
    fig_trend.update_traces(
        line=dict(color="#667eea", width=3),
        marker=dict(size=6, color="#667eea")
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

# ============================================================================
# TAB 3: CRIME TYPES
# ============================================================================

with tab3:
    st.markdown("### Crime Type Analysis")
    
    crime_df = top_crime_types(df_filtered, top_n=10)
    crime_df = crime_df.sort_values("crime_count", ascending=True)
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("#### Top 10 Crime Types (Horizontal Bar)")
        
        fig_bar = px.bar(
            crime_df,
            y="crime_type",
            x="crime_count",
            orientation="h",
            labels={"crime_type": "Crime Type", "crime_count": "Count"},
            color="crime_count",
            color_continuous_scale="Reds",
            height=500,
            title="Crime Frequency by Type"
        )
        
        fig_bar.update_layout(
            xaxis_title="Number of Incidents",
            yaxis_title="",
            hovermode="y unified",
            showlegend=False,
            font=dict(family="Segoe UI", size=11)
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.markdown("#### Top 5 Crime Distribution (Pie)")
        
        top5_crimes = crime_df.nlargest(5, "crime_count")
        
        fig_pie = px.pie(
            top5_crimes,
            names="crime_type",
            values="crime_count",
            hole=0.4,
            title="Top 5 Crimes Distribution"
        )
        
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            textfont=dict(size=11)
        )
        
        fig_pie.update_layout(
            height=500,
            font=dict(family="Segoe UI", size=11)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("#### Crime Type Statistics Table")
    
    crime_stats = crime_df.copy()
    total_count = crime_stats["crime_count"].sum()
    if total_count and total_count > 0:
        crime_stats["Percentage"] = (
            (crime_stats["crime_count"] / total_count * 100).fillna(0).round(2).astype(str) + "%"
        )
    else:
        crime_stats["Percentage"] = "0%"
    crime_stats = crime_stats.rename(columns={"crime_type": "Crime Type", "crime_count": "Count"})
    crime_stats = crime_stats[["Crime Type", "Count", "Percentage"]]
    
    st.dataframe(
        crime_stats.sort_values("Count", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# ============================================================================
# TAB 4: DETAILED ANALYTICS
# ============================================================================

with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Arrest Rate by Crime Type")
        
        arrest_by_crime = (
            df_filtered
            .groupby("primary_type")
            .agg({
                "arrest": ["sum", "count"]
            })
            .reset_index()
        )
        
        arrest_by_crime.columns = ["crime_type", "arrests", "total"]
        arrest_by_crime["arrest_rate"] = (arrest_by_crime["arrests"] / arrest_by_crime["total"] * 100).round(2)
        arrest_by_crime = arrest_by_crime.nlargest(8, "total")
        
        fig_arrest = px.bar(
            arrest_by_crime,
            x="crime_type",
            y="arrest_rate",
            color="arrest_rate",
            color_continuous_scale="Greens",
            labels={"crime_type": "Crime Type", "arrest_rate": "Arrest Rate (%)"},
            height=450,
            title="Arrest Rate by Crime Type"
        )
        
        fig_arrest.update_layout(
            xaxis_tickangle=-45,
            hovermode="x unified",
            font=dict(family="Segoe UI", size=11)
        )
        
        st.plotly_chart(fig_arrest, use_container_width=True)
    
    with col2:
        st.markdown("### Cluster Size Distribution")
        
        cluster_sizes = (
            df_filtered[df_filtered["st_cluster"] != -1]
            .groupby("st_cluster")
            .size()
            .reset_index(name="size")
            .sort_values("size", ascending=False)
        )
        
        if not cluster_sizes.empty:
            fig_clusters = px.box(
                cluster_sizes,
                y="size",
                labels={"size": "Cluster Size"},
                height=450,
                title="Hotspot Cluster Size Distribution"
            )
            fig_clusters.update_layout(
                hovermode="y unified",
                xaxis_title="",
                font=dict(family="Segoe UI", size=11)
            )
            st.plotly_chart(fig_clusters, use_container_width=True)
        else:
            st.info("No hotspot clusters in the selected filters (all points are noise).")
    
    st.markdown("### Summary Statistics")
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Avg Crimes/Day", f"{_safe_float(total / time_window):.1f}")
    
    with summary_col2:
        peak_hour = df_filtered.groupby("hour").size().idxmax()
        st.metric("Peak Hour", f"{_safe_int(peak_hour):02d}:00")
    
    with summary_col3:
        max_cluster = _safe_int(cluster_sizes.iloc[0]["size"]) if not cluster_sizes.empty else 0
        st.metric("Largest Hotspot", f"{max_cluster} crimes")
    
    with summary_col4:
        unique_crimes = _safe_int(df_filtered["primary_type"].nunique())
        st.metric("Crime Types", unique_crimes)
    
    st.markdown("---")
    st.markdown("### Raw Data Sample")
    
    display_cols = ["date", "latitude", "longitude", "primary_type", "hour", "arrest", "st_cluster"]
    display_cols = [col for col in display_cols if col in df_filtered.columns]
    sample_df = df_filtered[display_cols].head(100).copy()
    for c in sample_df.columns:
        if sample_df[c].dtype in ("float64", "float32"):
            sample_df[c] = sample_df[c].fillna(0.0)
    st.dataframe(sample_df, use_container_width=True, height=400)

# ============================================================================
# FOOTER
# ============================================================================

# st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("### 📖 About")
#     st.markdown("Advanced crime hotspot detection using DBSCAN algorithm on Chicago crime data.")

# with col2:
#     st.markdown("### 🔬 Methodology")
#     st.markdown("**DBSCAN Clustering** for spatiotemporal hotspot identification. Noise points (-1) indicate isolated incidents.")

# with col3:
#     st.markdown("### 📊 Data")
#     d_min, d_max = df["date"].min(), df["date"].max()
#     date_range = f"{d_min.date()} to {d_max.date()}" if pd.notna(d_min) and pd.notna(d_max) else "N/A"
#     st.markdown(f"**Dataset Size:** {len(df):,} total incidents\n**Time Range:** {date_range}")

