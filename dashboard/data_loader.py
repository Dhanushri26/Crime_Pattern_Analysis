import pandas as pd
import streamlit as st

@st.cache_data
def load_crime_data():
    df = pd.read_csv("../data/processed/chicago_crime_with_clusters.csv")

    # Parse datetime
    df["date"] = pd.to_datetime(df["date"])

    # Sanity check
    required_cols = {
        "latitude", "longitude", "primary_type",
        "arrest", "hour", "st_cluster", "date"
    }

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")

    return df
