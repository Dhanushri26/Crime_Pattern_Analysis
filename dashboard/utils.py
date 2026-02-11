from datetime import datetime, timedelta
import pandas as pd

def apply_time_filter(df, days):
    cutoff = datetime.now() - timedelta(days=days)
    return df[df["date"] >= cutoff]

def get_overview_metrics(df):
    total = len(df)
    noise_pct = float((df["st_cluster"] == -1).mean() * 100) if total > 0 else 0.0
    hotspots = int(df[df["st_cluster"] != -1]["st_cluster"].nunique())

    return total, hotspots, noise_pct


def get_exact_key_metrics(df):
    """Exact counts from data for key metrics (no rounding until display)."""
    total = len(df)
    if total == 0:
        return {
            "total_crimes": 0,
            "noise_count": 0,
            "crimes_in_hotspots": 0,
            "hotspot_count": 0,
            "total_arrests": 0,
            "arrest_rate_pct": 0.0,
            "noise_pct": 0.0,
            "avg_per_hotspot": 0.0,
        }
    noise_mask = df["st_cluster"] == -1
    noise_count = int(noise_mask.sum())
    hotspot_df = df[df["st_cluster"] != -1]
    crimes_in_hotspots = len(hotspot_df)
    hotspot_count = int(hotspot_df["st_cluster"].nunique())
    total_arrests = int(df["arrest"].sum()) if "arrest" in df.columns else 0
    arrest_rate_pct = float(total_arrests / total * 100)
    noise_pct = float(noise_count / total * 100)
    avg_per_hotspot = crimes_in_hotspots / hotspot_count if hotspot_count > 0 else 0.0
    return {
        "total_crimes": total,
        "noise_count": noise_count,
        "crimes_in_hotspots": crimes_in_hotspots,
        "hotspot_count": hotspot_count,
        "total_arrests": total_arrests,
        "arrest_rate_pct": arrest_rate_pct,
        "noise_pct": noise_pct,
        "avg_per_hotspot": avg_per_hotspot,
    }

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
    """Get top hotspots with exact stats from data: count, arrests, centroid, top crime, date range."""
    if "st_cluster" not in df.columns:
        return pd.DataFrame()

    cluster_df = df[df["st_cluster"] != -1]
    if cluster_df.empty:
        return pd.DataFrame()

    # Exact aggregates from data
    agg = cluster_df.groupby("st_cluster").agg(
        latitude=("latitude", "mean"),
        longitude=("longitude", "mean"),
        count=("primary_type", "count"),
        arrests=("arrest", "sum"),
        date_min=("date", "min"),
        date_max=("date", "max"),
    ).reset_index()

    # Arrest rate from exact counts
    agg["arrest_rate"] = (agg["arrests"] / agg["count"] * 100).round(2)
    agg["arrests"] = agg["arrests"].astype(int)

    # Top crime type per cluster (mode from data)
    def top_crime(s):
        vc = s.value_counts()
        return vc.index[0] if len(vc) else "—"

    top_crimes = cluster_df.groupby("st_cluster")["primary_type"].apply(top_crime).reset_index()
    top_crimes.columns = ["st_cluster", "top_crime_type"]
    agg = agg.merge(top_crimes, on="st_cluster", how="left")

    agg = agg.sort_values("count", ascending=False)
    return agg

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
    arrest_pct = float(total_arrests / len(df) * 100) if len(df) > 0 else 0.0
    
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
