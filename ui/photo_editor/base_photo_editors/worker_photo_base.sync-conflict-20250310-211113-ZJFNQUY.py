from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QLineEdit,
    QGridLayout,
    QApplication,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize

from utils.sk_logger import sk_log


class WorkerPhotoBase(QMainWindow):

    _window_dimensions = QSize(1300, 630)
    _list_widget_width = 320
    _list_widget_height = 590
    _photo_preview_width = 300
    _photo_preview_height = 300
    _text_input_width = 250
    _text_input_height = 35
    _quarter_button_size = QSize(80, 40)
    _half_button_size = QSize(145, 40)
    _three_quarter_button_size = QSize(205, 40)
    _standard_button_size = QSize(290, 40)
    _return_button_size = QSize(610, 40)

    def __init__(
        self,
        editor_type: str,
        parent=None,
    ) -> None:
        try:
            if editor_type is None or editor_type == "":
                raise ValueError("Editor type must be provided")
            super().__init__(parent)
            formatted_editor_type = " ".join(
                word.capitalize() for word in editor_type.split()
            )
            self.setWindowTitle(f"{formatted_editor_type} Photo Editor")
            self.left_side_name = f"Game {formatted_editor_type}"
            self.right_side_name = f"Local {formatted_editor_type}"
            self.setFixedSize(self._window_dimensions)
            self.setWindowFlags(
                Qt.WindowType.Dialog
                | Qt.WindowType.CustomizeWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.WindowTitleHint
            )
            self._center_window()
            self.setup_ui()
        except Exception as e:
            sk_log.error(f"WorkerPhotoBase __init__ error: {e}")
            raise e

    def _center_window(self) -> None:
        screen = QApplication.primaryScreen().geometry()
        center_x = (screen.width() - self.width()) // 2
        center_y = (screen.height() - self.height()) // 2
        self.move(center_x, center_y)

    def setup_ui(self) -> None:
        try:
            # Main Window Widget
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QVBoxLayout(main_widget)
            main_layout.setSpacing(5)
            main_layout.setContentsMargins(10, 10, 10, 10)

            # Grid for Main Content
            grid_layout = QGridLayout()
            main_layout.addLayout(grid_layout, stretch=1)
            grid_layout.setContentsMargins(0, 10, 0, 10)

            # Game Worker List Object
            self.left_list = QListWidget()
            self.left_list.setFixedSize(
                self._list_widget_width, self._list_widget_height
            )
            grid_layout.addWidget(self.left_list, 0, 0)

            # Local Worker List Object
            self.right_list = QListWidget()
            self.right_list.setFixedSize(
                self._list_widget_width, self._list_widget_height
            )
            grid_layout.addWidget(self.right_list, 0, 2)

            # Widget for Photo Preview and Options (Center Widget)
            center_widget = QWidget()
            center_layout = QGridLayout(center_widget)
            center_layout.setContentsMargins(0, 0, 0, 0)
            center_layout.setHorizontalSpacing(20)
            center_layout.setVerticalSpacing(10)

            # Row 0

            # Game Worker Photo Preview Object
            self.left_photo = QLabel(f"{self.left_side_name} Photo")
            self.left_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.left_photo.setStyleSheet("border: 1px solid black;")
            self.left_photo.setFixedSize(
                self._photo_preview_width, self._photo_preview_height
            )

            # Game Worker Photo Container
            row_0_left_widget = QWidget()
            row_0_left_layout = QHBoxLayout(row_0_left_widget)
            row_0_left_layout.setContentsMargins(0, 0, 0, 0)
            row_0_left_layout.setSpacing(5)
            row_0_left_layout.addWidget(self.left_photo)

            # Local Worker Photo Preview Object
            self.right_photo = QLabel(f"{self.right_side_name} Photo")
            self.right_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.right_photo.setStyleSheet("border: 1px solid black;")
            self.right_photo.setFixedSize(
                self._photo_preview_width, self._photo_preview_height
            )

            # Local Worker Photo Container
            row_0_right_widget = QWidget()
            row_0_right_layout = QHBoxLayout(row_0_right_widget)
            row_0_right_layout.setContentsMargins(0, 0, 0, 0)
            row_0_right_layout.setSpacing(5)
            row_0_right_layout.addWidget(self.right_photo)

            # Photos Container (Left and Right Row 1 Center Widget)
            center_layout.addWidget(
                row_0_left_widget, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter
            )
            center_layout.addWidget(
                row_0_right_widget, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Row 1

            # Unselect1 Button Object
            self.unselect_left_button = QPushButton(
                f"Unselect {self.left_side_name}"
            )
            self.unselect_left_button.setFixedSize(self._standard_button_size)

            # Unselect2 Button Object
            self.unselect_right_button = QPushButton(
                f"Unselect {self.right_side_name}"
            )
            self.unselect_right_button.setFixedSize(self._standard_button_size)

            # Left Unselect Button Container
            row_1_left_widget = QWidget()
            row_1_left_layout = QHBoxLayout(row_1_left_widget)
            row_1_left_layout.setContentsMargins(0, 0, 0, 0)
            row_1_left_layout.setSpacing(5)
            row_1_left_layout.addWidget(self.unselect_left_button)

            # Right Unselect Button Container
            row_1_right_widget = QWidget()
            row_1_right_layout = QHBoxLayout(row_1_right_widget)
            row_1_right_layout.setContentsMargins(0, 0, 0, 0)
            row_1_right_layout.setSpacing(5)
            row_1_right_layout.addWidget(self.unselect_right_button)

            # Unselect Container (Row 0 Center Widget)
            center_layout.addWidget(
                row_1_left_widget, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter
            )
            center_layout.addWidget(
                row_1_right_widget, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Row 2

            # Game Worker Name Label Object
            self.left_name_label = QLabel(f"{self.left_side_name} Name")
            self.left_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Local Worker Filename Object
            self.right_filename = QLabel(f"{self.right_side_name} Filename")
            self.right_filename.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Game Worker Name Container
            row_2_left_widget = QWidget()
            row_2_left_layout = QHBoxLayout(row_2_left_widget)
            row_2_left_layout.setContentsMargins(0, 10, 0, 10)
            row_2_left_layout.setSpacing(5)
            row_2_left_layout.addWidget(self.left_name_label)

            # Local Worker Filename Container
            row_2_right_widget = QWidget()
            row_2_right_layout = QHBoxLayout(row_2_right_widget)
            row_2_right_layout.setContentsMargins(0, 10, 0, 10)
            row_2_right_layout.setSpacing(5)
            row_2_right_layout.addWidget(self.right_filename)

            # Name Container (Left and Right Row 2 in Center Widget)
            center_layout.addWidget(
                row_2_left_widget, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter
            )
            center_layout.addWidget(
                row_2_right_widget, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Row 3

            # Game Worker Filename Object
            self.left_filename = QLabel(f"{self.left_side_name} Filename")
            self.left_filename.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # File Metadata Object
            self.right_metadata = QLabel(f"{self.right_side_name} Metadata")
            self.right_metadata.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Game Worker Filename Container
            row_3_left_widget = QWidget()
            row_3_left_layout = QHBoxLayout(row_3_left_widget)
            row_3_left_layout.setContentsMargins(0, 0, 0, 10)
            row_3_left_layout.setSpacing(5)
            row_3_left_layout.addWidget(self.left_filename)

            # Local File Metadata Container
            row_3_right_widget = QWidget()
            row_3_right_layout = QHBoxLayout(row_3_right_widget)
            row_3_right_layout.setContentsMargins(0, 0, 0, 10)
            row_3_right_layout.setSpacing(5)
            row_3_right_layout.addWidget(self.right_metadata)

            # Filename/Metadata Container (Left and Right Row 3 Center Widget)
            center_layout.addWidget(
                row_3_left_widget, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter
            )
            center_layout.addWidget(
                row_3_right_widget, 3, 1, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Row 4

            # Checkbox and Text Input for Custom Path Object
            self.checkbox = QCheckBox()
            self.text_input = QLineEdit()
            self.text_input.setFixedSize(
                self._text_input_width, self._text_input_height
            )
            row_4_left_widget = QWidget()
            row_4_left_layout = QHBoxLayout(row_4_left_widget)
            row_4_left_layout.setContentsMargins(0, 0, 0, 0)
            row_4_left_layout.setSpacing(5)
            row_4_left_layout.addWidget(self.checkbox)
            spacer = QSpacerItem(
                20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
            row_4_left_layout.addItem(spacer)
            row_4_left_layout.addWidget(self.text_input)

            # Use This and Delete Button Objects
            self.use_this_button = QPushButton("Use This")
            self.use_this_button.setFixedSize(self._half_button_size)
            self.delete_button = QPushButton("Delete")
            self.delete_button.setFixedSize(self._half_button_size)

            # Use This and Delete Button Container
            row_4_right_widget = QWidget()
            row_4_right_layout = QHBoxLayout(row_4_right_widget)
            row_4_right_layout.setContentsMargins(0, 0, 0, 0)
            row_4_right_layout.setSpacing(5)
            row_4_right_layout.addWidget(
                self.use_this_button, alignment=Qt.AlignmentFlag.AlignCenter
            )
            row_4_right_layout.addWidget(
                self.delete_button, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Checkbox/Text Input and Use/Delete Container (Row 4 Center Widget)
            center_layout.addWidget(
                row_4_left_widget, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter
            )
            center_layout.addWidget(
                row_4_right_widget, 4, 1, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Row 5

            # Clear Path and Apply Custom Button Objects
            self.clear_button = QPushButton("Clear Path")
            self.clear_button.setFixedSize(self._quarter_button_size)
            self.transfer_up_button = QPushButton("Apply Custom Path")
            self.transfer_up_button.setFixedSize(
                self._three_quarter_button_size
            )

            row_5_left_widget = QWidget()
            row_5_left_layout = QHBoxLayout(row_5_left_widget)
            row_5_left_layout.setContentsMargins(0, 0, 0, 0)
            row_5_left_layout.setSpacing(5)
            row_5_left_layout.addWidget(
                self.clear_button, alignment=Qt.AlignmentFlag.AlignCenter
            )
            row_5_left_layout.addWidget(
                self.transfer_up_button, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Upload New Photo Button Object
            self.upload_button = QPushButton("Upload New Photo")
            self.upload_button.setFixedSize(self._standard_button_size)

            # Upload New Photo Container
            row_5_right_widget = QWidget()
            row_5_right_layout = QHBoxLayout(row_5_right_widget)
            row_5_right_layout.setContentsMargins(0, 0, 0, 0)
            row_5_right_layout.setSpacing(5)
            row_5_right_layout.addWidget(
                self.upload_button, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Clear/Apply and Upload Container (Row 5 Center Widget)
            center_layout.addWidget(
                row_5_left_widget, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter
            )
            center_layout.addWidget(
                row_5_right_widget, 5, 1, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Row 6

            # Return Button Object
            self.return_button = QPushButton("Return to Photo Editor Menu")
            self.return_button.setFixedSize(self._return_button_size)
            self.return_button.clicked.connect(self.close)

            # Return Button Container
            row_6_widget = QWidget()
            row_6_layout = QHBoxLayout(row_6_widget)
            row_6_layout.setContentsMargins(0, 0, 0, 0)
            row_6_layout.setSpacing(5)
            row_6_layout.addWidget(
                self.return_button, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Return Container (Row 6 Center Widget)
            center_layout.addWidget(
                row_6_widget, 6, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter
            )

            # Add Center Widget to Grid Layout
            grid_layout.addWidget(
                center_widget, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter
            )

        except Exception as e:
            sk_log.error(f"PhotoWorkerEditor setup_ui error: {e}")
            raise e
