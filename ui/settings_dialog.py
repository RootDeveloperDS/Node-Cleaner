from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFileDialog, QListWidget, QComboBox
)
from core.settings import AppSettings

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 400)
        self.settings = AppSettings()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Default Scan Folder
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self._browse_folder)
        folder_layout.addWidget(QLabel("Default Scan Folder:"))
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(btn_browse)
        layout.addLayout(folder_layout)

        # Recovery Bin
        self.chk_recovery = QCheckBox("Use Recovery Bin (Move instead of permanently delete)")
        layout.addWidget(self.chk_recovery)

        # Ignore List
        layout.addWidget(QLabel("Ignore List (Paths containing these strings will be skipped):"))
        self.list_ignore = QListWidget()
        layout.addWidget(self.list_ignore)
        
        ignore_btn_layout = QHBoxLayout()
        self.input_ignore = QLineEdit()
        self.input_ignore.setPlaceholderText("e.g. .cache")
        btn_add_ignore = QPushButton("Add")
        btn_add_ignore.clicked.connect(self._add_ignore)
        btn_remove_ignore = QPushButton("Remove Selected")
        btn_remove_ignore.clicked.connect(self._remove_ignore)
        ignore_btn_layout.addWidget(self.input_ignore)
        ignore_btn_layout.addWidget(btn_add_ignore)
        ignore_btn_layout.addWidget(btn_remove_ignore)
        layout.addLayout(ignore_btn_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self._save_settings)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _load_settings(self):
        self.folder_input.setText(self.settings.get_default_scan_folder())
        self.chk_recovery.setChecked(self.settings.get_use_recovery_bin())
        
        self.list_ignore.clear()
        for item in self.settings.get_ignore_list():
            self.list_ignore.addItem(item)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Default Scan Folder")
        if folder:
            self.folder_input.setText(folder)

    def _add_ignore(self):
        text = self.input_ignore.text().strip()
        if text:
            # Check if exists
            items = [self.list_ignore.item(i).text() for i in range(self.list_ignore.count())]
            if text not in items:
                self.list_ignore.addItem(text)
            self.input_ignore.clear()

    def _remove_ignore(self):
        for item in self.list_ignore.selectedItems():
            self.list_ignore.takeItem(self.list_ignore.row(item))

    def _save_settings(self):
        self.settings.set_default_scan_folder(self.folder_input.text())
        self.settings.set_use_recovery_bin(self.chk_recovery.isChecked())
        
        ignore_list = [self.list_ignore.item(i).text() for i in range(self.list_ignore.count())]
        self.settings.set_ignore_list(ignore_list)
        
        self.accept()
