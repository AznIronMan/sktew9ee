from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QRadioButton,
    QPushButton,
    QFileDialog,
    QButtonGroup,
    QWidget,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QSize
from settings.settings_file import SettingsManager
from settings.settings_list import SettingWidgetType, DefaultSettings
from utils.sk_logger import sk_log


class SettingsWindow(QDialog):
    def __init__(self, parent=None) -> None:
        try:
            super().__init__(parent)
            self.setWindowTitle("Street Kings TEW9 Enhanced Editor Settings")
            self.setModal(True)
            self.setFixedSize(QSize(800, 400))
            self.setWindowFlags(
                Qt.WindowType.Dialog
                | Qt.WindowType.CustomizeWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.WindowTitleHint
            )
            self.settings_manager = SettingsManager()
            self.default_settings = DefaultSettings(
                self.settings_manager.hostname
            )
            self.widgets = {}
            settings_main_layout = QVBoxLayout(self)
            settings_main_layout.setSpacing(5)
            settings_main_layout.setContentsMargins(10, 10, 10, 10)
            settings_scroll = QScrollArea()
            settings_scroll.setWidgetResizable(True)
            settings_scroll_widget = QWidget()
            self.settings_layout = QVBoxLayout(settings_scroll_widget)
            self.settings_layout.setSpacing(5)
            self.settings_layout.setContentsMargins(5, 5, 5, 5)
            settings_scroll.setWidget(settings_scroll_widget)
            settings_main_layout.addWidget(settings_scroll)
            self.create_settings_widgets()
            settings_save_button = QPushButton("Save && Close")
            settings_save_button.setFixedSize(QSize(200, 40))
            settings_main_layout.addWidget(
                settings_save_button, alignment=Qt.AlignmentFlag.AlignCenter
            )
            settings_save_button.clicked.connect(self.save_and_close)
        except Exception as e:
            sk_log.error(f"SettingsWindow __init__ error: {e}")
            raise e

    def create_settings_widgets(self) -> None:
        try:
            for setting in self.default_settings.settings:
                if hasattr(setting, "visible") and not setting.visible:
                    continue
                current_value = self.settings_manager.get_value(setting.key)
                container = QWidget()
                layout = QHBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                label = QLabel(setting.label)
                label.setMinimumWidth(200)
                label.setAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                layout.addWidget(label)
                widget_container = QWidget()
                widget_layout = QHBoxLayout(widget_container)
                widget_layout.setContentsMargins(10, 0, 0, 0)
                widget_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                if setting.widget_type == SettingWidgetType.CHECKBOX:
                    widget = QCheckBox()
                    widget.setChecked(str(current_value).lower() == "true")
                    widget_layout.addWidget(widget)
                elif setting.widget_type == SettingWidgetType.RADIO:
                    widget = QWidget()
                    radio_layout = QHBoxLayout(widget)
                    radio_layout.setContentsMargins(0, 0, 0, 0)
                    radio_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                    button_group = QButtonGroup(widget)
                    for i, option in enumerate(setting.options):
                        radio = QRadioButton(option)
                        radio_layout.addWidget(radio)
                        button_group.addButton(radio, i)
                        if option == current_value:
                            radio.setChecked(True)
                    widget_layout.addWidget(widget)
                elif setting.widget_type == SettingWidgetType.PATH:
                    path_edit = QLineEdit(current_value)
                    path_edit.setMinimumWidth(200)
                    path_container = QWidget()
                    path_layout = QHBoxLayout(path_container)
                    path_layout.setContentsMargins(0, 0, 0, 0)
                    browse_button = QPushButton("...")
                    browse_button.setFixedWidth(30)
                    path_layout.addWidget(path_edit)
                    path_layout.addWidget(browse_button)
                    widget_layout.addWidget(path_container)
                    browse_button.clicked.connect(
                        lambda checked, edit=path_edit: self.browse_path(edit)
                    )
                    widget = path_edit
                else:
                    widget = QLineEdit(current_value)
                    widget.setMinimumWidth(200)
                    widget_layout.addWidget(widget)
                layout.addWidget(widget_container)
                layout.setStretch(1, 1)
                self.settings_layout.addWidget(container)
                self.widgets[setting.key] = widget
        except Exception as e:
            sk_log.error(f"SettingsWindow create_settings_widgets error: {e}")
            raise e

    def browse_path(self, line_edit: QLineEdit) -> None:
        try:
            path = QFileDialog.getExistingDirectory(self, "Select Directory")
            if path:
                line_edit.setText(path)
        except Exception as e:
            sk_log.error(f"SettingsWindow browse_path error: {e}")
            raise e

    def save_and_close(self) -> None:
        self.save_settings()
        self.accept()

    def save_settings(self) -> None:
        try:
            for key, widget in self.widgets.items():
                setting = self.default_settings.get_setting(key)
                if setting.widget_type == SettingWidgetType.CHECKBOX:
                    value = str(widget.isChecked()).lower()
                elif setting.widget_type == SettingWidgetType.RADIO:
                    button_group = widget.findChild(QButtonGroup)
                    checked_button = button_group.checkedButton()
                    value = (
                        checked_button.text()
                        if checked_button
                        else setting.default_value
                    )
                elif setting.widget_type == SettingWidgetType.PATH:
                    value = widget.text()
                else:
                    value = widget.text()
                self.settings_manager.set_value(key, value)
        except Exception as e:
            sk_log.error(f"SettingsWindow save_settings error: {e}")
            raise e

    def closeEvent(self, event) -> None:
        """Override close event to save settings before closing"""
        self.save_settings()
        event.accept()
