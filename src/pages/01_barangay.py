# pages\01_barangay.py
import streamlit as st
from streamlit_extras.row import row

from modules.clients import POSTGRES_CLIENT
from modules.parsers.barangay import read_psgc_excel_data, transform_df
from modules.streamlit_elements.table_actions import (
    create_table_modal,
    delete_table_modal,
    geocode_table_modal,
    update_table_modal,
)

POSTGRES_CLIENT = POSTGRES_CLIENT


# Streamlit page setup
st.title("Barangay Data")

with st.expander("Help"):
    st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")


try:
    # Read barangay table from database
    barangay_df = POSTGRES_CLIENT.read_table("barangay")

    # Display editable dataframe
    edited_barangay_df = st.data_editor(
        barangay_df, key="barangay_data_editor", hide_index=True
    )

    unsaved_changes = st.session_state.barangay_data_editor["edited_rows"]
    if len(unsaved_changes) > 0:
        st.info(f"You have {len(unsaved_changes)} unsaved changes.")

    table_buttons_row = row(3, vertical_align="center")
    if table_buttons_row.button(
        ":heavy_plus_sign: Upload Table",
        use_container_width=True,
        disabled=not (edited_barangay_df.empty),
    ):
        create_table_modal("barangay", edited_barangay_df)
    if table_buttons_row.button(
        ":wastebasket: Delete Table",
        use_container_width=True,
    ):
        delete_table_modal("barangay")
    if table_buttons_row.button(
        ":floppy_disk: Save Changes",
        use_container_width=True,
    ):
        update_table_modal("barangay", edited_barangay_df, unsaved_changes)
    if table_buttons_row.button(
        ":earth_asia: Geocode Table",
        use_container_width=True,
    ):
        geocode_table_modal("barangay")
    # delete converted_barangay_df if exists in session state
    if "converted_barangay_df" in st.session_state:
        del st.session_state["converted_barangay_df"]

except ValueError as e:
    st.error(f"An error occurred while reading the table: '{e}'.")
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
        create_table_modal("barangay", st.session_state.processed_barangay_df)
