import logging

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from modules.settings import DATABASE_URL

logging.basicConfig(level=logging.INFO)


class PostgresCRUD:
    def __init__(self):
        database_url = DATABASE_URL
        self.engine = create_engine(database_url)

    def create_table(self, table_name, df):
        logging.info(f"Creating table '{table_name}'...")
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
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"DROP TABLE {table_name} CASCADE;"))
                conn.commit()
            logging.info(f"Table '{table_name}' deleted successfully.")
        except SQLAlchemyError as e:
            logging.error(f"Error deleting table '{table_name}': {e}")
            raise e

    def execute_query(self, query):
        try:
            df = pd.read_sql_query(query, self.engine)
            return df
        except SQLAlchemyError as e:
            logging.error(f"Error executing query: {e}")
            return None
