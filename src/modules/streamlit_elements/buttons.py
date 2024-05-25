import pandas as pd
import streamlit as st
from streamlit_extras.row import row

from modules.clients import POSTGRES_CLIENT
from modules.controllers.geocoding import batch_geolocate_df

POSTGRES_CLIENT = POSTGRES_CLIENT


@st.experimental_dialog("Create Table")
def create_table_modal(table_name, df):
    st.write(f"Are you sure you want to save the table '{table_name}'?")
    confirm_row = row(1, vertical_align="center")
    if confirm_row.button(
        ":heavy_check_mark: Confirm",
        use_container_width=True,
    ):
        create_table(table_name, df)


@st.experimental_dialog("Update Table")
def update_table_modal(table_name, df, changes: dict):
    st.write(
        f"Are you sure you want to save {len(changes)} changes "
        f"to the table '{table_name}'?"
    )
    changes_df = pd.DataFrame.from_dict(changes, orient="index")
    st.write(changes_df)
    confirm_row = row(1, vertical_align="center")
    if confirm_row.button(
        ":heavy_check_mark: Confirm",
        use_container_width=True,
    ):
        update_table(df)


@st.experimental_dialog("Delete Table")
def delete_table_modal(table_name):
    st.write(f"Are you sure you want to delete the table '{table_name}'?")
    confirm_row = row(1, vertical_align="center")
    if confirm_row.button(
        ":heavy_check_mark: Confirm",
        use_container_width=True,
    ):
        delete_table(table_name)


@st.experimental_dialog("Geocode Table")
def geocode_table_modal(table_name):
    st.write(
        """:warning: This action may take a long time. Make sure to save
        any changes to the table first before geocoding it."""
    )
    st.write(f"Are you sure you want to geocode the table '{table_name}'?")
    skip_existing = st.checkbox("Skip rows with geolocation", value=True)
    confirm_row = row(1, vertical_align="center")
    if confirm_row.button(
        ":heavy_check_mark: Confirm",
        use_container_width=True,
    ):
        geocode_table(table_name, skip_existing)


def update_table(df):
    try:
        POSTGRES_CLIENT.create_table("barangay", df)
        st.success("Table updated successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"An error occurred while updating the table: '{e}'")


def delete_table(table_name):
    try:
        POSTGRES_CLIENT.delete_table(table_name)
        POSTGRES_CLIENT.delete_table(f"{table_name}_geocoding")
        st.success("Table deleted successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"An error occurred while deleting the table: '{e}'")


def create_geocoding_table(table_name, df):
    # Additional columns are the results of google maps geocoding
    additional_columns = [
        {"name": "string"},
        {"place_id": "string"},
        {"geometry.location.lat": "float"},
        {"geometry.location.lng": "float"},
        {"geometry.viewport.northeast.lat": "float"},
        {"geometry.viewport.northeast.lng": "float"},
        {"geometry.viewport.southwest.lat": "float"},
        {"geometry.viewport.southwest.lng": "float"},
    ]
    if table_name == "barangay":
        # Keep only id and 10-digit PSGC columns
        POSTGRES_CLIENT.create_table(
            f"{table_name}_geocoding",
            df[["10-digit PSGC"]],
            additional_columns=additional_columns,
        )
    elif table_name == "library":
        # Keep only id and 'NAME OF LIBRARY' columns
        POSTGRES_CLIENT.create_table(
            f"{table_name}_geocoding",
            df[["NAME OF LIBRARY"]],
            additional_columns=additional_columns,
        )
    else:
        raise ValueError(f"Table name '{table_name}' is not supported.")


def create_table(table_name, df):
    try:
        POSTGRES_CLIENT.create_table(table_name, df)
        st.success("Table saved successfully!")
        create_geocoding_table(table_name, df)
        st.rerun()
    except Exception as e:
        st.error(f"An error occurred while saving the table: '{e}'")


def geocode_table(table_name, skip_existing=True):
    try:
        batch_geolocate_df(table_name, skip_existing=skip_existing)
        st.success("Table geocoded successfully!")
    except Exception as e:
        st.error(f"An error occurred while geocoding the table: '{e}'")
