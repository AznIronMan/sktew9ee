import os
from typing import List, Tuple

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox

from ui.photo_editor.base_photo_editors.worker_photo_base import WorkerPhotoBase
from modules.photo_editor.photo_worker_engine import PhotoWorkerEngine
from modules.photo_editor.photo_agers_engine import PhotoAgersEngine

from utils.sk_logger import sk_log


class PhotoAgersEditor(WorkerPhotoBase):

    MAX_LABEL_TEXT_LENGTH = 40

    def __init__(self, parent=None) -> None:
        try:
            super().__init__(editor_type="Ager", parent=parent)
            with PhotoAgersEngine() as photo_agers_engine:
                try:
                    photo_agers_engine.ager_photo_cache_init(skip_check=True)
                except Exception as cache_error:
                    sk_log.warning(f"Cache initialization error: {cache_error}")
            self.initial_ui_setup()
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor __init__ error: {e}")
            raise e

    def initial_ui_setup(self) -> None:
        """Initialize the UI setup.

        Raises:
            Exception: If there is an error initializing the UI setup.
        """
        try:
            with PhotoAgersEngine() as photo_agers_engine:
                try:
                    game_agers, local_workers = (
                        photo_agers_engine.fetch_ager_photo_record_lists()
                    )
                except Exception as e:
                    sk_log.warning(
                        f"Cache fetch error, attempting rebuild: {e}"
                    )
                    photo_agers_engine.refresh_ager_photo_record_cache()

                    try:
                        game_agers, local_workers = (
                            photo_agers_engine.fetch_ager_photo_record_lists()
                        )
                    except Exception as refresh_error:
                        sk_log.error(f"Cache rebuild failed: {refresh_error}")
                        game_agers = []
                        local_workers = []
                        try:
                            with PhotoWorkerEngine() as photo_worker_engine:
                                local_files = (
                                    photo_worker_engine.fetch_worker_photos_from_dir()
                                )
                                local_workers = [
                                    {"local_contract_photo_file": f}
                                    for f in local_files
                                ]
                        except Exception as local_error:
                            sk_log.error(
                                f"Local files fetch failed: {local_error}"
                            )
                self._populate_left_list(game_agers)
                self._populate_right_list(local_workers)
                self.left_list.setSelectionMode(
                    self.left_list.SelectionMode.SingleSelection
                )
                self.right_list.setSelectionMode(
                    self.right_list.SelectionMode.ExtendedSelection
                )
                self.left_photo.setText("")
                self.right_photo.setText("")
                self.unselect_left_button.setEnabled(False)
                self.unselect_right_button.setEnabled(False)
                self.left_name_label.setText("")
                self.left_filename.setText("")
                self.right_filename.setText("")
                self.right_metadata.setText("")
                self.checkbox.setChecked(False)
                self.text_input.setText("")
                self.text_input.setEnabled(False)
                self.use_this_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                self.clear_button.setEnabled(False)
                self.transfer_up_button.setEnabled(False)
                self.upload_button.setEnabled(True)
                self.return_button.setEnabled(True)
                self.left_list.itemSelectionChanged.connect(
                    self._left_list_item_toggled
                )
                self.right_list.itemSelectionChanged.connect(
                    self._right_list_item_toggled
                )
                self.checkbox.stateChanged.connect(self._checkbox_state_changed)
                self.text_input.textChanged.connect(self._text_input_changed)
                self.unselect_left_button.clicked.connect(
                    self._unselect_left_button_clicked
                )
                self.unselect_right_button.clicked.connect(
                    self._unselect_right_button_clicked
                )
                self.clear_button.clicked.connect(self._clear_button_clicked)
                self.transfer_up_button.clicked.connect(
                    self._transfer_up_button_clicked
                )
                self.delete_button.clicked.connect(self._delete_button_clicked)
                self.refresh_left_button.clicked.connect(
                    self._refresh_left_list
                )
                self.refresh_right_button.clicked.connect(
                    self._refresh_right_list
                )
                self.use_this_button.clicked.connect(
                    self._use_this_button_clicked
                )
                self._checkbox_state_changed()
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor initial_ui_setup error: {e}")
            raise e

    def _populate_left_list(self, ager_list: List[dict]) -> None:
        """Populate the left list with the game agers.

        Args:
            ager_list (List[dict]): The list of game agers.

        Raises:
            Exception: If there is an error populating the left list.
        """
        try:
            if not ager_list:
                self.left_list.addItem("No game agers available")
                return
            for ager in ager_list:
                self.left_list.addItem(ager["game_ager_recordname"])
            self.left_list.sortItems()
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _populate_left_list error: {e}")
            raise e

    def _populate_right_list(self, worker_list: List[dict]) -> None:
        """Populate the right list with the local workers.

        Args:
            worker_list (List[dict]): The list of local workers.

        Raises:
            Exception: If there is an error populating the right list.
        """
        try:
            if not worker_list:
                self.right_list.addItem("No local photos available")
                return

            for worker in worker_list:
                if "local_contract_photo_file" in worker:
                    file_path = worker["local_contract_photo_file"]
                elif "local_worker_photo_file" in worker:
                    file_path = worker["local_worker_photo_file"]
                elif isinstance(worker, str):
                    file_path = worker
                else:
                    sk_log.warning(f"Unexpected worker format: {worker}")
                    file_path = str(worker)

                self.right_list.addItem(file_path)
            self.right_list.sortItems()
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _populate_right_list error: {e}")
            raise e

    def _left_list_item_toggled(self) -> None:
        """Handle the case when the left list item is toggled.

        Raises:
            Exception: If there is an error handling the case
            when the left list item is toggled.
        """
        try:
            selected_item = self.left_list.currentItem()
            if selected_item:
                ager_name = selected_item.text()
                filename, fileonly = self._fetch_photo_from_cache_by_ager_name(
                    ager_name
                )
                if filename:
                    pixmap = QPixmap(filename)
                    scaled_pixmap = pixmap.scaled(
                        300,
                        300,
                        aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                        transformMode=Qt.TransformationMode.SmoothTransformation,
                    )
                    self.left_photo.setPixmap(scaled_pixmap)
                    self.left_photo.setFixedSize(300, 300)
                    self.left_name_label.setText(ager_name)
                    self.left_filename.setText(fileonly)
                    self.unselect_left_button.setEnabled(True)
                else:
                    self._left_side_reset()
            else:
                self._left_side_reset()
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _left_list_item_toggled error: {e}")
            raise e

    def _left_side_reset(self) -> None:
        """Reset the left side of the UI.

        Raises:
            Exception: If there is an error resetting the left side of the UI.
        """
        try:
            self.left_photo.setText("")
            self.left_name_label.setText("")
            self.left_filename.setText("")
            self.unselect_left_button.setEnabled(False)
            self.unselect_left_button.setText("Unselect Ager")
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _left_side_reset error: {e}")
            raise e

    def _right_side_reset(self) -> None:
        """Reset the right side of the UI.

        Raises:
            Exception: If there is an error resetting the right side of the UI.
        """
        try:
            self.right_photo.setText("")
            self.right_filename.setText("")
            self.unselect_right_button.setEnabled(False)
            self.use_this_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.unselect_right_button.setText("Unselect Photo")
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _right_side_reset error: {e}")
            raise e

    def _right_list_item_toggled(self) -> None:
        """Handle the case when the right list item is toggled.

        Raises:
            Exception: If there is an error handling the case
            when the right list item is toggled.
        """
        try:
            number_of_items_selected = self.right_list.selectedItems()
            if len(number_of_items_selected) == 1:
                self._one_item_right_list_item_selected()
            elif len(number_of_items_selected) > 1:
                self._multiple_right_list_items_selected(
                    number_of_items_selected
                )
            else:
                self._right_side_reset()
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEditor right_list_item_selected error: {e}"
            )
            raise e

    def _one_item_right_list_item_selected(self) -> None:
        """Handle the case when one item is selected in the right list.

        Raises:
            Exception: If there is an error handling the case when
            one item is selected in the right list.
        """
        try:
            selected_item = self.right_list.currentItem()
            if selected_item:
                filename, fileonly = self._fetch_photo_from_cache_by_filename(
                    selected_item.text()
                )
                pixmap = QPixmap(filename)
                scaled_pixmap = pixmap.scaled(
                    300,
                    300,
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                    transformMode=Qt.TransformationMode.SmoothTransformation,
                )
                self.right_photo.setPixmap(scaled_pixmap)
                self.right_photo.setFixedSize(300, 300)
                self.right_filename.setText(fileonly)
                self.unselect_right_button.setEnabled(True)
                self.unselect_right_button.setText(f"Unselect {fileonly}")
                self.use_this_button.setEnabled(True)
                self.delete_button.setEnabled(True)
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEditor _one_item_right_list_item_selected error: {e}"
            )
            raise e

    def _multiple_right_list_items_selected(
        self, number_of_items_selected: int
    ) -> None:
        """Handle the case when multiple items are selected in the right list.

        Raises:
            Exception: If there is an error handling the case when
            multiple items are selected in the right list.
        """
        try:
            self.unselect_right_button.setText("Unselect All")
            self.right_photo.setText(
                f"Multiple Selected [{len(number_of_items_selected)}]"
            )
            self.right_filename.setText(
                self._format_right_list_items_selected()
            )
            self.right_metadata.setText(
                f"[{len(number_of_items_selected)} items selected]"
            )
            self.use_this_button.setEnabled(False)
            self.delete_button.setEnabled(True)
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEditor _multiple_right_list_items_selected error: {e}"
            )
            raise e

    def _fetch_photo_from_cache_by_ager_name(
        self, ager_name: str
    ) -> Tuple[str, str]:
        """Fetch the photo from the cache by the ager name.

        Args:
            ager_name (str): The name of the ager.

        Returns:
            Tuple[str, str]: The filename and the fileonly.
        """
        try:
            sk_log.debug(f"Fetching photo for ager name: {ager_name}")
            with PhotoAgersEngine() as photo_agers_engine:
                root_path = photo_agers_engine.worker_photo_path
                sk_log.debug(f"Worker photo path: {root_path}")
                fl = photo_agers_engine.fetch_ager_photo_filename_from_cache(
                    ager_name
                )
                sk_log.debug(f"Retrieved filename: {fl}")
                if fl:
                    full_path = os.path.join(root_path, fl)
                    sk_log.debug(f"Full image path: {full_path}")
                    if os.path.exists(full_path):
                        sk_log.debug(f"File exists at: {full_path}")
                    else:
                        sk_log.warning(f"File doesn't exist at: {full_path}")
                    return full_path, fl
                else:
                    sk_log.debug(f"No filename found for ager: {ager_name}")
                return None, None
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEditor _fetch_photo_from_cache_by_ager_name error: {e}"
            )
            raise e

    def _fetch_photo_from_cache_by_filename(
        self, filename: str
    ) -> Tuple[str, str]:
        """Fetch the photo from the cache by the filename.

        Args:
            filename (str): The filename of the photo.

        Returns:
            Tuple[str, str]: The filename and the fileonly.
        """
        try:
            with PhotoAgersEngine() as photo_agers_engine:
                root_path = photo_agers_engine.worker_photo_path
                return os.path.join(root_path, filename), filename
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEditor _fetch_photo_from_cache_by_filename error: {e}"
            )
            raise e

    def _checkbox_state_changed(self) -> None:
        """Handle the case when the checkbox state is changed.

        Raises:
            Exception: If there is an error handling the case when the
            checkbox state is changed.
        """
        try:
            is_checked = self.checkbox.isChecked()
            self.text_input.setEnabled(is_checked)
            if not is_checked:
                self.text_input.setText("")
                self.clear_button.setEnabled(False)
                self.transfer_up_button.setEnabled(False)
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _checkbox_state_changed error: {e}")
            raise e

    def _text_input_changed(self) -> None:
        """Handle the case when the text input is changed.

        Raises:
            Exception: If there is an error handling the case when the
            text input is changed.
        """
        try:
            if self.text_input.text():
                self.clear_button.setEnabled(True)
                self.transfer_up_button.setEnabled(True)
            else:
                self.clear_button.setEnabled(False)
                self.transfer_up_button.setEnabled(False)
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _text_input_changed error: {e}")
            raise e

    def _clear_button_clicked(self) -> None:
        """Handle the case when the clear button is clicked.

        Raises:
            Exception: If there is an error handling the case when the
            clear button is clicked.
        """
        try:
            self.text_input.setText("")
            self.clear_button.setEnabled(False)
            self.transfer_up_button.setEnabled(False)
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _clear_button_clicked error: {e}")
            raise e

    def _transfer_up_button_clicked(self) -> None:
        """Handle the case when the transfer up button is clicked.

        Raises:
            Exception: If there is an error handling the case when the
            transfer up button is clicked.
        """
        try:
            with PhotoAgersEngine() as photo_agers_engine:
                filename_to_use = self.text_input.text()
                if filename_to_use == "" or filename_to_use is None:
                    self._clear_button_clicked()
                    return
                append_gif = self.checkbox.isChecked()
                photo_agers_engine.update_ager_photo_filename(
                    self.left_name_label.text(), filename_to_use, append_gif
                )
                self._left_list_item_toggled()
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEditor _transfer_up_button_clicked error: {e}"
            )
            raise e

    def _unselect_left_button_clicked(self) -> None:
        """Handle the case when the unselect left button is clicked.

        Raises:
            Exception: If there is an error handling the case when the
            unselect left button is clicked.
        """
        try:
            self.left_list.clearSelection()
            self._left_side_reset()
            if self.checkbox.isChecked():
                self.checkbox.setChecked(False)
            self.left_photo.clear()
            self.left_photo.setText("")
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEditor _unselect_left_button_clicked error: {e}"
            )
            raise e

    def _unselect_right_button_clicked(self) -> None:
        """Handle the case when the unselect right button is clicked.

        Raises:
            Exception: If there is an error handling the case when the
            unselect right button is clicked.
        """
        try:
            self.right_list.clearSelection()
            self._right_side_reset()
            self.right_photo.clear()
            self.right_photo.setText("")
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEditor _unselect_right_button_clicked error: {e}"
            )
            raise e

    def _text_length_check(self, text: str) -> str:
        """Format the text length.

        Args:
            text (str): The text to format.
        Returns:
            str: The formatted text.
        """
        try:
            truncate_length = self.MAX_LABEL_TEXT_LENGTH // 2
            if len(text) > self.MAX_LABEL_TEXT_LENGTH:
                return f"{text[:truncate_length]}...{text[-truncate_length:]}"
            return f"{text}"
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _text_length_check error: {e}")
            raise e

    def _format_right_list_items_selected(self) -> str:
        """Format the right list items selected.

        Returns:
            str: The formatted right list items selected.
        """
        try:
            items_selected = self.right_list.selectedItems()
            all_items_text = "".join(item.text() for item in items_selected)
            return self._text_length_check(f"[{all_items_text}]")
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEditor _format_right_list_items_selected error: {e}"
            )
            raise e

    def _delete_button_clicked(self) -> None:
        """Handle the case when the delete button is clicked.
        Deletes selected files from the right list and updates the UI.

        Raises:
            Exception: If there is an error handling the delete operation.
        """
        try:
            selected_items = self.right_list.selectedItems()
            if not selected_items:
                return
            item_count = len(selected_items)
            confirm_message = (
                f"Are you sure you want to delete {item_count}"
                f" file{'s' if item_count > 1 else ''}?"
            )
            confirm = QMessageBox.question(
                self,
                "Confirm Deletion",
                confirm_message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return
            with PhotoWorkerEngine() as photo_worker_engine:
                root_path = photo_worker_engine.worker_photo_path
                deleted_files = []
                failed_files = []
                for item in selected_items:
                    filename = item.text()
                    full_path = os.path.join(root_path, filename)
                    try:
                        if os.path.exists(full_path):
                            os.remove(full_path)
                            deleted_files.append(filename)
                        else:
                            failed_files.append(f"{filename} (file not found)")
                    except PermissionError:
                        failed_files.append(f"{filename} (permission denied)")
                    except Exception as e:
                        failed_files.append(f"{filename} ({str(e)})")
                if failed_files:
                    error_message = (
                        "Failed to delete the following files:\n"
                        + "\n".join(failed_files)
                    )
                    QMessageBox.warning(self, "Deletion Error", error_message)
                    sk_log.error(
                        f"PhotoAgersEditor delete error: {error_message}"
                    )
                if deleted_files:
                    for filename in deleted_files:
                        items = self.right_list.findItems(
                            filename, Qt.MatchFlag.MatchExactly
                        )
                        for item in items:
                            row = self.right_list.row(item)
                            self.right_list.takeItem(row)
                    self._right_side_reset()
                    self.right_metadata.setText("")
                    self.right_photo.clear()
                    self.right_photo.setText("")
                    success_message = (
                        f"Successfully deleted {len(deleted_files)} file"
                        f"{'s' if len(deleted_files) > 1 else ''}."
                    )
                    QMessageBox.information(
                        self, "Deletion Successful", success_message
                    )
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _delete_button_clicked error: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while deleting files: {str(e)}",
            )
            raise e

    def _refresh_left_list(self) -> None:
        """Refresh the left list with updated game ager data.

        Raises:
            Exception: If there is an error refreshing the left list.
        """
        try:
            self._unselect_left_button_clicked()
            self.left_list.clear()
            with PhotoAgersEngine() as photo_agers_engine:
                try:
                    photo_agers_engine.refresh_ager_photo_record_cache()
                    game_agers, _ = (
                        photo_agers_engine.fetch_ager_photo_record_lists()
                    )
                    self._populate_left_list(game_agers)
                except Exception as e:
                    sk_log.warning(f"Could not refresh game agers: {e}")
                    self._populate_left_list([])
            QMessageBox.information(
                self,
                "Refresh Complete",
                "Game ager list has been refreshed.",
            )
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _refresh_left_list error: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while refreshing the game ager list: {str(e)}",
            )
            raise e

    def _refresh_right_list(self) -> None:
        """Refresh the right list with updated local photo data.

        Raises:
            Exception: If there is an error refreshing the right list.
        """
        try:
            self._unselect_right_button_clicked()
            self.right_list.clear()
            with PhotoAgersEngine() as photo_agers_engine:
                try:
                    photo_agers_engine.refresh_ager_photo_record_cache()
                    _, local_workers = (
                        photo_agers_engine.fetch_ager_photo_record_lists()
                    )
                    self._populate_right_list(local_workers)
                except Exception as e:
                    sk_log.warning(f"Could not refresh full cache: {e}")
                    with PhotoWorkerEngine() as photo_worker_engine:
                        local_files = (
                            photo_worker_engine.fetch_worker_photos_from_dir()
                        )
                        local_workers = [
                            {"local_contract_photo_file": f}
                            for f in local_files
                        ]
                        self._populate_right_list(local_workers)
            QMessageBox.information(
                self,
                "Refresh Complete",
                "Local photo list has been refreshed.",
            )
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor _refresh_right_list error: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while refreshing the local photo list: {str(e)}",
            )
            raise e

    def _use_this_button_clicked(self) -> None:
        """Handle the case when the use this button is clicked.

        Raises:
            Exception: If there is an error handling the case when the
            use this button is clicked.
        """
        try:
            selected_item = self.left_list.currentItem()
            if selected_item:
                ager_name = selected_item.text()
            selected_item = self.right_list.currentItem()
            if selected_item:
                filepath = selected_item.text()
            with PhotoAgersEngine() as photo_agers_engine:
                photo_agers_engine.update_ager_photo_filename(
                    ager_name, filepath
                )
            self._left_list_item_toggled()
        except Exception as e:
            sk_log.error(
                f"PhotoAgersEditor _use_this_button_clicked error: {e}"
            )
            raise e
