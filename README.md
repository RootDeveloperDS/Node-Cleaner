# 🧹 Developer Disk Cleaner

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-GUI-green.svg)](https://doc.qt.io/qtforpython/)

**Developer Disk Cleaner** is a lightning-fast, production-ready Windows desktop utility designed specifically for developers to safely manage, scan, and clean up massive `node_modules` folders scattered across their hard drives.

If you're tired of running out of disk space because of forgotten JavaScript projects, this tool is for you!

⭐ **If you find this project useful, please consider giving it a star on GitHub and following me for more awesome tools!** ⭐

---

## ✨ Features

- 🚀 **Lightning Fast Scanning**: Scans entire drives or specific folders in the background using multithreading (`QThread`), ensuring the UI never freezes.
- 🧠 **Smart Project Detection**: Automatically detects the framework (React, Next.js, Vue, Angular, Vite, etc.) and package manager (npm, yarn, pnpm, bun) of your projects.
- 🎨 **Modern Dark UI**: A beautiful, responsive, and distraction-free dark theme built with PySide6.
- 🛡️ **Recovery Bin & Dry Run**: 
  - **Dry Run**: See exactly how much space you'll recover before deleting anything.
  - **Recovery Bin**: Safely move `node_modules` to a temporary recycle bin instead of permanently deleting them, ensuring zero data loss.
- 📊 **Real-time Dashboard**: Instantly view the total number of projects, `node_modules` found, and the total space consumed.
- 🔍 **Advanced Filtering & Sorting**: Instantly search for specific projects or filter by frameworks.
- 📂 **Quick Actions**: Right-click any project to instantly open the project directory or the `node_modules` folder in your file explorer.
- 📥 **Export to CSV/JSON**: Easily export your scan results for record-keeping.

---

## 🛠️ Installation

### Prerequisites
- **Python 3.10** or higher installed on your system.

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/developer-disk-cleaner.git
   cd developer-disk-cleaner
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   You can run the application directly via Python:
   ```bash
   python main.py
   ```
   *Alternatively, if you are on Windows, you can simply double-click the `start.bat` file to launch the application instantly.*

---

## 📖 How to Use

1. **Scan your drive**: Click **Scan Folder(s)** and select your root development directory (e.g., `C:\Users\YourName\Documents\Projects`).
2. **Review your projects**: The tool will list all found `node_modules`, along with the project name, framework, and size.
3. **Select what to delete**: Use the checkboxes to select the old, inactive projects you want to clean up.
4. **Dry Run (Optional)**: Click **Dry Run** to verify how much disk space will be freed.
5. **Delete Selected**: Click **Delete Selected**. By default, folders are moved to a safe Recovery Bin. You can change this behavior in the **Settings**.

---

## 🏗️ Architecture

This project is built using a clean, modular Object-Oriented architecture using PySide6 (Qt for Python).

```text
DeveloperDiskCleaner/
├── main.py                     # Application entry point
├── start.bat                   # Windows quick-start script
├── requirements.txt            # Dependencies
├── core/                       # Core business logic
│   ├── scanner.py              # Background scanning (QThread)
│   ├── deleter.py              # Deletion logic (Dry Run, Permanent, Recovery Bin)
│   ├── detector.py             # Project detection heuristics
│   ├── exporter.py             # CSV/JSON data export
│   └── settings.py             # QSettings wrapper
├── ui/                         # GUI components
│   ├── main_window.py          # Main UI layout and interactions
│   ├── models.py               # Custom QAbstractTableModel for extreme performance
│   └── settings_dialog.py      # Preferences dialog
├── utils/                      # Helper utilities
│   ├── helpers.py              # Formatting functions
│   └── logger.py               # Application logging setup
└── resources/styles/           # QSS stylesheets (Dark Mode)
```

---

## 🤝 Contributing

Contributions are always welcome! Whether it's a bug report, a new feature suggestion, or a pull request, your input is highly valued.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

### ❤️ Show your support

If this tool saved your hard drive from overflowing, **please hit the ⭐ button at the top right of this page!** 
Follow me on GitHub to stay updated on my latest open-source projects!
