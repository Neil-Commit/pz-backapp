import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import json

def create_backup(source_dir: Path, dest_dir: Path, slot_name: str, label: str = ""):
    """
    Create a backup ZIP of a world.

    slot_name: e.g., "slot_1"
    label: optional descriptive name like "Before Louisville run"
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_path = dest_dir / f"{slot_name}_{timestamp}.zip"
    meta_path = dest_dir / f"{slot_name}_{timestamp}.json"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for p in source_dir.rglob("*"):
            zipf.write(p, p.relative_to(source_dir))

    meta = {
        "slot": slot_name,
        "world": source_dir.name,
        "timestamp": timestamp,
        "label": label,
        "size": zip_path.stat().st_size
    }

    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=4)

def restore_backup(zip_path: Path, target_dir: Path):
    """
    Restore a backup to the original world folder.
    WARNING: This deletes the current save folder first.
    """
    if target_dir.exists():
        shutil.rmtree(target_dir)

    target_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zipf:
        zipf.extractall(target_dir)
