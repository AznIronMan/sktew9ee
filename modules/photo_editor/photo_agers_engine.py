import re

from datetime import datetime
from typing import List, Tuple

from database.sqlite import SQLiteDatabase
from settings.settings_file import SettingsManager
from utils.sk_logger import sk_log


class PhotoAgersEngine:
    def __init__(self) -> None:
        try:
            from .picture_directories import PictureDirectories
            from .photo_cache import PhotoCache
            from database.tewdb import TEWDB
            from .photo_worker_engine import PhotoWorkerEngine

            self.tewdb = TEWDB()
            self.settings_manager = SettingsManager()
            self.photo_cache = PhotoCache()
            self.worker_photo_path = self.photo_cache.fetch_photo_root_path(
                PictureDirectories.WORKER_FOLDER
            )
            self.photo_worker_engine = PhotoWorkerEngine()

        except Exception as e:
            sk_log.error(f"PhotoAgersEngine __init__ error: {e}")
            raise e

    def __enter__(self) -> "PhotoAgersEngine":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def ager_photo_cache_init(self, skip_check: bool = False) -> bool:
        """Initialize the ager photo cache.

        Args:
            skip_check: Whether to skip the cache check.

        Returns:
            bool: Whether the cache was initialized.
        """
        try:
            cache_check = self._ager_photo_cache_check(skip_check)
            if not cache_check:
                self._build_ager_photo_record_cache()
                self._populate_ager_photo_record_cache()
                with SQLiteDatabase() as sqlitedb:
                    sqlitedb.insert(
                        "ager_photo_cache_log",
                        {
                            "timestamp": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "status": "initialized",
                        },
                    )
                    sqlitedb.commit()
                return True
            return True
        except Exception as e:
            sk_log.error(f"PhotoAgersEngine ager_photo_cache_init error: {e}")
            raise e

    def _ager_photo_cache_check(self, skip_check: bool = False) -> bool:
        """Check if the ager photo cache exists.

        Args:
            skip_check: Whether to skip the cache check.

        Returns:
            bool: Whether the cache exists.
        """
        try:
            if skip_check:
                return False
            with SQLiteDatabase() as sqlitedb:
                table_exists = sqlitedb.check_table_exists(
                    "game_ager_photo_cache"
                )
                if not table_exists:
                    return False
                ager_record_list = sqlitedb.execute_query(
                    "SELECT COUNT(*) as count FROM game_ager_photo_cache"
                )
                if not ager_record_list or ager_record_list[0]["count"] == 0:
                    return False
                return True
        except Exception as e:
            sk_log.error(f"PhotoAgersEngine _ager_photo_cache_check error: {e}")
            raise e

    def _build_ager_photo_record_cache(self) -> None:
        """Build the ager photo record cache."""
        try:
            with SQLiteDatabase() as sqlitedb:
                sqlitedb.execute_write(
                    "DROP TABLE IF EXISTS game_ager_photo_cache"
                )
                sqlitedb.execute_write(
                    "DROP TABLE IF EXISTS ager_photo_cache_log"
                )
                sqlitedb.create_table(
                    "ager_photo_cache_log",
                    {
                        "ager_photo_cache_log_id": (
                            "INTEGER PRIMARY KEY AUTOINCREMENT"
                        ),
                        "timestamp": "TEXT",
                        "status": "TEXT",
                    },
                )
                sqlitedb.insert(
                    "ager_photo_cache_log",
                    {
                        "timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "status": "created",
                    },
                )
                sqlitedb.create_table(
                    "game_ager_photo_cache",
                    {
                        "game_ager_photo_cache_id": (
                            "INTEGER PRIMARY KEY AUTOINCREMENT"
                        ),
                        "game_ager_uid": "INTEGER",
                        "game_ager_recordname": "TEXT",
                        "game_ager_worker_uid": "INTEGER",
                        "game_ager_trigger_age": "INTEGER",
                        "game_ager_photo_file": "TEXT",
                        "game_ager_photo_status": "TEXT",
                    },
                )
                sqlitedb.commit()
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEngine _build_ager_photo_record_cache error: {e}"
            )
            raise e

    def _fetch_ager_photo_records_from_db(self) -> List[Tuple]:
        """Fetch the ager photo records from the database."""
        try:
            from modules.tables.agers_table import AgersFunctions

            agers_functions = AgersFunctions()
            ager_record_list = agers_functions.fetch_all_agers_specific_cols(
                ["UID", "Recordname", "Worker", "Trigger", "Picture"]
            )
            return ager_record_list
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEngine _fetch_ager_photo_records_from_db error: {e}"
            )
            raise e

    def _populate_ager_photo_record_cache(self) -> None:
        """Populate the ager photo record cache."""
        try:
            ager_record_list = self._fetch_ager_photo_records_from_db()
            self._fill_ager_photo_record_cache(ager_record_list)
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEngine _populate_ager_photo_record_cache error: {e}"
            )
            raise e

    def _fill_ager_photo_record_cache(
        self, ager_record_list: List[Tuple]
    ) -> None:
        """Fill the ager photo record cache."""
        try:
            with SQLiteDatabase() as sqlitedb:
                for ager in ager_record_list:
                    sqlitedb.insert(
                        "game_ager_photo_cache",
                        {
                            "game_ager_uid": ager["UID"],
                            "game_ager_recordname": ager["Recordname"],
                            "game_ager_worker_uid": ager["Worker"],
                            "game_ager_trigger_age": ager["Trigger"],
                            "game_ager_photo_file": ager["Picture"],
                            "game_ager_photo_status": "new",
                        },
                    )
                    sqlitedb.commit()
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEngine _fill_ager_photo_record_cache error: {e}"
            )
            raise e

    def _fetch_ager_photo_record_cache(self) -> List[Tuple]:
        """Fetch the ager photo record cache."""
        try:
            with SQLiteDatabase() as sqlitedb:
                ager_record_list = sqlitedb.execute_query(
                    "SELECT * FROM game_ager_photo_cache"
                )
                if not ager_record_list or len(ager_record_list) == 0:
                    raise Exception("Ager record list is empty")
                return ager_record_list
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEngine _fetch_ager_photo_record_cache error: {e}"
            )
            raise e

    def _reset_ager_photo_record_cache(self) -> None:
        """Reset the ager photo record cache."""
        try:
            self._build_ager_photo_record_cache()
            ager_record_list = self._fetch_ager_photo_record_cache()
            if not ager_record_list:
                raise Exception("Ager record list is empty")
            self._fill_ager_photo_record_cache(ager_record_list)
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEngine _reset_ager_photo_record_cache error: {e}"
            )
            raise e

    def _fetch_worker_name_by_uid(self, worker_uid: int) -> str:
        """Fetch the worker name by UID.

        Args:
            worker_uid (int): The UID of the worker.

        Returns:
            str: The name of the worker or "Unknown" if not found.
        """
        try:
            from modules.tables.worker_table import WorkerFunctions

            with WorkerFunctions() as worker_functions:
                worker_data = worker_functions.fetch_worker_specific_cols(
                    worker_uid, ["Name"]
                )
                if worker_data and len(worker_data) > 0:
                    return worker_data[0]["Name"]
                return "Unknown"
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEngine _fetch_worker_name_by_uid error: {e}"
            )
            return "Unknown"

    def fetch_ager_photo_record_cache_lists(
        self,
    ) -> Tuple[List[dict], List[dict]]:
        """Fetch the ager photo record cache lists."""
        try:
            raw_ager_photo_record_list = self._fetch_ager_photo_record_cache()
            game_ager_record_list = []
            for ager in raw_ager_photo_record_list:
                ager_uid = ager["game_ager_uid"]
                worker_uid = ager["game_ager_worker_uid"]
                worker_name = self._fetch_worker_name_by_uid(worker_uid)
                ager_trigger_age = ager["game_ager_trigger_age"]
                combined_ager_record = (
                    f"{worker_name}[Age@{ager_trigger_age}][{ager_uid}]"
                )
                game_ager_record_list.append(
                    {
                        "game_ager_uid": ager_uid,
                        "game_ager_recordname": combined_ager_record,
                    }
                )
            try:
                local_workers = self._fetch_local_workers_from_cache()
                transformed_local_workers = []
                for worker in local_workers:
                    transformed_local_workers.append(
                        {
                            "local_contract_photo_file": worker[
                                "local_worker_photo_file"
                            ]
                        }
                    )
                return (game_ager_record_list, transformed_local_workers)
            except Exception as e:
                sk_log.warning(
                    "Error fetching local workers from cache: "
                    f"{e}, trying direct directory scan"
                )
                from .photo_worker_engine import PhotoWorkerEngine

                with PhotoWorkerEngine() as photo_worker_engine:
                    worker_files = (
                        photo_worker_engine.fetch_worker_photos_from_dir()
                    )
                    transformed_files = [
                        {"local_contract_photo_file": file}
                        for file in worker_files
                    ]
                    return (game_ager_record_list, transformed_files)
        except Exception as e:
            sk_log.error(
                "PhotoAgersEngine fetch_ager_photo_record_cache_lists error: "
                f"{e}"
            )
            raise e

    def _rebuild_ager_photo_record_cache(self) -> None:
        """Rebuild the ager photo record cache."""
        try:
            self._build_ager_photo_record_cache()
            self._populate_ager_photo_record_cache()
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEngine _rebuild_ager_photo_record_cache error: {e}"
            )
            raise e

    def refresh_ager_photo_record_cache(self) -> None:
        """Refresh the ager photo record cache."""
        try:
            try:
                self._reset_ager_photo_record_cache()
            except Exception as reset_error:
                sk_log.warning(f"Full cache reset failed: {reset_error}")
                self._rebuild_ager_photo_record_cache()
                with SQLiteDatabase() as sqlitedb:
                    sqlitedb.insert(
                        "ager_photo_cache_log",
                        {
                            "timestamp": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "status": "partial_refresh",
                        },
                    )
                    sqlitedb.commit()
                sk_log.info(
                    "Ager photo record cache partially refreshed (local files only)"
                )
                return

            with SQLiteDatabase() as sqlitedb:
                sqlitedb.insert(
                    "ager_photo_cache_log",
                    {
                        "timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "status": "refreshed",
                    },
                )
                sqlitedb.commit()
            sk_log.info("Ager photo record cache refreshed successfully")
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEngine refresh_ager_photo_record_cache error: {e}"
            )
            raise e

    def fetch_ager_photo_record_lists(self) -> Tuple[List[dict], List[dict]]:
        """Fetch the ager photo record lists."""
        try:
            return self.fetch_ager_photo_record_cache_lists()
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEngine fetch_ager_photo_record_lists error: {e}"
            )
            raise e

    def fetch_ager_photo_filename_from_cache(self, ager_name: str) -> str:
        """Fetch the ager photo filename from the cache.

        Args:
            ager_name (str): The ager name in format "WorkerName[Age@X][UID]"

        Returns:
            str: The filename for the ager photo
        """
        try:
            sk_log.debug(f"Fetching photo for ager: {ager_name}")
            uid_match = re.search(r"\[(\d+)\]$", ager_name)
            if not uid_match:
                sk_log.debug(f"No UID match found in ager name: {ager_name}")
                return ""
            ager_uid = int(uid_match.group(1))
            sk_log.debug(f"Extracted UID: {ager_uid}")

            with SQLiteDatabase() as sqlitedb:
                query = (
                    "SELECT game_ager_photo_file FROM game_ager_photo_cache WHERE "
                    f"game_ager_uid = {ager_uid}"
                )
                sk_log.debug(f"Executing query: {query}")
                result = sqlitedb.execute_query(query)
                if result and len(result) > 0:
                    filename = result[0]["game_ager_photo_file"]
                    sk_log.debug(f"Found photo filename: {filename}")
                    return filename
                sk_log.debug(f"No photo found for UID: {ager_uid}")
                return ""
        except Exception as e:
            sk_log.error(
                "PhotoAgersEngine fetch_ager_photo_filename_from_cache error: "
                f"{e}"
            )
            raise e

    def update_ager_photo_filename(
        self, ager_name: str, new_filename: str, append_gif: bool = False
    ) -> None:
        """Update the ager photo filename in the cache."""
        try:
            uid_match = re.search(r"\[(\d+)\]", ager_name)
            if not uid_match:
                return
            ager_uid = int(uid_match.group(1))

            with SQLiteDatabase() as sqlitedb:
                from utils.filer import Filer

                updated_filename = new_filename
                with Filer() as filer:
                    image_extension = filer.extract_extension(new_filename)
                    if image_extension is None:
                        image_extension = self.settings_manager.get_value(
                            "default_image_extension"
                        )
                        if image_extension is None:
                            raise Exception(
                                "Default image extension is not set in settings."
                            )
                    if not (append_gif and image_extension == "gif"):
                        updated_filename = filer.filepath_formatter(
                            new_filename, image_extension
                        )
                sqlitedb.execute_write(
                    "UPDATE game_ager_photo_cache SET game_ager_photo_file = ? "
                    "WHERE game_ager_uid = ?",
                    (updated_filename, ager_uid),
                )
                sqlitedb.commit()
                self.tewdb.update(
                    "UPDATE tblAger SET Picture = ? WHERE UID = ?",
                    (updated_filename, ager_uid),
                )
                sk_log.info(
                    f"Updated ager UID {ager_uid} with "
                    f"new photo: {updated_filename}"
                )
        except Exception as e:
            sk_log.error(
                "PhotoAgersEngine update_ager_photo_filename error: " f"{e}"
            )
            raise e

    def _fetch_local_workers_from_cache(self) -> List[dict]:
        """Fetch the local workers from the cache.

        Returns:
            List[dict]: List of local workers with keys 'local_worker_uid',
                'local_worker_photo_file', and 'local_worker_photo_status'
        """
        try:
            with SQLiteDatabase() as sqlitedb:
                worker_photo_list = sqlitedb.execute_query(
                    "SELECT * FROM local_worker_photo_cache"
                )
                if not worker_photo_list or len(worker_photo_list) == 0:
                    raise Exception("No local workers found in cache")
                return [dict(row) for row in worker_photo_list]
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEngine _fetch_local_workers_from_cache error: {e}"
            )
            raise e
