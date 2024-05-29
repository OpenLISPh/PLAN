import logging

import googlemaps
import pandas as pd
from stqdm import stqdm

from modules.clients import POSTGRES_CLIENT
from modules.settings import GCP_MAPS_API_KEY

GMAPS_CLIENT = googlemaps.Client(key=GCP_MAPS_API_KEY)
stqdm.pandas()


def _fetch_google_poi_data(place_name, location_bias=None):
    response = GMAPS_CLIENT.find_place(
        place_name,
        input_type="textquery",
        fields=["place_id", "geometry", "name"],
        language="en",
        location_bias=location_bias,
    )
    if not response["candidates"]:
        logging.error(f"No candidates found for '{place_name}'. Returned none.")
        return None
    return response["candidates"][0]


def _geolocate_batch(df_slice, poi_column):
    df = df_slice.copy()

    df["geolocation"] = df[poi_column].apply(lambda x: _fetch_google_poi_data(x))
    normalized_df = pd.json_normalize(df["geolocation"])

    df = df[["id"]]

    df.reset_index(drop=True, inplace=True)
    normalized_df.reset_index(drop=True, inplace=True)

    df = pd.concat([df, normalized_df], axis=1)
    return df


def get_poi_column(table_name):
    if table_name == "barangay":
        return "Address"
    elif table_name == "library":
        return "NAME OF LIBRARY"


def batch_geolocate_df(table_name, batch_size=20, skip_existing=True):
    # Batch process the dataframe with create_geolocation_df
    # with the given batch_size, and store it in the given table_name
    poi_column = get_poi_column(table_name)
    df = POSTGRES_CLIENT.read_table(table_name)

    if skip_existing:
        geolocation_df = POSTGRES_CLIENT.read_table(f"{table_name}_geocoding")
        # Get all not na values
        geolocation_df = geolocation_df[
            (geolocation_df["place_id"].notna())
            & (geolocation_df["place_id"] != "None")
            & (geolocation_df["place_id"] != "NaN")
        ]
        ids_to_skip = geolocation_df["id"].tolist()
        logging.info(f"Skipping {len(ids_to_skip)} rows")
        df = df[~df["id"].isin(ids_to_skip)]

    stqdm_desc = (
        f"Geolocating {len(df)} entries from '{table_name}' in batches of {batch_size}\n"
    )
    for i in stqdm(range(0, 10000, batch_size), desc=stqdm_desc):  # Use for testing
        # for i in stqdm(range(0, len(df), batch_size), desc=stqdm_desc):
        batch_slice = df[i : i + batch_size]
        batch_result = _geolocate_batch(batch_slice, poi_column)
        POSTGRES_CLIENT.update_table(f"{table_name}_geocoding", batch_result)
