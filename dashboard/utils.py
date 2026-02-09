from datetime import datetime, timedelta
import pandas as pd

def apply_time_filter(df, days):
    cutoff = datetime.now() - timedelta(days=days)
    return df[df["date"] >= cutoff]

def get_overview_metrics(df):
    total = len(df)
    noise_pct = (df["st_cluster"] == -1).mean() * 100 if total > 0 else 0
    hotspots = df[df["st_cluster"] != -1]["st_cluster"].nunique()

    return total, hotspots, noise_pct

def filter_by_cluster(df, cluster):
    if cluster == "All":
        return df
    return df[df["st_cluster"] == cluster]

def hourly_distribution(df):
    return df.groupby("hour").size().reset_index(name="count")

def top_crime_types(df, top_n=5):
    vc = df["primary_type"].value_counts().head(top_n)

    crime_df = vc.reset_index()
    crime_df.columns = ["crime_type", "crime_count"]

    return crime_df

def arrest_rate(df):
    if len(df) == 0:
        return 0
    return df["arrest"].mean() * 100

def get_cluster_hotspots(df):
    """Get top hotspots with crime stats"""
    if "st_cluster" not in df.columns:
        return pd.DataFrame()
    
    hotspot_stats = (
        df[df["st_cluster"] != -1]
        .groupby("st_cluster")
        .agg({
            "latitude": "mean",
            "longitude": "mean",
            "primary_type": "count",
            "arrest": "mean"
        })
        .reset_index()
        .rename(columns={"primary_type": "count", "arrest": "arrest_rate"})
    )
    
    hotspot_stats["arrest_rate"] = hotspot_stats["arrest_rate"] * 100
    hotspot_stats = hotspot_stats.sort_values("count", ascending=False)
    
    return hotspot_stats

def get_daily_crime_trend(df):
    """Get daily crime trend"""
    daily_df = (
        df
        .groupby(df["date"].dt.date)
        .size()
        .reset_index(name="count")
    )
    daily_df.columns = ["date", "crimes"]
    return daily_df

def get_hour_crime_distribution(df):
    """Get crime distribution by hour of day"""
    hour_dist = df.groupby("hour").size().reset_index(name="count")
    hour_dist["hour_label"] = hour_dist["hour"].astype(str) + ":00"
    return hour_dist

def get_day_week_distribution(df):
    """Get crime distribution by day of week"""
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_dist = df.groupby("day_name").size().reset_index(name="count")
    day_dist["day_name"] = pd.Categorical(day_dist["day_name"], categories=day_order, ordered=True)
    return day_dist.sort_values("day_name")

def get_arrest_statistics(df):
    """Get arrest statistics"""
    total_arrests = df["arrest"].sum() if "arrest" in df.columns else 0
    arrest_pct = (total_arrests / len(df) * 100) if len(df) > 0 else 0
    
    return {
        "total_arrests": int(total_arrests),
        "arrest_rate": arrest_pct
    }

def get_location_stats(df):
    """Get location statistics"""
    if len(df) == 0:
        return {"avg_lat": 0, "avg_lon": 0, "crime_area": 0}
    
    avg_lat = df["latitude"].mean()
    avg_lon = df["longitude"].mean()
    
    # Calculate approximate area in sq km
    lat_range = df["latitude"].max() - df["latitude"].min()
    lon_range = df["longitude"].max() - df["longitude"].min()
    
    return {
        "avg_lat": avg_lat,
        "avg_lon": avg_lon,
        "lat_range": lat_range,
        "lon_range": lon_range
    }
