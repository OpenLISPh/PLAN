# pages\02_library.py
import streamlit as st
from streamlit_extras.row import row

from modules.clients import POSTGRES_CLIENT
from modules.parsers.library import read_nlp_pdf_to_df
from modules.streamlit_elements.buttons import (
    create_table_modal,
    delete_table_modal,
    geocode_table_modal,
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
    edited_library_df = st.data_editor(
        library_df, key="library_data_editor", hide_index=True
    )

    unsaved_changes = st.session_state.library_data_editor["edited_rows"]
    if unsaved_changes:
        st.info(f"You have {len(unsaved_changes)} unsaved changes.")

    table_buttons_row = row(3, vertical_align="center")
    if table_buttons_row.button(
        ":heavy_plus_sign: Upload Table",
        use_container_width=True,
        disabled=not (library_df.empty),
    ):
        create_table_modal("library", edited_library_df)
    if table_buttons_row.button(
        ":floppy_disk: Save Changes",
        use_container_width=True,
    ):
        update_table_modal("library", edited_library_df, unsaved_changes)
    if table_buttons_row.button(
        ":wastebasket: Delete Table",
        use_container_width=True,
    ):
        delete_table_modal("library")
    if table_buttons_row.button(
        ":earth_asia: Geocode Table",
        use_container_width=True,
    ):
        geocode_table_modal("barangay")
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
        create_table_modal("library", st.session_state.processed_library_df)
