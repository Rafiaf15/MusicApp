from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt

def create_icon():
    """Buat icon aplikasi sederhana"""
    pixmap = QPixmap(256, 256)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Background circle
    painter.setBrush(QColor("#1DB954"))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, 256, 256)
    
    # Music note
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawText(60, 180, "🎵")
    
    painter.end()
    
    pixmap.save("icon.png")
    print("✅ Icon saved as icon.png")

if __name__ == "__main__":
    create_icon()