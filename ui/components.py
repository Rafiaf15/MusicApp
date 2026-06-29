from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
import qtawesome as qta


class AlbumArtLabel(QLabel):
    """Label untuk menampilkan album art dengan efek"""
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 200)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #1A1A1A;
                border-radius: 10px;
                border: 3px solid #2A2A2A;
            }
        """)
        self.setText("🎵")
        self.setFont(QFont("Segoe UI", 60))
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(Qt.black)
        self.setGraphicsEffect(shadow)


class LoadingOverlay(QWidget):
    """Overlay loading indicator"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.7);
                border-radius: 10px;
            }
        """)
        self.setVisible(False)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Spinner icon
        self.spinner = QLabel()
        self.spinner.setPixmap(qta.icon('fa5s.spinner', color='#1DB954', size=48).pixmap(48, 48))
        self.spinner.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.spinner)
        
        # Rotate animation
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_spinner)
        self.rotation_angle = 0
        
        # Loading text
        self.loading_text = QLabel("Memuat...")
        self.loading_text.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.loading_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.loading_text)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: #2A2A2A;
                border-radius: 4px;
                height: 8px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background: #1DB954;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
    def show_loading(self, text="Memuat..."):
        self.loading_text.setText(text)
        self.progress_bar.setValue(0)
        self.setVisible(True)
        self.rotation_timer.start(50)
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def hide_loading(self):
        self.setVisible(False)
        self.rotation_timer.stop()
        
    def rotate_spinner(self):
        self.rotation_angle = (self.rotation_angle + 10) % 360
        self.spinner.setPixmap(
            qta.icon('fa5s.spinner', color='#1DB954', size=48).pixmap(48, 48)
        )
        
    def resizeEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)