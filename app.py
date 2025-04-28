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
        window = MainMenu()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    main()
