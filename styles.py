MAIN_STYLE = """
    QWidget {
        background-color: #000000;
        color: #FFFFFF;
        font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
    }
    
    /* Main Window */
    QMainWindow, QWidget#centralWidget {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #121212, stop:1 #000000);
    }
    
    /* Search Box */
    QLineEdit {
        background-color: #2A2A2A;
        border: 2px solid #3A3A3A;
        border-radius: 25px;
        padding: 12px 25px;
        color: #FFFFFF;
        font-size: 14px;
        selection-background-color: #1DB954;
    }
    QLineEdit:focus {
        border: 2px solid #1DB954;
        background-color: #333333;
    }
    QLineEdit::placeholder {
        color: #727272;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #1DB954;
        color: #FFFFFF;
        border: none;
        border-radius: 25px;
        padding: 12px 35px;
        font-size: 14px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #1ED760;
        transform: scale(1.05);
    }
    QPushButton:pressed {
        background-color: #1AA34A;
    }
    QPushButton:disabled {
        background-color: #2A2A2A;
        color: #727272;
    }
    
    /* Control Buttons */
    QPushButton#controlBtn {
        background-color: #2A2A2A;
        border-radius: 50%;
        padding: 0px;
    }
    QPushButton#controlBtn:hover {
        background-color: #3A3A3A;
    }
    QPushButton#playBtn {
        background-color: #1DB954;
        border-radius: 50%;
        padding: 0px;
    }
    QPushButton#playBtn:hover {
        background-color: #1ED760;
        min-width: 75px;
        max-width: 75px;
        min-height: 75px;
        max-height: 75px;
    }
    
    /* List Widget */
    QListWidget {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 12px;
        padding: 8px;
        outline: none;
    }
    QListWidget::item {
        background-color: #282828;
        padding: 15px;
        border-radius: 8px;
        margin: 3px 0;
        border: 1px solid transparent;
    }
    QListWidget::item:selected {
        background-color: #2A2A2A;
        border: 1px solid #1DB954;
        color: #1DB954;
    }
    QListWidget::item:hover {
        background-color: #333333;
        border: 1px solid #404040;
    }
    QListWidget::item:hover:!selected {
        background-color: #3A3A3A;
    }
    QListWidget::scrollbar {
        background: #121212;
        width: 8px;
        border-radius: 4px;
    }
    QListWidget::scrollbar::handle {
        background: #4A4A4A;
        border-radius: 4px;
    }
    QListWidget::scrollbar::handle:hover {
        background: #5A5A5A;
    }
    
    /* Labels */
    QLabel {
        color: #FFFFFF;
        background: transparent;
    }
    QLabel#headerLabel {
        color: #1DB954;
        font-size: 32px;
        font-weight: 700;
        padding: 10px;
    }
    QLabel#nowPlayingLabel {
        color: #1DB954;
        font-size: 16px;
        font-weight: 600;
    }
    QLabel#timeLabel {
        color: #B3B3B3;
        font-size: 12px;
    }
    QLabel#statusLabel {
        color: #FF6B6B;
        font-size: 12px;
        font-style: italic;
    }
    
    /* Sliders */
    QSlider::groove:horizontal {
        background: #2A2A2A;
        height: 8px;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: #FFFFFF;
        width: 20px;
        margin: -6px 0;
        border-radius: 10px;
    }
    QSlider::handle:horizontal:hover {
        background: #1DB954;
        width: 24px;
        margin: -8px 0;
        border-radius: 12px;
    }
    QSlider::sub-page:horizontal {
        background: #1DB954;
        border-radius: 4px;
    }
    QSlider::add-page:horizontal {
        background: #2A2A2A;
        border-radius: 4px;
    }
    
    /* Progress Bar */
    QProgressBar {
        background: #2A2A2A;
        border-radius: 4px;
        height: 8px;
        text-align: center;
        border: none;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #1DB954, stop:1 #1ED760);
        border-radius: 4px;
    }
    
    /* Group Box */
    QGroupBox {
        border: 2px solid #2A2A2A;
        border-radius: 12px;
        margin-top: 12px;
        padding-top: 10px;
        font-weight: 600;
        font-size: 14px;
    }
    QGroupBox::title {
        color: #1DB954;
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 8px;
    }
    
    /* Scroll Area */
    QScrollArea {
        border: none;
        background: transparent;
    }
    
    /* Tool Tip */
    QToolTip {
        background-color: #282828;
        color: #FFFFFF;
        border: 1px solid #404040;
        border-radius: 6px;
        padding: 8px;
        font-size: 12px;
    }
"""

# Alternative Dark Theme (Purple)
PURPLE_THEME = """
    QWidget {
        background-color: #0A0A0F;
        color: #FFFFFF;
    }
    QLineEdit {
        background-color: #1A1A2E;
        border: 2px solid #2D2D44;
        border-radius: 25px;
        padding: 12px 25px;
    }
    QLineEdit:focus {
        border: 2px solid #9D4EDD;
    }
    QPushButton {
        background-color: #9D4EDD;
        border-radius: 25px;
        padding: 12px 35px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #B06AE5;
    }
    QListWidget {
        background-color: #16213E;
        border: 1px solid #1A1A2E;
        border-radius: 12px;
    }
    QListWidget::item {
        background-color: #1A1A2E;
        padding: 15px;
        border-radius: 8px;
        margin: 3px 0;
    }
    QListWidget::item:selected {
        background-color: #0F3460;
        border: 1px solid #9D4EDD;
    }
    QSlider::groove:horizontal {
        background: #1A1A2E;
        height: 8px;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: #9D4EDD;
        width: 20px;
        margin: -6px 0;
        border-radius: 10px;
    }
    QSlider::sub-page:horizontal {
        background: #9D4EDD;
        border-radius: 4px;
    }
"""