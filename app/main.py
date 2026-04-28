import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(
    page_title="Climate Dashboard",
    layout="wide"
)

st.title("Climate Comparison Dashboard")

# -------------------------
# Correct Data Folder Path
# -------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))

data_folder = os.path.join(
    os.path.dirname(base_dir),
    "data"
)

# -------------------------
# Climate Files Only
# -------------------------
files = [
    "ethiopia_clean.csv",
    "kenya_clean.csv",
    "nigeria_clean.csv",
    "sudan_clean.csv",
    "tanzania_clean.csv"
]

dfs = []

# -------------------------
# Load CSV Files
# -------------------------
for file_name in files:

    file_path = os.path.join(data_folder, file_name)

    if os.path.exists(file_path):

        try:
            df = pd.read_csv(file_path)

        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin1")

        # Clean columns
        df.columns = df.columns.str.strip().str.upper()

        # Add Country if missing
        if "COUNTRY" not in df.columns:
            country = file_name.replace("_clean.csv", "").capitalize()
            df["COUNTRY"] = country

        dfs.append(df)

# -------------------------
# Stop if Nothing Loaded
# -------------------------
if len(dfs) == 0:
    st.error("No climate CSV files found inside data folder.")
    st.write("Expected location:")
    st.code(data_folder)
    st.stop()

# -------------------------
# Combine Data
# -------------------------
data = pd.concat(dfs, ignore_index=True)

# -------------------------
# Validate DATE Column
# -------------------------
if "DATE" not in data.columns:
    st.error("DATE column not found.")
    st.write("Available columns:")
    st.write(list(data.columns))
    st.stop()

# -------------------------
# Convert Date
# -------------------------
data["DATE"] = pd.to_datetime(
    data["DATE"],
    errors="coerce"
)

data = data.dropna(subset=["DATE"])

# -------------------------
# Create Year
# -------------------------
data["YEAR"] = data["DATE"].dt.year

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("Filters")

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=sorted(data["COUNTRY"].unique()),
    default=sorted(data["COUNTRY"].unique())
)

year_range = st.sidebar.slider(
    "Select Year Range",
    int(data["YEAR"].min()),
    int(data["YEAR"].max()),
    (
        int(data["YEAR"].min()),
        int(data["YEAR"].max())
    )
)

selected_variable = st.sidebar.selectbox(
    "Select Variable",
    ["T2M", "PRECTOTCORR", "RH2M"]
)

# -------------------------
# Filter Data
# -------------------------
filtered = data[
    (data["COUNTRY"].isin(selected_countries)) &
    (data["YEAR"] >= year_range[0]) &
    (data["YEAR"] <= year_range[1])
]

# -------------------------
# Empty Filter Check
# -------------------------
if filtered.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# -------------------------
# Trend Chart
# -------------------------
st.subheader(f"{selected_variable} Trend Over Time")

trend = filtered.groupby(
    ["YEAR", "COUNTRY"]
)[selected_variable].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 6))

for country in trend["COUNTRY"].unique():

    subset = trend[trend["COUNTRY"] == country]

    ax.plot(
        subset["YEAR"],
        subset[selected_variable],
        label=country
    )

ax.set_xlabel("Year")
ax.set_ylabel(selected_variable)
ax.set_title(f"{selected_variable} Trend by Country")
ax.legend()

st.pyplot(fig)

# -------------------------
# Rainfall Distribution
# -------------------------
st.subheader("Precipitation Distribution")

fig2, ax2 = plt.subplots(figsize=(10, 6))

filtered.boxplot(
    column="PRECTOTCORR",
    by="COUNTRY",
    ax=ax2
)

plt.suptitle("")
ax2.set_title("Rainfall Distribution")
ax2.set_xlabel("Country")
ax2.set_ylabel("PRECTOTCORR")

st.pyplot(fig2)

# -------------------------
# Dataset Preview
# -------------------------
st.subheader("Dataset Preview")

st.dataframe(filtered.head())
