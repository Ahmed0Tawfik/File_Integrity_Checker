"""
baseline_tab.py — Browse and manage saved baseline snapshots.
"""

import os
from PyQt6.QtCore    import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QGroupBox,
)
from PyQt6.QtGui import QColor
from core.baseline import list_baselines
from ui.theme      import MAUVE, TEXT, SUBTEXT, GREEN, YELLOW


class BaselineTab(QWidget):
    open_in_verify = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._baselines = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel("📂  Baseline Manager")
        title.setObjectName("title")
        root.addWidget(title)

        subtitle = QLabel("Browse, inspect, and manage your saved baseline snapshots.")
        subtitle.setObjectName("subtitle")
        root.addWidget(subtitle)

        toolbar = QHBoxLayout()
        self.btn_refresh = QPushButton("↻  Refresh")
        self.btn_use     = QPushButton("✔  Use in Verify")
        self.btn_delete  = QPushButton("🗑  Delete")
        self.btn_use.setObjectName("primary")
        self.btn_delete.setObjectName("danger")
        self.btn_refresh.clicked.connect(self.refresh)
        self.btn_use.clicked.connect(self._use_selected)
        self.btn_delete.clicked.connect(self._delete_selected)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addWidget(self.btn_use)
        toolbar.addWidget(self.btn_delete)
        toolbar.addStretch()
        self.count_label = QLabel("")
        self.count_label.setStyleSheet(f"color: {SUBTEXT}; font-size: 11px;")
        toolbar.addWidget(self.count_label)
        root.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Filename", "Algorithm", "Files", "Scanned At", "Size (KB)", "Root Directory"]
        )
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._use_selected)
        self.table.selectionModel().selectionChanged.connect(self._on_selection)
        root.addWidget(self.table, 1)

        detail = QGroupBox("Selected Baseline Details")
        dl = QVBoxLayout(detail)
        self.detail_label = QLabel("Select a baseline to see its details.")
        self.detail_label.setStyleSheet(f"color:{SUBTEXT}; font-family:Consolas; font-size:12px;")
        self.detail_label.setWordWrap(True)
        dl.addWidget(self.detail_label)
        root.addWidget(detail)

    def refresh(self):
        self._baselines = list_baselines("baselines")
        self.table.setRowCount(len(self._baselines))
        self.count_label.setText(f"{len(self._baselines)} baseline(s) found")
        for row, bl in enumerate(self._baselines):
            algo_color = MAUVE if "sha256" in bl["algorithm"] else (
                YELLOW if bl["algorithm"] in ("sha1", "md5") else TEXT
            )
            data = [
                (bl["name"],              TEXT),
                (bl["algorithm"].upper(), algo_color),
                (str(bl["file_count"]),   GREEN),
                (bl["scanned_at"],        SUBTEXT),
                (str(bl["size_kb"]),      SUBTEXT),
                (bl["root"],              SUBTEXT),
            ]
            for col, (text, color) in enumerate(data):
                item = QTableWidgetItem(text)
                item.setForeground(QColor(color))
                self.table.setItem(row, col, item)

    def _on_selection(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._baselines):
            return
        bl = self._baselines[row]
        self.detail_label.setText(
            f"Path      : {bl['path']}\n"
            f"Algorithm : {bl['algorithm'].upper()}\n"
            f"Files     : {bl['file_count']}\n"
            f"Scanned   : {bl['scanned_at']}\n"
            f"Size      : {bl['size_kb']} KB\n"
            f"Root      : {bl['root']}"
        )

    def _use_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._baselines):
            self.status_message.emit("⚠  Select a baseline first.")
            return
        self.open_in_verify.emit(self._baselines[row]["path"])
        self.status_message.emit(f"📂  Loaded: {self._baselines[row]['name']}")

    def _delete_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._baselines):
            self.status_message.emit("⚠  Select a baseline to delete.")
            return
        bl = self._baselines[row]
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Permanently delete:\n{bl['path']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(bl["path"])
                self.status_message.emit(f"🗑  Deleted: {bl['name']}")
                self.refresh()
            except OSError as e:
                self.status_message.emit(f"❌  {e}")
