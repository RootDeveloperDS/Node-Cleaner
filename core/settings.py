from PySide6.QtCore import QSettings

class AppSettings:
    def __init__(self):
        self.settings = QSettings("DeveloperTools", "DiskCleaner")

    def get_default_scan_folder(self) -> str:
        return self.settings.value("default_scan_folder", "")

    def set_default_scan_folder(self, folder: str):
        self.settings.setValue("default_scan_folder", folder)

    def get_ignore_list(self) -> list:
        val = self.settings.value("ignore_list", [])
        if isinstance(val, str):
            return [val] if val else []
        return val

    def set_ignore_list(self, ignore_list: list):
        self.settings.setValue("ignore_list", ignore_list)

    def get_use_recovery_bin(self) -> bool:
        val = self.settings.value("use_recovery_bin", "true")
        return str(val).lower() == "true"

    def set_use_recovery_bin(self, use: bool):
        self.settings.setValue("use_recovery_bin", use)

    def get_theme(self) -> str:
        return self.settings.value("theme", "dark")

    def set_theme(self, theme: str):
        self.settings.setValue("theme", theme)
