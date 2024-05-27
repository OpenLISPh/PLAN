import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from modules.clients import POSTGRES_CLIENT
from modules.streamlit_elements import user_styling, user_ui

# Apply User Styling
user_styling.user_styling()

# Apply User UI
user_ui.sidebar()

# Show editable dataframe for Library
st.markdown("Selected Libraries")
original_library_df = st.session_state["library_df"]
selected_library_df = original_library_df[
    original_library_df["id"].isin(
        [i[0] for i in st.session_state["library_multiselect"]]
    )
]
selected_library_df["User Input"] = None
lib_column_order = tuple(["id", "NAME OF LIBRARY", "User Input"])
if not selected_library_df.empty:
    st.data_editor(
        selected_library_df,
        column_order=lib_column_order,
        hide_index=True,
        disabled=["id"],
    )
else:
    st.info("Please select at least one library.")


# Show editable dataframe for Barangay
st.markdown("Selected Barangays")
original_barangay_df = st.session_state["barangay_df"]
selected_barangay_df = original_barangay_df[
    original_barangay_df["id"].isin(
        [i[0] for i in st.session_state["barangay_multiselect"]]
    )
]
barangay_column_order = tuple(["id", "10-digit PSGC", "Name"])
if not selected_barangay_df.empty:
    st.data_editor(
        selected_barangay_df, column_order=barangay_column_order, hide_index=True
    )
else:
    st.info("Please select at least one barangay.")


# Get geodata for libraries and barangays
library_geocoding_df = POSTGRES_CLIENT.read_table("library_geocoding")
barangay_geocoding_df = POSTGRES_CLIENT.read_table("barangay_geocoding")

# Merge geocoding dataframes
selected_library_geocoding_df = pd.merge(
    selected_library_df,
    library_geocoding_df,
    left_on="id",
    right_on="id",
    how="left",
).rename(
    columns={"geometry.location.lat": "latitude", "geometry.location.lng": "longitude"}
)

# st.write(library_geocoding_df)
# st.write(selected_library_geocoding_df)

selected_barangay_geocoding_df = pd.merge(
    selected_barangay_df,
    barangay_geocoding_df,
    left_on="id",
    right_on="id",
    how="left",
).rename(
    columns={"geometry.location.lat": "latitude", "geometry.location.lng": "longitude"}
)


# Show map
if not selected_library_geocoding_df.empty and not selected_barangay_geocoding_df.empty:
    library_map = folium.Map(
        location=[
            selected_library_geocoding_df["latitude"].mean(),
            selected_library_geocoding_df["longitude"].mean(),
        ],
        zoom_start=11,
    )
    for lib_index, lib_row in selected_library_geocoding_df.iterrows():
        # st.write(f"Column names: {lib_row[6]}")
        folium.Marker(
            location=[lib_row["latitude"], lib_row["longitude"]],
            popup=lib_row[5],
        ).add_to(library_map)
    for brgy_index, brgy_row in selected_barangay_geocoding_df.iterrows():
        folium.Marker(
            location=[brgy_row["latitude"], brgy_row["longitude"]],
            popup=brgy_row["Name"],
            icon=folium.Icon(color="red"),
        ).add_to(library_map)
    st_folium(library_map, width=700, height=500)
