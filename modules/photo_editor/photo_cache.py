import os
from typing import List, Tuple

from settings.settings_file import SettingsManager
from utils.sk_logger import sk_log


class PhotoCache:
    def __init__(self) -> None:
        try:
            self.settings_manager = SettingsManager()

        except Exception as e:
            sk_log.error(f"PhotoCache __init__ error: {e}")
            raise e

    def __enter__(self) -> "PhotoCache":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def photo_cache_init(self, skip_check: bool = False) -> bool:
        from .photo_worker_engine import PhotoWorkerEngine

        with PhotoWorkerEngine() as photo_worker_engine:
            photo_worker_engine.worker_photo_cache_init(skip_check)

    def fetch_photo_root_path(self, additional_path: str | None = None) -> str:
        """Fetch the photo root path.

        Args:
            additional_path (str | None, optional): Additional path to add to the
            root path. Defaults to None.

        Returns:
            str: Builds the photo root path from the information in settings and
            appends the additional path if provided.

        Raises:
            e: Exception if the photo root path cannot be fetched.
        """
        try:
            self.tew9_core_path = self.settings_manager.get_value(
                "tew9_core_path"
            )
            self.tew9_pictures_pack_name = self.settings_manager.get_value(
                "tew9_pictures_pack_name"
            )
            self.worker_photo_path = self.settings_manager.get_value(
                "tew9_full_pictures_path_override"
            )
            if self.worker_photo_path == "":
                self.worker_photo_path = os.path.join(
                    self.tew9_core_path,
                    "Pictures",
                    self.tew9_pictures_pack_name,
                )
            if additional_path:
                self.worker_photo_path = os.path.join(
                    self.worker_photo_path, additional_path
                )
            self.worker_photo_path = os.path.normpath(self.worker_photo_path)
            return self.worker_photo_path
        except Exception as e:
            sk_log.error(f"PhotoCache fetch_photo_root_path error: {e}")
            raise e

    def photo_list_check(self, list: List[Tuple]) -> bool:
        """Check if the photo list is not empty.

        Args:
            list (List[Tuple]): List of photos.

        Returns:
            bool: True if the list is not empty, False otherwise.
        """
        try:
            if len(list) == 0:
                return False
            return True
        except TypeError as type_error:
            sk_log.debug(f"PhotoCache photo_list_check TypeError: {type_error}")
            return False
        except Exception as e:
            sk_log.debug(f"PhotoCache photo_list_check error: {e}")
            return False
