"""
compare_tab.py — Direct file-to-file comparison by hash.
"""

from PyQt6.QtCore    import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFileDialog, QGroupBox, QFrame,
)
from PyQt6.QtGui import QColor, QFont
from core.hasher import compare_files, get_supported_algorithms
from ui.theme    import GREEN, RED, YELLOW, MAUVE, TEXT, SUBTEXT, SURFACE0, MANTLE


class CompareWorker(QThread):
    finished = pyqtSignal(bool, str, str, str, str)  # match, h1, h2, f1, f2
    error    = pyqtSignal(str)

    def __init__(self, f1, f2, algo):
        super().__init__()
        self.f1, self.f2, self.algo = f1, f2, algo

    def run(self):
        try:
            match, h1, h2 = compare_files(self.f1, self.f2, self.algo)
            self.finished.emit(match, h1, h2, self.f1, self.f2)
        except Exception as e:
            self.error.emit(str(e))


class CompareTab(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel("⚖️  File Comparator")
        title.setObjectName("title")
        root.addWidget(title)

        subtitle = QLabel("Directly compare two files by hash — no baseline required.")
        subtitle.setObjectName("subtitle")
        root.addWidget(subtitle)

        cfg = QGroupBox("Select Files")
        cfg_lay = QVBoxLayout(cfg)

        f1_row = QHBoxLayout()
        self.f1_edit = QLineEdit(); self.f1_edit.setPlaceholderText("First file…")
        btn1 = QPushButton("Browse…"); btn1.clicked.connect(lambda: self._browse(self.f1_edit))
        f1_row.addWidget(QLabel("File 1:")); f1_row.addWidget(self.f1_edit, 1); f1_row.addWidget(btn1)

        f2_row = QHBoxLayout()
        self.f2_edit = QLineEdit(); self.f2_edit.setPlaceholderText("Second file…")
        btn2 = QPushButton("Browse…"); btn2.clicked.connect(lambda: self._browse(self.f2_edit))
        f2_row.addWidget(QLabel("File 2:")); f2_row.addWidget(self.f2_edit, 1); f2_row.addWidget(btn2)

        algo_row = QHBoxLayout()
        algo_row.addWidget(QLabel("Algorithm:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems([a.upper() for a in get_supported_algorithms()])
        self.algo_combo.setCurrentText("SHA256")
        algo_row.addWidget(self.algo_combo)
        algo_row.addStretch()

        self.btn_compare = QPushButton("  Compare Files")
        self.btn_compare.setObjectName("primary")
        self.btn_compare.setFixedHeight(38)
        self.btn_compare.clicked.connect(self._run)

        cfg_lay.addLayout(f1_row)
        cfg_lay.addLayout(f2_row)
        cfg_lay.addLayout(algo_row)
        cfg_lay.addWidget(self.btn_compare)
        root.addWidget(cfg)

        # Result panel
        self.result_frame = QFrame()
        self.result_frame.setStyleSheet(f"""
            QFrame {{ background:{SURFACE0}; border-radius:10px; border:1px solid #45475a; }}
        """)
        res_lay = QVBoxLayout(self.result_frame)
        res_lay.setContentsMargins(20, 16, 20, 16)

        self.result_icon  = QLabel("—")
        self.result_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_icon.setStyleSheet("font-size: 48px;")

        self.result_label = QLabel("Run a comparison to see results.")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet(f"font-size:15px; font-weight:bold; color:{SUBTEXT};")

        self.hash1_label = QLabel("")
        self.hash2_label = QLabel("")
        for lbl in (self.hash1_label, self.hash2_label):
            lbl.setStyleSheet(f"font-family:Consolas; font-size:12px; color:{SUBTEXT};")
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        res_lay.addWidget(self.result_icon)
        res_lay.addWidget(self.result_label)
        res_lay.addWidget(self.hash1_label)
        res_lay.addWidget(self.hash2_label)
        root.addWidget(self.result_frame)
        root.addStretch()

    def _browse(self, edit):
        f, _ = QFileDialog.getOpenFileName(self, "Select File")
        if f:
            edit.setText(f)

    def _run(self):
        f1 = self.f1_edit.text().strip()
        f2 = self.f2_edit.text().strip()
        if not f1 or not f2:
            self.status_message.emit("⚠  Please select both files.")
            return
        algo = self.algo_combo.currentText().lower()
        self.btn_compare.setEnabled(False)
        self.result_label.setText("Comparing…")
        self._worker = CompareWorker(f1, f2, algo)
        self._worker.finished.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_done(self, match, h1, h2, f1, f2):
        self.btn_compare.setEnabled(True)
        import os
        n1, n2 = os.path.basename(f1), os.path.basename(f2)
        if match:
            self.result_frame.setStyleSheet(f"""
                QFrame {{ background:{GREEN}18; border-radius:10px; border:1px solid {GREEN}66; }}
            """)
            self.result_icon.setText("✅")
            self.result_label.setText("Files are IDENTICAL")
            self.result_label.setStyleSheet(f"font-size:15px; font-weight:bold; color:{GREEN};")
            self.status_message.emit(f"✅  {n1} == {n2}  (hashes match)")
        else:
            self.result_frame.setStyleSheet(f"""
                QFrame {{ background:{RED}18; border-radius:10px; border:1px solid {RED}66; }}
            """)
            self.result_icon.setText("❌")
            self.result_label.setText("Files are DIFFERENT")
            self.result_label.setStyleSheet(f"font-size:15px; font-weight:bold; color:{RED};")
            self.status_message.emit(f"❌  {n1} ≠ {n2}  (hashes differ)")

        algo = self.algo_combo.currentText()
        self.hash1_label.setText(f"{n1}:\n{h1}")
        self.hash2_label.setText(f"{n2}:\n{h2}")

        # Highlight differing chars
        if not match:
            diff_html1, diff_html2 = "", ""
            for c1, c2 in zip(h1, h2):
                style1 = f'<span style="color:{RED};font-weight:bold;">{c1}</span>' if c1 != c2 else c1
                style2 = f'<span style="color:{RED};font-weight:bold;">{c2}</span>' if c1 != c2 else c2
                diff_html1 += style1
                diff_html2 += style2
            self.hash1_label.setText(f"<b>{n1}:</b><br><span style='font-family:Consolas;'>{diff_html1}</span>")
            self.hash2_label.setText(f"<b>{n2}:</b><br><span style='font-family:Consolas;'>{diff_html2}</span>")
            self.hash1_label.setTextFormat(Qt.TextFormat.RichText)
            self.hash2_label.setTextFormat(Qt.TextFormat.RichText)

    def _on_error(self, msg):
        self.btn_compare.setEnabled(True)
        self.result_label.setText(f"Error: {msg}")
        self.status_message.emit(f"❌  {msg}")
