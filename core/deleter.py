import os
import shutil
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QThread, Signal
from utils.logger import logger

class DeleteWorker(QThread):
    progress_updated = Signal(int, int, str)  # current, total, message
    delete_finished = Signal(int, int) # deleted_count, recovered_bytes
    error_occurred = Signal(str)

    def __init__(self, items_to_delete: list, mode: str):
        """
        :param items_to_delete: list of dicts with 'path', 'size', 'project_name'
        :param mode: 'permanent' or 'recovery'
        """
        super().__init__()
        self.items_to_delete = items_to_delete
        self.mode = mode
        self._is_running = True

    def run(self):
        deleted_count = 0
        recovered_bytes = 0
        total = len(self.items_to_delete)

        recovery_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "DeveloperDiskCleaner" / "RecycleBin"
        if self.mode == "recovery":
            try:
                recovery_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.error_occurred.emit(f"Failed to create recovery bin: {e}")
                return

        for i, item in enumerate(self.items_to_delete):
            if not self._is_running:
                break
            
            path_str = item["path"]
            project_name = item["project_name"]
            size = item.get("size", 0)

            self.progress_updated.emit(i + 1, total, f"Processing {project_name}...")

            try:
                if self.mode == "permanent":
                    shutil.rmtree(path_str, ignore_errors=True)
                    # Verify it's gone
                    if not os.path.exists(path_str):
                        deleted_count += 1
                        recovered_bytes += size
                    else:
                        logger.error(f"Failed to permanently delete {path_str}")

                elif self.mode == "recovery":
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    dest_name = f"{project_name}__node_modules__{timestamp}"
                    dest_path = recovery_dir / dest_name
                    
                    shutil.move(path_str, str(dest_path))
                    deleted_count += 1
                    recovered_bytes += size

            except Exception as e:
                logger.error(f"Error processing deletion for {path_str}: {e}")
                
        self.delete_finished.emit(deleted_count, recovered_bytes)

    def stop(self):
        self._is_running = False
