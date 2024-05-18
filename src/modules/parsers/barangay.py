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
