import requests
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import os
API_URL = "https://data.cityofchicago.org/resource/ijzp-q8t2.json?$limit=10000"

print("Fetching new crime data...")

# Fetch data
response = requests.get(API_URL)
data = response.json()

df = pd.DataFrame(data)

print("Data fetched:", len(df), "records")

# -----------------------
# Data preprocessing
# -----------------------

df["date"] = pd.to_datetime(df["date"])
df["hour"] = df["date"].dt.hour

df = df.dropna(subset=["latitude", "longitude"])

df["latitude"] = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)

# -----------------------
# Spatio-temporal features
# -----------------------

X = df[["latitude", "longitude", "hour"]]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -----------------------
# Run DBSCAN
# -----------------------

dbscan = DBSCAN(
    eps=0.25,
    min_samples=15
)

df["st_cluster"] = dbscan.fit_predict(X_scaled)

print("Clusters generated")

# -----------------------
# Save updated dataset
# -----------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

output_path = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "chicago_crime_with_clusters.csv"
)

df.to_csv(output_path, index=False)

print("Dataset saved to:", output_path)

print("Dataset updated successfully")
print("Update time:", datetime.now())