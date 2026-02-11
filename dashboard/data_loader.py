import pandas as pd
import streamlit as st
from pathlib import Path

# Resolve data path relative to this file (works from project root or dashboard/)
_BASE_DIR = Path(__file__).resolve().parent.parent
_DATA_PATH = _BASE_DIR / "data" / "processed" / "chicago_crime_with_clusters.csv"

@st.cache_data
def load_crime_data():
    if not _DATA_PATH.exists():
        raise FileNotFoundError(
            f"Crime data file not found: {_DATA_PATH}. "
            "Ensure 'data/processed/chicago_crime_with_clusters.csv' exists."
        )
    df = pd.read_csv(_DATA_PATH)

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
