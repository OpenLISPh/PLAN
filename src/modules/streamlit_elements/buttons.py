import pandas as pd
import streamlit as st
from streamlit_extras.row import row

from modules.clients import POSTGRES_CLIENT

POSTGRES_CLIENT = POSTGRES_CLIENT


@st.experimental_dialog("Update Table")
def update_table_modal(table_name, df, changes: dict):
    st.write(
        f"Are you sure you want to save {len(changes)} changes "
        f"to the table '{table_name}'?"
    )
    changes_df = pd.DataFrame.from_dict(changes, orient="index")
    st.write(changes_df)
    confirm_row = row(1, vertical_align="center")
    confirm_row.button(
        ":heavy_check_mark: Confirm",
        on_click=update_table,
        args=(df,),
        use_container_width=True,
    )


@st.experimental_dialog("Delete Table")
def delete_table_modal(table_name):
    st.write(f"Are you sure you want to delete the table '{table_name}'?")
    confirm_row = row(1, vertical_align="center")
    confirm_row.button(
        ":heavy_check_mark: Confirm",
        on_click=delete_table,
        args=(table_name,),
        use_container_width=True,
    )


@st.experimental_dialog("Geocode Table")
def geocode_table_modal(table_name):
    st.write(f"Are you sure you want to geocode the table '{table_name}'?")
    confirm_row = row(1, vertical_align="center")
    confirm_row.button(
        ":heavy_check_mark: Confirm",
        on_click=geocode_table,
        args=(table_name,),
        use_container_width=True,
    )


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
        st.success("Table deleted successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"An error occurred while deleting the table: '{e}'")


def create_table(table_name, df):
    try:
        POSTGRES_CLIENT.create_table(table_name, df)
        st.success("Table saved successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"An error occurred while saving the table: '{e}'")


def geocode_table(table_name):
    pass
