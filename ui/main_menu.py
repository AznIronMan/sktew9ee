from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
from settings.settings_file import SettingsManager
from settings.settings_list import APP_VERSION
from ui.photo_editor.photo_base_menu import PhotoEditorMenu
from utils.sk_logger import sk_log


class MainMenu(QMainWindow):
    def __init__(self) -> None:
        try:
            super().__init__()
            self.setWindowTitle(
                f"Street Kings TEW9 Enhanced Editor v{APP_VERSION}"
            )
            self.setFixedSize(600, 800)
            self._center_window()
            mm_central_widget = QWidget()
            self.setCentralWidget(mm_central_widget)
            mm_layout = QVBoxLayout(mm_central_widget)
            mm_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            mm_image_label = QLabel()
            mm_image_label.setFixedSize(512, 512)
            settings = SettingsManager()
            mm_image_path = settings.get_value("title_screen_image_path")
            if mm_image_path is None or mm_image_path == "[default]":
                mm_image_path = "./bin/title.png"
                settings.set_value("title_screen_image_path", mm_image_path)
            mm_title_image = QPixmap(mm_image_path)
            if mm_title_image.isNull():
                mm_title_image = QPixmap(400, 200)
                mm_title_image.fill(Qt.GlobalColor.lightGray)
                mm_image_label.setText("Image Not Found")
                mm_image_label.setStyleSheet(
                    "QLabel { color: black; font-size: 16px; }"
                )
                mm_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                scaled_mm_title_image = mm_title_image.scaled(
                    512,
                    512,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                mm_image_label.setPixmap(scaled_mm_title_image)
            mm_image_label.setScaledContents(True)
            mm_layout.addWidget(
                mm_image_label, alignment=Qt.AlignmentFlag.AlignCenter
            )
            mm_buttons = [
                "Worker Editor",
                "Photo Editor",
                "Moves Editor",
                "Fed Editor",
                "Broadcast Editor",
                "Gimmick Editor",
                "Narrative Editor",
                "Settings",
                "Exit",
            ]
            self.mm_windows = []
            disabled_mm_buttons = []
            hidden_mm_buttons = [
                "Worker Editor",
                "Moves Editor",
                "Fed Editor",
                "Broadcast Editor",
                "Gimmick Editor",
                "Narrative Editor",
            ]

            for mm_button_text in mm_buttons:
                mm_button = QPushButton(mm_button_text)
                mm_button.setFixedSize(QSize(200, 40))
                mm_layout.addWidget(
                    mm_button, alignment=Qt.AlignmentFlag.AlignCenter
                )
                if mm_button_text in disabled_mm_buttons:
                    mm_button.setEnabled(False)
                elif mm_button_text in hidden_mm_buttons:
                    mm_button.setVisible(False)
                elif mm_button_text == "Exit":
                    mm_button.clicked.connect(self.close)
                elif mm_button_text == "Settings":
                    mm_button.clicked.connect(self.open_settings)
                elif mm_button_text == "Photo Editor":
                    mm_button.clicked.connect(self.open_photo_editor)
        except Exception as e:
            sk_log.error(f"MainMenu init error: {e}")
            raise e

    def _center_window(self) -> None:
        try:
            screen = QApplication.primaryScreen().geometry()
            center_x = (screen.width() - self.width()) // 2
            center_y = (screen.height() - self.height()) // 2
            self.move(center_x, center_y)
        except Exception as e:
            sk_log.error(f"MainMenu _center_window error: {e}")
            raise e

    def open_settings(self) -> None:
        try:
            from ui.settings_menu import SettingsWindow

            settings_window = SettingsWindow(self)
            self.mm_windows.append(settings_window)
            settings_window.setWindowModality(
                Qt.WindowModality.ApplicationModal
            )
            settings_window.show()
        except Exception as e:
            sk_log.error(f"MainMenu open_settings error: {e}")
            raise e

    def open_photo_editor(self) -> None:
        try:
            photo_editor_window = PhotoEditorMenu(self)
            self.mm_windows.append(photo_editor_window)
            photo_editor_window.setWindowModality(
                Qt.WindowModality.ApplicationModal
            )
            photo_editor_window.show()
        except Exception as e:
            sk_log.error(f"MainMenu open_photo_editor error: {e}")
            raise e
