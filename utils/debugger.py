from settings.settings_file import SettingsManager


class Debugger:
    def __init__(self) -> None:
        import os
        import sys

        if sys.platform == "darwin":
            devnull = open(os.devnull, "w")
            os.dup2(devnull.fileno(), sys.stderr.fileno())
        self.settings = self.fetch_settings()
        self.debug_mode_value = self.settings.get_value("debug_mode")
        if self.debug_mode_value is None:
            self.debug_mode = "false"
        else:
            self.debug_mode = self.debug_mode_value.lower() == "true"
        os.environ["DEBUG"] = str(self.debug_mode)

    def fetch_settings(self) -> SettingsManager:
        settings = SettingsManager()
        settings.initialize_settings()
        return settings

    def debug_mode_check(self) -> None:
        if self.debug_mode:
            print("[DEBUG]: Debug mode is enabled")
