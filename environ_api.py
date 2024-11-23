import streamlit as st
import pandas as pd
import numpy as np
import datetime
import altair as alt

# Generate data with daily trends
def generate_trend_data(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq="15min")
    time = date_range.time  # Extract time of day

    # Light: Low at night, high during the day
    light = [
        100 if t.hour < 6 or t.hour >= 18 else np.random.uniform(700, 1000)
        for t in date_range
    ]

    # Temperature: 16°C at night, 21°C during the day with variability
    temp = [
        np.random.uniform(15, 17) if t.hour < 6 or t.hour >= 18 else np.random.uniform(20, 22)
        for t in date_range
    ]

    # Humidity: Low and stable at night, increasing during the day
    humidity = [
        np.random.uniform(30, 40) if t.hour < 6 or t.hour >= 18 else np.random.uniform(50, 70)
        for t in date_range
    ]

    # Sound: Low at night, peaks during classroom lessons (5 per day)
    sound = []
    for t in date_range:
        if t.hour < 6 or t.hour >= 18:  # Night hours
            sound.append(np.random.uniform(10, 20))
        elif t.hour in [8, 10, 12, 14, 16]:  # Lesson peaks
            sound.append(np.random.uniform(50, 80))
        else:
            sound.append(np.random.uniform(20, 30))

    # Combine into a DataFrame
    data = pd.DataFrame({
        "DateTime": date_range,
        "Light (lux)": light,
        "Temperature (°C)": temp,
        "Humidity (%)": humidity,
        "Sound Level (dB)": sound
    })

    return data

# Streamlit App
st.set_page_config(page_title="EnvironmentalAPI", layout="wide")

# Initialize session state for refreshing
if "refresh_data" not in st.session_state:
    st.session_state.refresh_data = False

# Sidebar/Left Column
with st.sidebar:
    st.title("EnvironmentalAPI")
    st.subheader("Filters")

    metric = st.selectbox(
        "Select Environmental Metric",
        options=["Temperature (°C)", "Humidity (%)", "Sound Level (dB)", "Light (lux)"]
    )

    location = st.selectbox(
        "Select Location",
        options=["Tech 1", "Tech 2"]
    )

    start_date = st.date_input(
        "Start Date",
        value=datetime.date(2024, 1, 1)
    )

    end_date = st.date_input(
        "End Date",
        value=datetime.date(2024, 1, 2)
    )

    if start_date > end_date:
        st.error("Start date cannot be after the end date!")

    # Refresh Button
    if st.button("Refresh Data"):
        st.session_state.refresh_data = not st.session_state.refresh_data

# Generate Data
data = generate_trend_data(start_date, end_date)

# Main Content
st.header(f"Selected Metric: {metric}")
st.subheader(f"Location: {location}")
st.write(f"Displaying data from {start_date} to {end_date}")

# Filter Data by Metric
metric_column = metric
data_filtered = data[["DateTime", metric_column]].rename(columns={metric_column: "Value"})

# Altair Chart with Shaded Area
st.subheader("Environmental Data Over Time")
area_chart = (
    alt.Chart(data_filtered)
    .mark_area(opacity=0.2, interpolate="monotone")
    .encode(
        x=alt.X("DateTime:T", title="Date"),
        y=alt.Y("Value:Q", title=metric),
    )
)

line_chart = (
    alt.Chart(data_filtered)
    .mark_line(interpolate="monotone", strokeWidth=2)
    .encode(
        x=alt.X("DateTime:T", title="Date"),
        y=alt.Y("Value:Q", title=metric),
        tooltip=["DateTime:T", "Value:Q"]
    )
)

# Combine line and area charts
combined_chart = (area_chart + line_chart).properties(
    width=700,  # Customize width
    height=400,  # Customize height
    title=f"{metric} Over Time"
).interactive()  # Allow zoom and pan

st.altair_chart(combined_chart, use_container_width=True)

# Analytics Table
st.subheader("Analytics Summary")
max_value = data_filtered["Value"].max()
min_value = data_filtered["Value"].min()
average_value = data_filtered["Value"].mean()

analytics_table = pd.DataFrame({
    "Statistic": ["Max Value", "Min Value", "Average Value"],
    "Value": [f"{max_value:.2f}", f"{min_value:.2f}", f"{average_value:.2f}"]
})

st.table(analytics_table)
