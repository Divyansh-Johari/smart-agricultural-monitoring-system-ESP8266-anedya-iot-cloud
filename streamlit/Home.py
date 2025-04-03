import streamlit as st
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh

from utils.anedya import anedya_config, fetchHumidityData, fetchTemperatureData, fetchMoistureData

nodeId = "157743b8-3975-11ef-9ecc-a1461caa74a3"
apiKey = "a97a55bb0925ad628f6d2c4d7664f4b0919e198e2720504d2c02901dc7387408"

st.set_page_config(page_title="Agriculture Dashboard", layout="wide")
st_autorefresh(interval=10000, limit=None, key="auto-refresh-handler")

st.title("Smart Agriculture Dashboard")
st.subheader("Real-time Monitoring and Crop Recommendations")

# User Inputs
location = st.selectbox("Select your location", ["North India", "South India", "West India", "East India"])
season = st.selectbox("Select the current season", ["Summer", "Monsoon", "Winter"])

# Fetch live data with error handling
anedya_config(nodeId, apiKey)

def safe_fetch(fetch_function, name):
    try:
        return fetch_function()
    except Exception as e:
        st.error(f"Error fetching {name} data: {e}")
        return pd.DataFrame()

humidityData = safe_fetch(fetchHumidityData, "humidity")
temperatureData = safe_fetch(fetchTemperatureData, "temperature")
moistureData = safe_fetch(fetchMoistureData, "moisture")

# Display live sensor data
st.subheader("Current Sensor Data")
cols = st.columns(3)
cols[0].metric("Humidity", f"{humidityData.iloc[-1]['value']}%" if not humidityData.empty else "N/A")
cols[1].metric("Temperature", f"{temperatureData.iloc[-1]['value']}°C" if not temperatureData.empty else "N/A")
cols[2].metric("Moisture", f"{moistureData.iloc[-1]['value']}" if not moistureData.empty else "N/A")

# Crop Recommendation Function
def get_crop_recommendations(location, season):
    crop_data = {
        "North India": {"Summer": ["Maize", "Bajra"], "Monsoon": ["Rice", "Millets"], "Winter": ["Wheat", "Mustard"]},
        "South India": {"Summer": ["Ragi", "Groundnut"], "Monsoon": ["Paddy", "Turmeric"], "Winter": ["Sunflower", "Barley"]},
        "West India": {"Summer": ["Cotton", "Jowar"], "Monsoon": ["Sugarcane", "Soybean"], "Winter": ["Chickpea", "Wheat"]},
        "East India": {"Summer": ["Jute", "Sesame"], "Monsoon": ["Rice", "Tea"], "Winter": ["Potato", "Mustard"]},
    }
    return crop_data.get(location, {}).get(season, "No recommendations available")

# Nutrient Suggestion Function
def get_nutrient_suggestions(moistureData, temperatureData):
    if moistureData.empty or temperatureData.empty:
        return "No data available for analysis."
    
    moisture_level = moistureData.iloc[-1]['value']
    temperature_level = temperatureData.iloc[-1]['value']
    
    if moisture_level < 30:
        moisture_status = "Low moisture detected. Add organic matter and mulching."
    else:
        moisture_status = "Moisture levels are adequate."
    
    if temperature_level > 35:
        temperature_status = "High temperature detected. Consider shade nets or irrigation."
    else:
        temperature_status = "Temperature is within optimal range."
    
    return f"{moisture_status} {temperature_status}"

# Crop Recommendation
st.subheader("Recommended Crops")
crop_suggestions = get_crop_recommendations(location, season)
st.write(crop_suggestions)

# Nutrient Suggestion
st.subheader("Soil Nutrient Suggestions")
nutrient_suggestions = get_nutrient_suggestions(moistureData, temperatureData)
st.write(nutrient_suggestions)

# Plot Temperature Graph
st.subheader("Temperature Trends")
if not temperatureData.empty:
    temperature_chart = alt.Chart(temperatureData).mark_line(color='red').encode(
        x='Datetime:T',
        y='value:Q',
        tooltip=['Datetime:T', 'value:Q']
    ).interactive()
    st.altair_chart(temperature_chart, use_container_width=True)
else:
    st.write("No Temperature Data Available")

# Plot Humidity Graph
st.subheader("Humidity Trends")
if not humidityData.empty:
    humidity_chart = alt.Chart(humidityData).mark_line(color='blue').encode(
        x='Datetime:T',
        y='value:Q',
        tooltip=['Datetime:T', 'value:Q']
    ).interactive()
    st.altair_chart(humidity_chart, use_container_width=True)
else:
    st.write("No Humidity Data Available")

# Plot Moisture Graph
st.subheader("Moisture Trends")
if not moistureData.empty:
    moisture_chart = alt.Chart(moistureData).mark_line(color='green').encode(
        x='Datetime:T',
        y='value:Q',
        tooltip=['Datetime:T', 'value:Q']
    ).interactive()
    st.altair_chart(moisture_chart, use_container_width=True)
else:
    st.write("No Moisture Data Available")

st.success("Dashboard Updated Successfully!")
