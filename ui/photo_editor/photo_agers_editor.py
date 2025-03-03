from ui.photo_editor.base_photo_editors.worker_photo_base import WorkerPhotoBase
from utils.sk_logger import sk_log


class PhotoAgersEditor(WorkerPhotoBase):
    def __init__(self, parent=None) -> None:
        try:
            super().__init__(editor_type="Ager", parent=parent)
            # self.populate_left_list()
        except Exception as e:
            sk_log.error(f"PhotoAgersEditor __init__ error: {e}")
            raise e

    # this is an example of how to populate the left list
    # def populate_left_list(self) -> None:
    #     try:
    #         for i in range(1, 6):
    #             self.left_list.addItem(str(i))
    #     except Exception as e:
    #         sk_log.error(f"PhotoWorkerEditor populate_left_list error: {e}")
    #         raise e
