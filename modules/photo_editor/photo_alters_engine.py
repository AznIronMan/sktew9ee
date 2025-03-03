import re

from datetime import datetime
from typing import List, Tuple

from database.sqlite import SQLiteDatabase
from settings.settings_file import SettingsManager
from utils.sk_logger import sk_log


class PhotoAltersEngine:
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
            sk_log.error(f"PhotoAltersEngine __init__ error: {e}")
            raise e

    def __enter__(self) -> "PhotoAltersEngine":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def alter_photo_cache_init(self, skip_check: bool = False) -> bool:
        """Initialize the alter photo cache.

        Args:
            skip_check: Whether to skip the cache check.

        Returns:
            bool: Whether the cache was initialized.
        """
        try:
            cache_check = self._alter_photo_cache_check(skip_check)
            if not cache_check:
                self._build_alter_photo_record_cache()
                self._populate_alter_photo_record_cache()
                with SQLiteDatabase() as sqlitedb:
                    sqlitedb.insert(
                        "alter_photo_cache_log",
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
            sk_log.error(f"PhotoAltersEngine alter_photo_cache_init error: {e}")
            raise e

    def _alter_photo_cache_check(self, skip_check: bool = False) -> bool:
        """Check if the alter photo cache exists.

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
                    "game_alter_photo_cache"
                )
                if not table_exists:
                    return False
                alter_record_list = sqlitedb.execute_query(
                    "SELECT COUNT(*) as count FROM game_alter_photo_cache"
                )
                if not alter_record_list or alter_record_list[0]["count"] == 0:
                    return False
                return True
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine _alter_photo_cache_check error: {e}"
            )
            return False

    def _build_alter_photo_record_cache(self) -> None:
        """Rebuild the alter photo cache."""
        try:

            with SQLiteDatabase() as sqlitedb:
                sqlitedb.execute_write(
                    "DROP TABLE IF EXISTS game_alter_photo_cache"
                )
                sqlitedb.execute_write(
                    "DROP TABLE IF EXISTS alter_photo_cache_log"
                )
                sqlitedb.create_table(
                    "alter_photo_cache_log",
                    {
                        "alter_photo_cache_log_id": (
                            "INTEGER PRIMARY KEY AUTOINCREMENT"
                        ),
                        "timestamp": "TEXT",
                        "status": "TEXT",
                    },
                )
                sqlitedb.insert(
                    "alter_photo_cache_log",
                    {
                        "timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "status": "created",
                    },
                )
                sqlitedb.create_table(
                    "game_alter_photo_cache",
                    {
                        "game_alter_uid": "INTEGER PRIMARY KEY AUTOINCREMENT",
                        "game_alter_alter_uid": "INTEGER",
                        "game_alter_recordname": "TEXT",
                        "game_alter_worker_uid": "INTEGER",
                        "game_alter_photo_file": "TEXT",
                        "game_alter_photo_status": "TEXT",
                    },
                )
                sqlitedb.commit()
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine _build_alter_photo_cache error: {e}"
            )
            raise e

    def _fetch_alter_photo_records_from_db(self) -> List[Tuple]:
        """Fetch the alter record from the database."""
        try:
            from modules.tables.alter_table import AlterFunctions

            alter_functions = AlterFunctions()
            alter_record_list = alter_functions.fetch_all_alters_specific_cols(
                ["UID", "WorkerUID", "Recordname", "Picture"]
            )
            return alter_record_list
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine _fetch_alter_photo_records_from_db error: {e}"
            )
            raise e

    def _populate_alter_photo_record_cache(self) -> None:
        """Populate the game alter record cache."""
        try:
            alter_record_list = self._fetch_alter_photo_records_from_db()
            self._fill_alter_photo_record_cache(alter_record_list)
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine _populate_alter_record_photo_cache error: {e}"
            )
            raise e

    def _fill_alter_photo_record_cache(
        self, alter_record_list: List[Tuple]
    ) -> None:
        """Build the game alter record cache."""
        try:
            with SQLiteDatabase() as sqlitedb:
                for alter in alter_record_list:
                    sqlitedb.insert(
                        "game_alter_photo_cache",
                        {
                            "game_alter_alter_uid": alter["UID"],
                            "game_alter_recordname": alter["Recordname"],
                            "game_alter_worker_uid": alter["WorkerUID"],
                            "game_alter_photo_file": alter["Picture"],
                            "game_alter_photo_status": "new",
                        },
                    )
                    sqlitedb.commit()
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine _build_alter_record_photo_cache error: {e}"
            )

    def _fetch_alter_photo_record_cache(self) -> List[Tuple]:
        """Fetch the game alter record cache."""
        try:
            with SQLiteDatabase() as sqlitedb:
                alter_record_list = sqlitedb.execute_query(
                    "SELECT * FROM game_alter_photo_cache"
                )
                if not alter_record_list or len(alter_record_list) == 0:
                    raise Exception("Alter record list is empty")
                return alter_record_list
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine _fetch_alter_record_photo_cache error: {e}"
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
                f"PhotoAltersEngine _fetch_local_workers_from_cache error: {e}"
            )
            raise e

    def _reset_alter_photo_record_cache(self) -> None:
        """Reset the alter photo cache."""
        try:
            self._build_alter_photo_record_cache()
            right_list = self.photo_worker_engine.fetch_worker_photos_from_dir()
            if not right_list:
                raise Exception("Right list is empty")
            alter_record_list = self._fetch_alter_photo_records_from_db()
            if not alter_record_list:
                raise Exception("Alter record list is empty")
            self._fill_alter_photo_record_cache(alter_record_list)
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine _reset_alter_photo_cache error: {e}"
            )
            raise e

    def fetch_alter_photo_record_cache_lists(
        self,
    ) -> Tuple[List[dict], List[dict]]:
        """Fetch the alter record list.

        Returns:
            A tuple containing the game alter record list and local workers.
        """
        try:
            raw_alter_photo_record_list = self._fetch_alter_photo_record_cache()
            game_alter_record_list = []

            for alter in raw_alter_photo_record_list:
                alter_recordname = alter["game_alter_recordname"]
                alter_uid = alter["game_alter_alter_uid"]
                if "|" in alter_recordname:
                    worker_name = alter_recordname.split("|")[0]
                    alter_parts = alter_recordname.split("|")[1:]
                    alter_desc = "|".join(alter_parts)
                else:
                    worker_name = alter_recordname
                    alter_desc = ""
                combined_alter_record = f"{worker_name}[{alter_uid}]"
                if alter_desc:
                    combined_alter_record += f"[{alter_desc}]"
                game_alter_record_list.append(
                    {
                        "game_alter_uid": alter_uid,
                        "game_alter_name": combined_alter_record,
                    }
                )
            try:
                local_workers = self._fetch_local_workers_from_cache()
                transformed_local_workers = []
                for worker in local_workers:
                    transformed_local_workers.append(
                        {
                            "local_alter_photo_file": worker[
                                "local_worker_photo_file"
                            ]
                        }
                    )
                return (game_alter_record_list, transformed_local_workers)
            except Exception:
                from .photo_worker_engine import PhotoWorkerEngine

                with PhotoWorkerEngine() as photo_worker_engine:
                    worker_files = (
                        photo_worker_engine.fetch_worker_photos_from_dir()
                    )
                    return (
                        game_alter_record_list,
                        [
                            {"local_alter_photo_file": file}
                            for file in worker_files
                        ],
                    )

        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine fetch_alter_record_lists error: {e}"
            )
            raise e

    def _rebuild_alter_photo_record_cache(self) -> None:
        """Rebuild the alter photo record cache."""
        try:
            self._build_alter_photo_record_cache()
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine _rebuild_alter_photo_record_cache error: {e}"
            )
            raise e

    def refresh_alter_photo_record_cache(self) -> None:
        """Refresh the alter photo record cache."""
        try:
            try:
                self._reset_alter_photo_record_cache()
            except Exception as reset_error:
                sk_log.warning(f"Full cache reset failed: {reset_error}")
                self._rebuild_alter_photo_record_cache()
                with SQLiteDatabase() as sqlitedb:
                    sqlitedb.insert(
                        "alter_photo_cache_log",
                        {
                            "timestamp": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "status": "partial_refresh",
                        },
                    )
                    sqlitedb.commit()
                sk_log.info(
                    "Alter photo record cache partially refreshed (local files only)"
                )
                return

            with SQLiteDatabase() as sqlitedb:
                sqlitedb.insert(
                    "alter_photo_cache_log",
                    {
                        "timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "status": "refreshed",
                    },
                )
                sqlitedb.commit()
            sk_log.info("Alter photo record cache refreshed successfully")
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine refresh_alter_photo_record_cache error: {e}"
            )
            raise e

    def fetch_alter_record_lists(self) -> Tuple[List[dict], List[dict]]:
        """Fetch the alter record list.

        Returns:
            A tuple containing the game alter record list and local workers.
        """
        try:
            return self.fetch_alter_photo_record_cache_lists()
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine fetch_alter_record_lists error: {e}"
            )
            raise e

    def fetch_alter_filename_from_cache(self, alter_name: str) -> str:
        """Fetch the alter filename from the cache.

        Args:
            alter_name: The name of the alter to fetch the filename for.

        Returns:
            The filename of the alter, or empty string if not found.
        """
        try:
            uid_match = re.search(r"\[(\d+)\]", alter_name)
            if not uid_match:
                return ""

            alter_uid = int(uid_match.group(1))

            with SQLiteDatabase() as sqlitedb:
                result = sqlitedb.execute_query(
                    f"SELECT game_alter_photo_file FROM game_alter_photo_cache "
                    f"WHERE game_alter_alter_uid = {alter_uid}"
                )
                if result and len(result) > 0:
                    return result[0]["game_alter_photo_file"]
                return ""
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine fetch_alter_filename_from_cache error: {e}"
            )
            return ""

    def update_alter_photo_filename(
        self, alter_name: str, new_filename: str, append_gif: bool = False
    ) -> None:
        """Update the alter photo filename in the cache and database.

        Args:
            alter_name: The name of the alter with format "Name[UID][Description]".
            new_filename: The new filename to update the alter photo to.
            append_gif: Whether to append .gif if there's no extension. 
            Defaults to False.

        Raises:
            Exception: If there is an error updating the alter photo filename.
        """
        try:

            uid_match = re.search(r"\[(\d+)\]", alter_name)
            if not uid_match:
                raise Exception(f"Invalid alter name format: {alter_name}")

            alter_uid = int(uid_match.group(1))

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
                    "UPDATE game_alter_photo_cache SET game_alter_photo_file = ? "
                    "WHERE game_alter_alter_uid = ?",
                    (updated_filename, alter_uid),
                )
                sqlitedb.commit()
                self.tewdb.update(
                    "UPDATE tblAlternate SET Picture = ? WHERE UID = ?",
                    (updated_filename, alter_uid),
                )
                sk_log.info(
                    f"Updated alter UID {alter_uid} with new photo: {updated_filename}"
                )
        except Exception as e:
            sk_log.error(
                f"PhotoAltersEngine update_alter_photo_filename error: {e}"
            )
            raise e
