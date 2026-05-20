"""
main_window.py — QMainWindow with sidebar navigation and stacked pages.
"""

from PyQt6.QtCore    import Qt, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget,
    QLabel, QStatusBar, QFrame,
)
from PyQt6.QtGui import QIcon, QFont

from ui.verify_tab    import VerifyTab
from ui.baseline_tab  import BaselineTab
from ui.compare_tab   import CompareTab
from ui.avalanche_tab import AvalancheTab
from ui.logs_tab      import LogsTab
from ui.theme         import DARK_THEME, MANTLE, MAUVE, SURFACE0, SUBTEXT, TEXT


NAV_ITEMS = [
    ("🔍", "Scan & Verify",    "Monitor files and detect tampering"),
    ("📂", "Baselines",        "Manage saved baseline snapshots"),
    ("⚖️", "Compare Files",   "Hash-compare two files directly"),
    ("🌊", "Avalanche Demo",   "See the avalanche effect live"),
    ("📋", "Logs",             "Review past integrity scan logs"),
]


class SidebarItem(QListWidgetItem):
    def __init__(self, icon_text: str, label: str):
        super().__init__(f"  {icon_text}  {label}")
        self.setFont(QFont("Segoe UI", 11))
        self.setSizeHint(QSize(190, 48))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Integrity Checker  —  IDS Tool")
        self.setMinimumSize(1050, 680)
        self.resize(1200, 750)
        self.setStyleSheet(DARK_THEME)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(210)
        sidebar_widget.setStyleSheet(f"background:{MANTLE};")
        sb_lay = QVBoxLayout(sidebar_widget)
        sb_lay.setContentsMargins(0, 0, 0, 0)
        sb_lay.setSpacing(0)

        # App logo / header
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #313244, stop:1 {MANTLE});
                border-bottom: 1px solid {SURFACE0};
            }}
        """)
        header.setFixedHeight(72)
        hdr_lay = QVBoxLayout(header)
        hdr_lay.setContentsMargins(16, 10, 16, 10)

        app_title = QLabel("🛡  FileGuard")
        app_title.setStyleSheet(f"color:{MAUVE}; font-size:16px; font-weight:bold;")
        app_sub = QLabel("Integrity Checker v1.0")
        app_sub.setStyleSheet(f"color:{SUBTEXT}; font-size:10px;")
        hdr_lay.addWidget(app_title)
        hdr_lay.addWidget(app_sub)
        sb_lay.addWidget(header)

        # Nav list
        self.sidebar = QListWidget()
        self.sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        for icon, label, _ in NAV_ITEMS:
            self.sidebar.addItem(SidebarItem(icon, label))
        self.sidebar.setCurrentRow(0)
        sb_lay.addWidget(self.sidebar, 1)

        # Sidebar footer
        footer = QLabel("  Python + PyQt6")
        footer.setStyleSheet(f"color:{SUBTEXT}; font-size:10px; padding:10px;")
        sb_lay.addWidget(footer)

        # ── Content area ──────────────────────────────────────────────────────
        self.pages = QStackedWidget()

        self.verify_tab    = VerifyTab()
        self.baseline_tab  = BaselineTab()
        self.compare_tab   = CompareTab()
        self.avalanche_tab = AvalancheTab()
        self.logs_tab      = LogsTab()

        for tab in (self.verify_tab, self.baseline_tab, self.compare_tab,
                    self.avalanche_tab, self.logs_tab):
            self.pages.addWidget(tab)

        # ── Wiring ────────────────────────────────────────────────────────────
        self.sidebar.currentRowChanged.connect(self._on_nav)
        self.sidebar.currentRowChanged.connect(self._on_nav_sidebar)

        # Cross-tab signals
        self.verify_tab.status_message.connect(self._set_status)
        self.verify_tab.log_saved.connect(
            lambda _: (self.logs_tab.refresh(), self._set_status(f"Log saved → {_}"))
        )
        self.baseline_tab.open_in_verify.connect(self._load_baseline_in_verify)
        self.baseline_tab.status_message.connect(self._set_status)
        self.compare_tab.status_message.connect(self._set_status)
        self.logs_tab.status_message.connect(self._set_status)

        # Layout
        main_lay.addWidget(sidebar_widget)
        main_lay.addWidget(self.pages, 1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._set_status("Ready — select a directory and save a baseline to get started.")

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _on_nav(self, index):
        self.pages.setCurrentIndex(index)

    def _on_nav_sidebar(self, index):
        # Refresh tabs that need it when navigated to
        if index == 1:
            self.baseline_tab.refresh()
        elif index == 4:
            self.logs_tab.refresh()

    # ── Cross-tab helpers ──────────────────────────────────────────────────────

    def _load_baseline_in_verify(self, path: str):
        self.verify_tab.set_baseline(path)
        self.sidebar.setCurrentRow(0)
        self._set_status(f"📂  Baseline loaded in Verify tab: {path}")

    def _set_status(self, message: str):
        self.status_bar.showMessage(message)
