import re

from datetime import datetime
from typing import List, Tuple

from database.sqlite import SQLiteDatabase
from settings.settings_file import SettingsManager
from utils.sk_logger import sk_log


class PhotoContractEngine:

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
            sk_log.error(f"PhotoContractEngine __init__ error: {e}")
            raise e

    def __enter__(self) -> "PhotoContractEngine":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def contract_photo_cache_init(self, skip_check: bool = False) -> bool:
        """Initialize the contract photo cache.

        Args:
            skip_check: Whether to skip the cache check.

        Returns:
            bool: Whether the cache was initialized.
        """
        try:
            cache_check = self._contract_photo_cache_check(skip_check)
            if not cache_check:
                self._build_contract_photo_record_cache()
                self._populate_contract_photo_record_cache()
                with SQLiteDatabase() as sqlitedb:
                    sqlitedb.insert(
                        "contract_photo_cache_log",
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
            sk_log.error(
                f"PhotoContractEngine contract_photo_cache_init error: {e}"
            )
            raise e

    def _contract_photo_cache_check(self, skip_check: bool = False) -> bool:
        """Check if the contract photo cache exists.

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
                    "game_contract_photo_cache"
                )
                if not table_exists:
                    return False
                contract_record_list = sqlitedb.execute_query(
                    "SELECT COUNT(*) as count FROM game_contract_photo_cache"
                )
                if (
                    not contract_record_list
                    or contract_record_list[0]["count"] == 0
                ):
                    return False
                return True
        except Exception as e:
            sk_log.error(
                f"PhotoContractEngine _contract_photo_cache_check error: {e}"
            )
            raise e

    def _build_contract_photo_record_cache(self) -> None:
        """Build the contract photo record cache."""
        try:
            with SQLiteDatabase() as sqlitedb:
                sqlitedb.execute_write(
                    "DROP TABLE IF EXISTS game_contract_photo_cache"
                )
                sqlitedb.execute_write(
                    "DROP TABLE IF EXISTS contract_photo_cache_log"
                )
                sqlitedb.create_table(
                    "contract_photo_cache_log",
                    {
                        "contract_photo_cache_log_id": (
                            "INTEGER PRIMARY KEY AUTOINCREMENT"
                        ),
                        "timestamp": "TEXT",
                        "status": "TEXT",
                    },
                )
                sqlitedb.insert(
                    "contract_photo_cache_log",
                    {
                        "timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "status": "created",
                    },
                )
                sqlitedb.create_table(
                    "game_contract_photo_cache",
                    {
                        "game_contract_photo_cache_id": (
                            "INTEGER PRIMARY KEY AUTOINCREMENT"
                        ),
                        "game_contract_uid": "INTEGER",
                        "game_contract_fedid": "INTEGER",
                        "game_contract_recordname": "TEXT",
                        "game_contract_worker_uid": "INTEGER",
                        "game_contract_photo_file": "TEXT",
                        "game_contract_photo_status": "TEXT",
                    },
                )
                sqlitedb.commit()
        except Exception as e:
            sk_log.error(
                f"PhotoContractEngine _build_contract_photo_record_cache error: {e}"
            )
            raise e

    def _fetch_contract_photo_records_from_db(self) -> List[Tuple]:
        """Fetch the contract photo records from the database."""
        try:
            from modules.tables.contract_table import ContractFunctions

            contract_functions = ContractFunctions()
            contract_record_list = (
                contract_functions.fetch_all_contracts_specific_cols(
                    ["UID", "FedUID", "WorkerUID", "Name", "Picture"]
                )
            )
            return contract_record_list
        except Exception as e:
            sk_log.error(
                f"PhotoContractEngine _fetch_contract_photo_records_from_db error: {e}"
            )
            raise e

    def _populate_contract_photo_record_cache(self) -> None:
        """Populate the contract photo record cache."""
        try:
            contract_record_list = self._fetch_contract_photo_records_from_db()
            self._fill_contract_photo_record_cache(contract_record_list)
        except Exception as e:
            sk_log.error(
                f"PhotoContractEngine _populate_contract_photo_record_cache error: {e}"
            )
            raise e

    def _fill_contract_photo_record_cache(
        self, contract_record_list: List[Tuple]
    ) -> None:
        """Fill the contract photo record cache."""
        try:
            with SQLiteDatabase() as sqlitedb:
                for contract in contract_record_list:
                    sqlitedb.insert(
                        "game_contract_photo_cache",
                        {
                            "game_contract_uid": contract["UID"],
                            "game_contract_fedid": contract["FedUID"],
                            "game_contract_recordname": contract["Name"],
                            "game_contract_worker_uid": contract["WorkerUID"],
                            "game_contract_photo_file": contract["Picture"],
                            "game_contract_photo_status": "new",
                        },
                    )
                    sqlitedb.commit()
        except Exception as e:
            sk_log.error(
                f"PhotoContractEngine _fill_contract_photo_record_cache error: {e}"
            )
            raise e

    def _fetch_contract_photo_record_cache(self) -> List[Tuple]:
        """Fetch the contract photo record cache."""
        try:
            with SQLiteDatabase() as sqlitedb:
                contract_record_list = sqlitedb.execute_query(
                    "SELECT * FROM game_contract_photo_cache"
                )
                if not contract_record_list or len(contract_record_list) == 0:
                    raise Exception("Contract record list is empty")
                return contract_record_list
        except Exception as e:
            sk_log.error(
                f"PhotoContractEngine _fetch_contract_photo_record_cache error: {e}"
            )
            raise e

    def _reset_contract_photo_record_cache(self) -> None:
        """Reset the contract photo record cache."""
        try:
            self._build_contract_photo_record_cache()
            contract_record_list = self._fetch_contract_photo_records_from_db()
            if not contract_record_list:
                raise Exception("Contract record list is empty")
            self._fill_contract_photo_record_cache(contract_record_list)
        except Exception as e:
            sk_log.error(
                f"PhotoContractEngine _reset_contract_photo_record_cache error: {e}"
            )
            raise e

    def fetch_contract_photo_record_cache_lists(
        self,
    ) -> Tuple[List[dict], List[dict]]:
        """Fetch the contract photo record cache lists."""
        """should be in RecordName[FEDINITIALS][UID] format"""
        try:
            raw_contract_photo_record_list = (
                self._fetch_contract_photo_record_cache()
            )
            game_contract_record_list = []
            for contract in raw_contract_photo_record_list:
                contract_recordname = contract["game_contract_recordname"]
                contract_uid = contract["game_contract_uid"]
                contract_fedid = contract["game_contract_fedid"]
                # get fed initials from fed_table.py here
                # Fix for MS Access parameter issue
                try:
                    # First try with proper parameter binding
                    fed_initials = self.tewdb.select(
                        "SELECT Initials FROM tblFed WHERE UID = ?",
                        (contract_fedid,),
                    )
                except Exception as e:
                    sk_log.warning(
                        f"FedInitials query failed with proper binding: {e}, trying alternative approach"
                    )
                    # Fallback: try with direct embedding (less secure but may work)
                    try:
                        query = f"SELECT Initials FROM tblFed WHERE UID = {contract_fedid}"
                        fed_initials = self.tewdb.select(query)
                    except Exception as e2:
                        sk_log.error(
                            f"FedInitials fallback query also failed: {e2}, using placeholder"
                        )
                        # Provide a placeholder if all else fails
                        fed_initials = [{"Initials": "UNK"}]

                if not fed_initials:
                    sk_log.warning(
                        f"FedInitials not found for FedUID={contract_fedid}, using placeholder"
                    )
                    fed_initials = [{"Initials": "UNK"}]

                combined_contract_record = f"{contract_recordname}[{fed_initials[0]['Initials']}][{contract_uid}]"
                game_contract_record_list.append(
                    {
                        "game_contract_uid": contract_uid,
                        "game_contract_name": combined_contract_record,
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
                return (game_contract_record_list, transformed_local_workers)
            except Exception as e:
                sk_log.warning(
                    f"Error fetching local workers from cache: {e}, trying direct directory scan"
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
                    return (game_contract_record_list, transformed_files)
        except Exception as e:
            sk_log.error(
                "PhotoContractEngine fetch_contract_photo_record_cache_lists "
                f"error: {e}"
            )
            raise e

    def _rebuild_contract_photo_record_cache(self) -> None:
        """Rebuild the contract photo record cache."""
        try:
            self._build_contract_photo_record_cache()
            self._populate_contract_photo_record_cache()
        except Exception as e:
            sk_log.error(
                f"PhotoContractEngine _rebuild_contract_photo_record_cache error: {e}"
            )
            raise e

    def refresh_contract_photo_record_cache(self) -> None:
        """Refresh the contract photo record cache."""
        try:
            try:
                self._reset_contract_photo_record_cache()
            except Exception as reset_error:
                sk_log.warning(f"Full cache reset failed: {reset_error}")
                self._rebuild_contract_photo_record_cache()
                with SQLiteDatabase() as sqlitedb:
                    sqlitedb.insert(
                        "contract_photo_cache_log",
                        {
                            "timestamp": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "status": "partial_refresh",
                        },
                    )
                    sqlitedb.commit()
                sk_log.info(
                    "Contract photo record cache partially refreshed (local files only)"
                )
                return

            with SQLiteDatabase() as sqlitedb:
                sqlitedb.insert(
                    "contract_photo_cache_log",
                    {
                        "timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "status": "refreshed",
                    },
                )
                sqlitedb.commit()
            sk_log.info("Contract photo record cache refreshed successfully")
        except Exception as e:
            sk_log.error(
                f"PhotoContractEngine refresh_contract_photo_record_cache error: {e}"
            )
            raise e

    def fetch_contract_photo_record_lists(
        self,
    ) -> Tuple[List[dict], List[dict]]:
        """Fetch the contract photo record lists."""
        try:
            return self.fetch_contract_photo_record_cache_lists()
        except Exception as e:
            sk_log.error(
                f"PhotoContractEngine fetch_contract_photo_record_lists error: {e}"
            )
            raise e

    def fetch_contract_photo_filename_from_cache(
        self, contract_name: str
    ) -> str:
        """Fetch the contract photo filename from the cache."""
        try:
            uid_match = re.search(r"\[(\d+)\]", contract_name)
            if not uid_match:
                return ""
            contract_uid = int(uid_match.group(1))

            with SQLiteDatabase() as sqlitedb:
                result = sqlitedb.execute_query(
                    f"SELECT game_contract_photo_file FROM game_contract_photo_cache "
                    f"WHERE game_contract_uid = {contract_uid}"
                )
                if result and len(result) > 0:
                    return result[0]["game_contract_photo_file"]
                return ""
        except Exception as e:
            sk_log.error(
                "PhotoContractEngine fetch_contract_photo_filename_from_cache "
                f"error: {e}"
            )
            return ""

    def update_contract_photo_filename(
        self, contract_name: str, new_filename: str, append_gif: bool = False
    ) -> None:
        """Update the contract photo filename in the cache."""
        try:
            uid_match = re.search(r"\[(\d+)\]", contract_name)
            if not uid_match:
                raise ValueError("Invalid contract name format")
            contract_uid = int(uid_match.group(1))

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
                    "UPDATE game_contract_photo_cache SET game_contract_photo_file = ? "
                    "WHERE game_contract_uid = ?",
                    (updated_filename, contract_uid),
                )
                sqlitedb.commit()
                self.tewdb.update(
                    "UPDATE tblContract SET Picture = ? WHERE UID = ?",
                    (updated_filename, contract_uid),
                )
                sk_log.info(
                    f"Updated contract UID {contract_uid} with "
                    f"new photo: {updated_filename}"
                )
        except Exception as e:
            sk_log.error(
                f"PhotoContractEngine update_contract_photo_filename error: {e}"
            )
            raise e
