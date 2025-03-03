import os
from typing import List, Tuple

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox

from ui.photo_editor.base_photo_editors.worker_photo_base import WorkerPhotoBase
from modules.photo_editor.photo_worker_engine import PhotoWorkerEngine

from utils.sk_logger import sk_log


class PhotoWorkerEditor(WorkerPhotoBase):

    MAX_LABEL_TEXT_LENGTH = 40

    def __init__(self, parent=None) -> None:
        try:
            super().__init__(editor_type="worker", parent=parent)

            # Try to initialize the cache if it's empty
            with PhotoWorkerEngine() as photo_worker_engine:
                try:
                    # Check if cache exists and has data
                    photo_worker_engine.worker_photo_cache_init(skip_check=True)
                except Exception as cache_error:
                    sk_log.warning(f"Cache initialization error: {cache_error}")

            # Now proceed with UI setup
            self.initial_ui_setup()
        except Exception as e:
            sk_log.error(f"PhotoWorkerEditor __init__ error: {e}")
            raise e

    def initial_ui_setup(self) -> None:
        """Initialize the UI setup.

        Raises:
            Exception: If there is an error initializing the UI setup.
        """
        try:
            with PhotoWorkerEngine() as photo_worker_engine:
                try:
                    # Try to get both game and local workers from cache
                    game_workers, local_workers = (
                        photo_worker_engine.fetch_worker_photo_cache_lists()
                    )
                except Exception as e:
                    # If cache is empty or corrupted, try to rebuild it
                    sk_log.warning(
                        f"Cache fetch error, attempting rebuild: {e}"
                    )
                    photo_worker_engine.refresh_worker_photo_cache()

                    try:
                        # Try again after refresh
                        game_workers, local_workers = (
                            photo_worker_engine.fetch_worker_photo_cache_lists()
                        )
                    except Exception as refresh_error:
                        # If still failing, use empty lists but don't crash
                        sk_log.error(f"Cache rebuild failed: {refresh_error}")
                        game_workers = []
                        local_workers = []

                        # Try to at least get local files
                        try:
                            local_files = (
                                photo_worker_engine._fetch_worker_photos_from_dir()
                            )
                            local_workers = [
                                {"local_worker_photo_file": f}
                                for f in local_files
                            ]
                        except Exception as local_error:
                            sk_log.error(
                                f"Local files fetch failed: {local_error}"
                            )

                # Populate lists with whatever data we have
                self._populate_left_list(game_workers)
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
                # Connect unselect buttons to their respective methods
                self.unselect_left_button.clicked.connect(
                    self._unselect_left_button_clicked
                )
                self.unselect_right_button.clicked.connect(
                    self._unselect_right_button_clicked
                )
                # Connect other buttons
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
                # Initialize UI state based on checkbox (which is unchecked by default)
                self._checkbox_state_changed()
        except Exception as e:
            sk_log.error(f"PhotoWorkerEditor initial_ui_setup error: {e}")
            raise e

    def _populate_left_list(self, worker_list: List[dict]) -> None:
        """Populate the left list with the game worker names.

        Args:
            worker_list (List[dict]): The list of game worker names.

        Raises:
            Exception: If there is an error populating the left list.
        """
        try:
            if not worker_list:
                # Add a placeholder item if the list is empty
                self.left_list.addItem("No game workers available")
                return

            for worker in worker_list:
                self.left_list.addItem(worker["game_worker_name"])
            self.left_list.sortItems()
        except Exception as e:
            sk_log.error(f"PhotoWorkerEditor populate_left_list error: {e}")
            raise e

    def _populate_right_list(self, worker_list: List[dict]) -> None:
        """Populate the right list with the local worker photo files.

        Args:
            worker_list (List[dict]): The list of worker photo files.

        Raises:
            Exception: If there is an error populating the right list.
        """
        try:
            if not worker_list:
                # Add a placeholder item if the list is empty
                self.right_list.addItem("No local photos available")
                return

            for filename in worker_list:
                self.right_list.addItem(filename["local_worker_photo_file"])
            self.right_list.sortItems()
        except Exception as e:
            sk_log.error(f"PhotoWorkerEditor populate_right_list error: {e}")
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
                worker_name = selected_item.text()
                filename, fileonly = (
                    self._fetch_photo_from_cache_by_worker_name(worker_name)
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
                    self.left_name_label.setText(worker_name)
                    self.left_filename.setText(fileonly)
                    self.unselect_left_button.setEnabled(True)
                else:
                    self._left_side_reset()
            else:
                self._left_side_reset()
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEditor left_list_item_selected error: {e}"
            )
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
            self.unselect_left_button.setText("Unselect Worker")
        except Exception as e:
            sk_log.error(f"PhotoWorkerEditor _left_side_reset error: {e}")
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
            sk_log.error(f"PhotoWorkerEditor _right_side_reset error: {e}")
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
                f"PhotoWorkerEditor right_list_item_selected error: {e}"
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
                f"PhotoWorkerEditor _one_item_right_list_item_selected error: {e}"
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
                f"PhotoWorkerEditor _multiple_right_list_items_selected error: {e}"
            )
            raise e

    def _fetch_photo_from_cache_by_worker_name(
        self, worker_name: str
    ) -> Tuple[str, str]:
        """Fetch the photo from the cache by the worker name.

        Args:
            worker_name (str): The name of the worker.

        Returns:
            Tuple[str, str]: The filename and the fileonly.
        """
        try:
            with PhotoWorkerEngine() as photo_worker_engine:
                root_path = photo_worker_engine.worker_photo_path
                filename = photo_worker_engine.fetch_worker_filename_from_cache(
                    worker_name
                )
                if filename:
                    return os.path.join(root_path, filename), filename
                return None, None
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEditor _fetch_photo_from_cache error: {e}"
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
            with PhotoWorkerEngine() as photo_worker_engine:
                root_path = photo_worker_engine.worker_photo_path
                return os.path.join(root_path, filename), filename
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEditor _fetch_photo_from_cache_by_filename error: {e}"
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

            # Clear text input if checkbox is unchecked
            if not is_checked:
                self.text_input.setText("")
                self.clear_button.setEnabled(False)
                self.transfer_up_button.setEnabled(False)

        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEditor _checkbox_state_changed error: {e}"
            )
            raise e

    def _text_input_changed(self) -> None:
        """Handle the case when the text input is changed.

        Raises:
            Exception: If there is an error handling the case when
            the text input is changed.
        """
        try:
            if self.text_input.text():
                self.clear_button.setEnabled(True)
                self.transfer_up_button.setEnabled(True)
            else:
                self.clear_button.setEnabled(False)
                self.transfer_up_button.setEnabled(False)
        except Exception as e:
            sk_log.error(f"PhotoWorkerEditor _text_input_changed error: {e}")
            raise e

    def _clear_button_clicked(self) -> None:
        """Handle the case when the clear button is clicked.

        Raises:
            Exception: If there is an error handling the case when
            the clear button is clicked.
        """
        try:
            self.text_input.setText("")
            self.clear_button.setEnabled(False)
            self.transfer_up_button.setEnabled(False)
        except Exception as e:
            sk_log.error(f"PhotoWorkerEditor _clear_button_clicked error: {e}")
            raise e

    def _transfer_up_button_clicked(self) -> None:
        """Handle the case when the transfer up button is clicked.

        Raises:
            Exception: If there is an error handling the case when the
            transfer up button is clicked.
        """
        try:
            with PhotoWorkerEngine() as photo_worker_engine:
                filename_to_use = self.text_input.text()
                if filename_to_use == "" or filename_to_use is None:
                    self._clear_button_clicked()
                    return
                photo_worker_engine.update_worker_photo_filename(
                    self.left_name_label.text(), filename_to_use
                )
                # Refresh the left list item display
                self._left_list_item_toggled()
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEditor _transfer_up_button_clicked error: {e}"
            )
            raise e

    def _unselect_left_button_clicked(self) -> None:
        """Handle the case when the unselect left button is clicked.

        Raises:
            Exception: If there is an error handling the case
            when the unselect left button is clicked.
        """
        try:
            self.left_list.clearSelection()
            self._left_side_reset()
            # Also uncheck the checkbox if it's checked
            if self.checkbox.isChecked():
                self.checkbox.setChecked(False)
            # Clear the photo display
            self.left_photo.clear()
            self.left_photo.setText("")
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEditor _unselect_left_button_clicked error: {e}"
            )
            raise e

    def _unselect_right_button_clicked(self) -> None:
        """Handle the case when the unselect right button is clicked.

        Raises:
            Exception: If there is an error handling the case
            when the unselect right button is clicked.
        """
        try:
            self.right_list.clearSelection()
            self._right_side_reset()
            self.right_metadata.setText("")
            # Clear the photo display
            self.right_photo.clear()
            self.right_photo.setText("")
        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEditor _unselect_right_button_clicked error: {e}"
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
            sk_log.error(f"PhotoWorkerEditor _text_length_check error: {e}")
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
                f"PhotoWorkerEditor _format_right_list_items_selected error: {e}"
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
                        f"PhotoWorkerEditor delete error: {error_message}"
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
            sk_log.error(f"PhotoWorkerEditor _delete_button_clicked error: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while deleting files: {str(e)}",
            )
            raise e

    def _refresh_left_list(self) -> None:
        """Refresh the left list with updated game worker data.

        Raises:
            Exception: If there is an error refreshing the left list.
        """
        try:
            self._unselect_left_button_clicked()
            self.left_list.clear()
            with PhotoWorkerEngine() as photo_worker_engine:
                try:
                    photo_worker_engine.refresh_worker_photo_cache()
                    game_workers, _ = (
                        photo_worker_engine.fetch_worker_photo_cache_lists()
                    )
                    self._populate_left_list(game_workers)
                except Exception as e:
                    sk_log.warning(f"Could not refresh game workers: {e}")
                    self._populate_left_list([])
            QMessageBox.information(
                self,
                "Refresh Complete",
                "Game worker list has been refreshed.",
            )
        except Exception as e:
            sk_log.error(f"PhotoWorkerEditor _refresh_left_list error: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while refreshing game worker list: {str(e)}",
            )
            raise e

    def _refresh_right_list(self) -> None:
        """Refresh the right list with updated local worker photo files.

        Raises:
            Exception: If there is an error refreshing the right list.
        """
        try:
            self._unselect_right_button_clicked()
            self.right_list.clear()
            with PhotoWorkerEngine() as photo_worker_engine:
                try:
                    photo_worker_engine.refresh_worker_photo_cache()
                    _, local_workers = (
                        photo_worker_engine.fetch_worker_photo_cache_lists()
                    )
                    self._populate_right_list(local_workers)
                except Exception as e:
                    sk_log.warning(f"Could not refresh full cache: {e}")
                    local_files = (
                        photo_worker_engine._fetch_worker_photos_from_dir()
                    )
                    local_workers = [
                        {"local_worker_photo_file": f} for f in local_files
                    ]
                    self._populate_right_list(local_workers)
            QMessageBox.information(
                self,
                "Refresh Complete",
                "Local photo list has been refreshed.",
            )
        except Exception as e:
            sk_log.error(f"PhotoWorkerEditor _refresh_right_list error: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while refreshing local photo list: {str(e)}",
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
                worker_name = selected_item.text()
                _, fileonly_left = self._fetch_photo_from_cache_by_worker_name(
                    worker_name
                )
            selected_item = self.right_list.currentItem()
            if selected_item:
                fileonly_right = selected_item.text()
            with PhotoWorkerEngine() as photo_worker_engine:
                photo_worker_engine.update_worker_photo_filename(
                    worker_name, fileonly_right
                )
            self._left_list_item_toggled()

        except Exception as e:
            sk_log.error(
                f"PhotoWorkerEditor _use_this_button_clicked error: {e}"
            )
            raise e
