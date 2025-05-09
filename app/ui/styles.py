"""
UI styling for the Fast SMS Alert System.
"""

# Dark theme style sheet for a modern, sleek appearance
DARK_THEME = """
QWidget {
    background-color: #2E2E2E;
    color: #EEEEEE;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

QMainWindow {
    background-color: #2E2E2E;
}

QTabWidget::pane {
    border: 1px solid #444444;
    background-color: #2E2E2E;
}

QTabBar::tab {
    background-color: #444444;
    color: #EEEEEE;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: #007BFF;
}

QLabel {
    color: #EEEEEE;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #444444;
    color: #EEEEEE;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #007BFF;
}

QPushButton {
    background-color: #007BFF;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #0069D9;
}

QPushButton:pressed {
    background-color: #005CBF;
}

QPushButton:disabled {
    background-color: #666666;
    color: #999999;
}

QPushButton#start_button {
    background-color: #28A745;
}

QPushButton#start_button:hover {
    background-color: #218838;
}

QPushButton#start_button:pressed {
    background-color: #1E7E34;
}

QPushButton#stop_button {
    background-color: #DC3545;
}

QPushButton#stop_button:hover {
    background-color: #C82333;
}

QPushButton#stop_button:pressed {
    background-color: #BD2130;
}

QPushButton#test_button {
    background-color: #FFC107;
    color: #212529;
}

QPushButton#test_button:hover {
    background-color: #E0A800;
}

QPushButton#test_button:pressed {
    background-color: #D39E00;
}

QGroupBox {
    border: 1px solid #444444;
    border-radius: 4px;
    margin-top: 12px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 3px;
}

QComboBox {
    background-color: #444444;
    color: #EEEEEE;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(assets/icons/down-arrow.png);
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #444444;
    border: 1px solid #555555;
    selection-background-color: #007BFF;
}

QScrollBar:vertical {
    border: none;
    background-color: #2E2E2E;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #666666;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #007BFF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #2E2E2E;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #666666;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #007BFF;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QStatusBar {
    background-color: #2E2E2E;
    color: #BBBBBB;
}

QMenuBar {
    background-color: #2E2E2E;
    color: #EEEEEE;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 10px;
}

QMenuBar::item:selected {
    background-color: #007BFF;
}

QMenu {
    background-color: #2E2E2E;
    border: 1px solid #444444;
}

QMenu::item {
    padding: 6px 20px;
}

QMenu::item:selected {
    background-color: #007BFF;
}
"""

# Function to get the appropriate style sheet based on the theme name
def get_stylesheet(theme_name: str = "dark") -> str:
    """
    Get the appropriate style sheet based on the theme name.
    
    Args:
        theme_name: Name of the theme to use
        
    Returns:
        str: Style sheet as a string
    """
    if theme_name.lower() == "dark":
        return DARK_THEME
    else:
        return DARK_THEME  # Default to dark theme for now 