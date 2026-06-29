MAIN_STYLE = """
    QWidget {
        background-color: #121212;
        color: white;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QLineEdit {
        background-color: #282828;
        border: 1px solid #404040;
        border-radius: 20px;
        padding: 10px 20px;
        color: white;
        font-size: 14px;
    }
    QPushButton {
        background-color: #1DB954;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 30px;
        font-size: 14px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1ed760;
    }
    QPushButton:disabled {
        background-color: #404040;
    }
    QListWidget {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 8px;
        padding: 8px;
    }
    QListWidget::item {
        background-color: #282828;
        padding: 10px;
        border-radius: 4px;
        margin: 2px 0;
    }
    QListWidget::item:selected {
        background-color: #2A2A2A;
        border-left: 3px solid #1DB954;
        color: #1DB954;
    }
    QListWidget::item:hover {
        background-color: #333333;
    }
    QLabel { color: white; }
    QSlider::groove:horizontal {
        background: #404040;
        height: 6px;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #1DB954;
        width: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }
    QSlider::sub-page:horizontal {
        background: #1DB954;
        border-radius: 3px;
    }
    QProgressBar {
        background: #404040;
        border-radius: 3px;
        height: 6px;
        text-align: center;
        color: white;
    }
    QProgressBar::chunk {
        background: #1DB954;
        border-radius: 3px;
    }
"""