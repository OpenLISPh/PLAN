import streamlit as st

from modules.clients import POSTGRES_CLIENT


# def get_list
def sidebar():
    # Sidebar
    st.sidebar.markdown("# Libraries")
    # Read library table from database
    library_df = POSTGRES_CLIENT.read_table("library")
    # Row id and library name
    library_selection = [(row.id, row._6) for row in library_df.itertuples()]
    st.session_state["library_df"] = library_df
    st.sidebar.multiselect(
        "Select Libraries", library_selection, key="library_multiselect"
    )

    # Sidebar
    st.sidebar.markdown("# Barangays")
    # Read barangay table from database
    barangay_df = POSTGRES_CLIENT.read_table("barangay")
    # Add to session_state
    st.session_state["barangay_df"] = barangay_df
    # Row id and barangay name
    barangay_selection = [(row.id, row.Name) for row in barangay_df.itertuples()]
    st.sidebar.multiselect(
        "Select Barangays", barangay_selection, key="barangay_multiselect"
    )
