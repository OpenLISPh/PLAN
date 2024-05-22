# pages\01_barangay.py
import streamlit as st

from modules.clients import POSTGRES_CLIENT
from modules.parsers.barangay import read_psgc_excel_data, transform_df
from modules.streamlit_elements.buttons import create_table, delete_table, update_table

POSTGRES_CLIENT = POSTGRES_CLIENT


# Streamlit page setup
st.title("Barangay Data")

with st.expander("Help"):
    st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")


try:
    # Read barangay table from database
    barangay_df = POSTGRES_CLIENT.read_table("barangay")

    # Display editable dataframe
    edited_barangay_df = st.data_editor(barangay_df, key="barangay_data_editor")

    unsaved_changes = len(st.session_state.barangay_data_editor["edited_rows"])
    if unsaved_changes > 0:
        st.info(f"You have {unsaved_changes} unsaved changes.")

    # button to update table
    if st.button("Update Table"):
        update_table(edited_barangay_df)

    # button to delete table
    if st.button("Delete Table"):
        delete_table("barangay")

    # delete converted_barangay_df if exists in session state
    if "converted_barangay_df" in st.session_state:
        del st.session_state["converted_barangay_df"]

except ValueError as e:
    st.error(f"An error occurred while reading the table: '{e}'. Check Help?")
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload PSGC Barangay Publication XLSX", type="xlsx", key="file_uploader"
    )

    # Check if a new file is uploaded
    if uploaded_file is not None and (
        "uploaded_file" not in st.session_state
        or st.session_state.uploaded_file != uploaded_file
    ):
        st.session_state.uploaded_file = uploaded_file
        st.session_state.converted_barangay_df = read_psgc_excel_data(uploaded_file)

# Display DataFrame if available
if "converted_barangay_df" in st.session_state:
    st.session_state.processed_barangay_df = transform_df(
        st.session_state.converted_barangay_df
    )
    st.dataframe(st.session_state.processed_barangay_df)

    if st.button("Save to Database"):
        create_table("barangay", st.session_state.processed_barangay_df)
