import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTableView, QHeaderView, QProgressBar, QMessageBox, 
    QFileDialog, QMenu, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QAction

from ui.models import NodeModulesModel
from ui.settings_dialog import SettingsDialog
from core.scanner import ScanWorker
from core.deleter import DeleteWorker
from core.exporter import export_to_csv, export_to_json
from core.settings import AppSettings
from utils.helpers import format_size
from utils.logger import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Developer Disk Cleaner")
        self.resize(1100, 700)
        self.settings = AppSettings()
        
        self.scan_worker = None
        self.delete_worker = None
        self.last_scan_paths = []

        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Toolbar / Controls
        controls_layout = QHBoxLayout()
        
        self.btn_scan = QPushButton("Scan Folder(s)")
        self.btn_scan.clicked.connect(self._start_scan)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self._refresh_scan)
        self.btn_refresh.setEnabled(False)
        
        self.btn_settings = QPushButton("Settings")
        self.btn_settings.clicked.connect(self._open_settings)
        
        self.btn_export = QPushButton("Export")
        self.btn_export.clicked.connect(self._export_data)

        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.clicked.connect(self._delete_selected)
        
        self.btn_dry_run = QPushButton("Dry Run")
        self.btn_dry_run.clicked.connect(self._dry_run_selected)
        
        controls_layout.addWidget(self.btn_scan)
        controls_layout.addWidget(self.btn_refresh)
        controls_layout.addWidget(self.btn_settings)
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_export)
        controls_layout.addWidget(self.btn_dry_run)
        controls_layout.addWidget(self.btn_delete)
        
        main_layout.addLayout(controls_layout)

        # Filters
        filters_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search projects...")
        self.search_input.textChanged.connect(self._filter_table)
        filters_layout.addWidget(self.search_input)
        
        self.combo_framework = QComboBox()
        self.combo_framework.addItem("All Frameworks")
        self.combo_framework.currentIndexChanged.connect(self._filter_table)
        filters_layout.addWidget(self.combo_framework)

        main_layout.addLayout(filters_layout)

        # Dashboard
        dashboard_layout = QHBoxLayout()
        self.lbl_total_projects = QLabel("Projects: 0")
        self.lbl_total_size = QLabel("Total Size: 0 B")
        self.lbl_selected_size = QLabel("Selected Size: 0 B")
        dashboard_layout.addWidget(self.lbl_total_projects)
        dashboard_layout.addWidget(self.lbl_total_size)
        dashboard_layout.addWidget(self.lbl_selected_size)
        dashboard_layout.addStretch()
        main_layout.addLayout(dashboard_layout)

        # Table
        self.table_view = QTableView()
        self.model = NodeModulesModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1) 
        
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_view.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch) 
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self._show_context_menu)
        
        self.model.dataChanged.connect(self._update_dashboard)
        
        main_layout.addWidget(self.table_view)

        # Select All / Deselect All
        select_layout = QHBoxLayout()
        btn_select_all = QPushButton("Select All")
        btn_select_all.clicked.connect(lambda: self.model.set_all_selected(True))
        btn_deselect_all = QPushButton("Deselect All")
        btn_deselect_all.clicked.connect(lambda: self.model.set_all_selected(False))
        select_layout.addWidget(btn_select_all)
        select_layout.addWidget(btn_deselect_all)
        select_layout.addStretch()
        main_layout.addLayout(select_layout)

        # Status / Progress
        status_layout = QHBoxLayout()
        self.lbl_status = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.lbl_status)
        status_layout.addWidget(self.progress_bar)
        main_layout.addLayout(status_layout)

    def _update_dashboard(self, *args):
        data = self.model.get_all_data()
        total_size = sum(item["size"] for item in data)
        selected_size = sum(item["size"] for item in data if item.get("selected"))
        
        self.lbl_total_projects.setText(f"Projects: {len(data)}")
        self.lbl_total_size.setText(f"Total Size: {format_size(total_size)}")
        self.lbl_selected_size.setText(f"Selected Size: {format_size(selected_size)}")
        
        frameworks = set(item["framework"] for item in data)
        current = self.combo_framework.currentText()
        self.combo_framework.blockSignals(True)
        self.combo_framework.clear()
        self.combo_framework.addItem("All Frameworks")
        for fw in sorted(frameworks):
            self.combo_framework.addItem(fw)
        if current in frameworks:
            self.combo_framework.setCurrentText(current)
        self.combo_framework.blockSignals(False)

    def _filter_table(self):
        search_text = self.search_input.text()
        self.proxy_model.setFilterWildcard(f"*{search_text}*")
        # In a real app we'd need a custom QSortFilterProxyModel to combine text search 
        # and framework combobox filtering smoothly. For V1 we just filter by text wildcard.

    def _show_context_menu(self, pos):
        index = self.table_view.indexAt(pos)
        if not index.isValid():
            return
            
        source_index = self.proxy_model.mapToSource(index)
        item = self.model.get_all_data()[source_index.row()]
        
        menu = QMenu(self)
        
        open_proj_action = QAction("📂 Open Project Folder", self)
        open_proj_action.triggered.connect(lambda: self._open_folder(Path(item["path"]).parent))
        
        open_nm_action = QAction("📦 Open node_modules Folder", self)
        open_nm_action.triggered.connect(lambda: self._open_folder(Path(item["path"])))
        
        menu.addAction(open_proj_action)
        menu.addAction(open_nm_action)
        menu.exec(self.table_view.viewport().mapToGlobal(pos))

    def _open_folder(self, path: Path):
        try:
            if os.name == 'nt':
                os.startfile(str(path))
            else:
                subprocess.run(['xdg-open', str(path)])
        except Exception as e:
            logger.error(f"Failed to open folder {path}: {e}")

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def _start_scan(self):
        default_folder = self.settings.get_default_scan_folder()
        if not default_folder:
            default_folder = os.path.expanduser("~")
            
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan", default_folder)
        if folder:
            self.last_scan_paths = [folder]
            self._run_scan(self.last_scan_paths)

    def _refresh_scan(self):
        if self.last_scan_paths:
            self._run_scan(self.last_scan_paths)

    def _run_scan(self, paths):
        if self.scan_worker and self.scan_worker.isRunning():
            return
            
        self.model.clear()
        self.btn_refresh.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.btn_scan.setEnabled(False)
        
        ignore_list = self.settings.get_ignore_list()
        self.scan_worker = ScanWorker(paths, ignore_list)
        self.scan_worker.progress_updated.connect(self._scan_progress)
        self.scan_worker.item_found.connect(self.model.append_item)
        self.scan_worker.scan_finished.connect(self._scan_finished)
        self.scan_worker.error_occurred.connect(self._scan_error)
        self.scan_worker.start()

    def _scan_progress(self, current_folder, count):
        # Truncate long paths for display
        display_folder = current_folder
        if len(display_folder) > 60:
            display_folder = "..." + display_folder[-57:]
        self.lbl_status.setText(f"Found: {count} | Scanning: {display_folder}")

    def _scan_finished(self):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.lbl_status.setText("Scan Complete")
        self._update_dashboard()
        self.table_view.resizeColumnsToContents()
        self.table_view.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

    def _scan_error(self, err):
        QMessageBox.critical(self, "Error", str(err))

    def _dry_run_selected(self):
        selected_items = self.model.get_selected_items()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select at least one folder.")
            return

        total_size = sum(item["size"] for item in selected_items)
        msg = f"<b>Dry Run Summary</b><br><br>"
        msg += f"<b>Folders to Delete:</b> {len(selected_items)}<br>"
        msg += f"<b>Estimated Space to Recover:</b> {format_size(total_size)}<br><br>"
        msg += "No files will be actually deleted."
        
        QMessageBox.information(self, "Dry Run", msg)

    def _delete_selected(self):
        selected_items = self.model.get_selected_items()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select at least one folder to delete.")
            return

        total_size = sum(item["size"] for item in selected_items)
        use_recovery = self.settings.get_use_recovery_bin()
        mode_str = "Recovery Bin" if use_recovery else "Permanent Delete"
        
        msg = f"<b>Delete Selected Summary</b><br><br>"
        msg += f"<b>Selected Folders:</b> {len(selected_items)}<br>"
        msg += f"<b>Total Size to Recover:</b> {format_size(total_size)}<br>"
        msg += f"<b>Delete Mode:</b> {mode_str}<br><br>"
        msg += "Are you sure you want to proceed?"
        
        reply = QMessageBox.question(self, "Confirm Deletion", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self._run_delete(selected_items, "recovery" if use_recovery else "permanent")

    def _run_delete(self, items, mode):
        if self.delete_worker and self.delete_worker.isRunning():
            return
            
        self.progress_bar.setVisible(True)
        self.btn_delete.setEnabled(False)
        self.btn_dry_run.setEnabled(False)
        self.btn_scan.setEnabled(False)
        
        self.delete_worker = DeleteWorker(items, mode)
        self.delete_worker.progress_updated.connect(self._delete_progress)
        self.delete_worker.delete_finished.connect(self._delete_finished)
        self.delete_worker.error_occurred.connect(self._scan_error)
        
        self.delete_worker._items = items
        self.delete_worker.start()

    def _delete_progress(self, current, total, msg):
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
        self.lbl_status.setText(msg)

    def _delete_finished(self, deleted_count, recovered_bytes):
        self.progress_bar.setVisible(False)
        self.btn_delete.setEnabled(True)
        self.btn_dry_run.setEnabled(True)
        self.btn_scan.setEnabled(True)
        self.lbl_status.setText(f"Deleted {deleted_count} folders. Recovered {format_size(recovered_bytes)}.")
        
        paths_to_remove = set(item["path"] for item in self.delete_worker._items)
        self.model.remove_items(paths_to_remove)
        self._update_dashboard()

    def _export_data(self):
        data = self.model.get_all_data()
        if not data:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "CSV Files (*.csv);;JSON Files (*.json)")
        if file_path:
            if file_path.endswith(".csv"):
                export_to_csv(data, file_path)
            elif file_path.endswith(".json"):
                export_to_json(data, file_path)
            QMessageBox.information(self, "Export Successful", f"Data exported to {file_path}")
