import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from modules.clients import POSTGRES_CLIENT
from modules.controllers.fca import (
    calculate_brgy_catchment_areas,
    calculate_distance_matrix,
    calculate_gaussian_weight_df,
    calculate_library_catchment_areas,
)
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

library_geocoding_df = POSTGRES_CLIENT.read_table("library_geocoding")

selected_library_geocoding_df = pd.merge(
    selected_library_df,
    library_geocoding_df,
    left_on=["id", "NAME OF LIBRARY"],
    right_on=["id", "NAME OF LIBRARY"],
    how="inner",
).rename(
    columns={"geometry.location.lat": "latitude", "geometry.location.lng": "longitude"}
)

selected_library_geocoding_df["collection_size"] = 0
lib_column_order = tuple(
    ["id", "NAME OF LIBRARY", "place_id", "latitude", "longitude", "collection_size"]
)
if not selected_library_geocoding_df.empty:
    edited_selected_library_geocoding_df = st.data_editor(
        selected_library_geocoding_df,
        column_order=lib_column_order,
        hide_index=True,
        disabled=["id"],
        use_container_width=True,
    )
else:
    edited_selected_library_geocoding_df = pd.DataFrame()
    st.info("Please select at least one library.")


# Show editable dataframe for Barangay
st.markdown("Selected Barangays")
original_barangay_df = st.session_state["barangay_df"]
selected_barangay_df = original_barangay_df[
    original_barangay_df["id"].isin(
        [i[0] for i in st.session_state["barangay_multiselect"]]
    )
]

barangay_geocoding_df = POSTGRES_CLIENT.read_table("barangay_geocoding")

selected_barangay_geocoding_df = pd.merge(
    selected_barangay_df,
    barangay_geocoding_df,
    left_on="id",
    right_on="id",
    how="inner",
).rename(
    columns={"geometry.location.lat": "latitude", "geometry.location.lng": "longitude"}
)
barangay_column_order = tuple(
    ["id", "10-digit PSGC", "Name", "2020 Population", "latitude", "longitude"]
)
if not selected_barangay_geocoding_df.empty:
    edited_selected_barangay_geocoding_df = st.data_editor(
        selected_barangay_geocoding_df,
        column_order=barangay_column_order,
        hide_index=True,
        disabled=["id"],
        use_container_width=True,
    )
else:
    edited_selected_barangay_geocoding_df = pd.DataFrame()
    st.info("Please select at least one barangay.")


# Show map
if not selected_library_geocoding_df.empty and not selected_barangay_geocoding_df.empty:
    library_map = folium.Map(
        location=[
            selected_library_geocoding_df["latitude"].mean(),
            selected_library_geocoding_df["longitude"].mean(),
        ],
        zoom_start=11,
    )

    lib_valid_rows = selected_library_geocoding_df.dropna(
        subset=["latitude", "longitude"]
    )
    lib_invalid_rows = selected_library_geocoding_df[
        selected_library_geocoding_df[["latitude", "longitude"]].isna().any(axis=1)
    ]

    brgy_valid_rows = selected_barangay_geocoding_df.dropna(
        subset=["latitude", "longitude"]
    )
    brgy_invalid_rows = selected_barangay_geocoding_df[
        selected_barangay_geocoding_df[["latitude", "longitude"]].isna().any(axis=1)
    ]

    if len(lib_invalid_rows) > 0:
        st.info(
            f"The following libraries have no location data: {lib_invalid_rows['NAME OF LIBRARY'].tolist()}"
        )
    if len(brgy_invalid_rows) > 0:
        st.info(
            f"The following barangays have no location data: {brgy_invalid_rows['Name'].tolist()}"
        )

    for lib_index, lib_row in lib_valid_rows.iterrows():
        folium.Marker(
            location=[lib_row["latitude"], lib_row["longitude"]],
            popup=lib_row.iloc[5],
        ).add_to(library_map)
    for brgy_index, brgy_row in brgy_valid_rows.iterrows():
        folium.Marker(
            location=[brgy_row["latitude"], brgy_row["longitude"]],
            popup=brgy_row["Name"],
            icon=folium.Icon(color="red"),
        ).add_to(library_map)
    st_folium(library_map, width=700, height=500)

# E2SFCA
if (
    not edited_selected_library_geocoding_df.empty
    and not edited_selected_barangay_geocoding_df.empty
):
    # Catchment radius slider
    catchment_radius_slider = st.slider(
        "Catchment Radius (km)",
        min_value=1,
        max_value=20,
        value=2,
        step=1,
    )

    # Library FCA
    library_fca_df = calculate_library_catchment_areas(
        libraries_df=edited_selected_library_geocoding_df,
        barangays_df=edited_selected_barangay_geocoding_df,
        catchment_radius_km=catchment_radius_slider,
    )
    st.write("Library FCA")
    st.dataframe(library_fca_df, use_container_width=True, hide_index=True)

    # Distance Matrix
    distance_matrix = calculate_distance_matrix(
        libraries_df=edited_selected_library_geocoding_df,
        barangays_df=edited_selected_barangay_geocoding_df,
    )
    st.write("Distance Matrix")
    st.dataframe(distance_matrix, use_container_width=True)

    decay_parameter_slider = st.slider(
        "Decay Parameter (m)",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100,
    )

    # Weighted Distance Matrix
    weighted_distance_matrix = calculate_gaussian_weight_df(
        distance_matrix=distance_matrix,
        decay_parameter=decay_parameter_slider,
        cut_off=catchment_radius_slider * 1000,  # in meters
    )
    st.write("Weighted Distance Matrix")
    st.dataframe(weighted_distance_matrix, use_container_width=True)

    # E2SFCA
    st.write("E2SFCA")
    barangay_fca_df = calculate_brgy_catchment_areas(
        libraries_df=edited_selected_library_geocoding_df,
        libraries_fca_df=library_fca_df,
        barangays_df=edited_selected_barangay_geocoding_df,
        catchment_radius_km=catchment_radius_slider,
        decay_parameter=decay_parameter_slider,
        cut_off=catchment_radius_slider * 1000,  # in meters
    )
    st.dataframe(barangay_fca_df, use_container_width=True, hide_index=True)
