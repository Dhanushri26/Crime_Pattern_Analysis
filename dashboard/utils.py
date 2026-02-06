from datetime import datetime, timedelta

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
