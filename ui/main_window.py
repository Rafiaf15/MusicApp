from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QLabel, QSlider, 
    QMessageBox, QSystemTrayIcon, QMenu, QAction, QProgressBar,
    QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QSize, QUrl, QTimer
from PyQt5.QtGui import QFont, QIcon, QKeyEvent
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import qtawesome as qta
import os

from .components import AlbumArtLabel, LoadingOverlay
from .styles import MAIN_STYLE


class MainWindow(QWidget):
    """Optimized main window dengan better resource management"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("🎵 Music Player Pro")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet(MAIN_STYLE)
        self.setObjectName("centralWidget")
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Network manager dengan cache
        self.nam = QNetworkAccessManager()
        
        # UI state
        self._force_quit = False
        
        # Setup UI
        self.setup_ui()
        self.setup_tray_icon()
        
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Auto-hide status label
        self._status_timer = QTimer()
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._clear_status)
    
    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(30, 30, 30, 30)

        left_panel = self.create_left_panel()
        main_layout.addLayout(left_panel, 1)

        right_panel = self.create_right_panel()
        main_layout.addLayout(right_panel, 1)

        self.setLayout(main_layout)
        
        self.loading_overlay = LoadingOverlay(self)
    
    def create_left_panel(self):
        """Panel kiri: Album art, controls, progress"""
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Header - gunakan font default yang aman
        header = QLabel("🎵 Music Player Pro")
        header.setObjectName("headerLabel")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 24, QFont.Bold))  # Font yang aman
        layout.addWidget(header)

        # Album Art
        self.album_art = AlbumArtLabel()
        layout.addWidget(self.album_art, alignment=Qt.AlignCenter)

        # Now Playing Info
        self.now_playing_label = QLabel("Tidak ada lagu yang diputar")
        self.now_playing_label.setObjectName("nowPlayingLabel")
        self.now_playing_label.setAlignment(Qt.AlignCenter)
        self.now_playing_label.setWordWrap(True)
        layout.addWidget(self.now_playing_label)

        # Loading progress bar
        self.fetch_progress = QProgressBar()
        self.fetch_progress.setRange(0, 100)
        self.fetch_progress.setValue(0)
        self.fetch_progress.setVisible(False)
        self.fetch_progress.setFixedHeight(6)
        self.fetch_progress.setTextVisible(False)
        self.fetch_progress.setStyleSheet("""
            QProgressBar {
                background: #2A2A2A;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1DB954, stop:1 #1ED760);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.fetch_progress)

        # Progress Bar
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        layout.addWidget(self.progress_slider)

        # Time Labels
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("0:00")
        self.current_time_label.setObjectName("timeLabel")
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        self.duration_label = QLabel("0:00")
        self.duration_label.setObjectName("timeLabel")
        time_layout.addWidget(self.duration_label)
        layout.addLayout(time_layout)

        # Shuffle & Repeat buttons
        mode_layout = QHBoxLayout()
        mode_layout.addStretch()
        
        self.shuffle_btn = QPushButton()
        self.shuffle_btn.setObjectName("modeBtn")
        self.shuffle_btn.setFixedSize(45, 45)
        self.shuffle_btn.setIcon(qta.icon('fa5s.random', color='#B3B3B3', size=18))
        self.shuffle_btn.setIconSize(QSize(18, 18))
        self.shuffle_btn.setToolTip("Shuffle (S)")
        mode_layout.addWidget(self.shuffle_btn)
        
        self.repeat_btn = QPushButton()
        self.repeat_btn.setObjectName("modeBtn")
        self.repeat_btn.setFixedSize(45, 45)
        self.repeat_btn.setIcon(qta.icon('fa5s.sync', color='#B3B3B3', size=18))
        self.repeat_btn.setIconSize(QSize(18, 18))
        self.repeat_btn.setToolTip("Repeat (R)")
        mode_layout.addWidget(self.repeat_btn)
        
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Control Buttons
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()

        self.prev_btn = QPushButton()
        self.prev_btn.setObjectName("controlBtn")
        self.prev_btn.setFixedSize(60, 60)
        self.prev_btn.setIcon(qta.icon('fa5s.step-backward', color='white', size=24))
        self.prev_btn.setIconSize(QSize(24, 24))
        self.prev_btn.setToolTip("Previous (←)")
        self.prev_btn.setEnabled(False)
        controls_layout.addWidget(self.prev_btn)

        self.play_btn = QPushButton()
        self.play_btn.setObjectName("playBtn")
        self.play_btn.setFixedSize(80, 80)
        self.play_btn.setIcon(qta.icon('fa5s.play', color='white', size=32))
        self.play_btn.setIconSize(QSize(32, 32))
        self.play_btn.setToolTip("Play/Pause (Space)")
        self.play_btn.setEnabled(False)
        controls_layout.addWidget(self.play_btn)

        self.next_btn = QPushButton()
        self.next_btn.setObjectName("controlBtn")
        self.next_btn.setFixedSize(60, 60)
        self.next_btn.setIcon(qta.icon('fa5s.step-forward', color='white', size=24))
        self.next_btn.setIconSize(QSize(24, 24))
        self.next_btn.setToolTip("Next (→)")
        self.next_btn.setEnabled(False)
        controls_layout.addWidget(self.next_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Volume Control
        volume_layout = QHBoxLayout()
        self.volume_icon_btn = QPushButton()
        self.volume_icon_btn.setFixedSize(30, 30)
        self.volume_icon_btn.setIcon(qta.icon('fa5s.volume-up', color='white', size=16))
        self.volume_icon_btn.setIconSize(QSize(16, 16))
        self.volume_icon_btn.setToolTip("Volume (↑/↓)")
        self.volume_icon_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background: #333333;
                border-radius: 4px;
            }
        """)
        volume_layout.addWidget(self.volume_icon_btn)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(200)
        volume_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("70%")
        self.volume_label.setObjectName("timeLabel")
        volume_layout.addWidget(self.volume_label)
        layout.addLayout(volume_layout)

        # Status Label dengan opacity effect
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.8)
        self.status_label.setGraphicsEffect(opacity_effect)
        
        layout.addWidget(self.status_label)

        # Keyboard shortcuts hint
        hint_label = QLabel("⌨️ Space: Play  |  ←→: Prev/Next  |  ↑↓: Vol  |  Ctrl+Q: Quit  |  Esc: Minimize")
        hint_label.setStyleSheet("color: #727272; font-size: 10px; margin-top: 10px;")
        hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint_label)

        layout.addStretch()
        return layout
    
    def create_right_panel(self):
        """Panel kanan: Search dan song list"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Search Section
        search_layout_h = QHBoxLayout()
        search_icon = QLabel()
        search_icon.setPixmap(qta.icon('fa5s.search', color='#1DB954', size=20).pixmap(20, 20))
        search_layout_h.addWidget(search_icon)
        
        search_label = QLabel("Cari Lagu")
        search_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        search_layout_h.addWidget(search_label)
        search_layout_h.addStretch()
        layout.addLayout(search_layout_h)

        search_box_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Masukkan judul lagu atau artis...")
        search_box_layout.addWidget(self.search_box)

        self.search_btn = QPushButton()
        self.search_btn.setIcon(qta.icon('fa5s.search', color='white', size=16))
        self.search_btn.setIconSize(QSize(16, 16))
        self.search_btn.setFixedSize(80, 40)
        self.search_btn.setToolTip("Cari (Enter)")
        search_box_layout.addWidget(self.search_btn)
        layout.addLayout(search_box_layout)

        # Loading Label
        self.loading_label = QLabel("")
        self.loading_label.setStyleSheet("color: #1DB954; font-size: 12px;")
        layout.addWidget(self.loading_label)

        # Song List
        list_layout_h = QHBoxLayout()
        list_icon = QLabel()
        list_icon.setPixmap(qta.icon('fa5s.list', color='#1DB954', size=20).pixmap(20, 20))
        list_layout_h.addWidget(list_icon)
        
        list_label = QLabel("Daftar Lagu")
        list_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        list_layout_h.addWidget(list_label)
        
        self.song_count_label = QLabel("")
        self.song_count_label.setStyleSheet("color: #B3B3B3; font-size: 12px;")
        list_layout_h.addWidget(self.song_count_label)
        list_layout_h.addStretch()
        layout.addLayout(list_layout_h)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #181818;
                border: 1px solid #282828;
                border-radius: 8px;
                padding: 8px;
                color: white;
                outline: none;
            }
            QListWidget::item {
                background-color: #282828;
                padding: 10px;
                border-radius: 4px;
                margin: 2px 0;
                border-left: 3px solid transparent;
            }
            QListWidget::item:selected {
                background-color: #2A2A2A;
                border-left: 3px solid #1DB954;
                color: #1DB954;
            }
            QListWidget::item:hover {
                background-color: #333333;
            }
        """)
        layout.addWidget(self.list_widget)

        return layout
    
    def setup_tray_icon(self):
        """Setup system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("⚠️ System tray tidak tersedia")
            self.tray_icon = None
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icon.png')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(qta.icon('fa5s.music', color='#1DB954', size=32))
        
        self.tray_icon.setToolTip("🎵 Music Player Pro")
        
        tray_menu = QMenu()
        
        # Simpan semua action sebagai attribute
        self.tray_play_action = QAction("▶ Play")
        tray_menu.addAction(self.tray_play_action)
        
        self.tray_next_action = QAction("⏭ Next")
        tray_menu.addAction(self.tray_next_action)
        
        self.tray_prev_action = QAction("⏮ Previous")
        tray_menu.addAction(self.tray_prev_action)
        
        tray_menu.addSeparator()
        
        self.tray_show_action = QAction("👁 Show Window")
        tray_menu.addAction(self.tray_show_action)
        
        self.tray_quit_action = QAction("❌ Quit")
        tray_menu.addAction(self.tray_quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
    
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_from_tray()
    
    def show_from_tray(self):
        self.show()
        self.showNormal()
        self.activateWindow()
    
    def show_status_message(self, message, timeout=3000):
        """Show status message dengan auto-hide"""
        self.status_label.setText(message)
        self._status_timer.start(timeout)
    
    def _clear_status(self):
        """Clear status label"""
        self.status_label.setText("")
    
def closeEvent(self, event):
    """Override close event - tanya user mau minimize atau quit"""
    # Cek apakah dipanggil dari quit_app (sudah konfirmasi)
    if self._force_quit:
        self._force_quit = False
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.hide()
        event.accept()
        return
    
    # Buat dialog custom yang lebih rapi
    msg_box = QMessageBox(self)
    msg_box.setWindowTitle("Keluar Aplikasi")
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setText("<b style='font-size: 14px;'>Apa yang ingin Anda lakukan?</b>")
    msg_box.setInformativeText(
        "<span style='color: #B3B3B3; font-size: 12px;'>"
        "Minimize untuk menjalankan di background,<br>"
        "atau Quit untuk keluar sepenuhnya."
        "</span>"
    )
    
    # Tambah button custom dengan styling berbeda
    btn_minimize = msg_box.addButton("📍  Minimize", QMessageBox.AcceptRole)
    btn_quit = msg_box.addButton("❌  Quit", QMessageBox.DestructiveRole)
    btn_cancel = msg_box.addButton("Batal", QMessageBox.RejectRole)
    
    msg_box.setDefaultButton(btn_minimize)
    
    # Styling dialog yang lebih rapi dan konsisten
    msg_box.setStyleSheet("""
        /* Background dialog */
        QMessageBox {
            background-color: #282828;
            color: white;
            border: 1px solid #3E3E3E;
        }
        
        /* Icon dan label utama */
        QMessageBox QLabel#qt_msgbox_label,
        QMessageBox QLabel#qt_msgboxex_icon_label {
            color: white;
            background: transparent;
            min-width: 300px;
        }
        
        /* Informative text */
        QMessageBox QLabel {
            color: #B3B3B3;
            font-size: 12px;
            padding: 5px;
            background: transparent;
        }
        
        /* Semua tombol - base style */
        QMessageBox QPushButton {
            color: white;
            border: none;
            border-radius: 18px;
            padding: 10px 24px;
            font-weight: bold;
            font-size: 13px;
            min-width: 120px;
            min-height: 36px;
        }
        
        /* Tombol Minimize - Hijau (Spotify) */
        QMessageBox QPushButton[text*="Minimize"] {
            background-color: #1DB954;
        }
        QMessageBox QPushButton[text*="Minimize"]:hover {
            background-color: #1ED760;
        }
        QMessageBox QPushButton[text*="Minimize"]:pressed {
            background-color: #1AA34A;
        }
        
        /* Tombol Quit - Merah (Destructive) */
        QMessageBox QPushButton[text*="Quit"] {
            background-color: #E22134;
        }
        QMessageBox QPushButton[text*="Quit"]:hover {
            background-color: #FF2A40;
        }
        QMessageBox QPushButton[text*="Quit"]:pressed {
            background-color: #C41E2E;
        }
        
        /* Tombol Batal - Abu-abu (Neutral) */
        QMessageBox QPushButton[text*="Batal"] {
            background-color: #3E3E3E;
        }
        QMessageBox QPushButton[text*="Batal"]:hover {
            background-color: #4E4E4E;
        }
        QMessageBox QPushButton[text*="Batal"]:pressed {
            background-color: #2E2E2E;
        }
        
        /* Focus state untuk accessibility */
        QMessageBox QPushButton:focus {
            outline: 2px solid #1DB954;
            outline-offset: 2px;
        }
    """)
    
    msg_box.exec_()
    
    clicked = msg_box.clickedButton()
    
    if clicked == btn_quit:
        self._force_quit = True
        self.close()
    elif clicked == btn_minimize:
        if hasattr(self, 'tray_icon') and self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "Music Player Pro",
                "🎵 Aplikasi berjalan di background.\nKlik kanan icon tray untuk menu.",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            self._force_quit = True
            self.close()
    else:
        event.ignore()
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, '_status_timer'):
            self._status_timer.stop()