import datetime
import socket
from pathlib import Path
from typing import Optional

from database.sqlite_path import set_db_path
from database.sqlite import SQLiteDatabase


class SettingsManager:
    def __init__(self) -> None:
        self.hostname = socket.gethostname().split(".")[0].lower()
        self.settings_path = Path(
            f"{self.hostname}.{fetch_settings_file_ext()}"
        )
        set_db_path(self.settings_path)
        self.db = None
        self._logger = None
        self._initialized = False
        self._ensure_initialized()

    @property
    def lazy_sk_log(self):
        """Lazy load the logger to avoid circular imports."""
        if self._logger is None:
            try:
                from utils.sk_logger import sk_log

                self._logger = sk_log
            except ImportError:
                import logging
                import os

                fallback_logger = logging.getLogger("sqlite_fallback")
                if not fallback_logger.handlers:
                    handler = logging.StreamHandler()
                    handler.setFormatter(
                        logging.Formatter("%(levelname)s: %(message)s")
                    )
                    fallback_logger.addHandler(handler)
                    debug_enabled = (
                        os.getenv("DEBUG", "false").lower() == "true"
                    )
                    fallback_logger.setLevel(
                        logging.DEBUG if debug_enabled else logging.INFO
                    )
                    log_dir = "./.logs/"
                    Path(log_dir).mkdir(parents=True, exist_ok=True)
                    log_file_name = (
                        f"{self.hostname}-"
                        f"{datetime.datetime.now().strftime('%Y%m%d')}.log"
                    )
                    file_handler = logging.FileHandler(
                        os.path.join(log_dir, log_file_name), mode="a"
                    )
                    file_handler.setFormatter(
                        logging.Formatter("%(levelname)s: %(message)s")
                    )
                    fallback_logger.addHandler(file_handler)
                    self._logger = fallback_logger
        return self._logger

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            self.initialize_settings()
            self._initialized = True

    def get_value(self, key: str) -> str:
        self._ensure_initialized()
        """Get a value from the settings database."""
        self.lazy_sk_log.debug(f"Getting value for key: {key}")
        return (
            self.db.execute_query(
                "SELECT value FROM settings WHERE key = ?", (key,)
            )[0][0]
            if self.db.execute_query(
                "SELECT value FROM settings WHERE key = ?", (key,)
            )
            else None
        )

    def set_value(self, key: str, value: str) -> None:
        self._ensure_initialized()
        """Set a value in the settings database."""
        self.lazy_sk_log.debug(f"Setting value for key: {key}")
        self.db.execute_write(
            (
                "INSERT INTO settings (key, value) VALUES (?, ?) ON "
                "CONFLICT(key) DO UPDATE SET value = ?"
            ),
            (key, value, value),
        )

    def _update_table_schema(self) -> None:
        """Update existing tables with new columns if they're missing."""
        self.lazy_sk_log.debug("Checking for schema updates")
        settings_cols = {
            col[1]
            for col in self.db.execute_query("PRAGMA table_info(settings)")
        }
        init_cols = {
            col[1]
            for col in self.db.execute_query(
                "PRAGMA table_info(settings_initialization)"
            )
        }
        if "last_modified" not in settings_cols:
            self.lazy_sk_log.debug(
                "Adding last_modified column to settings table"
            )
            self.db.execute_write(
                "ALTER TABLE settings ADD COLUMN last_modified "
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            )
        if "version" not in init_cols:
            self.lazy_sk_log.debug(
                "Adding version column to settings_initialization table"
            )
            self.db.execute_write(
                "ALTER TABLE settings_initialization ADD COLUMN version "
                "TEXT DEFAULT '1.0'"
            )
        if "initialized_by" not in init_cols:
            self.lazy_sk_log.debug(
                "Adding initialized_by column to settings_initialization table"
            )
            self.db.execute_write(
                "ALTER TABLE settings_initialization ADD COLUMN "
                "initialized_by TEXT"
            )

    def initialize_settings(self) -> None:
        """Create and initialize settings database if it doesn't exist."""
        self.lazy_sk_log.debug(f"Initializing settings at {self.settings_path}")
        self.db = SQLiteDatabase(str(self.settings_path))
        existing_tables = {
            row[0]
            for row in self.db.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "settings" not in existing_tables:
            self.lazy_sk_log.debug("Creating settings table")
            self.db.create_table(
                "settings",
                {
                    "key": "TEXT PRIMARY KEY",
                    "value": "TEXT",
                    "last_modified": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                },
            )
        current_settings = {
            row[0]: row[1]
            for row in self.db.execute_query("SELECT key, value FROM settings")
        }
        from settings.settings_list import DefaultSettings

        defaults = DefaultSettings(self.hostname)
        default_settings = defaults.get_defaults_list()
        missing_settings = [
            (key, value)
            for key, value in default_settings
            if key not in current_settings
        ]
        if missing_settings:
            self.lazy_sk_log.debug(
                f"Adding {len(missing_settings)} missing settings"
            )
            self.db.execute_many(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                missing_settings,
            )
        if "settings_initialization" not in existing_tables:
            self.lazy_sk_log.debug("Creating settings_initialization table")
            self.db.create_table(
                "settings_initialization",
                {
                    "id": "INTEGER PRIMARY KEY",
                    "initialization_date": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                    "version": "TEXT DEFAULT '1.0'",
                    "initialized_by": "TEXT",
                },
            )
        self._update_table_schema()

        init_count = self.db.get_row_count("settings_initialization")
        if init_count == 0:
            self.lazy_sk_log.debug("Inserting initialization record")
            self.db.insert(
                "settings_initialization",
                {"initialization_date": datetime.datetime.now().isoformat()},
            )

    def load_settings(self) -> SQLiteDatabase:
        """
        Load settings database.
        :return: Database connection to settings.
        """
        self.lazy_sk_log.debug(f"Loading settings from {self.settings_path}")
        if not self.settings_path.exists():
            self.initialize_settings()
        elif self.db is None:
            self.db = SQLiteDatabase(str(self.settings_path))
        self.lazy_sk_log.debug("Settings loaded successfully")
        return self.db

    def get_initialization_date(self) -> Optional[str]:
        """Get settings initialization date."""
        self.lazy_sk_log.debug("Getting settings initialization date")
        db = self.load_settings()
        result = db.execute_query(
            "SELECT initialization_date FROM settings_initialization LIMIT 1"
        )
        self.lazy_sk_log.debug(f"Settings initialization date: {result[0][0]}")
        return result[0][0] if result else None

    def update_initialization_date(self) -> None:
        """Update settings initialization date."""
        self.lazy_sk_log.debug("Updating settings initialization date")
        db = self.load_settings()
        db.execute_write(
            """
            UPDATE settings_initialization 
            SET initialization_date = ?
            WHERE id = (
                SELECT id FROM settings_initialization LIMIT 1
            )
        """,
            (datetime.datetime.now().isoformat(),),
        )
        self.lazy_sk_log.debug("Settings initialization date updated")

    def close(self) -> None:
        """Close database connection."""
        if self.db:
            self.db.close()
            self.db = None

    def __enter__(self) -> "SettingsManager":
        """Context manager entry."""
        self.load_settings()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


def fetch_settings_file_ext() -> str:
    from settings.settings_list import SETTINGS_FILE_EXT

    return SETTINGS_FILE_EXT
