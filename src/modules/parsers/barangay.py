import pandas as pd


def generate_geographic_code_mappings(orig_df):
    # Create mappings for region, province, and municipality/city
    region_mapping = orig_df[orig_df["Geographic Level"] == "Reg"].copy()
    province_mapping = orig_df[orig_df["Geographic Level"] == "Prov"].copy()
    municipality_city_mapping = orig_df[
        (orig_df["Geographic Level"] == "Mun") | (orig_df["Geographic Level"] == "City")
    ].copy()

    # Extract codes and names
    region_mapping["Region Code"] = region_mapping["10-digit PSGC"]
    province_mapping["Province Code"] = province_mapping["10-digit PSGC"]
    municipality_city_mapping["Municipality / City Code"] = municipality_city_mapping[
        "10-digit PSGC"
    ]

    # Group submunicipality under their parent City/Municipality
    # e.g. Turn "Tondo" into "Tondo, City of Manila"
    submunicipality_mapping = orig_df[orig_df["Geographic Level"] == "SubMun"].copy()
    submunicipality_mapping["SubMun Code"] = submunicipality_mapping["10-digit PSGC"]
    submunicipality_mapping["Parent Code"] = (
        submunicipality_mapping["10-digit PSGC"].str[:5] + "00000"
    )
    submunicipality_mapping["Parent Name"] = submunicipality_mapping["Parent Code"].map(
        municipality_city_mapping.set_index("10-digit PSGC")["Name"]
    )
    submunicipality_mapping["Name"] = (
        submunicipality_mapping["Name"] + ", " + submunicipality_mapping["Parent Name"]
    )

    # Rename Name as Municipality / City Name
    submunicipality_mapping = (
        submunicipality_mapping[["10-digit PSGC", "SubMun Code", "Name"]]
        .drop_duplicates()
        .rename(columns={"SubMun Code": "Municipality / City Code"})
    )

    # Append submunicipality mapping to municipality_city_mapping
    # SubMun code column will be concatenated with Municipality / City Name
    municipality_city_mapping = pd.concat(
        [municipality_city_mapping, submunicipality_mapping], axis=0
    )

    # Ensure only unique mappings are present
    region_mapping = (
        region_mapping[["Region Code", "Name"]]
        .drop_duplicates()
        .rename(columns={"Name": "Region Name"})
    )
    province_mapping = (
        province_mapping[["Province Code", "Name"]]
        .drop_duplicates()
        .rename(columns={"Name": "Province Name"})
    )
    municipality_city_mapping = (
        municipality_city_mapping[["Municipality / City Code", "Name"]]
        .drop_duplicates()
        .rename(columns={"Name": "Municipality / City Name"})
    )

    return region_mapping, province_mapping, municipality_city_mapping


def transform_df(orig_df):
    orig_df["10-digit PSGC"] = orig_df["10-digit PSGC"].astype(
        str
    )  # Ensure '10-digit PSGC' is string type

    # Generate mappings
    region_mapping, province_mapping, municipality_city_mapping = (
        generate_geographic_code_mappings(orig_df)
    )

    # Filter to only include barangays
    df_bgy = orig_df[orig_df["Geographic Level"] == "Bgy"].copy()

    # Generate codes for lookup
    df_bgy["Region Code"] = df_bgy["10-digit PSGC"].str[:2] + "00000000"
    df_bgy["Province Code"] = df_bgy["10-digit PSGC"].str[:5] + "00000"
    df_bgy["Municipality / City Code"] = df_bgy["10-digit PSGC"].str[:7] + "000"

    # Merge to assign names
    df_bgy = df_bgy.merge(region_mapping, how="left", on="Region Code")
    df_bgy = df_bgy.merge(province_mapping, how="left", on="Province Code")
    df_bgy = df_bgy.merge(
        municipality_city_mapping, how="left", on="Municipality / City Code"
    )

    # Rename columns
    df_bgy.rename(
        columns={
            "Region Name": "Region",
            "Province Name": "Province",
            "Municipality / City Name": "Municipality / City",
        },
        inplace=True,
    )

    # Drop extra columns
    df_bgy.drop(
        ["Region Code", "Province Code", "Municipality / City Code"], axis=1, inplace=True
    )

    # Drop columns where column names start with 'Unnamed'
    df_bgy = df_bgy.loc[:, ~df_bgy.columns.str.contains("^Unnamed")]

    # Create address column
    df_bgy["Address"] = df_bgy.apply(
        lambda row: ", ".join(
            filter(
                None,
                [
                    (
                        str(row["Name"]) + " Barangay Hall"
                        if pd.notnull(row["Name"])
                        else ""
                    ),
                    (
                        str(row["Municipality / City"])
                        if pd.notnull(row["Municipality / City"])
                        else ""
                    ),
                    str(row["Province"]) if pd.notnull(row["Province"]) else "",
                    str(row["Region"]) if pd.notnull(row["Region"]) else "",
                ],
            )
        ),
        axis=1,
    )

    return df_bgy


def convert_xlsx_to_df(xlsx_file):
    psgc_df = pd.read_excel(xlsx_file, sheet_name="PSGC", dtype=str)
    return psgc_df
