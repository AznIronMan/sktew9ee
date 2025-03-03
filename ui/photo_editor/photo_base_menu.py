from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QApplication,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QSize
from ui.photo_editor.photo_agers_editor import PhotoAgersEditor
from ui.photo_editor.photo_contract_editor import PhotoContractEditor
from utils.sk_logger import sk_log
from ui.photo_editor.photo_worker_editor import PhotoWorkerEditor
from ui.photo_editor.photo_alters_editor import PhotoAltersEditor


class PhotoEditorMenu(QMainWindow):
    def __init__(self, parent=None) -> None:
        try:
            super().__init__(parent)
            self.setWindowTitle("Photo Editor Menu")
            self.setFixedSize(QSize(300, 300))
            self.setWindowFlags(
                Qt.WindowType.Dialog
                | Qt.WindowType.CustomizeWindowHint
                | Qt.WindowType.WindowTitleHint
            )
            self._center_window()
            self.setup_ui()
        except Exception as e:
            sk_log.error(f"PhotoEditorMenu __init__ error: {e}")
            raise e

    def _center_window(self) -> None:
        screen = QApplication.primaryScreen().geometry()
        center_x = (screen.width() - self.width()) // 2
        center_y = (screen.height() - self.height()) // 2
        self.move(center_x, center_y)

    def setup_ui(self) -> None:
        try:
            pb_central_widget = QWidget()
            self.setCentralWidget(pb_central_widget)
            pb_layout = QVBoxLayout(pb_central_widget)
            pb_layout.setSpacing(5)
            pb_layout.setContentsMargins(10, 10, 10, 10)
            pb_buttons = [
                "Worker Main",
                "Alter Egos",
                "Contract Photos",
                "Picture Changes (Agers)",
                "Return to Main Menu",
            ]
            disabled_pb_buttons = []
            hidden_pb_buttons = []
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QWidget()
            buttons_layout = QVBoxLayout(scroll_widget)
            buttons_layout.setSpacing(5)
            buttons_layout.setContentsMargins(5, 5, 5, 5)
            self.pb_buttons = {}
            for pb_btn_text in pb_buttons:
                pb_btn = QPushButton(pb_btn_text)
                pb_btn.setFixedSize(QSize(200, 40))
                buttons_layout.addWidget(
                    pb_btn, alignment=Qt.AlignmentFlag.AlignCenter
                )
                if pb_btn_text in disabled_pb_buttons:
                    pb_btn.setEnabled(False)
                elif pb_btn_text in hidden_pb_buttons:
                    pb_btn.setVisible(False)
                elif pb_btn_text == "Picture Changes (Agers)":
                    pb_btn.clicked.connect(self.open_agers_editor)
                elif pb_btn_text == "Contract Photos":
                    pb_btn.clicked.connect(self.open_contract_editor)
                elif pb_btn_text == "Alter Egos":
                    pb_btn.clicked.connect(self.open_alters_editor)
                elif pb_btn_text == "Worker Main":
                    pb_btn.clicked.connect(self.open_worker_editor)
                elif pb_btn_text == "Return to Main Menu":
                    pb_btn.clicked.connect(self.close)
                self.pb_buttons[pb_btn_text] = pb_btn
            scroll_area.setWidget(scroll_widget)
            pb_layout.addWidget(scroll_area)
        except Exception as e:
            sk_log.error(f"PhotoEditorMenu setup_ui error: {e}")
            raise e

    def open_worker_editor(self) -> None:
        try:
            self.worker_editor = PhotoWorkerEditor(self)
            self.worker_editor.setWindowModality(
                Qt.WindowModality.ApplicationModal
            )
            self.worker_editor.show()
        except Exception as e:
            sk_log.error(f"PhotoEditorMenu open_worker_editor error: {e}")
            raise e

    def open_alters_editor(self) -> None:
        try:
            self.alters_editor = PhotoAltersEditor(self)
            self.alters_editor.setWindowModality(
                Qt.WindowModality.ApplicationModal
            )
            self.alters_editor.show()
        except Exception as e:
            sk_log.error(f"PhotoEditorMenu open_alters_editor error: {e}")
            raise e

    def open_contract_editor(self) -> None:
        try:
            self.contract_editor = PhotoContractEditor(self)
            self.contract_editor.setWindowModality(
                Qt.WindowModality.ApplicationModal
            )
            self.contract_editor.show()
        except Exception as e:
            sk_log.error(f"PhotoEditorMenu open_contract_editor error: {e}")
            raise e

    def open_agers_editor(self) -> None:
        try:
            self.agers_editor = PhotoAgersEditor(self)
            self.agers_editor.setWindowModality(
                Qt.WindowModality.ApplicationModal
            )
            self.agers_editor.show()
        except Exception as e:
            sk_log.error(f"PhotoEditorMenu open_agers_editor error: {e}")
            raise e
