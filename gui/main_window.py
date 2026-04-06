from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QWidget, QFrame,
    QLabel, QMessageBox, QComboBox, QProgressBar, QInputDialog
)
from PySide6.QtGui import QIcon
from pathlib import Path
import os
import json

from core.paths import get_all_worlds
from core.backup import restore_backup
from gui.worker import BackupWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PZ Save Manager by NealNeil")
        self.resize(450, 250)

        # --- Set window icon reliably ---
        icon_path = Path(__file__).parent.parent / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            print(f"Warning: icon not found at {icon_path}")

        # Professional Disclaimer
        QMessageBox.warning(
            self,
            "Caution",
            "This software is provided 'AS IS', without warranty of any kind, express or implied.\n\n"
            "While designed to assist with Project Zomboid save management, it is currently in "
            "development. Users should be aware that save corruption is possible.\n\n"
            "The developer (NealNeil) shall not be held liable for any damages or data loss "
            "resulting from the use of this software."
        )

        # Worlds and backup folder
        self.worlds = get_all_worlds()
        self.manual_dir = Path("backups/manual")
        self.manual_dir.mkdir(parents=True, exist_ok=True)
        self.worker = None

        # --- Widgets ---
        self.world_select = QComboBox()
        for w in self.worlds:
            self.world_select.addItem(f"{w['mode']} - {w['name']}")
        self.world_select.currentIndexChanged.connect(self.refresh_backup_list)

        self.save_btn = QPushButton("Create Manual Save")
        self.save_btn.clicked.connect(self.manual_save)

        self.backup_dropdown = QComboBox()

        self.restore_btn = QPushButton("Restore Selected Backup")
        self.restore_btn.clicked.connect(self.restore_selected)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.open_folder_btn = QPushButton("Open Backup Folder")
        self.open_folder_btn.clicked.connect(self.open_backup_folder)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()

        # --- Layout ---
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Step 1: Select World"))
        layout.addWidget(self.world_select)
        layout.addWidget(self.save_btn)
        layout.addSpacing(10)
        layout.addWidget(QLabel("Step 2: Select Backup to Restore"))
        layout.addWidget(self.backup_dropdown)
        layout.addWidget(self.restore_btn)
        layout.addWidget(self.progress)
        layout.addSpacing(10)
        layout.addWidget(self.line)
        layout.addSpacing(5)
        layout.addWidget(self.open_folder_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.refresh_backup_list()

    # -------------------------
    # Refresh backup dropdown
    # -------------------------
    def refresh_backup_list(self):
        self.backup_dropdown.clear()
        index = self.world_select.currentIndex()
        if index < 0:
            return
        world = self.worlds[index]

        for zip_file in sorted(self.manual_dir.glob("*.zip"), reverse=True):
            meta_file = zip_file.with_suffix(".json")
            if meta_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)
                    if meta.get("world") == world["name"]:
                        label = meta.get("label", "")
                        timestamp = meta.get("timestamp", "")
                        display_text = f"{label} ({timestamp})" if label else f"{zip_file.name} ({timestamp})"
                        self.backup_dropdown.addItem(display_text, zip_file)

    # -------------------------
    # Restore backup
    # -------------------------
    def restore_selected(self):
        zip_path = self.backup_dropdown.currentData()
        if not zip_path:
            QMessageBox.warning(self, "No Selection", "Please select a backup from the list.")
            return

        index = self.world_select.currentIndex()
        world = self.worlds[index]

        confirm = QMessageBox.question(
            self,
            "Confirm Restore",
            f"Restore '{zip_path.name}'?\n\nThis will overwrite your current save!",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            self.progress.show()
            restore_backup(zip_path, world["path"])
            self.progress.hide()
            QMessageBox.information(self, "Success", "Backup restored successfully!")
        except Exception as e:
            self.progress.hide()
            QMessageBox.critical(self, "Error", f"Failed to restore: {str(e)}")

    # -------------------------
    # Manual save
    # -------------------------
    def manual_save(self):
        index = self.world_select.currentIndex()
        world = self.worlds[index]

        label, ok = QInputDialog.getText(self, "Save Name", "Give this backup a name:")
        if not ok:
            return

        self.progress.show()
        self.save_btn.setEnabled(False)

        self.worker = BackupWorker(world["path"], self.manual_dir, "manual_slot", label=label)
        self.worker.finished.connect(self.on_backup_done)
        self.worker.error.connect(self.on_backup_error)
        self.worker.start()

    def on_backup_done(self):
        self.progress.hide()
        self.save_btn.setEnabled(True)
        QMessageBox.information(self, "Success", "Save created!")
        self.refresh_backup_list()

    def on_backup_error(self, msg):
        self.progress.hide()
        self.save_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", msg)

    # -------------------------
    # Open backup folder
    # -------------------------
    def open_backup_folder(self):
        os.startfile(self.manual_dir.resolve())
