"""
verify_tab.py — Scan + Verify panel (the main tab).
"""

import os
import time
from pathlib import Path

from PyQt6.QtCore    import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QProgressBar, QTableWidget, QTableWidgetItem,
    QFileDialog, QCheckBox, QFrame, QHeaderView, QSplitter, QGroupBox,
    QAbstractItemView, QSizePolicy,
)
from PyQt6.QtGui import QColor, QFont

from core.scanner  import scan_directory
from core.baseline import save_baseline
from core.verifier import verify_integrity
from core.hasher   import get_supported_algorithms
from ui.theme      import STATUS_COLORS, SEVERITY_COLORS, MANTLE, SURFACE0, MAUVE, TEXT, SUBTEXT, GREEN, YELLOW, RED, BLUE, SURFACE1


# ── Worker threads ────────────────────────────────────────────────────────────

class ScanWorker(QThread):
    progress = pyqtSignal(int, int, str)   # current, total, filename
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, directory, algorithm, ignore_patterns=None):
        super().__init__()
        self.directory       = directory
        self.algorithm       = algorithm
        self.ignore_patterns = ignore_patterns or []

    def run(self):
        try:
            result = scan_directory(
                self.directory,
                self.algorithm,
                self.ignore_patterns or None,
                lambda cur, tot, name: self.progress.emit(cur, tot, name),
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class VerifyWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, directory, baseline_path, algorithm=None, ignore_patterns=None):
        super().__init__()
        self.directory       = directory
        self.baseline_path   = baseline_path
        self.algorithm       = algorithm
        self.ignore_patterns = ignore_patterns or []

    def run(self):
        try:
            result = verify_integrity(
                self.directory,
                self.baseline_path,
                self.algorithm or None,
                self.ignore_patterns or None,
                lambda cur, tot, name: self.progress.emit(cur, tot, name),
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ── Stat card widget ─────────────────────────────────────────────────────────

class StatCard(QFrame):
    def __init__(self, label: str, color: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setFixedHeight(90)
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: {SURFACE0};
                border: 1px solid {color}44;
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)

        self.number = QLabel("0")
        self.number.setObjectName("stat_number")
        self.number.setStyleSheet(f"color: {color}; font-size: 30px; font-weight: bold;")
        self.number.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel(label.upper())
        lbl.setObjectName("stat_label")
        lbl.setStyleSheet(f"color: {color}99; font-size: 10px; letter-spacing: 1px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.number)
        layout.addWidget(lbl)

    def set_value(self, n: int):
        self.number.setText(str(n))


# ── Main verify tab ───────────────────────────────────────────────────────────

class VerifyTab(QWidget):
    status_message = pyqtSignal(str)
    log_saved      = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker        = None
        self._last_result   = None
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # Title
        title = QLabel("🔍  Scan & Verify Integrity")
        title.setObjectName("title")
        root.addWidget(title)

        subtitle = QLabel("Scan a directory to create a baseline, then verify it for tampering at any time.")
        subtitle.setObjectName("subtitle")
        root.addWidget(subtitle)

        # ── Config group ──────────────────────────────────────────────────────
        cfg_group = QGroupBox("Configuration")
        cfg_layout = QVBoxLayout(cfg_group)
        cfg_layout.setSpacing(10)

        # Directory row
        dir_row = QHBoxLayout()
        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText("Select a directory to monitor…")
        btn_browse_dir = QPushButton("Browse…")
        btn_browse_dir.clicked.connect(self._browse_dir)
        dir_row.addWidget(QLabel("Directory:"))
        dir_row.addWidget(self.dir_edit, 1)
        dir_row.addWidget(btn_browse_dir)

        # Baseline row
        bl_row = QHBoxLayout()
        self.bl_edit = QLineEdit()
        self.bl_edit.setPlaceholderText("Baseline .json path (for verify)…")
        btn_browse_bl = QPushButton("Browse…")
        btn_browse_bl.clicked.connect(self._browse_baseline)
        bl_row.addWidget(QLabel("Baseline:  "))
        bl_row.addWidget(self.bl_edit, 1)
        bl_row.addWidget(btn_browse_bl)

        # Algorithm + ignore row
        algo_row = QHBoxLayout()
        algo_row.addWidget(QLabel("Algorithm:"))
        self.algo_combo = QComboBox()
        algos = get_supported_algorithms()
        self.algo_combo.addItems([a.upper() for a in algos])
        self.algo_combo.setCurrentText("SHA256")
        algo_row.addWidget(self.algo_combo)

        algo_row.addSpacing(20)
        algo_row.addWidget(QLabel("Ignore patterns:"))
        self.ignore_edit = QLineEdit()
        self.ignore_edit.setPlaceholderText("*.log, *.tmp, __pycache__")
        algo_row.addWidget(self.ignore_edit, 1)

        cfg_layout.addLayout(dir_row)
        cfg_layout.addLayout(bl_row)
        cfg_layout.addLayout(algo_row)

        # Action buttons
        btn_row = QHBoxLayout()
        self.btn_scan   = QPushButton("💾  Save Baseline")
        self.btn_verify = QPushButton("🔐  Verify Now")
        self.btn_scan.setObjectName("primary")
        self.btn_verify.setObjectName("success")
        self.btn_scan.clicked.connect(self._run_scan)
        self.btn_verify.clicked.connect(self._run_verify)
        btn_row.addWidget(self.btn_scan)
        btn_row.addWidget(self.btn_verify)
        btn_row.addStretch()

        self.save_log_chk = QCheckBox("Auto-save log after verify")
        self.save_log_chk.setChecked(True)
        btn_row.addWidget(self.save_log_chk)

        cfg_layout.addLayout(btn_row)
        root.addWidget(cfg_group)

        # ── Progress bar ──────────────────────────────────────────────────────
        prog_layout = QHBoxLayout()
        self.progress_bar  = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_label = QLabel("Idle")
        self.progress_label.setStyleSheet(f"color: {SUBTEXT}; font-size: 11px;")
        prog_layout.addWidget(self.progress_bar, 1)
        prog_layout.addWidget(self.progress_label)
        root.addLayout(prog_layout)

        # ── Stat cards ────────────────────────────────────────────────────────
        cards_row = QHBoxLayout()
        self.card_unchanged = StatCard("Unchanged", GREEN)
        self.card_modified  = StatCard("Modified",  YELLOW)
        self.card_deleted   = StatCard("Deleted",   RED)
        self.card_new       = StatCard("New",        BLUE)
        for card in (self.card_unchanged, self.card_modified,
                     self.card_deleted, self.card_new):
            cards_row.addWidget(card)
        root.addLayout(cards_row)

        # ── Results table ─────────────────────────────────────────────────────
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Status", "Severity", "File Path", "Old Size", "New Size"]
        )
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        root.addWidget(self.table, 1)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Directory")
        if d:
            self.dir_edit.setText(d)

    def _browse_baseline(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Select Baseline", "baselines", "JSON Files (*.json)"
        )
        if f:
            self.bl_edit.setText(f)

    def _get_ignore_patterns(self):
        raw = self.ignore_edit.text().strip()
        if not raw:
            return []
        return [p.strip() for p in raw.split(",") if p.strip()]

    def _set_busy(self, busy: bool):
        self.btn_scan.setEnabled(not busy)
        self.btn_verify.setEnabled(not busy)

    def _on_progress(self, cur, tot, name):
        if tot > 0:
            self.progress_bar.setValue(int(cur / tot * 100))
        self.progress_label.setText(f"[{cur}/{tot}] {Path(name).name[:50]}")

    # ── Scan (save baseline) ──────────────────────────────────────────────────

    def _run_scan(self):
        directory = self.dir_edit.text().strip()
        if not directory or not os.path.isdir(directory):
            self.status_message.emit("⚠  Please select a valid directory first.")
            return

        algo = self.algo_combo.currentText().lower()
        ignore = self._get_ignore_patterns()

        out_dir = Path("baselines")
        out_dir.mkdir(exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_path = str(out_dir / f"baseline_{ts}.json")

        self._set_busy(True)
        self.progress_bar.setValue(0)
        self.status_message.emit(f"Scanning {directory}…")

        self._worker = ScanWorker(directory, algo, ignore)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(lambda res: self._on_scan_done(res, out_path))
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_scan_done(self, result, out_path):
        self._set_busy(False)
        self.progress_bar.setValue(100)
        file_count = result.get("__meta__", {}).get("file_count", len(result) - 1)
        try:
            save_baseline(result, out_path)
            self.bl_edit.setText(out_path)
            self.status_message.emit(
                f"✅  Baseline saved → {out_path}  ({file_count} files)"
            )
        except Exception as e:
            self._on_error(str(e))

    # ── Verify ────────────────────────────────────────────────────────────────

    def _run_verify(self):
        directory = self.dir_edit.text().strip()
        baseline  = self.bl_edit.text().strip()

        if not directory or not os.path.isdir(directory):
            self.status_message.emit("⚠  Please select a valid directory first.")
            return
        if not baseline or not os.path.isfile(baseline):
            self.status_message.emit("⚠  Please select a valid baseline .json file.")
            return

        algo   = self.algo_combo.currentText().lower()
        ignore = self._get_ignore_patterns()

        self._set_busy(True)
        self.progress_bar.setValue(0)
        self.status_message.emit("Verifying integrity…")
        self.table.setRowCount(0)

        self._worker = VerifyWorker(directory, baseline, algo, ignore)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_verify_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_verify_done(self, result):
        self._set_busy(False)
        self.progress_bar.setValue(100)
        self._last_result = result

        s = result.get("summary", {})
        self.card_unchanged.set_value(s.get("unchanged", 0))
        self.card_modified.set_value(s.get("modified",  0))
        self.card_deleted.set_value(s.get("deleted",   0))
        self.card_new.set_value(s.get("new",       0))

        self._populate_table(result)

        changed = s.get("modified", 0) + s.get("deleted", 0) + s.get("new", 0)
        icon = "🚨" if changed else "✅"
        self.status_message.emit(
            f"{icon}  Verify complete — {s.get('total',0)} files in {s.get('elapsed_s',0)}s  "
            f"| Modified: {s.get('modified',0)}  Deleted: {s.get('deleted',0)}  New: {s.get('new',0)}"
        )

        if self.save_log_chk.isChecked():
            from core.reporter import save_log
            try:
                log_path = save_log(result)
                self.log_saved.emit(log_path)
                self.status_message.emit(
                    self.status_message.receivers(self.status_message) and
                    f"{icon}  Verify complete — log saved → {log_path}" or ""
                )
            except Exception:
                pass

    def _populate_table(self, result):
        all_items = []
        for status in ("Modified", "Deleted", "New", "Unchanged"):
            for item in result.get(status.lower(), []):
                all_items.append(item)

        self.table.setRowCount(len(all_items))
        for row, item in enumerate(all_items):
            status   = item.get("status", "")
            severity = item.get("severity", "MEDIUM")

            status_item = QTableWidgetItem(status)
            status_color = QColor(STATUS_COLORS.get(status, TEXT))
            status_item.setForeground(status_color)
            status_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

            sev_item = QTableWidgetItem(severity)
            sev_color = QColor(SEVERITY_COLORS.get(severity, SUBTEXT))
            sev_item.setForeground(sev_color)

            path_item = QTableWidgetItem(item.get("path", ""))
            path_item.setForeground(QColor(TEXT))

            old_sz = item.get("old_size", 0)
            new_sz = item.get("new_size", 0)
            from core.reporter import format_size
            old_sz_item = QTableWidgetItem(format_size(old_sz) if old_sz else "—")
            new_sz_item = QTableWidgetItem(format_size(new_sz) if new_sz else "—")

            for itm in (status_item, sev_item, path_item, old_sz_item, new_sz_item):
                itm.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

            self.table.setItem(row, 0, status_item)
            self.table.setItem(row, 1, sev_item)
            self.table.setItem(row, 2, path_item)
            self.table.setItem(row, 3, old_sz_item)
            self.table.setItem(row, 4, new_sz_item)

            # Row background tint
            bg = QColor(STATUS_COLORS.get(status, "#313244"))
            bg.setAlpha(20)
            for col in range(5):
                self.table.item(row, col).setBackground(bg)

    def _on_error(self, msg):
        self._set_busy(False)
        self.status_message.emit(f"❌  Error: {msg}")

    # ── Public API ─────────────────────────────────────────────────────────────

    def set_directory(self, path: str):
        self.dir_edit.setText(path)

    def set_baseline(self, path: str):
        self.bl_edit.setText(path)
