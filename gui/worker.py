from PySide6.QtCore import QThread, Signal
from core.backup import create_backup

class BackupWorker(QThread):
    finished = Signal()
    error = Signal(str)

    def __init__(self, source_dir, dest_dir, slot, label=""):
        super().__init__()
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.slot = slot
        self.label = label

    def run(self):
        try:
            create_backup(self.source_dir, self.dest_dir, self.slot, self.label)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
