import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.settings import AppSettings

def main():
    app = QApplication(sys.argv)
    
    # Check Theme Setting
    settings = AppSettings()
    theme = settings.get_theme()
    
    # Load QSS
    style_path = Path(__file__).parent / "resources" / "styles" / f"{theme}.qss"
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
            
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
