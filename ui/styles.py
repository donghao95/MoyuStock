
# Modern Theme Colors (Refined)

# Theme Definitions
DARK_THEME = {
    # Main Colors
    "APP_BG": "#1e1e1e",
    "WIDGET_BG": "#252526",
    "HEADER_BG": "#2d2d2d",
    "BORDER_COLOR": "#333333",
    
    # Text
    "TEXT_COLOR": "#cccccc",        # Primary
    "TEXT_SECONDARY": "#999999",    # Secondary/Placeholder
    
    # Interactions
    "HOVER_COLOR": "#2a2d2e",
    "SELECTION_BG": "#094771",      # VS Code Blue selection
    "SELECTION_COLOR": "#ffffff",
    
    # Brand & Status
    "BRAND_PRIMARY": "#3794ff",     # Blue
    "BRAND_SECONDARY": "#45B7AA",
    "COLOR_UP": "#f85149",          # Red (GitHub Dark)
    "COLOR_DOWN": "#2ea043",        # Green (GitHub Dark)
    "COLOR_FLAT": "#8b949e",
    
    "STATUS_OK": "#2ea043",
    "STATUS_WARN": "#d29922",
    "STATUS_ERR": "#f85149",
    
    # Components
    "TABLE_ALT_BG": "#202020",
    "SCROLL_HANDLE": "#424242",
    
    # Buttons
    "BTN_BG": "#313131",
    "BTN_HOVER": "#3c3c3c",
    "BTN_PRESSED": "#252526",
    "BTN_BORDER": "#454545",
    
    # Table Operations
    "TABLE_BTN_BG": "transparent",
    "TABLE_BTN_HOVER": "#3c3c3c",
    "TABLE_BTN_COLOR": "#cccccc",
    
    # Mini Mode
    "MINI_TEXT_SHADOW": "#000000",
    "MINI_BG_COLOR": "#1a1a2e",
    "MINI_BG_HOVER_COLOR": "#16213e",
    "GRADIENT_START": "#1e1e2e",
    "GRADIENT_END": "#1e1e1e"
}

LIGHT_THEME = {
    # Main Colors
    "APP_BG": "#f0f2f5",
    "WIDGET_BG": "#ffffff",
    "HEADER_BG": "#fafafa",
    "BORDER_COLOR": "#d9d9d9",
    
    # Text
    "TEXT_COLOR": "#000000",        # Primary
    "TEXT_SECONDARY": "#666666",    # Secondary
    
    # Interactions
    "HOVER_COLOR": "#f5f5f5",
    "SELECTION_BG": "#e6f4ff",      # Ant Design Blue
    "SELECTION_COLOR": "#000000",
    
    # Brand & Status
    "BRAND_PRIMARY": "#1677ff",     # Ant Design Blue
    "BRAND_SECONDARY": "#5ac8fa",
    "COLOR_UP": "#ff4d4f",          # Red
    "COLOR_DOWN": "#52c41a",        # Green
    "COLOR_FLAT": "#8c8c8c",
    
    "STATUS_OK": "#52c41a",
    "STATUS_WARN": "#faad14",
    "STATUS_ERR": "#ff4d4f",
    
    # Components
    "TABLE_ALT_BG": "#fafafa",
    "SCROLL_HANDLE": "#c1c1c1",
    
    # Buttons
    "BTN_BG": "#ffffff",
    "BTN_HOVER": "#f5f5f5",
    "BTN_PRESSED": "#e6e6e6",
    "BTN_BORDER": "#d9d9d9",
    
    # Table Operations
    "TABLE_BTN_BG": "transparent",
    "TABLE_BTN_HOVER": "#f0f0f0",
    "TABLE_BTN_COLOR": "#666666",
    
    # Mini Mode
    "MINI_TEXT_SHADOW": "#ffffff",
    "MINI_BG_COLOR": "#ffffff",
    "MINI_BG_HOVER_COLOR": "#e6e6fa",
    "GRADIENT_START": "#ffffff",
    "GRADIENT_END": "#f0f0f0"
}

THEMES = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME
}

# Compatibility Constants (Default to Dark)
COLOR_UP = DARK_THEME["COLOR_UP"]
COLOR_DOWN = DARK_THEME["COLOR_DOWN"]
COLOR_FLAT = DARK_THEME["COLOR_FLAT"]
MINI_BG_COLOR = DARK_THEME["MINI_BG_COLOR"]
MINI_BG_HOVER_COLOR = DARK_THEME["MINI_BG_HOVER_COLOR"]

# Template
STYLESHEET_TEMPLATE = """
/* Base Application Style */
QMainWindow, QDialog {{
    background-color: {APP_BG};
    color: {TEXT_COLOR};
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    font-size: 14px;
}}

/* Generic Widget Defaults - Instead of * */
QWidget {{
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    font-size: 14px;
    outline: none;
    color: {TEXT_COLOR};
    /* NO global background-color here to prevent transparency issues */
}}

/* --- Container & Layout Widgets --- */
QFrame, QWidget#central_widget {{
    background-color: transparent;
}}

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QGroupBox {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 15px;
    font-weight: bold;
    color: {TEXT_COLOR};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}}

/* --- Text & Labels --- */
QLabel {{
    background-color: transparent;
    color: {TEXT_COLOR};
    padding: 0px;
}}
QLabel[class="text-secondary"] {{
    color: {TEXT_SECONDARY};
    font-size: 11px;
}}
QLabel[class="text-title"] {{
    color: {TEXT_COLOR};
    font-size: 16px;
    font-weight: bold;
}}
QLabel[class="text-brand"] {{
    color: {BRAND_PRIMARY};
    font-weight: bold;
}}

/* --- Input Widgets --- */
QLineEdit {{
    background-color: {WIDGET_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    padding: 6px 10px;
    color: {TEXT_COLOR};
    selection-background-color: {BRAND_PRIMARY};
    selection-color: #ffffff;
}}
QLineEdit:focus {{
    border: 1px solid {BRAND_PRIMARY};
}}
QLineEdit::placeholder {{
    color: {TEXT_SECONDARY};
}}

QComboBox, QDoubleSpinBox {{
    background-color: {WIDGET_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    padding: 5px 10px;
    min-height: 25px;
    color: {TEXT_COLOR};
    selection-background-color: {BRAND_PRIMARY};
    selection-color: #ffffff;
}}
QComboBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {BRAND_PRIMARY};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {WIDGET_BG};
    border: 1px solid {BORDER_COLOR};
    selection-background-color: {BRAND_PRIMARY};
    selection-color: #ffffff;
    color: {TEXT_COLOR};
    outline: none;
}}

/* --- List & Table Widgets --- */
QListWidget {{
    background-color: {WIDGET_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    color: {TEXT_COLOR};
    outline: none;
}}
QListWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {BORDER_COLOR};
    color: {TEXT_COLOR};
}}
QListWidget::item:selected {{
    background-color: {SELECTION_BG};
    color: {SELECTION_COLOR};
}}

QTableWidget {{
    background-color: {WIDGET_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    gridline-color: {BORDER_COLOR};
    selection-background-color: {SELECTION_BG};
    selection-color: {SELECTION_COLOR};
    alternate-background-color: {TABLE_ALT_BG};
    color: {TEXT_COLOR};
}}
QTableWidget::item {{
    padding: 6px 4px;
    border-bottom: 1px solid {BORDER_COLOR};
}}
QTableWidget::item:selected {{
    background-color: {SELECTION_BG};
    color: {SELECTION_COLOR};
}}
QTableWidget::item:hover {{
    background-color: {HOVER_COLOR}; 
}}

QHeaderView {{
    background-color: {HEADER_BG};
    border: none;
}}
QHeaderView::section {{
    background-color: {HEADER_BG};
    padding: 8px;
    border: none;
    border-bottom: 2px solid {BORDER_COLOR};
    font-weight: 600;
    color: {TEXT_SECONDARY};
}}

/* --- Buttons --- */
QPushButton {{
    background-color: {BTN_BG};
    border: 1px solid {BTN_BORDER};
    padding: 5px 15px;
    border-radius: 4px;
    color: {TEXT_COLOR};
}}
QPushButton:hover {{
    background-color: {BTN_HOVER};
    border-color: {BRAND_PRIMARY};
}}
QPushButton:pressed {{
    background-color: {BTN_PRESSED};
}}
QPushButton:disabled {{
    background-color: {APP_BG};
    color: {TEXT_SECONDARY};
    border-color: {BORDER_COLOR};
}}

/* Special Buttons */
QPushButton[class="btn-primary"] {{
    background-color: {BRAND_SECONDARY};
    color: #ffffff;
    font-weight: bold;
    border: none;
}}
QPushButton[class="btn-primary"]:hover {{
    background-color: {BRAND_PRIMARY}; 
}}

QPushButton[class="btn-danger"] {{
    background-color: transparent;
    border: 1px solid {STATUS_ERR};
    color: {STATUS_ERR};
}}
QPushButton[class="btn-danger"]:hover {{
    background-color: {STATUS_ERR};
    color: #ffffff;
}}

/* Table Operation Buttons */
QPushButton[class="table_btn_up"], QPushButton[class="table_btn_down"] {{
    background-color: {TABLE_BTN_BG};
    border: none;
    border-radius: 3px;
    color: {TABLE_BTN_COLOR};
    padding: 4px;
    font-size: 14px;
}}
QPushButton[class="table_btn_up"]:hover, QPushButton[class="table_btn_down"]:hover {{
    background-color: {TABLE_BTN_HOVER};
    color: {TEXT_COLOR};
}}

QPushButton[class="table_btn_alert"] {{
    background-color: transparent;
    border: 1px solid {STATUS_WARN};
    border-radius: 3px;
    color: {STATUS_WARN};
    padding: 2px;
    font-size: 12px;
    max-width: 24px;
    max-height: 24px;
}}
QPushButton[class="table_btn_alert"]:hover {{
    background-color: {STATUS_WARN};
    color: #ffffff;
}}

QPushButton[class="table_btn_del"] {{
    background-color: transparent;
    border: 1px solid {STATUS_ERR};
    border-radius: 3px;
    color: {STATUS_ERR};
    padding: 2px;
    font-size: 16px;
    font-weight: bold;
    max-width: 24px;
    max-height: 24px;
}}
QPushButton[class="table_btn_del"]:hover {{
    background-color: {STATUS_ERR};
    color: #ffffff;
}}

/* --- Menus & Tooltips --- */
QMenu {{
    background-color: {WIDGET_BG};
    border: 1px solid {BORDER_COLOR};
    padding: 4px;
    border-radius: 4px;
}}
QMenu::item {{
    padding: 6px 24px;
    color: {TEXT_COLOR};
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: {BRAND_PRIMARY};
    color: #ffffff;
}}
QMenu::separator {{
    height: 1px;
    background: {BORDER_COLOR};
    margin: 4px 0px;
}}

QToolTip {{
    background-color: {WIDGET_BG};
    color: {TEXT_COLOR};
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    padding: 4px 8px;
}}

/* --- ScrollBars --- */
QScrollBar:vertical {{
    border: none;
    background: {APP_BG};
    width: 10px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {SCROLL_HANDLE};
    min-height: 20px;
    border-radius: 5px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: {BRAND_PRIMARY};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

QScrollBar:horizontal {{
    border: none;
    background: {APP_BG};
    height: 10px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background: {SCROLL_HANDLE};
    min-width: 20px;
    border-radius: 5px;
    margin: 2px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {BRAND_PRIMARY};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}

/* --- Chart Dialog Text --- */
QLabel[class="chart-title"] {{
    font-size: 16px; 
    font-weight: bold;
    color: {BRAND_PRIMARY};
}}
QLabel[class="chart-price"] {{
    font-size: 18px; 
    font-weight: bold;
}}
QLabel[class="chart-change"] {{
    font-size: 14px;
}}
QLabel[class="chart-placeholder"] {{
    font-size: 14px;
    color: {TEXT_SECONDARY};
}}
"""

def get_stylesheet(theme):
    return STYLESHEET_TEMPLATE.format(**theme)
