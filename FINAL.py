"""
Name: Andhika Sitepu
CS230: Section 6
Data: Airports Dataset (airports.csv)
URL: Link to your web application on Streamlit Cloud (if posted)

Description:
This program explores and visualizes airport data in New England states using Streamlit.
The output will provide insights from  maps, charts, and tables.
"""

import pandas as pd
import streamlit as st
import pydeck as pdk
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# [ST4]
st.set_page_config(page_title="New England Airport Explorer", layout="wide")
st.sidebar.image("logo.png",
use_container_width=True)

# Load and clean data [DA1]
@st.cache_data
def load_data():
    data = pd.read_csv('airports.csv')
    data = data.dropna(subset=["latitude_deg", "longitude_deg"])
    data = data.drop(columns=["scheduled_service", "gps_code", "iata_code",
                               "local_code", "home_link", "wikipedia_link", "keywords"], errors="ignore")
    region_labels = {
        "US-MA": "Massachusetts",
        "US-CT": "Connecticut",
        "US-RI": "Rhode Island",
        "US-NH": "New Hampshire",
        "US-VT": "Vermont",
        "US-ME": "Maine",
    }
    data["region_label"] = data["iso_region"].map(region_labels)

    # Add RGB color mappings for regions
    region_colors = {
        "Massachusetts": [255, 0, 0],  # Red
        "Connecticut": [0, 255, 0],    # Green
        "Rhode Island": [0, 0, 255],  # Blue
        "New Hampshire": [255, 255, 0],  # Yellow
        "Vermont": [255, 165, 0],     # Orange
        "Maine": [128, 0, 128],       # Purple
    }
    data["region_color"] = data["region_label"].map(region_colors)
    return data

# Extra address and location filter function
def geocode_address(address):
    geolocator = Nominatim(user_agent="airport_locator")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Function to calculate distance
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).miles

# Load full dataset
airports_data = load_data()

# Filter data for New England states
new_england_data = airports_data[airports_data["region_label"].notnull()]

# Sidebar Filters
st.sidebar.title("Filters")

# [ST1] Dropdown for airport type with "Select All" option
airport_types = ["Select All"] + list(new_england_data["type"].unique())
airport_type = st.sidebar.selectbox("Select Airport Type", airport_types)
if airport_type == "Select All":
    filtered_airport_type = new_england_data["type"]
else:
    filtered_airport_type = [airport_type]

# [ST2] Multiselect for regions
selected_regions = st.sidebar.multiselect(
    "Select Regions",
    new_england_data["region_label"].unique(),
    default=new_england_data["region_label"].unique(),
)

# [ST3] Slider for elevation range
elevation_range = st.sidebar.slider(
    "Select Elevation Range (ft)",
    0,
    10000,
    (0, 10000)
)

#Extra address
st.sidebar.subheader("Find Nearest Airports")
user_address = st.sidebar.text_input("Enter Your Address", value="Boston, MA")

# Filter data based on user inputs
filtered_data = new_england_data[
    (new_england_data["type"].isin(filtered_airport_type)) &
    (new_england_data["region_label"].isin(selected_regions)) &
    (new_england_data["elevation_ft"] >= elevation_range[0]) &
    (new_england_data["elevation_ft"] <= elevation_range[1])
]

# Main Section Title and Subtitle
st.markdown("<h1 style='text-align: center; font-size: 40px; font-weight: bold; color: red;'>New England Airport Explorer</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-size: 24px; font-weight: bold;'>Airports in the New England region with interactive maps and filters</h3>", unsafe_allow_html=True)

# [VIZ1] Bar Chart for Airport Distribution by Region
st.subheader("Airport Distribution by Region")
if not filtered_data.empty:
    region_counts = filtered_data["region_label"].value_counts()
    st.bar_chart(region_counts)
else:
    st.warning("No data available for chart.")

# [VIZ2] Table of Filtered Data
st.subheader("Filtered Airport Data")
if not filtered_data.empty:
    st.dataframe(filtered_data[["name", "type", "region_label", "elevation_ft"]])
else:
    st.warning("No data available for table.")

# [MAP] Interactive Map of Airport Locations with Legend and Color Coding
st.subheader("Airport Locations")
if not filtered_data.empty:
    legend_html = """
    <div style="text-align: left; padding: 10px;">
        <b>Legend:</b><br>
        <div style="display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background-color: rgb(255, 0, 0); margin-right: 5px;"></div> Massachusetts
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background-color: rgb(0, 255, 0); margin-right: 5px;"></div> Connecticut
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background-color: rgb(0, 0, 255); margin-right: 5px;"></div> Rhode Island
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background-color: rgb(255, 255, 0); margin-right: 5px;"></div> New Hampshire
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background-color: rgb(255, 165, 0); margin-right: 5px;"></div> Vermont
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background-color: rgb(128, 0, 128); margin-right: 5px;"></div> Maine
        </div>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)

    # Display the map with color-coded regions
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v11",
        initial_view_state=pdk.ViewState(
            latitude=filtered_data["latitude_deg"].mean(),
            longitude=filtered_data["longitude_deg"].mean(),
            zoom=6,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=filtered_data,
                get_position="[longitude_deg, latitude_deg]",
                get_color="region_color",  # Reference region color
                get_radius=1000,
                pickable=True,
            )
        ],
        tooltip={"html": "<b>Airport:</b> {name}<br><b>Region:</b> {region_label}<br><b>Elevation:</b> {elevation_ft} ft"}
    ))
else:
    st.warning("No airports to display on the map.")

# Statistics [PY2]
def airport_statistics(data):
    """Return max, min, and average elevation using NumPy along with airport names."""
    elevations = data["elevation_ft"].to_numpy()
    max_index = np.argmax(elevations)
    min_index = np.argmin(elevations)
    max_elevation = elevations[max_index]
    min_elevation = elevations[min_index]
    avg_elevation = np.mean(elevations)
    return max_index, min_index, max_elevation, min_elevation, avg_elevation, len(elevations)

if not filtered_data.empty:
    max_index, min_index, max_elevation, min_elevation, avg_elevation, total_airports = airport_statistics(filtered_data)
    max_airport = filtered_data.iloc[max_index]
    min_airport = filtered_data.iloc[min_index]

    st.markdown(
        f"<span style='font-size: 20px;'>**Max Elevation (ft):** {max_elevation} ({max_airport['name']})</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span style='font-size: 20px;'>**Min Elevation (ft):** {min_elevation} ({min_airport['name']})</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span style='font-size: 20px;'>**Average Elevation (ft):** {avg_elevation:.2f}</span> "
        f"<span style='font-size: 16px;'>(based on {total_airports} airports)</span>",
        unsafe_allow_html=True,
    )
else:
    st.warning("No data matches your filters.")

# Geocode user address and calculate distances
if user_address:
    user_lat, user_lon = geocode_address(user_address)
    if user_lat is not None and user_lon is not None:
        # Calculate distances
        filtered_data["distance_from_user"] = filtered_data.apply(
            lambda row: calculate_distance(user_lat, user_lon, row["latitude_deg"], row["longitude_deg"]),
            axis=1
        )

        # Find the 5 nearest airports
        nearest_airports = filtered_data.nsmallest(5, "distance_from_user")

        # Display results in a simple table
        st.subheader("Five Nearest Airports")
        st.write(nearest_airports[["name", "region_label", "distance_from_user"]])
    else:
        st.warning("Could not locate the provided address. Please try again.")

# Footer Information
st.sidebar.info("Created by Andhika Sitepu")