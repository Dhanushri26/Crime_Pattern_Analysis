# 🚔 Crime Hotspot Analysis Dashboard

An interactive spatio-temporal crime analysis dashboard that identifies **crime hotspots**, **time-based risk patterns**, and **crime composition trends** using clustering and data visualization techniques.

Built with **Streamlit** and **Plotly**, the project focuses on transforming raw crime data into **clear, actionable insights**.

---

## 📌 Problem Statement

Urban crime datasets are large, noisy, and difficult to interpret in raw form.  
Traditional tables fail to answer key questions such as:

- Where do crimes concentrate?
- When does crime risk peak?
- What types of crimes dominate hotspots?

This project addresses these gaps through **spatial clustering**, **temporal analysis**, and **interactive visualization**.

---

## 🎯 Objectives

- Detect spatial crime hotspots using clustering
- Analyze temporal crime patterns (hourly & daily)
- Enable intuitive, interactive data exploration
- Reduce cognitive load through strong visual hierarchy
- Present insights in an interview-ready, production-style dashboard

---

## ✨ Features

### 🔹 Hotspot Detection
- Spatial clustering using **DBSCAN**
- Automatic identification of noise (outliers)
- Cluster-level filtering

### 🔹 Temporal Analysis
- Day × Hour crime intensity heatmap
- Rolling time window analysis (7–365 days)
- Identification of high-risk time periods

### 🔹 Interactive Dashboard
- KPI overview (total crimes, active hotspots, noise ratio)
- Map-based hotspot visualization
- Crime type distribution (Bar / Pie toggle)
- Real-time filtering without page reloads

### 🔹 Clean UX Design
- Clear visual hierarchy
- One-question-per-section layout
- Progressive disclosure of detail

---

## 🛠️ Tech Stack

| Component | Technology |
|---------|------------|
| Frontend | Streamlit |
| Visualization | Plotly |
| Data Processing | Pandas |
| Clustering | DBSCAN (scikit-learn) |
| Mapping | Mapbox (OpenStreetMap) |
| Language | Python |

---

## 🗂️ Project Structure


crime-hotspot-dashboard/
│
├── app.py # Main Streamlit dashboard
├── data_loader.py # Data loading & preprocessing
├── utils.py # Metrics, filtering & aggregation logic
├── requirements.txt # Python dependencies
├── README.md # Project documentation
└── data/
└── crime_data.csv # Chicago crime dataset



---

## ⚙️ Data Pipeline


Raw Crime Data
↓
Data Cleaning & Feature Engineering
↓
DBSCAN Spatial Clustering
↓
Temporal Aggregations
↓
Interactive Visualization Dashboard



---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/crime-hotspot-dashboard.git
cd crime-hotspot-dashboard


pip install -r requirements.txt

streamlit run app.py
