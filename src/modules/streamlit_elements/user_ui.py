import streamlit as st

from modules.clients import POSTGRES_CLIENT


# def get_list
def sidebar():
    # Sidebar
    st.sidebar.markdown("# Libraries")
    # Read library table from database
    library_df = POSTGRES_CLIENT.read_table("library")
    # Select Location multiselect
    st.sidebar.multiselect(
        "Select Location", library_df["LOCATION"].unique(), key="location_multiselect"
    )
    library_filter = list(
        library_df[
            library_df["LOCATION"].isin(list(st.session_state["location_multiselect"]))
        ]["id"].unique()
    )
    # Row id and library name
    library_selection = [
        (row.id, row._6)
        for row in library_df[library_df["id"].isin(library_filter)].itertuples()
    ]
    st.session_state["library_df"] = library_df
    library_multiselect_container = st.sidebar.container()
    library_select_all = st.sidebar.checkbox("Select All", key="library_select_all")
    if library_select_all:
        library_multiselect_container.multiselect(
            "Select Libraries",
            library_selection,
            key="library_multiselect",
            default=library_selection,
        )
    else:
        library_multiselect_container.multiselect(
            "Select Libraries", library_selection, key="library_multiselect"
        )

    # Sidebar
    st.sidebar.markdown("# Barangays")
    # Read barangay table from database
    barangay_df = POSTGRES_CLIENT.read_table("barangay")
    # For rows whose "Province" column is empty, fill it with their "Region"
    barangay_df["Province"] = barangay_df["Province"].fillna(barangay_df["Region"])
    # For rows whose "Municipality / City" column is empty, fill it with their "Province"
    barangay_df["Municipality / City"] = barangay_df["Municipality / City"].fillna(
        barangay_df["Province"]
    )
    # Get unique values of column "Region"
    region_selection = list(barangay_df["Region"].unique())
    st.sidebar.multiselect("Select Region", region_selection, key="region_multiselect")
    # Get unique values of column "Province" based on selected region on region_selection
    province_selection = list(
        barangay_df[
            barangay_df["Region"].isin(list(st.session_state["region_multiselect"]))
        ]["Province"].unique()
    )
    st.sidebar.multiselect(
        "Select Province", province_selection, key="province_multiselect", disabled=False
    )
    # Get unique values of column "Municipality / City" based on selected province on province_selection
    municipality_selection = list(
        barangay_df[
            (barangay_df["Region"].isin(list(st.session_state["region_multiselect"])))
            & (
                barangay_df["Province"].isin(
                    list(st.session_state["province_multiselect"])
                )
            )
        ]["Municipality / City"].unique()
    )
    st.sidebar.multiselect(
        "Select Municipality / City",
        municipality_selection,
        key="municipality_multiselect",
        disabled=False,
    )
    st.session_state["barangay_df"] = barangay_df
    barangay_filter = list(
        barangay_df[
            (barangay_df["Region"].isin(list(st.session_state["region_multiselect"])))
            & (
                barangay_df["Province"].isin(
                    list(st.session_state["province_multiselect"])
                )
            )
            & (
                barangay_df["Municipality / City"].isin(
                    list(st.session_state["municipality_multiselect"])
                )
            )
        ]["id"].unique()
    )
    barangay_selection = [
        (row.id, row.Name)
        for row in barangay_df[barangay_df["id"].isin(barangay_filter)].itertuples()
    ]
    barangay_selection = sorted(barangay_selection, key=lambda x: x[0])
    barangay_multiselect_container = st.sidebar.container()
    brgy_select_all = st.sidebar.checkbox("Select All", key="brgy_select_all")
    if brgy_select_all:
        barangay_multiselect_container.multiselect(
            "Select Barangays",
            barangay_selection,
            key="barangay_multiselect",
            default=barangay_selection,
        )
    else:
        barangay_multiselect_container.multiselect(
            "Select Barangays", barangay_selection, key="barangay_multiselect"
        )
