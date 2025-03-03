from typing import Dict, List, Optional, Union

from database.msaccess import MSAccessDB
from database.skydbapi import SkyDBAPI
from settings.settings_file import SettingsManager
from utils.sk_logger import sk_log


class TEWDB:
    def __init__(self) -> None:
        self.settings = SettingsManager()
        self.db_mode = self.settings.get_value("database_mode")
        self.db_instance: Union[MSAccessDB, SkyDBAPI, None] = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize the appropriate database instance based on settings."""
        if self.db_mode == "msaccess":
            self.db_instance = MSAccessDB()
            self.db_instance.connect()
        elif self.db_mode == "skydbapi":
            self.db_instance = SkyDBAPI()
        else:
            sk_log.error(
                f"TEWDB initialization failed: Unsupported database mode"
                f": {self.db_mode}"
            )
            raise ValueError(f"Unsupported database mode: {self.db_mode}")

        sk_log.debug(f"Initialized TEWDB with mode: {self.db_mode}")

    def create(self, query: str, params: Optional[List] = None) -> None:
        """Execute a CREATE query."""
        sk_log.debug(f"TEWDB executing CREATE query via {self.db_mode}")
        self.db_instance.create(query, params)

    def insert(self, query: str, params: Optional[List] = None) -> None:
        """Execute an INSERT query."""
        sk_log.debug(f"TEWDB executing INSERT query via {self.db_mode}")
        self.db_instance.insert(query, params)

    def update(self, query: str, params: Optional[List] = None) -> None:
        """Execute an UPDATE query."""
        sk_log.debug(f"TEWDB executing UPDATE query via {self.db_mode}")
        self.db_instance.update(query, params)

    def delete(self, query: str, params: Optional[List] = None) -> None:
        """Execute a DELETE query."""
        sk_log.debug(f"TEWDB executing DELETE query via {self.db_mode}")
        self.db_instance.delete(query, params)

    def select(self, query: str, params: Optional[List] = None) -> List[Dict]:
        """Execute a SELECT query and return results."""
        sk_log.debug(f"TEWDB executing SELECT query via {self.db_mode}")
        return self.db_instance.select(query, params)

    def custom_query(
        self, query: str, params: Optional[List] = None
    ) -> Optional[List[Dict]]:
        """Execute a custom query and return results if it's a SELECT query."""
        sk_log.debug(f"TEWDB executing custom query via {self.db_mode}")
        return self.db_instance.custom_query(query, params)

    def close(self) -> None:
        """Close the database connection if applicable."""
        if self.db_instance and hasattr(self.db_instance, "close"):
            self.db_instance.close()
            sk_log.debug(f"Closed TEWDB connection for {self.db_mode}")

    def __enter__(self) -> "TEWDB":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
