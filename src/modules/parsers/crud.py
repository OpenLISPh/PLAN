import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()


class PostgresCRUD:
    def __init__(self):
        database_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(database_url)

    def create_table(self, table_name, df):
        try:
            df.to_sql(table_name, self.engine, index=False, if_exists="replace")
            print(f"Table '{table_name}' created successfully.")
        except SQLAlchemyError as e:
            print(f"Error creating table '{table_name}': {e}")

    def read_table(self, table_name):
        try:
            df = pd.read_sql_table(table_name, self.engine)
            return df
        except SQLAlchemyError as e:
            print(f"Error reading table '{table_name}': {e}")
            return None

    def update_table(self, table_name, df):
        try:
            df.to_sql(table_name, self.engine, index=False, if_exists="replace")
            print(f"Table '{table_name}' updated successfully.")
        except SQLAlchemyError as e:
            print(f"Error updating table '{table_name}': {e}")

    def delete_table(self, table_name):
        try:
            with self.engine.connect() as conn:
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            print(f"Table '{table_name}' deleted successfully.")
        except SQLAlchemyError as e:
            print(f"Error deleting table '{table_name}': {e}")

    def execute_query(self, query):
        try:
            df = pd.read_sql_query(query, self.engine)
            return df
        except SQLAlchemyError as e:
            print(f"Error executing query: {e}")
            return None
