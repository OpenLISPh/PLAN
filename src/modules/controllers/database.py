import logging

import numpy as np
import pandas as pd
from sqlalchemy import MetaData, Table, create_engine, text, update
from sqlalchemy.exc import SQLAlchemyError

from modules.settings import DATABASE_URL

logging.basicConfig(level=logging.INFO)


class PostgresCRUD:
    def __init__(self):
        database_url = DATABASE_URL
        self.engine = create_engine(database_url)
        self.metadata = MetaData()

    def create_table(self, table_name, df, additional_columns: list = None):
        logging.info(f"Creating table '{table_name}'...")
        if additional_columns:
            for column in additional_columns:
                logging.info(f"column: {column}")
                for column_name, dtype in column.items():
                    if dtype == "string":
                        df[column_name] = None
                        df[column_name] = df[column_name].astype(str)
                    elif dtype == "float":
                        df[column_name] = None
                        df[column_name] = df[column_name].astype(float)
                    # Handle other data types as needed
        try:
            df.to_sql(
                table_name, self.engine, index=True, index_label="id", if_exists="replace"
            )
            with self.engine.connect() as connection:
                # Add primary key constraint
                connection.execute(
                    text(f'ALTER TABLE "{table_name}" ADD PRIMARY KEY (id);')
                )
            logging.info(f"Table '{table_name}' created successfully.")
        except SQLAlchemyError as e:
            logging.error(f"Error creating table '{table_name}': {e}")
            raise e

    def read_table(self, table_name):
        try:
            df = pd.read_sql_table(table_name, self.engine)
            return df
        except SQLAlchemyError as e:
            logging.error(f"Error reading table '{table_name}': {e}")
            raise e

    def delete_table(self, table_name):
        logging.info(f"Deleting table '{table_name}'...")
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"DROP TABLE {table_name} CASCADE;"))
                conn.commit()
            logging.info(f"Table '{table_name}' deleted successfully.")
        except SQLAlchemyError as e:
            logging.error(f"Error deleting table '{table_name}': {e}")
            raise e

    def update_table(self, table_name, df):
        logging.info(f"Updating table '{table_name}' with {len(df)} rows...")
        try:
            with self.engine.connect() as connection:
                table = Table(table_name, self.metadata, autoload_with=self.engine)
                for _, row in df.iterrows():
                    # Convert row to a dictionary with native Python types
                    row_dict = row.to_dict()
                    row_dict = {
                        key: (
                            value.item()
                            if isinstance(value, (np.integer, np.floating))
                            else value
                        )
                        for key, value in row_dict.items()
                    }

                    stmt = (
                        update(table).where(table.c.id == row_dict["id"]).values(row_dict)
                    )
                    connection.execute(stmt)
                connection.commit()
            logging.info(f"Table '{table_name}' updated successfully.")
        except SQLAlchemyError as e:
            logging.error(f"Error updating table '{table_name}': {e}")
            raise e

    def execute_query(self, query):
        try:
            df = pd.read_sql_query(query, self.engine)
            return df
        except SQLAlchemyError as e:
            logging.error(f"Error executing query: {e}")
            return None
