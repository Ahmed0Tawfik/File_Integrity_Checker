"""
logs_tab.py — View previous integrity scan logs with tamper timeline.
"""

import os
from pathlib import Path
from PyQt6.QtCore    import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QPlainTextEdit, QSplitter, QGroupBox,
)
from PyQt6.QtGui import QColor, QFont
from core.reporter import parse_log_history
from ui.theme      import MAUVE, TEXT, SUBTEXT, GREEN, YELLOW, RED, BLUE, SURFACE0


class LogsTab(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._logs = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel("📋  Integrity Log Viewer")
        title.setObjectName("title")
        root.addWidget(title)

        subtitle = QLabel(
            "Review the tamper-detection history. Each row is a past verify run — "
            "click to read the full log."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        toolbar = QHBoxLayout()
        self.btn_refresh = QPushButton("↻  Refresh")
        self.btn_refresh.clicked.connect(self.refresh)
        self.btn_delete  = QPushButton("🗑  Delete Log")
        self.btn_delete.setObjectName("danger")
        self.btn_delete.clicked.connect(self._delete_selected)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addWidget(self.btn_delete)
        toolbar.addStretch()
        self.count_label = QLabel("")
        self.count_label.setStyleSheet(f"color:{SUBTEXT}; font-size:11px;")
        toolbar.addWidget(self.count_label)
        root.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # Top — log list
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Timestamp", "Modified", "Deleted", "New", "Unchanged"]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.selectionModel().currentRowChanged.connect(
            lambda cur, _: self._load_log_content(cur.row())
        )
        splitter.addWidget(self.table)

        # Bottom — log content viewer
        self.log_viewer = QPlainTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setPlaceholderText("Select a log entry above to view its full content…")
        self.log_viewer.setFont(QFont("Consolas", 11))
        splitter.addWidget(self.log_viewer)
        splitter.setSizes([300, 400])

        root.addWidget(splitter, 1)

    def refresh(self):
        self._logs = parse_log_history("logs")
        self.table.setRowCount(len(self._logs))
        self.count_label.setText(f"{len(self._logs)} log(s) found")

        for row, log in enumerate(self._logs):
            ts_item = QTableWidgetItem(log["timestamp"])
            ts_item.setForeground(QColor(MAUVE))

            mod_item = QTableWidgetItem(str(log["modified"]))
            mod_item.setForeground(QColor(YELLOW if log["modified"] > 0 else SUBTEXT))

            del_item = QTableWidgetItem(str(log["deleted"]))
            del_item.setForeground(QColor(RED if log["deleted"] > 0 else SUBTEXT))

            new_item = QTableWidgetItem(str(log["new"]))
            new_item.setForeground(QColor(BLUE if log["new"] > 0 else SUBTEXT))

            unc_item = QTableWidgetItem(str(log["unchanged"]))
            unc_item.setForeground(QColor(GREEN))

            for col, item in enumerate(
                [ts_item, mod_item, del_item, new_item, unc_item]
            ):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

            # Highlight rows with changes
            if log["modified"] > 0 or log["deleted"] > 0 or log["new"] > 0:
                bg = QColor(YELLOW)
                bg.setAlpha(15)
                for col in range(5):
                    self.table.item(row, col).setBackground(bg)

        if self.table.rowCount() > 0:
            self.table.selectRow(0)

    def _load_log_content(self, row):
        if row < 0 or row >= len(self._logs):
            return
        path = self._logs[row]["path"]
        try:
            content = Path(path).read_text(encoding="utf-8")
            self.log_viewer.setPlainText(content)
            self.status_message.emit(f"📋  Viewing: {self._logs[row]['name']}")
        except OSError as e:
            self.log_viewer.setPlainText(f"Error reading log: {e}")

    def _delete_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._logs):
            self.status_message.emit("⚠  Select a log to delete.")
            return
        log = self._logs[row]
        try:
            os.remove(log["path"])
            self.status_message.emit(f"🗑  Deleted: {log['name']}")
            self.refresh()
        except OSError as e:
            self.status_message.emit(f"❌  {e}")
