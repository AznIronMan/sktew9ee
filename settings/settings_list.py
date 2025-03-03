from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from utils.sk_logger import sk_log

APP_VERSION = "0.0.1"
SETTINGS_FILE_EXT = "sktew9ee"


class SettingWidgetType(Enum):
    TEXT = "text"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    PATH = "path"
    NUMBER = "number"


@dataclass
class Setting:
    key: str
    default_value: Any
    description: str = ""
    value_type: str = "str"
    required: bool = True
    label: str = ""
    widget_type: SettingWidgetType = SettingWidgetType.TEXT
    options: List[str] = None
    visible: bool = True

    def __post_init__(self):
        if not self.label:
            self.label = self.key.replace("_", " ").title()
        if self.options is None:
            self.options = []


class DefaultSettings:
    def __init__(self, hostname: str) -> None:
        self.hostname = hostname
        self._initialize_settings()

    def _initialize_settings(self) -> None:
        """Initialize all application settings."""
        try:
            self._settings = [
                Setting(
                    "debug_mode",
                    "false",
                    "Enable debug mode",
                    value_type="bool",
                    widget_type=SettingWidgetType.CHECKBOX,
                    label="Debug Mode",
                    visible=True,
                ),
                Setting(
                    "hostname",
                    self.hostname,
                    "Host machine name",
                    required=True,
                    widget_type=SettingWidgetType.TEXT,
                    visible=False,
                    label="Computer Name",
                ),
                Setting(
                    "app_version",
                    APP_VERSION,
                    "Application version",
                    required=True,
                    widget_type=SettingWidgetType.TEXT,
                    visible=False,
                    label="Application Version",
                ),
                Setting(
                    "settings_file_ext",
                    ".sktew9ee",
                    "Settings file extension",
                    required=True,
                    widget_type=SettingWidgetType.TEXT,
                    visible=False,
                    label="Settings File Extension",
                ),
                Setting(
                    "database_mode",
                    "skydbapi",
                    "Database connection mode",
                    required=True,
                    widget_type=SettingWidgetType.RADIO,
                    options=["skydbapi", "direct"],
                    label="Select Database Mode",
                ),
                Setting(
                    "log_cli",
                    "true",
                    "Enable console logging",
                    value_type="bool",
                    widget_type=SettingWidgetType.CHECKBOX,
                    label="Console Logging",
                ),
                Setting(
                    "log_file",
                    "true",
                    "Enable file logging",
                    value_type="bool",
                    widget_type=SettingWidgetType.CHECKBOX,
                    label="File Logging",
                ),
                Setting(
                    "log_dir",
                    "./.logs/",
                    "Directory for log files",
                    value_type="path",
                    widget_type=SettingWidgetType.PATH,
                    label="Log Directory",
                ),
                Setting(
                    "skydb_api_ssl",
                    "false",
                    "Use SSL for API connection",
                    value_type="bool",
                    widget_type=SettingWidgetType.CHECKBOX,
                    label="Use SSL for SKyDBAPI connection",
                ),
                Setting(
                    "skydb_api_server",
                    "localhost",
                    "SkyDB API server address",
                    widget_type=SettingWidgetType.TEXT,
                    label="SKyDB API Server Address",
                ),
                Setting(
                    "skydb_api_port",
                    "9020",
                    "SkyDB API server port",
                    value_type="int",
                    widget_type=SettingWidgetType.NUMBER,
                    label="SKyDB API Server Port",
                ),
                Setting(
                    "tew9_core_path",
                    "C:\\TEW9\\",
                    "Path to TEW9 installation",
                    value_type="path",
                    widget_type=SettingWidgetType.PATH,
                    label="TEW9 Core Installation Path",
                ),
                Setting(
                    "tew9_game_database_name",
                    "Default",
                    "TEW9 Active Database Name",
                    value_type="str",
                    widget_type=SettingWidgetType.TEXT,
                    label="TEW9 Active Database Name",
                ),
                Setting(
                    "tew9_pictures_pack_name",
                    "Default",
                    "TEW9 Pictures Pack Name",
                    value_type="str",
                    widget_type=SettingWidgetType.TEXT,
                    label="TEW9 Picture Pack Name",
                ),
                Setting(
                    "tew9_full_db_path_override",
                    "",
                    "Override TEW9 full database path",
                    value_type="path",
                    widget_type=SettingWidgetType.PATH,
                    required=False,
                    label="TEW9 Full Database Path Override",
                ),
                Setting(
                    "tew9_full_pictures_path_override",
                    "",
                    "Override TEW9 full pictures path",
                    value_type="path",
                    widget_type=SettingWidgetType.PATH,
                    required=False,
                    label="TEW9 Full Pictures Path Override",
                ),
                Setting(
                    "default_image_extension",
                    ".gif",
                    "Default image extension",
                    value_type="str",
                    widget_type=SettingWidgetType.TEXT,
                    label="Default Image Extension",
                ),
                Setting(
                    "title_screen_image_path",
                    "./bin/title.png",
                    "Path to title screen image",
                    value_type="path",
                    widget_type=SettingWidgetType.PATH,
                    label="Title Screen Image",
                ),
                Setting(
                    "photo_cache_max_age",
                    "720",
                    "Maximum age of photo cache in hours",
                    value_type="int",
                    widget_type=SettingWidgetType.NUMBER,
                    label="Photo Cache Maximum Age",
                ),
            ]
            sk_log.debug(f"Initialized {len(self._settings)} default settings")
        except Exception as e:
            sk_log.error(f"Failed to initialize settings: {e}")
            raise

    @property
    def settings(self) -> List[Setting]:
        """Get list of all settings."""
        return self._settings

    def get_setting(self, key: str) -> Setting:
        """Get a setting by key."""
        try:
            for setting in self._settings:
                if setting.key == key:
                    return setting
            raise KeyError(f"Setting '{key}' not found")
        except Exception as e:
            sk_log.error(f"Failed to get setting '{key}': {e}")
            raise

    def get_defaults_list(self) -> List[Tuple[str, str]]:
        """Get list of (key, value) tuples for database insertion."""
        try:
            defaults = [(s.key, str(s.default_value)) for s in self._settings]
            sk_log.debug(f"Generated defaults list with {len(defaults)} items")
            return defaults
        except Exception as e:
            sk_log.error(f"Failed to generate defaults list: {e}")
            raise

    def get_defaults_dict(self) -> Dict[str, str]:
        """Get dictionary of default settings."""
        try:
            defaults = {s.key: str(s.default_value) for s in self._settings}
            sk_log.debug(f"Generated defaults dict with {len(defaults)} items")
            return defaults
        except Exception as e:
            sk_log.error(f"Failed to generate defaults dict: {e}")
            raise

    def validate_value(self, key: str, value: str) -> bool:
        """
        Validate a setting value based on its type.

        Args:
            key: Setting key to validate
            value: Value to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            setting = self.get_setting(key)
            if value is None:
                return not setting.required

            if setting.value_type == "bool":
                is_valid = str(value).lower() in ("true", "false")
            elif setting.value_type == "int":
                is_valid = True if value == "" else bool(int(value))
            elif setting.value_type == "path":
                if value == "":
                    is_valid = not setting.required
                else:
                    Path(value)
                    is_valid = True
            else:
                is_valid = True

            sk_log.debug(
                f"Validated setting '{key}' with value '{value}': {is_valid}"
            )
            return is_valid

        except Exception as e:
            sk_log.error(f"Validation failed for setting '{key}': {e}")
            return False

    def convert_value(
        self, key: str, value: str
    ) -> Union[str, bool, int, Path, None]:
        """
        Convert a string value to its proper type.

        Args:
            key: Setting key to convert
            value: Value to convert

        Returns:
            Converted value in appropriate type
        """
        try:
            setting = self.get_setting(key)
            if value is None:
                if not setting.required:
                    return None
                raise ValueError(f"Required setting {key} cannot be None")

            if setting.value_type == "bool":
                converted = str(value).lower() == "true"
            elif setting.value_type == "int":
                converted = int(value)
            elif setting.value_type == "path":
                converted = Path(value) if value else None
            else:
                converted = value

            sk_log.debug(
                f"Converted setting '{key}' from '{value}' to {type(converted)}"
            )
            return converted

        except Exception as e:
            sk_log.error(f"Conversion failed for setting '{key}': {e}")
            raise
