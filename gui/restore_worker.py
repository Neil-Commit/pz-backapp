from PySide6.QtCore import QThread, Signal
from core.backup import restore_backup
import shutil

class RestoreWorker(QThread):
    finished = Signal()
    error = Signal(str)

    def __init__(self, zip_path, target_dir):
        super().__init__()
        self.zip_path = zip_path
        self.target_dir = target_dir

    def run(self):
        try:
            restore_backup(self.zip_path, self.target_dir)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
