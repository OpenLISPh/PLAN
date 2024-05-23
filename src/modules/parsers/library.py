import pandas as pd
import tabula


def _identify_header(df):
    """Identifies header in df"""
    # Define expected header columns
    expected_columns = ["REGION", "LOCATION", "NAME OF LIBRARY"]

    # Iterate through DataFrame rows to find a match
    for index, row in df.iterrows():
        # Check if the current row contains all expected header columns
        if all(col in row.values for col in expected_columns):
            return index
    return None  # Return None if no header row is found


def read_nlp_pdf_to_df(library_directory_path):
    """Reads NLP library directory pdf to return a pandas dataframe"""
    # Read all pages into a list of pandas dataframes
    df_list = tabula.read_pdf(library_directory_path, pages="all", multiple_tables=True)

    # Identify which row contains the header
    header_index = _identify_header(df_list[0])

    # Drop row 0 until header in the first page
    df_list[0].drop(df_list[0].index[:header_index], inplace=True)
    df_list[0].reset_index(drop=True, inplace=True)

    # Concatenate all dataframes
    combined_df = pd.concat(df_list, ignore_index=True)

    # Set column names using the first row
    combined_df.columns = combined_df.iloc[0]
    combined_df.drop(index=0, inplace=True)

    # Drop the first column if it's "NO."
    if combined_df.columns[0] == "NO.":
        combined_df.drop(columns=combined_df.columns[0], inplace=True)
        combined_df.reset_index(drop=True, inplace=True)

    # Cast Region column as string
    combined_df["REGION"] = combined_df["REGION"].astype(str)

    # Replace newlines with spaces, cleanup addresses
    combined_df.replace({r"\r\n|\r|\n": " "}, regex=True, inplace=True)

    # Reset index
    result_df = combined_df.reset_index(drop=True)

    return result_df
