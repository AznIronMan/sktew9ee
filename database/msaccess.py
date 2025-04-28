import os
import pyodbc

from settings.settings_file import SettingsManager
from utils.entree import Entree
from utils.sk_logger import sk_log


class MSAccessDB:
    def __init__(self):
        self.meal_time = Entree()
        settings = SettingsManager()
        self.tew9_core_path = settings.get_value("tew9_core_path")
        self.tew9_game_database_name = settings.get_value(
            "tew9_game_database_name"
        )
        self.tew9_full_db_path_override = settings.get_value(
            "tew9_full_db_path_override"
        )
        if (
            self.tew9_full_db_path_override
            and self.tew9_full_db_path_override.strip()
        ):
            self.db_path = self.tew9_full_db_path_override
        else:
            self.db_path = os.path.normpath(
                os.path.join(
                    self.tew9_core_path,
                    "Databases",
                    self.tew9_game_database_name,
                    "TEW9.mdb",
                )
            )

        self.dinner_time = self.meal_time.whats_for_dinner()
        self.connection = None

    def connect(self):
        try:
            sk_log.debug(f"Database path constructed as: {self.db_path}")
            sk_log.debug(f"Connecting to MS Access database: {self.db_path}")
            if self.dinner_time:
                conn_str = (
                    f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
                    f"DBQ={self.db_path};"
                    f"PWD={self.dinner_time};"
                )
            else:
                conn_str = (
                    f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
                    f"DBQ={self.db_path};"
                )

            self.connection = pyodbc.connect(conn_str)
            sk_log.debug("Connected to the MS Access database successfully.")
        except pyodbc.Error as e:
            sk_log.error(f"Error connecting to MS Access database: {e}")
            raise

    def create(self, query, params=None):
        sk_log.debug(f"Creating table with query: {query}")
        self._execute_non_select_query(query, params)

    def insert(self, query, params=None):
        sk_log.debug(f"Inserting data with query: {query}")
        self._execute_non_select_query(query, params)

    def update(self, query, params=None):
        sk_log.debug(f"Updating data with query: {query}")
        self._execute_non_select_query(query, params)

    def delete(self, query, params=None):
        sk_log.debug(f"Deleting data with query: {query}")
        self._execute_non_select_query(query, params)

    def select(self, query, params=None):
        sk_log.debug(f"Selecting data with query: {query}")
        return self._execute_select_query(query, params)

    def custom_query(self, query, params=None):
        sk_log.debug(f"Executing custom query: {query}")
        if query.strip().upper().startswith("SELECT"):
            return self._execute_select_query(query, params)
        else:
            self._execute_non_select_query(query, params)

    def _execute_select_query(self, query, params=None):
        """Executes a SELECT query and returns the results."""
        sk_log.debug(f"MS Access executing SELECT query: {query}")
        if not self.connection:
            raise ConnectionError(
                "MS Access database connection is not established. "
                "Call connect() first."
            )

        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            result = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            sk_log.debug(f"MS Access SELECT query result: {result}")
            return [dict(zip(columns, row)) for row in result]
        except pyodbc.Error as e:
            sk_log.error(f"Error executing MS Access SELECT query: {e}")
            raise
        finally:
            cursor.close()
            sk_log.debug("MS Access connection closed.")

    def _execute_non_select_query(self, query, params=None):
        """Executes a non-SELECT query (e.g., CREATE, INSERT, UPDATE, DELETE)."""
        if not self.connection:
            raise ConnectionError(
                "MS Access database connection is not established. "
                "Call connect() first."
            )

        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            self.connection.commit()
            sk_log.debug("MS Access query executed successfully.")
        except pyodbc.Error as e:
            sk_log.error(f"Error executing MS Access non-SELECT query: {e}")
            raise
        finally:
            cursor.close()
            sk_log.debug("MS Access connection closed.")

    def close(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            sk_log.debug("MS Access connection closed.")
