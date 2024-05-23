# pages\02_library.py
import streamlit as st

from modules.clients import POSTGRES_CLIENT
from modules.parsers.library import read_nlp_pdf_to_df
from modules.streamlit_elements.buttons import (
    create_table,
    delete_table_modal,
    update_table_modal,
)

POSTGRES_CLIENT = POSTGRES_CLIENT


# Streamlit page setup
st.title("Library Data")

with st.expander("Help"):
    st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")

try:
    # Read library table from database
    library_df = POSTGRES_CLIENT.read_table("library")

    # Display editable dataframe
    edited_library_df = st.data_editor(library_df, key="library_data_editor")

    unsaved_changes = st.session_state.library_data_editor["edited_rows"]
    if unsaved_changes:
        st.info(f"You have {len(unsaved_changes)} unsaved changes.")

    # button to update table
    if st.button("Update Table"):
        update_table_modal("library", edited_library_df, unsaved_changes)

    # button to delete table
    if st.button("Delete Table"):
        delete_table_modal("library")

    # delete something in session state?
    if "processed_library_df" in st.session_state:
        del st.session_state["processed_library_df"]
except ValueError as e:
    st.error(f"An error occurred while reading the table: '{e}'")
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload NLP Directory PDF", type="pdf", key="file_uploader"
    )

    # Check if a new file is uploaded
    if uploaded_file is not None and (
        "uploaded_file" not in st.session_state
        or st.session_state.uploaded_file != uploaded_file
    ):
        st.session_state.uploaded_file = uploaded_file
        st.session_state.processed_library_df = read_nlp_pdf_to_df(uploaded_file)

# Display DataFrame if available
if "processed_library_df" in st.session_state:
    st.dataframe(st.session_state.processed_library_df)

    if st.button("Save to Database"):
        create_table("library", st.session_state.processed_library_df)
