import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class SQLiteDatabase:
    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize SQLite database connection.

        Args:
            db_path: Path to the SQLite database file. If None, uses configured path.
        """
        from database.sqlite_path import get_db_path

        if db_path is None:
            configured_path = get_db_path()
            if configured_path is None:
                raise ValueError("Database path not configured")
            self.db_path = configured_path
        else:
            self.db_path = Path(db_path)

        self.conn: Optional[sqlite3.Connection] = None
        self._logger = None
        self._init_connection()

    @property
    def lazy_sk_log(self):
        """Lazy load the logger to avoid circular imports."""
        if self._logger is None:
            try:
                from utils.sk_logger import sk_log

                self._logger = sk_log
            except ImportError:
                import logging

                fallback_logger = logging.getLogger("sqlite_fallback")
                if not fallback_logger.handlers:
                    handler = logging.StreamHandler()
                    handler.setFormatter(
                        logging.Formatter("%(levelname)s: %(message)s")
                    )
                    fallback_logger.addHandler(handler)
                    fallback_logger.setLevel(logging.INFO)
                self._logger = fallback_logger
        return self._logger

    def _init_connection(self) -> None:
        """Initialize database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.lazy_sk_log.debug(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            self.lazy_sk_log.error(f"Failed to connect to database: {e}")
            raise

    def _check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        try:
            table_exists = self.execute_query(
                "SELECT name from sqlite_master where type='table' and "
                f"name='{table_name}'"
            )
            if table_exists:
                return True
            else:
                return False
        except sqlite3.Error:
            self.lazy_sk_log.debug(f"Table {table_name} does not exist.")
            return False

    def _check_table_has_records(self, table_name: str) -> bool:
        """Check if a table exists."""
        try:
            has_records = self.execute_query(
                f"SELECT COUNT(*) FROM {table_name}"
            )
            if has_records[0][0] == 0:
                return False
            else:
                return True
        except sqlite3.Error:
            self.lazy_sk_log.debug(f"Table {table_name} does not exist.")
            return False

    def execute_query(self, query: str, params: tuple = ()) -> List[Tuple]:
        """Execute a SELECT query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of query results
        """
        try:
            if not self.conn:
                self._init_connection()
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.lazy_sk_log.error(f"Query execution failed: {e}")
            self.lazy_sk_log.error(f"Query: {query}")
            raise

    def execute_write(self, query: str, params: tuple = ()) -> None:
        """Execute a write query (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query string
            params: Query parameters
        """
        try:
            if not self.conn:
                self._init_connection()
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            self.lazy_sk_log.error(f"Write operation failed: {e}")
            self.lazy_sk_log.error(f"Query: {query}")
            raise

    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute multiple write operations.

        Args:
            query: SQL query string
            params_list: List of parameter tuples
        """
        try:
            if not self.conn:
                self._init_connection()
            cursor = self.conn.cursor()
            cursor.executemany(query, params_list)
            self.conn.commit()
        except sqlite3.Error as e:
            self.lazy_sk_log.error(f"Batch operation failed: {e}")
            self.lazy_sk_log.error(f"Query: {query}")
            raise

    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """Create a new table.

        Args:
            table_name: Name of the table
            columns: Dictionary of column names and their SQL types
        """
        columns_def = ", ".join(f"{k} {v}" for k, v in columns.items())
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        try:
            self.execute_write(query)
            self.lazy_sk_log.debug(f"Table created: {table_name}")
        except sqlite3.Error as e:
            self.lazy_sk_log.error(f"Failed to create table {table_name}: {e}")
            raise

    def insert(self, table: str, data: Dict[str, Any]) -> None:
        """Insert a single row into a table.

        Args:
            table: Table name
            data: Dictionary of column names and values
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        try:
            self.execute_write(query, tuple(data.values()))
        except sqlite3.Error as e:
            self.lazy_sk_log.error(f"Insert operation failed: {e}")
            raise

    def get_row_count(self, table: str) -> int:
        """Get the number of rows in a table.

        Args:
            table: Table name

        Returns:
            Number of rows in the table
        """
        try:
            result = self.execute_query(f"SELECT COUNT(*) FROM {table}")
            return result[0][0]
        except sqlite3.Error as e:
            self.lazy_sk_log.error(f"Failed to get row count for {table}: {e}")
            raise

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.lazy_sk_log.debug("Database connection closed")

    def commit(self) -> None:
        """Commit pending database transactions."""
        try:
            if not self.conn:
                self._init_connection()
            self.conn.commit()
        except sqlite3.Error as e:
            self.lazy_sk_log.error(f"Commit failed: {e}")
            raise

    def __enter__(self) -> "SQLiteDatabase":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
