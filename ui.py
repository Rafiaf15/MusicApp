from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QLabel, QSlider, 
    QMessageBox, QFrame, QGraphicsDropShadowEffect,
    QSystemTrayIcon, QMenu, QAction, QProgressBar, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QSize, QUrl
from PyQt5.QtGui import QFont, QPixmap, QIcon, QKeyEvent
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import vlc
import os
import random
import qtawesome as qta 

from threads import SearchThread, URLFetchThread
from styles import MAIN_STYLE


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


class MusicApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🎵 Music Player Pro")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet(MAIN_STYLE)
        self.setObjectName("centralWidget")
        
        # ✅ NEW: Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Data songs
        self.songs = []
        self.audio_urls = {}  # Cache URL: index -> url
        self.current_index = -1
        self.audio_url = None
        self.is_playing = False
        self.duration_ms = 0
        
        # ✅ NEW: Shuffle & Repeat states
        self.shuffle_mode = False
        self.repeat_mode = 0  # 0=no repeat, 1=repeat all, 2=repeat one
        self.play_history = []  # History untuk previous saat shuffle
        self.shuffled_indices = []  # Order acak untuk shuffle
        
        # ✅ NEW: Loading state
        self.is_loading = False
        self._force_quit = False  # Flag untuk quit tanpa dialog

        # VLC Instance
        self.vlc_instance = vlc.Instance('--no-xlib', '--quiet')
        self.player = self.vlc_instance.media_player_new()
        
        # Network manager untuk album art
        self.nam = QNetworkAccessManager()
        
        # Timer untuk update progress
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(500)
        
        # ✅ NEW: Spinner animation timer
        self.spinner_timer = QTimer()
        self.spinner_timer.timeout.connect(self.animate_spinner)
        self.spinner_angle = 0

        self.setup_ui()
        self.setup_tray_icon()  # ✅ NEW: System tray
        self.player.audio_set_volume(70)
        
        # Focus ke window agar keyboard shortcuts bekerja
        self.setFocusPolicy(Qt.StrongFocus)

    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # LEFT PANEL - Player Controls
        left_panel = self.create_left_panel()
        main_layout.addLayout(left_panel, 1)

        # RIGHT PANEL - Song List
        right_panel = self.create_right_panel()
        main_layout.addLayout(right_panel, 1)

        self.setLayout(main_layout)
        
        # ✅ NEW: Loading overlay
        self.loading_overlay = LoadingOverlay(self)

    def create_left_panel(self):
        """Panel kiri: Album art, controls, progress"""
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Header
        header = QLabel("🎵 Music Player Pro")
        header.setObjectName("headerLabel")
        header.setAlignment(Qt.AlignCenter)
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

        # ✅ NEW: Loading progress bar di bawah now playing
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
        self.progress_slider.sliderMoved.connect(self.seek_to)
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

        # ✅ NEW: Shuffle & Repeat buttons (di atas control buttons)
        mode_layout = QHBoxLayout()
        mode_layout.addStretch()
        
        self.shuffle_btn = QPushButton()
        self.shuffle_btn.setObjectName("modeBtn")
        self.shuffle_btn.setFixedSize(45, 45)
        self.shuffle_btn.setIcon(qta.icon('fa5s.random', color='#B3B3B3', size=18))
        self.shuffle_btn.setIconSize(QSize(18, 18))
        self.shuffle_btn.setToolTip("Shuffle (S)")
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.shuffle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 22px;
            }
            QPushButton:hover {
                background: #2A2A2A;
            }
        """)
        mode_layout.addWidget(self.shuffle_btn)
        
        self.repeat_btn = QPushButton()
        self.repeat_btn.setObjectName("modeBtn")
        self.repeat_btn.setFixedSize(45, 45)
        self.repeat_btn.setIcon(qta.icon('fa5s.sync', color='#B3B3B3', size=18))
        self.repeat_btn.setIconSize(QSize(18, 18))
        self.repeat_btn.setToolTip("Repeat (R)")
        self.repeat_btn.clicked.connect(self.toggle_repeat)
        self.repeat_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 22px;
            }
            QPushButton:hover {
                background: #2A2A2A;
            }
        """)
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
        self.prev_btn.clicked.connect(self.play_previous)
        self.prev_btn.setEnabled(False)
        controls_layout.addWidget(self.prev_btn)

        self.play_btn = QPushButton()
        self.play_btn.setObjectName("playBtn")
        self.play_btn.setFixedSize(80, 80)
        self.play_btn.setIcon(qta.icon('fa5s.play', color='white', size=32))
        self.play_btn.setIconSize(QSize(32, 32))
        self.play_btn.setToolTip("Play/Pause (Space)")
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setEnabled(False)
        controls_layout.addWidget(self.play_btn)

        self.next_btn = QPushButton()
        self.next_btn.setObjectName("controlBtn")
        self.next_btn.setFixedSize(60, 60)
        self.next_btn.setIcon(qta.icon('fa5s.step-forward', color='white', size=24))
        self.next_btn.setIconSize(QSize(24, 24))
        self.next_btn.setToolTip("Next (→)")
        self.next_btn.clicked.connect(self.play_next)
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
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_slider.setFixedWidth(200)
        volume_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("70%")
        self.volume_label.setObjectName("timeLabel")
        volume_layout.addWidget(self.volume_label)
        layout.addLayout(volume_layout)

        # Status Label
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # ✅ UPDATED: Keyboard shortcuts hint
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
        self.search_box.returnPressed.connect(self.search_music)
        search_box_layout.addWidget(self.search_box)

        self.search_btn = QPushButton()
        self.search_btn.setIcon(qta.icon('fa5s.search', color='white', size=16))
        self.search_btn.setIconSize(QSize(16, 16))
        self.search_btn.setFixedSize(80, 40)
        self.search_btn.setToolTip("Cari (Enter)")
        self.search_btn.clicked.connect(self.search_music)
        search_box_layout.addWidget(self.search_btn)
        layout.addLayout(search_box_layout)

        # ✅ NEW: Better Loading Label dengan progress
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
        
        # ✅ NEW: Song count label
        self.song_count_label = QLabel("")
        self.song_count_label.setStyleSheet("color: #B3B3B3; font-size: 12px;")
        list_layout_h.addWidget(self.song_count_label)
        list_layout_h.addStretch()
        layout.addLayout(list_layout_h)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.play_selected)
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

    # ==================== SYSTEM TRAY ====================
    def setup_tray_icon(self):
        """Setup system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("⚠️ System tray tidak tersedia")
            self.tray_icon = None
            return
            
        # Buat tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Pakai icon dari file atau fallback ke qtawesome
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(qta.icon('fa5s.music', color='#1DB954', size=32))
            
        self.tray_icon.setToolTip("🎵 Music Player Pro")
        
        # Menu tray
        tray_menu = QMenu()
        
        # Play/Pause action
        self.tray_play_action = QAction("▶ Play")
        self.tray_play_action.triggered.connect(self.toggle_play)
        tray_menu.addAction(self.tray_play_action)
        
        # Next action
        tray_next_action = QAction("⏭ Next")
        tray_next_action.triggered.connect(self.play_next)
        tray_menu.addAction(tray_next_action)
        
        # Previous action
        tray_prev_action = QAction("⏮ Previous")
        tray_prev_action.triggered.connect(self.play_previous)
        tray_menu.addAction(tray_prev_action)
        
        tray_menu.addSeparator()
        
        # Show action
        tray_show_action = QAction("👁 Show Window")
        tray_show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(tray_show_action)
        
        # Quit action
        tray_quit_action = QAction("❌ Quit")
        tray_quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(tray_quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Double click tray icon untuk show window
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        """Handle tray icon click"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_from_tray()

    def show_from_tray(self):
        """Show window dari tray"""
        self.show()
        self.showNormal()
        self.activateWindow()

    def quit_app(self):
        """Quit aplikasi dari tray"""
        self._force_quit = True
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.hide()
        self.close()

    def closeEvent(self, event):
        """Override close event - tanya user mau minimize atau quit"""
        # Cek apakah dipanggil dari quit_app (sudah konfirmasi)
        if self._force_quit:
            self._force_quit = False
            self.player.stop()
            self.timer.stop()
            self.spinner_timer.stop()
            if hasattr(self, 'thread') and self.thread.isRunning():
                self.thread.quit()
                self.thread.wait()
            if hasattr(self, 'url_thread') and self.url_thread.isRunning():
                self.url_thread.quit()
                self.url_thread.wait()
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.hide()
            event.accept()
            return
        
        # Tampilkan dialog konfirmasi
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Keluar Aplikasi")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText("<b>Apa yang ingin Anda lakukan?</b>")
        msg_box.setInformativeText("Minimize untuk menjalankan di background, atau Quit untuk keluar sepenuhnya.")
        
        # Tambah button custom
        btn_minimize = msg_box.addButton("📍 Minimize", QMessageBox.AcceptRole)
        btn_quit = msg_box.addButton("❌ Quit", QMessageBox.DestructiveRole)
        btn_cancel = msg_box.addButton("Batal", QMessageBox.RejectRole)
        
        msg_box.setDefaultButton(btn_minimize)
        
        # Styling dialog
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #282828;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 13px;
            }
            QMessageBox QPushButton {
                background-color: #1DB954;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 100px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1ED760;
            }
        """)
        
        msg_box.exec_()
        
        clicked = msg_box.clickedButton()
        
        if clicked == btn_quit:
            # ✅ Quit aplikasi
            self._force_quit = True
            self.close()  # Recursive call, akan di-handle di atas
            
        elif clicked == btn_minimize:
            # ✅ Minimize ke tray
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
                # Tray tidak tersedia, langsung quit
                self._force_quit = True
                self.close()
        else:
            # Batal
            event.ignore()

    # ==================== KEYBOARD SHORTCUTS ====================
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard shortcuts"""
        key = event.key()
        modifiers = event.modifiers()
        
        # ✅ Ctrl+Q = Instant Quit
        if key == Qt.Key_Q and modifiers == Qt.ControlModifier:
            self._force_quit = True
            self.close()
            event.accept()
            return
        
        # ✅ Escape = Minimize ke tray
        if key == Qt.Key_Escape:
            if hasattr(self, 'tray_icon') and self.tray_icon and self.tray_icon.isVisible():
                self.hide()
                event.accept()
                return
        
        # Space: Play/Pause
        if key == Qt.Key_Space:
            self.toggle_play()
            event.accept()
            
        # Arrow Left: Previous
        elif key == Qt.Key_Left:
            self.play_previous()
            event.accept()
            
        # Arrow Right: Next
        elif key == Qt.Key_Right:
            self.play_next()
            event.accept()
            
        # Arrow Up: Volume Up
        elif key == Qt.Key_Up:
            new_volume = min(100, self.volume_slider.value() + 5)
            self.volume_slider.setValue(new_volume)
            event.accept()
            
        # Arrow Down: Volume Down
        elif key == Qt.Key_Down:
            new_volume = max(0, self.volume_slider.value() - 5)
            self.volume_slider.setValue(new_volume)
            event.accept()
            
        # M: Mute/Unmute
        elif key == Qt.Key_M:
            if self.player.audio_get_volume() > 0:
                self.player.audio_set_mute(True)
                self.status_label.setText("🔇 Muted")
            else:
                self.player.audio_set_mute(False)
                self.status_label.setText("🔊 Unmuted")
            event.accept()
            
        # S: Toggle Shuffle
        elif key == Qt.Key_S:
            self.toggle_shuffle()
            event.accept()
            
        # R: Toggle Repeat
        elif key == Qt.Key_R:
            self.toggle_repeat()
            event.accept()
            
        else:
            super().keyPressEvent(event)

    # ==================== SHUFFLE & REPEAT ====================
    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        self.shuffle_mode = not self.shuffle_mode
        
        if self.shuffle_mode:
            # Generate shuffled order
            self.shuffled_indices = list(range(len(self.songs)))
            random.shuffle(self.shuffled_indices)
            
            # Highlight current position
            if self.current_index >= 0 and self.current_index in self.shuffled_indices:
                self.shuffled_indices.remove(self.current_index)
                self.shuffled_indices.insert(0, self.current_index)
            
            self.shuffle_btn.setIcon(qta.icon('fa5s.random', color='#1DB954', size=18))
            self.status_label.setText("🔀 Shuffle ON")
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.showMessage("Shuffle", "Mode acak aktif", QSystemTrayIcon.Information, 1500)
        else:
            self.shuffle_btn.setIcon(qta.icon('fa5s.random', color='#B3B3B3', size=18))
            self.status_label.setText("🔀 Shuffle OFF")
            self.shuffled_indices = []

    def toggle_repeat(self):
        """Toggle repeat mode: 0=no repeat, 1=repeat all, 2=repeat one"""
        self.repeat_mode = (self.repeat_mode + 1) % 3
        
        if self.repeat_mode == 0:
            self.repeat_btn.setIcon(qta.icon('fa5s.sync', color='#B3B3B3', size=18))
            self.status_label.setText("🔁 Repeat OFF")
        elif self.repeat_mode == 1:
            self.repeat_btn.setIcon(qta.icon('fa5s.sync', color='#1DB954', size=18))
            self.status_label.setText("🔁 Repeat ALL")
        elif self.repeat_mode == 2:
            self.repeat_btn.setIcon(qta.icon('fa5s.redo', color='#1DB954', size=18))
            self.status_label.setText("🔂 Repeat ONE")

    def get_next_index(self):
        """Get next index berdasarkan mode shuffle/repeat"""
        if not self.songs:
            return -1
            
        if self.repeat_mode == 2:
            # Repeat one: kembali ke index yang sama
            return self.current_index
            
        if self.shuffle_mode and self.shuffled_indices:
            # Shuffle mode
            try:
                current_pos = self.shuffled_indices.index(self.current_index)
                if current_pos + 1 < len(self.shuffled_indices):
                    return self.shuffled_indices[current_pos + 1]
                elif self.repeat_mode == 1:
                    # Repeat all: shuffle ulang
                    random.shuffle(self.shuffled_indices)
                    return self.shuffled_indices[0]
                else:
                    return -1  # Stop
            except ValueError:
                return self.shuffled_indices[0] if self.shuffled_indices else -1
        else:
            # Normal mode
            next_idx = self.current_index + 1
            if next_idx < len(self.songs):
                return next_idx
            elif self.repeat_mode == 1:
                return 0  # Repeat all: kembali ke awal
            else:
                return -1  # Stop

    def get_previous_index(self):
        """Get previous index"""
        if not self.songs:
            return -1
            
        if self.shuffle_mode and self.play_history:
            return self.play_history.pop()
        else:
            prev_idx = self.current_index - 1
            if prev_idx >= 0:
                return prev_idx
            elif self.repeat_mode == 1:
                return len(self.songs) - 1
            else:
                return -1

    # ==================== SEARCH ====================
    def search_music(self):
        query = self.search_box.text().strip()
        if not query:
            return

        self.search_btn.setEnabled(False)
        self.search_btn.setIcon(qta.icon('fa5s.spinner', color='white', size=16, spin=True))
        self.list_widget.clear()
        self.list_widget.addItem("🔍 Mencari lagu...")
        self.loading_label.setText("⏳ Sedang mencari...")
        self.status_label.setText("")
        self.audio_urls.clear()
        self.song_count_label.setText("")
        self.fetch_progress.setVisible(False)

        self.thread = SearchThread(query)
        self.thread.finished.connect(self.on_search_finished)
        self.thread.error.connect(self.on_search_error)
        self.thread.start()

    def on_search_finished(self, results):
        self.search_btn.setEnabled(True)
        self.search_btn.setIcon(qta.icon('fa5s.search', color='white', size=16))
        self.songs = results
        self.list_widget.clear()

        if not self.songs:
            self.list_widget.addItem("❌ Tidak ada hasil ditemukan")
            self.loading_label.setText("")
            self.song_count_label.setText("")
            return

        for i, song in enumerate(self.songs):
            title = song.get('title', 'Unknown Title')
            artists = song.get('artists', [])
            artist_name = artists[0].get('name', 'Unknown Artist') if artists else 'Unknown Artist'
            duration = song.get('duration', '')
            
            item_text = f"{i+1}. {title} - {artist_name}"
            if duration:
                item_text += f" ({duration})"
            item_text += " ⏳"
            
            self.list_widget.addItem(item_text)

        self.song_count_label.setText(f"({len(self.songs)} lagu)")
        self.loading_label.setText("⏳ Memuat URL audio...")
        self.fetch_urls_background()

    def on_search_error(self, error_msg):
        self.search_btn.setEnabled(True)
        self.search_btn.setIcon(qta.icon('fa5s.search', color='white', size=16))
        self.list_widget.clear()
        self.list_widget.addItem("❌ Gagal mencari lagu")
        self.loading_label.setText("")
        self.song_count_label.setText("")
        QMessageBox.critical(self, "Error", f"Gagal mencari: {error_msg}")

    # ==================== URL FETCH ====================
    def fetch_urls_background(self):
        """Fetch URL untuk semua lagu secara parallel"""
        songs_with_indices = [(i, song) for i, song in enumerate(self.songs)]
        
        self.url_thread = URLFetchThread(songs_with_indices)
        self.url_thread.url_ready.connect(self.on_url_ready)
        self.url_thread.fetch_complete.connect(self.on_fetch_complete)
        self.url_thread.error.connect(self.on_url_error)
        self.url_thread.start()
        
        # ✅ NEW: Show progress bar
        self.fetch_progress.setVisible(True)
        self.fetch_progress.setValue(0)

    def on_url_ready(self, index, url):
        """Simpan URL ke cache"""
        self.audio_urls[index] = url
        
        item = self.list_widget.item(index)
        if item:
            text = item.text().replace(" ⏳", " ✅")
            item.setText(text)
        
        loaded = len(self.audio_urls)
        total = len(self.songs)
        
        # ✅ NEW: Update progress bar
        progress = int((loaded / total) * 100) if total > 0 else 0
        self.fetch_progress.setValue(progress)
        self.loading_label.setText(f"⏳ Loading... {loaded}/{total} ({progress}%)")

    def on_url_error(self, index, error_msg):
        """Handle error saat fetch URL"""
        item = self.list_widget.item(index)
        if item:
            text = item.text().replace(" ⏳", " ❌")
            item.setText(text)

    def on_fetch_complete(self):
        """Semua URL sudah selesai di-fetch"""
        loaded = len(self.audio_urls)
        self.loading_label.setText(f"✅ {loaded}/{len(self.songs)} lagu siap diputar")
        self.fetch_progress.setVisible(False)
        
        # ✅ NEW: Show tray notification
        if hasattr(self, 'tray_icon') and self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                "Music Player Pro",
                f"✅ {loaded} lagu siap diputar!",
                QSystemTrayIcon.Information,
                2000
            )

    # ==================== PLAYBACK ====================
    def play_selected(self, item):
        index = self.list_widget.currentRow()
        if 0 <= index < len(self.songs):
            # Save to history untuk shuffle
            if self.current_index >= 0 and self.current_index != index:
                self.play_history.append(self.current_index)
                if len(self.play_history) > 50:  # Limit history
                    self.play_history.pop(0)
            
            self.current_index = index
            self.load_and_play()

    def load_and_play(self):
        if self.current_index < 0 or self.current_index >= len(self.songs):
            return

        if self.current_index in self.audio_urls:
            self.play_from_url(self.audio_urls[self.current_index])
        else:
            self.status_label.setText("⏳ URL belum siap, tunggu sebentar...")
            self.play_btn.setEnabled(False)
            self.play_btn.setIcon(qta.icon('fa5s.spinner', color='white', size=32, spin=True))
            QTimer.singleShot(1000, self.load_and_play)

    def play_from_url(self, url):
        """Play lagu dari URL yang sudah di-cache"""
        song = self.songs[self.current_index]
        video_id = song.get("videoId")
        title = song.get('title', 'Unknown')
        artists = song.get('artists', [])
        artist = artists[0].get('name', 'Unknown') if artists else 'Unknown'
        thumbnail = song.get('thumbnails', [{}])[-1].get('url', '')

        self.now_playing_label.setText(f"🎵 {title}\n{artist}")
        self.status_label.setText("▶ Sedang memutar...")
        
        # ✅ NEW: Update tray tooltip
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.setToolTip(f"🎵 {title} - {artist}")
            self.tray_play_action.setText("⏸ Pause")
        
        if thumbnail:
            self.load_album_art(thumbnail)

        self.audio_url = url
        media = self.vlc_instance.media_new(url)
        self.player.set_media(media)
        self.player.play()
        
        self.is_playing = True
        self.play_btn.setEnabled(True)
        self.play_btn.setIcon(qta.icon('fa5s.pause', color='white', size=32))
        
        # Enable/disable prev/next berdasarkan mode
        self.prev_btn.setEnabled(self.can_go_previous())
        self.next_btn.setEnabled(self.can_go_next())
        
        # ✅ NEW: Highlight current song in list
        self.highlight_current_song()

    def highlight_current_song(self):
        """Highlight lagu yang sedang diputar di list"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item:
                text = item.text()
                # Remove previous highlight markers
                text = text.replace("▶ ", "").replace("  ", " ")
                # Add highlight to current
                if i == self.current_index:
                    text = "▶ " + text
                item.setText(text)

    def can_go_previous(self):
        """Check apakah bisa go previous"""
        if self.shuffle_mode and self.play_history:
            return True
        if self.repeat_mode == 1:
            return True
        return self.current_index > 0

    def can_go_next(self):
        """Check apakah bisa go next"""
        if self.repeat_mode > 0:
            return True
        if self.shuffle_mode and self.shuffled_indices:
            try:
                current_pos = self.shuffled_indices.index(self.current_index)
                return current_pos + 1 < len(self.shuffled_indices)
            except ValueError:
                return True
        return self.current_index < len(self.songs) - 1

    def load_album_art(self, url):
        """Load album art dari URL"""
        try:
            request = QNetworkRequest(QUrl(url))
            reply = self.nam.get(request)
            reply.finished.connect(lambda: self.on_album_art_loaded(reply))
        except:
            pass

    def on_album_art_loaded(self, reply):
        """Callback saat album art selesai load"""
        try:
            data = reply.readAll()
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.album_art.setPixmap(scaled_pixmap)
        except:
            pass

    def toggle_play(self):
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
            self.play_btn.setIcon(qta.icon('fa5s.play', color='white', size=32))
            self.status_label.setText("⏸ Dijeda")
            if hasattr(self, 'tray_play_action'):
                self.tray_play_action.setText("▶ Play")
        else:
            if self.audio_url:
                self.player.play()
                self.is_playing = True
                self.play_btn.setIcon(qta.icon('fa5s.pause', color='white', size=32))
                self.status_label.setText("▶ Sedang memutar...")
                if hasattr(self, 'tray_play_action'):
                    self.tray_play_action.setText("⏸ Pause")
            elif self.current_index >= 0:
                self.load_and_play()

    def play_previous(self):
        prev_idx = self.get_previous_index()
        if prev_idx >= 0:
            self.current_index = prev_idx
            self.list_widget.setCurrentRow(self.current_index)
            self.load_and_play()

    def play_next(self):
        next_idx = self.get_next_index()
        if next_idx >= 0:
            # Save to history
            if self.current_index >= 0:
                self.play_history.append(self.current_index)
                if len(self.play_history) > 50:
                    self.play_history.pop(0)
            
            self.current_index = next_idx
            self.list_widget.setCurrentRow(self.current_index)
            self.load_and_play()
        else:
            # Tidak ada lagu berikutnya, stop
            self.player.stop()
            self.is_playing = False
            self.play_btn.setIcon(qta.icon('fa5s.play', color='white', size=32))
            self.status_label.setText("⏹ Selesai")

    # ==================== CONTROLS ====================
    def set_volume(self, value):
        self.player.audio_set_volume(value)
        self.volume_label.setText(f"{value}%")
        
        # ✅ NEW: Update volume icon
        if value == 0:
            self.volume_icon_btn.setIcon(qta.icon('fa5s.volume-mute', color='white', size=16))
        elif value < 50:
            self.volume_icon_btn.setIcon(qta.icon('fa5s.volume-down', color='white', size=16))
        else:
            self.volume_icon_btn.setIcon(qta.icon('fa5s.volume-up', color='white', size=16))

    def seek_to(self, position):
        if self.duration_ms > 0:
            seek_ms = int((position / 1000.0) * self.duration_ms)
            self.player.set_time(seek_ms)

    def update_progress(self):
        if self.player.is_playing():
            current = self.player.get_time()
            total = self.player.get_length()
            
            if total > 0:
                self.duration_ms = total
                progress = int((current / total) * 1000)
                self.progress_slider.setValue(progress)
                self.current_time_label.setText(self.format_time(current))
                self.duration_label.setText(self.format_time(total))
                
                # Auto next saat lagu selesai
                if current >= total - 500:
                    self.play_next()

    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

    def animate_spinner(self):
        """Animate spinner saat loading"""
        self.spinner_angle = (self.spinner_angle + 10) % 360