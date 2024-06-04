import logging

import numpy as np
import pandas as pd
from geopy.distance import geodesic, great_circle


def get_service_to_population_ratio(population, collection_size):
    if population == 0:
        return 0
    return collection_size / population


def calculate_library_catchment_areas(
    libraries_df,
    barangays_df,
    catchment_radius_km,
    brgy_population_col="2020 Population",
    libraries_name_col="NAME OF LIBRARY",
    brgy_name_col="Name",
    decay_parameter=1000,
    cut_off=2000,
):
    # Initialize a list to hold the catchment area data
    catchment_areas = []
    # Iterate over each library to calculate its catchment area
    for _, lib in libraries_df.iterrows():
        logging.info(f"Calculating catchment for {lib[libraries_name_col]}")
        logging.info(f"Collection Size: {lib['collection_size']}")
        lib_coord = (lib["latitude"], lib["longitude"])
        raw_catchment_population = 0
        weighted_catchment_population = 0
        catchment_barangays = []
        # Check each barangay for inclusion in the catchment area
        for _, brgy in barangays_df.iterrows():
            brgy_coord = (brgy["latitude"], brgy["longitude"])
            if great_circle(lib_coord, brgy_coord).kilometers <= catchment_radius_km:
                distance = calculate_distance(brgy_coord, lib_coord)
                weight = gaussian_weight(distance, decay_parameter, cut_off)
                raw_catchment_population += int(brgy[brgy_population_col])
                weighted_catchment_population += int(brgy[brgy_population_col]) * weight
                catchment_barangays.append(
                    (brgy[brgy_name_col], brgy[brgy_population_col])
                )
        # Append the calculated data to the list
        catchment_areas.append(
            {
                "id": lib["id"],
                f"{libraries_name_col}": lib[libraries_name_col],
                "collection_size": lib["collection_size"],
                "Raw Catchment Population": raw_catchment_population,
                # "Service to Population Ratio": get_service_to_population_ratio(
                #     raw_catchment_population, lib["collection_size"]
                # ),
                "Weighted Catchment Population": weighted_catchment_population,
                "Service to Population Ratio": get_service_to_population_ratio(
                    weighted_catchment_population, lib["collection_size"]
                ),
                "Catchment Barangays": catchment_barangays,
            }
        )

    # Convert the list of dictionaries to a DataFrame for easier analysis
    return pd.DataFrame(catchment_areas)


def calculate_distance(location1, location2):
    return geodesic(location1, location2).meters


def calculate_distance_matrix(libraries_df, barangays_df):
    distance_matrix = pd.DataFrame(index=barangays_df.index, columns=libraries_df.index)
    for brgy_index, brgy in barangays_df.iterrows():
        for lib_index, lib in libraries_df.iterrows():
            distance_matrix.at[brgy_index, lib_index] = calculate_distance(
                (brgy["latitude"], brgy["longitude"]),
                (lib["latitude"], lib["longitude"]),
            )
    distance_matrix.insert(0, "Barangay", barangays_df["Name"])
    distance_matrix.index = barangays_df["id"]
    distance_matrix.columns = ["Barangay"] + list(libraries_df["NAME OF LIBRARY"])
    return distance_matrix


def convert_to_str(item):
    if isinstance(item, (tuple, list)):
        return str(tuple(round(x, 4) if isinstance(x, np.float64) else x for x in item))
    return item


def calculate_brgy_catchment_areas(
    libraries_df,
    libraries_fca_df,
    barangays_df,
    catchment_radius_km,
    brgy_population_col="2020 Population",
    libraries_name_col="NAME OF LIBRARY",
    brgy_name_col="Name",
    decay_parameter=1000,
    cut_off=2000,
):
    # Initialize a list to hold the catchment area data
    catchment_areas = []
    # Iterate over each library to calculate its catchment area
    for _, brgy in barangays_df.iterrows():
        logging.info(f"Calculating catchment for {brgy[brgy_name_col]}")
        brgy_coord = (brgy["latitude"], brgy["longitude"])
        catchment_total_weighted_ratio = 0
        catchment_libraries = []
        # Check each library for inclusion in the catchment area
        for _, lib in libraries_df.iterrows():
            lib_coord = (lib["latitude"], lib["longitude"])
            if great_circle(brgy_coord, lib_coord).kilometers <= catchment_radius_km:
                distance = calculate_distance(brgy_coord, lib_coord)
                weight = gaussian_weight(distance, decay_parameter, cut_off)
                service_to_population_ratio = libraries_fca_df.loc[
                    libraries_fca_df["id"] == lib["id"], "Service to Population Ratio"
                ].values[0]
                weighted_ratio = service_to_population_ratio * weight
                catchment_total_weighted_ratio += weighted_ratio
                catchment_libraries.append((lib[libraries_name_col], weighted_ratio))
        # Resolves the issue where weighted_ratio is a tuple containing a np.float64
        catchment_libraries = [convert_to_str(lib) for lib in catchment_libraries]
        # Append the calculated data to the list
        catchment_areas.append(
            {
                "id": brgy["id"],
                f"{brgy_name_col}": brgy[brgy_name_col],
                f"{brgy_population_col}": brgy[brgy_population_col],
                "Catchment Library Accessibility Weighted Ratio": catchment_total_weighted_ratio,
                "Catchment Libraries": catchment_libraries,
            }
        )

    # Convert the list of dictionaries to a DataFrame for easier analysis
    return pd.DataFrame(catchment_areas)


def gaussian_weight(distance, decay_parameter=1000, cut_off=2000):
    if distance > cut_off:
        return 0
    return np.exp(-((distance / decay_parameter) ** 2))


def calculate_gaussian_weight_df(distance_matrix, decay_parameter=1000, cut_off=2000):
    # Apply the Gaussian weight function only to numerical columns
    weighted_distances = distance_matrix.drop(columns=["Barangay"]).applymap(
        lambda x: gaussian_weight(x, decay_parameter, cut_off)
    )

    # Reinsert the 'Name' column back into the weighted distances DataFrame
    weighted_distance_matrix = distance_matrix[["Barangay"]].join(weighted_distances)

    return weighted_distance_matrix
