import streamlit as st

from modules.clients import POSTGRES_CLIENT

POSTGRES_CLIENT = POSTGRES_CLIENT


def update_table(df):
    try:
        POSTGRES_CLIENT.create_table("barangay", df)
        st.success("Table updated successfully!")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"An error occurred while updating the table: '{e}'")


def delete_table(table_name):
    try:
        POSTGRES_CLIENT.delete_table(table_name)
        st.success("Table deleted successfully!")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"An error occurred while deleting the table: '{e}'")


def create_table(table_name, df):
    try:
        POSTGRES_CLIENT.create_table(table_name, df)
        st.success("Table saved successfully!")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"An error occurred while saving the table: '{e}'")
