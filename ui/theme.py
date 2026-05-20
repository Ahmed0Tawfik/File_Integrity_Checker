"""
theme.py — Dark theme stylesheet (QSS) for the entire application.
Inspired by Catppuccin Mocha palette.
"""

# ── Palette ──────────────────────────────────────────────────────────────────
CRUST   = "#11111b"
MANTLE  = "#181825"
BASE    = "#1e1e2e"
SURFACE0= "#313244"
SURFACE1= "#45475a"
SURFACE2= "#585b70"
OVERLAY = "#6c7086"
TEXT    = "#cdd6f4"
SUBTEXT = "#a6adc8"
LAVENDER= "#b4befe"
BLUE    = "#89b4fa"
SAPPHIRE= "#74c7ec"
SKY     = "#89dceb"
TEAL    = "#94e2d5"
GREEN   = "#a6e3a1"
YELLOW  = "#f9e2af"
PEACH   = "#fab387"
MAROON  = "#eba0ac"
RED     = "#f38ba8"
MAUVE   = "#cba6f7"
PINK    = "#f5c2e7"

# ── Severity colours ─────────────────────────────────────────────────────────
SEVERITY_COLORS = {
    "CRITICAL": RED,
    "HIGH":     PEACH,
    "MEDIUM":   YELLOW,
    "LOW":      GREEN,
    "UNKNOWN":  OVERLAY,
}

# ── Status colours ────────────────────────────────────────────────────────────
STATUS_COLORS = {
    "Unchanged": GREEN,
    "Modified":  YELLOW,
    "Deleted":   RED,
    "New":       BLUE,
}

# ── Full QSS stylesheet ───────────────────────────────────────────────────────
DARK_THEME = f"""
/* ── Global ─────────────────────────────── */
QMainWindow, QWidget {{
    background-color: {BASE};
    color: {TEXT};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}}

QDialog {{
    background-color: {MANTLE};
    color: {TEXT};
}}

/* ── Sidebar list ────────────────────────── */
QListWidget {{
    background-color: {MANTLE};
    border: none;
    border-right: 1px solid {SURFACE0};
    outline: none;
    padding: 8px 4px;
}}
QListWidget::item {{
    padding: 12px 18px;
    border-radius: 8px;
    margin: 2px 6px;
    color: {SUBTEXT};
    font-size: 13px;
}}
QListWidget::item:selected {{
    background-color: {SURFACE0};
    color: {MAUVE};
    font-weight: bold;
}}
QListWidget::item:hover:!selected {{
    background-color: {SURFACE0}88;
    color: {TEXT};
}}

/* ── Buttons ─────────────────────────────── */
QPushButton {{
    background-color: {SURFACE0};
    color: {TEXT};
    border: 1px solid {SURFACE1};
    border-radius: 7px;
    padding: 7px 18px;
    font-size: 13px;
    min-height: 28px;
}}
QPushButton:hover {{
    background-color: {SURFACE1};
    border-color: {MAUVE};
}}
QPushButton:pressed {{
    background-color: {SURFACE2};
}}
QPushButton:disabled {{
    color: {OVERLAY};
    border-color: {SURFACE0};
}}
QPushButton#primary {{
    background-color: {MAUVE};
    color: {CRUST};
    border: none;
    font-weight: bold;
}}
QPushButton#primary:hover {{
    background-color: {LAVENDER};
}}
QPushButton#danger {{
    background-color: {RED};
    color: {CRUST};
    border: none;
    font-weight: bold;
}}
QPushButton#danger:hover {{
    background-color: {MAROON};
}}
QPushButton#success {{
    background-color: {GREEN};
    color: {CRUST};
    border: none;
    font-weight: bold;
}}

/* ── Line edits ──────────────────────────── */
QLineEdit {{
    background-color: {SURFACE0};
    color: {TEXT};
    border: 1px solid {SURFACE1};
    border-radius: 7px;
    padding: 6px 10px;
    selection-background-color: {MAUVE};
    selection-color: {CRUST};
}}
QLineEdit:focus {{
    border-color: {MAUVE};
}}

/* ── ComboBox ────────────────────────────── */
QComboBox {{
    background-color: {SURFACE0};
    color: {TEXT};
    border: 1px solid {SURFACE1};
    border-radius: 7px;
    padding: 6px 10px;
    min-width: 90px;
}}
QComboBox:hover {{ border-color: {MAUVE}; }}
QComboBox::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox QAbstractItemView {{
    background-color: {SURFACE0};
    color: {TEXT};
    selection-background-color: {MAUVE};
    selection-color: {CRUST};
    border: 1px solid {SURFACE1};
    border-radius: 6px;
}}

/* ── Table ───────────────────────────────── */
QTableWidget {{
    background-color: {MANTLE};
    color: {TEXT};
    border: 1px solid {SURFACE0};
    border-radius: 8px;
    gridline-color: {SURFACE0};
    alternate-background-color: {BASE};
    selection-background-color: {SURFACE1};
}}
QTableWidget::item {{
    padding: 5px 8px;
}}
QHeaderView::section {{
    background-color: {BASE};
    color: {SUBTEXT};
    font-size: 11px;
    font-weight: bold;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {SURFACE0};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
QHeaderView::section:first {{ border-top-left-radius: 8px; }}
QHeaderView::section:last  {{ border-top-right-radius: 8px; }}

/* ── Progress bar ────────────────────────── */
QProgressBar {{
    background-color: {SURFACE0};
    border: none;
    border-radius: 5px;
    height: 8px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {MAUVE}, stop:1 {BLUE});
    border-radius: 5px;
}}

/* ── Scroll bars ─────────────────────────── */
QScrollBar:vertical {{
    background: {MANTLE};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {SURFACE1};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {MAUVE}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QScrollBar:horizontal {{
    background: {MANTLE};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {SURFACE1};
    border-radius: 4px;
    min-width: 20px;
}}
QScrollBar::handle:horizontal:hover {{ background: {MAUVE}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Checkboxes ──────────────────────────── */
QCheckBox {{
    color: {TEXT};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid {SURFACE1};
    background: {SURFACE0};
}}
QCheckBox::indicator:checked {{
    background-color: {MAUVE};
    border-color: {MAUVE};
}}

/* ── GroupBox ────────────────────────────── */
QGroupBox {{
    border: 1px solid {SURFACE0};
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 10px;
    font-size: 11px;
    color: {SUBTEXT};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {MAUVE};
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── Splitter ────────────────────────────── */
QSplitter::handle {{
    background-color: {SURFACE0};
    width: 1px;
}}

/* ── Text areas (logs) ───────────────────── */
QPlainTextEdit, QTextEdit {{
    background-color: {MANTLE};
    color: {TEXT};
    border: 1px solid {SURFACE0};
    border-radius: 8px;
    padding: 8px;
    font-family: 'Consolas', 'JetBrains Mono', monospace;
    font-size: 12px;
}}

/* ── Labels ──────────────────────────────── */
QLabel#title {{
    font-size: 20px;
    font-weight: bold;
    color: {MAUVE};
}}
QLabel#subtitle {{
    font-size: 12px;
    color: {SUBTEXT};
}}
QLabel#stat_number {{
    font-size: 28px;
    font-weight: bold;
}}
QLabel#stat_label {{
    font-size: 11px;
    color: {SUBTEXT};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── Tooltip ─────────────────────────────── */
QToolTip {{
    background-color: {SURFACE0};
    color: {TEXT};
    border: 1px solid {SURFACE1};
    border-radius: 5px;
    padding: 4px 8px;
}}

/* ── Status bar ──────────────────────────── */
QStatusBar {{
    background-color: {MANTLE};
    color: {SUBTEXT};
    border-top: 1px solid {SURFACE0};
    font-size: 11px;
}}
"""
