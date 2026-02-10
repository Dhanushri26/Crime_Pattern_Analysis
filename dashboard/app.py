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
            --neutral-color: #7f7f7f;
        }

        * {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Page background */
        .main {
            background-color: #f5f6fa;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e0e4ea;
        }

        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {
            color: #1f3a93;
        }

        /* Metric cards – equal height and width for neat display */
        [data-testid="stMetric"] {
            background: #ffffff;
            padding: 1rem 1.25rem;
            border-radius: 12px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
            border: 1px solid #e3e7f0;
            min-height: 115px;
            width: 100%;
            box-sizing: border-box;
        }

        [data-testid="stMetricValue"] {
            color: #111827;
            font-size: 2.1em;
            font-weight: 700;
        }

        [data-testid="stMetricLabel"] {
            color: #4b5563;
            font-size: 0.95em;
            font-weight: 500;
        }

        /* Headings */
        h1 {
            color: #111827;
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 6px;
        }

        h2 {
            color: #1f2933;
            font-size: 1.8em;
            font-weight: 600;
            margin-top: 28px;
            margin-bottom: 10px;
        }

        h3 {
            color: #374151;
            font-size: 1.25em;
            font-weight: 600;
        }

        .section-divider {
            background: linear-gradient(90deg, #1f77b4 0%, #764ba2 100%);
            height: 3px;
            margin: 26px 0;
            border-radius: 999px;
            opacity: 0.85;
            font-size: 10px;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem;
        }

        .stTabs [data-baseweb="tab-list"] button {
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.6rem 1rem;
            border-radius: 999px;
        }

        /* Dataframe styling */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_data
def cached_load_data():
    return load_crime_data()

df = cached_load_data()

# ============================================================================
# HEADER SECTION
# ============================================================================

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### Crime Pattern Analysis Dashboard")
    st.markdown("#### Advanced spatio-temporal hotspot detection for Chicago")
    # st.markdown("**Data source:** Chicago crime dataset | **Methodology:** DBSCAN clustering on space–time features")

# with col2:
#     st.info(f"**Last refreshed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

st.sidebar.markdown("## 🔧 Analysis Filters")
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

st.markdown("## 📈 Key Metrics")

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
        value=hotspots,
        help="Number of spatial clusters detected"
    )

with metric_cols[2]:
    st.metric(
        label="Arrests Made",
        value=arrests_stats["total_arrests"],
        delta=f"{arrests_stats['arrest_rate']:.1f}%",
        help="Total arrests and arrest rate"
    )

with metric_cols[3]:
    st.metric(
        label="Noise Ratio",
        value=f"{noise_pct:.1f}%",
        help="Crimes not belonging to any hotspot"
    )

with metric_cols[4]:
    avg_crimes_per_cluster = total / hotspots if hotspots > 0 else 0
    st.metric(
        label="Avg per Hotspot",
        value=f"{avg_crimes_per_cluster:.0f}",
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
            color_continuous_scale="Viridis",
            title="Crime Hotspots Distribution"
        )
        
        fig_map.update_traces(
            hovertemplate="<b>%{hover_name}</b><br>" +
            "Latitude: %{lat:.4f}<br>" +
            "Longitude: %{lon:.4f}<br>" +
            "Hour: %{customdata[1]}<br>" +
            "Arrested: %{customdata[2]}<br>" +
            "Cluster: %{customdata[3]}<extra></extra>"
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
            for idx, row in hotspot_data.head(5).iterrows():
                with st.container():
                    col_a, col_b = st.columns([1, 1])
                    with col_a:
                        st.metric(
                            f"Hotspot {int(row['st_cluster'])}",
                            f"{int(row['count'])} crimes",
                            help=f"Lat: {row['latitude']:.4f}, Lon: {row['longitude']:.4f}"
                        )
                    with col_b:
                        st.metric(
                            "Arrest Rate",
                            f"{row['arrest_rate']:.1f}%"
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
    
    # Reorder days
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_df["day_name"] = pd.Categorical(
        heatmap_df["day_name"],
        categories=day_order,
        ordered=True
    )
    heatmap_df = heatmap_df.sort_values(["day_name", "hour"])
    
    # Create heatmap
    fig_heatmap = px.density_heatmap(
        heatmap_df,
        x="hour",
        y="day_name",
        z="count",
        nbinsx=24,
        nbinsy=7,
        color_continuous_scale="RdYlBu_r",
        labels={"count": "Crime Count", "hour": "Hour of Day", "day_name": "Day of Week"},
        height=450,
        title="Crime Activity Heatmap"
    )
    
    fig_heatmap.update_layout(
        xaxis_title="Hour of Day (24h format)",
        yaxis_title="Day of Week",
        coloraxis_colorbar=dict(title="Crime Count"),
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
    crime_stats["Percentage"] = (crime_stats["crime_count"] / crime_stats["crime_count"].sum() * 100).round(2).astype(str) + "%"
    crime_stats = crime_stats.rename(columns={"crime_type": "Crime Type", "crime_count": "Count"})
    crime_stats = crime_stats[["Crime Type", "Count", "Percentage"]]
    
    st.dataframe(
        crime_stats.sort_values("Count", ascending=False ),
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
    
    st.markdown("### Summary Statistics")
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Avg Crimes/Day", f"{total/time_window:.1f}")
    
    with summary_col2:
        peak_hour = df_filtered.groupby("hour").size().idxmax()
        st.metric("Peak Hour", f"{peak_hour:02d}:00")
    
    with summary_col3:
        max_cluster = cluster_sizes.iloc[0]["size"] if not cluster_sizes.empty else 0
        st.metric("Largest Hotspot", f"{int(max_cluster)} crimes")
    
    with summary_col4:
        unique_crimes = df_filtered["primary_type"].nunique()
        st.metric("Crime Types", unique_crimes)
    
    st.markdown("---")
    st.markdown("### Raw Data Sample")
    
    display_cols = ["date", "latitude", "longitude", "primary_type", "hour", "arrest", "st_cluster"]
    display_cols = [col for col in display_cols if col in df_filtered.columns]
    
    st.dataframe(
        df_filtered[display_cols].head(100),
        use_container_width=True,
        height=400
    )

