import pandas as pd
import streamlit as st

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
    if st.button("Confirm"):
        update_table(df)


@st.experimental_dialog("Delete Table")
def delete_table_modal(table_name):
    st.write(f"Are you sure you want to delete the table '{table_name}'?")
    if st.button("Confirm"):
        delete_table(table_name)


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
