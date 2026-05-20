"""
avalanche_tab.py — Interactive avalanche effect demonstration.
"""

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QGroupBox,
)
from PyQt6.QtGui import QFont
from core.hasher import avalanche_demo, get_supported_algorithms
from ui.theme    import MAUVE, RED, GREEN, YELLOW, TEXT, SUBTEXT, SURFACE0, MANTLE, PEACH


class AvalancheTab(QWidget):
    status_message = None  # not needed but kept for consistency

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._run_demo()  # pre-fill with default example

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel("🌊  Avalanche Effect Demo")
        title.setObjectName("title")
        root.addWidget(title)

        subtitle = QLabel(
            "Demonstrates how a tiny change in input (even one character) causes ~50% of "
            "hash bits to flip — the hallmark of a strong hash function."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        # Input group
        inp = QGroupBox("Inputs")
        inp_lay = QVBoxLayout(inp)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Input A:"))
        self.input1 = QLineEdit("Hello, World!")
        self.input1.textChanged.connect(self._run_demo)
        row1.addWidget(self.input1, 1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Input B:"))
        self.input2 = QLineEdit("Hello, World?")
        self.input2.textChanged.connect(self._run_demo)
        row2.addWidget(self.input2, 1)

        algo_row = QHBoxLayout()
        algo_row.addWidget(QLabel("Algorithm:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems([a.upper() for a in get_supported_algorithms()])
        self.algo_combo.setCurrentText("SHA256")
        self.algo_combo.currentTextChanged.connect(self._run_demo)
        algo_row.addWidget(self.algo_combo)
        algo_row.addStretch()

        inp_lay.addLayout(row1)
        inp_lay.addLayout(row2)
        inp_lay.addLayout(algo_row)
        root.addWidget(inp)

        # Hash display
        hashes = QGroupBox("Hash Output (differing characters highlighted in red)")
        h_lay = QVBoxLayout(hashes)

        self.hash1_label = QLabel()
        self.hash1_label.setTextFormat(Qt.TextFormat.RichText)
        self.hash1_label.setStyleSheet(f"font-family:Consolas; font-size:13px; color:{TEXT};")
        self.hash1_label.setWordWrap(True)

        self.hash2_label = QLabel()
        self.hash2_label.setTextFormat(Qt.TextFormat.RichText)
        self.hash2_label.setStyleSheet(f"font-family:Consolas; font-size:13px; color:{TEXT};")
        self.hash2_label.setWordWrap(True)

        h_lay.addWidget(self.hash1_label)
        h_lay.addWidget(self.hash2_label)
        root.addWidget(hashes)

        # Stats bar
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet(f"""
            QFrame {{
                background: {SURFACE0};
                border-radius: 10px;
                border: 1px solid #45475a;
            }}
        """)
        stats_lay = QHBoxLayout(self.stats_frame)
        stats_lay.setContentsMargins(20, 14, 20, 14)

        self.stat_hex   = self._make_stat("Hex chars differ", PEACH)
        self.stat_bits  = self._make_stat("Bits differ",      MAUVE)
        self.stat_pct   = self._make_stat("Bit flip %",       RED)
        self.stat_total = self._make_stat("Total bits",       SUBTEXT)

        for s in (self.stat_hex, self.stat_bits, self.stat_pct, self.stat_total):
            stats_lay.addWidget(s)
        root.addWidget(self.stats_frame)

        # Explanation
        explain = QGroupBox("Why This Matters")
        ex_lay = QVBoxLayout(explain)
        ex_text = QLabel(
            "The <b>avalanche effect</b> ensures that even a single-bit change in the input "
            "propagates through the entire hash, making it impossible to predict or reverse-engineer "
            "the original input from the output. This is a critical security property — without it, "
            "an attacker could craft a modified file that produces the same hash as the original, "
            "defeating tamper detection entirely.\n\n"
            "Strong algorithms (SHA-256, SHA-512) achieve ~50% bit flip rate, which is ideal. "
            "Weak algorithms (MD5, SHA-1) still exhibit avalanche, but have <i>collision vulnerabilities</i> "
            "— different inputs that produce the same hash — making them unsafe for security use."
        )
        ex_text.setWordWrap(True)
        ex_text.setStyleSheet(f"color:{SUBTEXT}; font-size:12px; line-height:1.6;")
        ex_text.setTextFormat(Qt.TextFormat.RichText)
        ex_lay.addWidget(ex_text)
        root.addWidget(explain)
        root.addStretch()

    def _make_stat(self, label, color):
        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background: transparent; }}")
        lay = QVBoxLayout(frame)
        lay.setSpacing(2)
        lay.setContentsMargins(0, 0, 0, 0)

        num = QLabel("—")
        num.setObjectName("stat_number")
        num.setStyleSheet(f"color:{color}; font-size:26px; font-weight:bold;")
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"color:{color}88; font-size:9px; letter-spacing:1px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(num)
        lay.addWidget(lbl)
        frame._num_label = num
        return frame

    def _run_demo(self):
        t1 = self.input1.text()
        t2 = self.input2.text()
        algo = self.algo_combo.currentText().lower()

        if not t1 or not t2:
            return

        try:
            res = avalanche_demo(t1, t2, algo)
        except Exception as e:
            self.hash1_label.setText(f"Error: {e}")
            return

        h1, h2 = res["hash1"], res["hash2"]

        # Build highlighted HTML
        html1, html2 = "", ""
        for c1, c2 in zip(h1, h2):
            if c1 != c2:
                html1 += f'<span style="color:{RED}; font-weight:bold; text-decoration:underline;">{c1}</span>'
                html2 += f'<span style="color:{RED}; font-weight:bold; text-decoration:underline;">{c2}</span>'
            else:
                html1 += f'<span style="color:{GREEN};">{c1}</span>'
                html2 += f'<span style="color:{GREEN};">{c2}</span>'

        self.hash1_label.setText(
            f'<b style="color:{SUBTEXT};">A → </b>'
            f'<span style="font-family:Consolas;">{html1}</span>'
        )
        self.hash2_label.setText(
            f'<b style="color:{SUBTEXT};">B → </b>'
            f'<span style="font-family:Consolas;">{html2}</span>'
        )

        self.stat_hex._num_label.setText(
            f"{res['hex_diff_count']}/{res['total_hex_chars']}"
        )
        self.stat_bits._num_label.setText(str(res["bit_diff_count"]))
        pct = res["bit_diff_percent"]
        self.stat_pct._num_label.setText(f"{pct}%")
        # Color the pct stat: green if near 50%, red if far away
        color = GREEN if 40 <= pct <= 60 else YELLOW if 25 <= pct <= 75 else RED
        self.stat_pct._num_label.setStyleSheet(
            f"color:{color}; font-size:26px; font-weight:bold;"
        )
        self.stat_total._num_label.setText(str(res["total_bits"]))
