import os
from pathlib import Path
from PySide6.QtCore import QThread, Signal
from core.detector import detect_project_info, calculate_status
from utils.logger import logger

def get_directory_size(path: str) -> int:
    """Calculate the total size of a directory in bytes."""
    total_size = 0
    try:
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except Exception as e:
        logger.debug(f"Error calculating size for {path}: {e}")
    return total_size

class ScanWorker(QThread):
    # Signals
    progress_updated = Signal(str, int)  # current_folder, count_found
    item_found = Signal(dict)
    scan_finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, root_paths: list, ignore_list: list = None):
        super().__init__()
        self.root_paths = root_paths
        self.ignore_list = ignore_list or []
        self._is_running = True
        self.found_count = 0

    def run(self):
        try:
            for root_path in self.root_paths:
                if not self._is_running:
                    break
                self._scan_directory(Path(root_path))
        except Exception as e:
            self.error_occurred.emit(str(e))
            logger.error(f"Scan error: {e}")
        finally:
            self.scan_finished.emit()

    def _scan_directory(self, current_path: Path):
        if not self._is_running:
            return

        try:
            # Check ignore list
            if any(ignore_str in str(current_path) for ignore_str in self.ignore_list):
                return

            self.progress_updated.emit(str(current_path), self.found_count)

            if current_path.name == "node_modules" and current_path.is_dir():
                # Found node_modules
                self.found_count += 1
                size = get_directory_size(str(current_path))
                info = detect_project_info(str(current_path))
                status = calculate_status(info["last_modified"], info["has_git"])

                item_data = {
                    "path": str(current_path),
                    "project_name": info["project_name"],
                    "framework": info["framework"],
                    "package_manager": info["package_manager"],
                    "size": size,
                    "last_modified": info["last_modified"],
                    "status": status,
                    "has_git": info["has_git"]
                }
                self.item_found.emit(item_data)
                
                # Do not recurse inside node_modules
                return

            # If not node_modules, recurse into subdirectories
            for child in current_path.iterdir():
                if not self._is_running:
                    break
                if child.is_dir() and not child.is_symlink():
                    self._scan_directory(child)

        except PermissionError:
            pass  # Expected for some system folders
        except Exception as e:
            logger.debug(f"Error scanning {current_path}: {e}")

    def stop(self):
        self._is_running = False
