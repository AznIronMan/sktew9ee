from datetime import datetime, timedelta
from typing import List, Tuple

from database.sqlite import SQLiteDatabase
from settings.settings_file import SettingsManager
from utils.sk_logger import sk_log


class PhotoWorkerEngine:
    def __init__(self) -> None:
        try:
            from .picture_directories import PictureDirectories
            from .photo_cache import PhotoCache
            from database.tewdb import TEWDB

            self.tewdb = TEWDB()
            self.settings_manager = SettingsManager()
            self.photo_cache = PhotoCache()
            self.worker_photo_path = self.photo_cache.fetch_photo_root_path(
                PictureDirectories.WORKER_FOLDER
            )

        except Exception as e:
            sk_log.error(f"PhotoWorkerEngine __init__ error: {e}")
            raise e

    def __enter__(self) -> "PhotoWorkerEngine":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def fetch_worker_filename_from_cache(self, worker_name: str) -> str:
        try:
            with SQLiteDatabase() as sqlitedb:
                result = sqlitedb.execute_query(
                    f"SELECT game_worker_photo_file FROM game_worker_photo_cache "
                    f"WHERE game_worker_name = '{worker_name}'"
                )
                if result and len(result) > 0:
                    return result[0]["game_worker_photo_file"]
                return ""
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine fetch_worker_filename_from_cache error: {e}"
            )
            raise e

    def fetch_worker_photo_cache_lists(self) -> Tuple[List[Tuple], List[Tuple]]:
        """Fetch the worker photo cache lists.

        Returns:
            Tuple[List[Tuple], List[Tuple]]: Tuple of lists of worker photos.
        """
        try:
            return (
                self._fetch_game_workers_from_cache(),
                self._fetch_local_workers_from_cache(),
            )
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine fetch_worker_photo_cache_lists error: {e}"
            )
            raise e

    def worker_photo_cache_init(self, skip_check: bool = False) -> bool:
        try:
            cache_check = self._worker_photo_cache_check(skip_check)
            sk_log.debug(f"cache_check: {cache_check}")
            if not cache_check:
                self._reset_worker_photo_cache()
            return True
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine worker_photo_cache_init error: {e}"
            )
            raise e

    def update_worker_photo_filename(
        self, worker_name: str, new_filename: str, append_gif: bool = False
    ) -> None:
        """Update the worker photo filename in the cache.

        Args:
            worker_name (str): The name of the worker.
            new_filename (str): The new filename to update the worker photo filename to.
            append_gif (bool, optional): Whether to append .gif if there's no extension.
            Defaults to False.

        Raises:
            Exception: If there is an error updating the worker photo filename.
        """
        try:
            with SQLiteDatabase() as sqlitedb:
                from utils.filer import Filer

                updated_filename = new_filename
                with Filer() as filer:
                    image_extension = filer.extract_extension(new_filename)
                    if append_gif and image_extension is None:
                        updated_filename = f"{new_filename}.gif"
                        image_extension = "gif"
                    elif image_extension is None:
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
                    "UPDATE game_worker_photo_cache SET game_worker_photo_file "
                    "= ? WHERE game_worker_name = ?",
                    (updated_filename, worker_name),
                )
                sqlitedb.commit()
                self.tewdb.update(
                    "UPDATE tblWorker SET Picture = ? WHERE Name = ?",
                    (updated_filename, worker_name),
                )
                sk_log.info(
                    f"Updated worker {worker_name} with photo: {updated_filename}"
                )
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine update_worker_photo_filename error: {e}"
            )
            raise e

    def build_local_worker_photo_cache(
        self, worker_photo_list: List[str]
    ) -> None:
        """Build the local worker photo cache.

        Args:
            worker_photo_list (List[str]): List of worker photo filenames to build the
            local worker photo cache from.

        Raises:
            e: Exception if the local worker photo cache cannot be built.
        """
        try:
            with SQLiteDatabase() as sqlitedb:
                for filename in worker_photo_list:
                    sqlitedb.insert(
                        "local_worker_photo_cache",
                        {
                            "local_worker_photo_file": filename,
                            "local_worker_photo_status": "new",
                        },
                    )
                sqlitedb.commit()
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine build_local_worker_photo_cache error: {e}"
            )
            raise e

    def _build_game_worker_photo_cache(
        self, worker_photo_list: List[dict]
    ) -> None:
        """Build the game worker photo cache.

        Args:
            worker_photo_list (List[dict]): List of worker photo dictionaries containing
                'uid', 'Name', and 'Picture' keys

        Raises:
            Exception: If the game worker photo cache cannot be built
        """
        try:
            with SQLiteDatabase() as sqlitedb:
                for worker in worker_photo_list:
                    sqlitedb.insert(
                        "game_worker_photo_cache",
                        {
                            "game_worker_uid": worker["uid"],
                            "game_worker_name": worker["Name"],
                            "game_worker_photo_file": worker["Picture"],
                            "game_worker_photo_status": "new",
                        },
                    )
                sqlitedb.commit()
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine build_game_worker_photo_cache error: {e}"
            )
            raise e

    def _fetch_game_workers_from_cache(self) -> List[dict]:
        """Fetch the game workers from the cache.

        Returns:
            List[dict]: List of game workers with keys 'game_worker_uid',
                'game_worker_name', 'game_worker_photo_file', and
                'game_worker_photo_status'
        """
        try:
            with SQLiteDatabase() as sqlitedb:
                worker_photo_list = sqlitedb.execute_query(
                    "SELECT * FROM game_worker_photo_cache"
                )
                if not worker_photo_list or len(worker_photo_list) == 0:
                    raise Exception("No game workers found in cache")
                return [dict(row) for row in worker_photo_list]
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine fetch_game_workers_from_cache error: {e}"
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
                f"PhotoWorkerEngine fetch_local_workers_from_cache error: {e}"
            )
            raise e

    def fetch_worker_photos_from_dir(self) -> List[str]:
        """Fetch the worker photos from the directory.

        Returns:
            List[str]: List of worker photo filenames.

        Raises:
            e: Exception if the worker photos cannot be fetched from the directory.
        """
        from utils.filer import Filer
        from .picture_directories import PictureDirectories
        from .photo_cache import PhotoCache

        try:
            with Filer() as filer:
                photo_cache = PhotoCache()
                worker_photo_paths = filer.fetch_files_from_directory(
                    photo_cache.fetch_photo_root_path(
                        PictureDirectories.WORKER_FOLDER
                    ),
                    include_patterns=["*.gif", "*.png"],
                )
                worker_photo_list = [path.name for path in worker_photo_paths]
                return worker_photo_list
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine fetch_worker_photos_from_dir error: {e}"
            )
            raise e

    def _fetch_worker_photo_paths_from_db(self) -> List[Tuple]:
        """Fetch the worker photo paths from the database.

        Returns:
            List[Tuple]: List of worker photo paths.

        Raises:
            e: Exception if the worker photo paths cannot be fetched from the database.
        """
        from modules.tables.worker_table import WorkerFunctions

        try:
            worker_functions = WorkerFunctions()
            worker_photo_list = (
                worker_functions.fetch_all_workers_specific_cols(
                    ["uid", "Name", "Picture"]
                )
            )
            return worker_photo_list
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine fetch_worker_photo_list error: {e}"
            )
            raise e

    def _fetch_worker_photo_lists(self) -> Tuple[List[Tuple], List[Tuple]]:
        """Fetch the worker photo lists.

        Returns:
            Tuple[List[Tuple], List[Tuple]]: Tuple of lists of worker photos.

        Raises:
            e: Exception if the worker photo lists cannot be fetched.
        """
        try:
            from .photo_cache import PhotoCache

            with PhotoCache() as photo_cache:
                worker_photo_list_from_dir = self.fetch_worker_photos_from_dir()
                if not photo_cache.photo_list_check(worker_photo_list_from_dir):
                    raise Exception("Worker photo list from dir is empty")
                worker_photo_list_from_db = (
                    self._fetch_worker_photo_paths_from_db()
                )
                if not photo_cache.photo_list_check(worker_photo_list_from_db):
                    raise Exception("Worker photo list from db is empty")
                return worker_photo_list_from_dir, worker_photo_list_from_db
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine _fetch_worker_photo_lists error: {e}"
            )
            raise e

    def _rebuild_worker_photo_cache(self) -> None:
        """Rebuild the worker photo cache.

        Raises:
            e: Exception if the worker photo cache cannot be rebuilt.
        """
        try:
            with SQLiteDatabase() as sqlitedb:
                sqlitedb.execute_write(
                    "DROP TABLE IF EXISTS local_worker_photo_cache"
                )
                sqlitedb.execute_write(
                    "DROP TABLE IF EXISTS game_worker_photo_cache"
                )
                sqlitedb.execute_write(
                    "DROP TABLE IF EXISTS worker_photo_cache_log"
                )
                sqlitedb.create_table(
                    "worker_photo_cache_log",
                    {
                        "worker_photo_cache_log_id": (
                            "INTEGER PRIMARY KEY AUTOINCREMENT"
                        ),
                        "timestamp": "TEXT",
                        "status": "TEXT",
                    },
                )
                sqlitedb.insert(
                    "worker_photo_cache_log",
                    {
                        "timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "status": "created",
                    },
                )
                sqlitedb.create_table(
                    "local_worker_photo_cache",
                    {
                        "local_worker_uid": "INTEGER PRIMARY KEY AUTOINCREMENT",
                        "local_worker_photo_file": "TEXT",
                        "local_worker_photo_status": "TEXT",
                    },
                )
                sqlitedb.create_table(
                    "game_worker_photo_cache",
                    {
                        "game_worker_uid": "INTEGER PRIMARY KEY AUTOINCREMENT",
                        "game_worker_name": "TEXT",
                        "game_worker_photo_file": "TEXT",
                        "game_worker_photo_status": "TEXT",
                    },
                )
                sqlitedb.commit()
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine rebuild_worker_photo_cache error: {e}"
            )

    def _reset_worker_photo_cache(self) -> bool:
        """Reset the worker photo cache.

        Returns:
            bool: True if the worker photo cache was reset, False otherwise.

        Raises:
            e: Exception if the worker photo cache cannot be reset.
        """
        try:
            self._rebuild_worker_photo_cache()
            worker_dir_list, worker_db_list = self._fetch_worker_photo_lists()
            self.build_local_worker_photo_cache(worker_dir_list)
            self._build_game_worker_photo_cache(worker_db_list)
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine reset_worker_photo_cache error: {e}"
            )

    def _verify_worker_photo_cache_is_ready(self) -> bool:
        """Verify if the worker photo cache is ready.

        Returns:
            bool: True if the worker photo cache is ready, False otherwise.

        Raises:
            e: Exception if the worker photo cache cannot be verified.
        """
        try:
            sk_log.debug("PhotoWorkerEngine verify_worker_photo_cache_is_ready")
            with SQLiteDatabase() as sqlitedb:
                table_exists = sqlitedb._check_table_exists(
                    "worker_photo_cache_log"
                )
                sk_log.debug(f"table_exists: {table_exists}")
                if not table_exists:
                    sk_log.debug("table_exists is False")
                    return False
                sk_log.debug("table_exists is True")
                logs_found = sqlitedb.execute_query(
                    "SELECT * FROM worker_photo_cache_log ORDER BY "
                    "timestamp DESC LIMIT 1"
                )
                sk_log.debug(f"logs_found: {logs_found}")
                if not logs_found:
                    sk_log.debug("logs_found is False")
                    return False
                sk_log.debug("logs_found is True")
                with SettingsManager() as settings_manager:
                    max_age = int(
                        settings_manager.get_value("photo_cache_max_age")
                    )
                    sk_log.debug(f"max_age: {max_age}")
                    last_record = logs_found[0]
                    last_timestamp = datetime.strptime(
                        last_record[1], "%Y-%m-%d %H:%M:%S"
                    )
                    sk_log.debug(f"last_record: {last_record}")
                    if last_timestamp < datetime.now() - timedelta(
                        hours=max_age
                    ):
                        sk_log.debug("last_record is older than max_age")
                        return False
                    sk_log.debug("last_record is not older than max_age")
                    return True
        except Exception as e:
            sk_log.debug(
                "PhotoWorkerEngine verify_clear_worker_photo_cache_age "
                f"did not complete: {e}"
            )
            return False

    def _verify_local_worker_photo_cache_status(self) -> bool:
        """Verify if the local worker photo cache is ready.

        Returns:
            bool: True if the local worker photo cache is ready, False otherwise.

        Raises:
            e: Exception if the local worker photo cache cannot be verified.
        """
        try:
            with SQLiteDatabase() as sqlitedb:
                table_exists = sqlitedb._check_table_exists(
                    "local_worker_photo_cache"
                )
                if not table_exists:
                    return False
                at_least_one_record = sqlitedb._check_table_has_records(
                    "local_worker_photo_cache"
                )
                if not at_least_one_record:
                    return False
                return True
        except Exception as e:
            sk_log.debug(
                f"PhotoWorkerEngine verify_local_worker_photo_cache_status error: {e}"
            )
            return False

    def _worker_photo_cache_check(self, skip_check: bool = False) -> bool:
        """Verify if the worker photo cache is up to date.

        Returns:
            bool: True if the worker photo cache is up to date, False otherwise.

        Raises:
            e: Exception if the worker photo cache cannot be verified.
        """
        try:
            ready_check = self._verify_worker_photo_cache_is_ready()
            sk_log.debug(f"ready_check: {ready_check}")
            if skip_check or not ready_check:
                return False
            return True
        except Exception as e:
            sk_log.debug(
                f"PhotoWorkerEngine worker_photo_cache_check error: {e}"
            )
            return False

    def refresh_worker_photo_cache(self) -> None:
        """Refresh the worker photo cache by rebuilding it with current data.

        This method resets the cache and rebuilds it with fresh data from
        the directory and database.

        Raises:
            Exception: If there is an error refreshing the worker photo cache.
        """
        try:
            local_files = self.fetch_worker_photos_from_dir()
            if not local_files:
                raise Exception("No local worker photo files found")
            try:
                self._reset_worker_photo_cache()
            except Exception as reset_error:
                sk_log.warning(f"Full cache reset failed: {reset_error}")
                self._rebuild_worker_photo_cache()
                self.build_local_worker_photo_cache(local_files)
                with SQLiteDatabase() as sqlitedb:
                    sqlitedb.insert(
                        "worker_photo_cache_log",
                        {
                            "timestamp": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "status": "partial_refresh",
                        },
                    )
                    sqlitedb.commit()

                sk_log.info(
                    "Worker photo cache partially refreshed (local files only)"
                )
                return
            with SQLiteDatabase() as sqlitedb:
                sqlitedb.insert(
                    "worker_photo_cache_log",
                    {
                        "timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "status": "refreshed",
                    },
                )
                sqlitedb.commit()
            sk_log.info("Worker photo cache refreshed successfully")
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEngine refresh_worker_photo_cache error: {e}"
            )
            raise e
