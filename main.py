

import sys
import os

# Ensure project root is always on the Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create required directories
for d in ("baselines", "logs"):
    os.makedirs(d, exist_ok=True)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore    import Qt
from ui.main_window  import MainWindow


def main():
    # Enable High DPI support
    app = QApplication(sys.argv)
    app.setApplicationName("FileGuard — File Integrity Checker")
    app.setOrganizationName("FileGuard")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
