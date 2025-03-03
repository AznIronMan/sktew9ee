import sys

from settings.settings_file import SettingsManager
from PyQt6.QtWidgets import QApplication
from ui.main_menu import MainMenu
from utils.debugger import Debugger


def main() -> None:
    try:
        debugger = Debugger()
        debugger.debug_mode_check()

        settings = SettingsManager()
        settings.initialize_settings()

        app = QApplication(sys.argv)

        # dev of photo editor
        # from ui.photo_editor.photo_base_menu import PhotoWorkerEditor

        # open_photo_editor = PhotoWorkerEditor()
        # open_photo_editor.show()

        # end of dev of photo editor

        window = MainMenu()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    main()


# save this for later

# from modules.photo_editor.photo_cache import PhotoCache
# from modules.photo_editor.photo_worker_engine import PhotoWorkerEngine

# photo_cache = PhotoCache()
# photo_cache.photo_cache_init()

# photo_worker_engine = PhotoWorkerEngine()
# game_worker_photo_list, local_worker_photo_list = (
#     photo_worker_engine.fetch_worker_photo_cache_lists()
# )

# print(game_worker_photo_list)
# print(local_worker_photo_list)
