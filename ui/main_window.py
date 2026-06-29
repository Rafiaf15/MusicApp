from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QListWidget, QLabel, QSlider,
    QMessageBox, QSystemTrayIcon, QMenu, QAction, QProgressBar,
    QGraphicsOpacityEffect, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtNetwork import QNetworkAccessManager
import qtawesome as qta
import os

from .components import AlbumArtLabel, LoadingOverlay
from .styles import MAIN_STYLE


# ─── Palette ────────────────────────────────────────────────────────────────
GREEN       = "#1DB954"
GREEN_LIGHT = "#1ED760"
GREEN_DARK  = "#1AA34A"
BG_BASE     = "#121212"
BG_PANEL    = "#181818"
BG_CARD     = "#242424"
BG_ELEVATED = "#2A2A2A"
BORDER      = "#333333"
TEXT_PRIMARY = "#FFFFFF"
TEXT_MUTED   = "#B3B3B3"
TEXT_FAINT   = "#727272"
RED         = "#E22134"
RED_LIGHT   = "#FF2A40"
RED_DARK    = "#C41E2E"


CARD_STYLE = f"""
    QFrame {{
        background-color: {BG_CARD};
        border-radius: 12px;
        border: 1px solid {BORDER};
    }}
"""

SLIDER_STYLE = f"""
    QSlider::groove:horizontal {{
        height: 4px;
        background: {BG_ELEVATED};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {TEXT_PRIMARY};
        width: 14px;
        height: 14px;
        border-radius: 7px;
        margin: -5px 0;
    }}
    QSlider::handle:horizontal:hover {{
        background: {GREEN_LIGHT};
        width: 16px;
        height: 16px;
        border-radius: 8px;
        margin: -6px 0;
    }}
    QSlider::sub-page:horizontal {{
        background: {GREEN};
        border-radius: 2px;
    }}
"""

VOLUME_SLIDER_STYLE = SLIDER_STYLE + f"""
    QSlider::sub-page:horizontal {{
        background: {TEXT_MUTED};
        border-radius: 2px;
    }}
"""

DIALOG_STYLE = f"""
    QMessageBox {{
        background-color: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}
    QMessageBox QLabel {{
        color: {TEXT_MUTED};
        font-size: 12px;
        padding: 4px;
        background: transparent;
    }}
    QMessageBox QLabel#qt_msgbox_label {{
        color: {TEXT_PRIMARY};
        font-size: 14px;
        font-weight: bold;
    }}
    QMessageBox QPushButton {{
        color: {TEXT_PRIMARY};
        border: none;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: bold;
        font-size: 13px;
        min-width: 110px;
        min-height: 38px;
    }}
    QMessageBox QPushButton[text*="Minimize"] {{
        background-color: {GREEN};
    }}
    QMessageBox QPushButton[text*="Minimize"]:hover {{
        background-color: {GREEN_LIGHT};
    }}
    QMessageBox QPushButton[text*="Quit"] {{
        background-color: {RED};
    }}
    QMessageBox QPushButton[text*="Quit"]:hover {{
        background-color: {RED_LIGHT};
    }}
    QMessageBox QPushButton[text*="Batal"] {{
        background-color: {BG_ELEVATED};
    }}
    QMessageBox QPushButton[text*="Batal"]:hover {{
        background-color: {BORDER};
    }}
    QMessageBox QPushButton:focus {{
        outline: 2px solid {GREEN};
        outline-offset: 2px;
    }}
"""


def _label(text="", obj_name="", font_size=12, bold=False, color=TEXT_PRIMARY, align=Qt.AlignLeft):
    lbl = QLabel(text)
    if obj_name:
        lbl.setObjectName(obj_name)
    weight = QFont.Bold if bold else QFont.Normal
    lbl.setFont(QFont("Segoe UI", font_size, weight))
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    lbl.setAlignment(align)
    return lbl


def _divider():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {BORDER}; background: {BORDER}; max-height: 1px;")
    return line


def _icon_btn(icon_name, color=TEXT_PRIMARY, size=20, fixed=(40, 40), tooltip="", obj_name=""):
    btn = QPushButton()
    btn.setIcon(qta.icon(icon_name, color=color, size=size))
    btn.setIconSize(QSize(size, size))
    btn.setFixedSize(*fixed)
    btn.setFocusPolicy(Qt.NoFocus)  # Prevent focus rectangle on click
    if tooltip:
        btn.setToolTip(tooltip)
    if obj_name:
        btn.setObjectName(obj_name)
    return btn


# ─── Main Window ─────────────────────────────────────────────────────────────

class MainWindow(QWidget):
    """Music Player Pro — redesigned for visual clarity."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Player Pro")
        self.setGeometry(100, 100, 1060, 780)
        self.setStyleSheet(MAIN_STYLE)
        self.setObjectName("centralWidget")
        self._force_quit = False

        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png"
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.nam = QNetworkAccessManager()
        self._status_timer = QTimer()
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._clear_status)

        self.setup_ui()
        self.setup_tray_icon()
        self.setFocusPolicy(Qt.StrongFocus)

    # ── Layout ───────────────────────────────────────────────────────────────

    def setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        root.addLayout(self._build_left_panel(), 45)
        root.addLayout(self._build_right_panel(), 55)

        self.loading_overlay = LoadingOverlay(self)

    # ── Left panel ───────────────────────────────────────────────────────────

    def _build_left_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(0)

        # ── Header ──────────────────────────────────────────────
        hdr = _label("Music Player Pro", font_size=20, bold=True,
                      color=TEXT_PRIMARY, align=Qt.AlignCenter)
        hdr.setContentsMargins(0, 0, 0, 16)
        layout.addWidget(hdr)

        # ── Player Card ──────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(CARD_STYLE)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 24, 20, 24)
        card_layout.setSpacing(16)

        # Album Art
        self.album_art = AlbumArtLabel()
        card_layout.addWidget(self.album_art, alignment=Qt.AlignCenter)

        # Now Playing
        self.now_playing_label = _label(
            "Tidak ada lagu yang diputar",
            font_size=13, color=TEXT_MUTED, align=Qt.AlignCenter
        )
        self.now_playing_label.setObjectName("nowPlayingLabel")
        self.now_playing_label.setWordWrap(True)
        card_layout.addWidget(self.now_playing_label)

        # Fetch Progress (hidden by default)
        self.fetch_progress = QProgressBar()
        self.fetch_progress.setRange(0, 100)
        self.fetch_progress.setValue(0)
        self.fetch_progress.setVisible(False)
        self.fetch_progress.setFixedHeight(4)
        self.fetch_progress.setTextVisible(False)
        self.fetch_progress.setStyleSheet(f"""
            QProgressBar {{
                background: {BG_ELEVATED};
                border-radius: 2px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {GREEN}, stop:1 {GREEN_LIGHT});
                border-radius: 2px;
            }}
        """)
        card_layout.addWidget(self.fetch_progress)

        card_layout.addWidget(_divider())

        # Progress Slider + Time
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.setStyleSheet(SLIDER_STYLE)
        card_layout.addWidget(self.progress_slider)

        time_row = QHBoxLayout()
        self.current_time_label = _label("0:00", font_size=10, color=TEXT_FAINT)
        self.duration_label     = _label("0:00", font_size=10, color=TEXT_FAINT, align=Qt.AlignRight)
        time_row.addWidget(self.current_time_label)
        time_row.addStretch()
        time_row.addWidget(self.duration_label)
        card_layout.addLayout(time_row)

        # Shuffle / Repeat
        mode_row = QHBoxLayout()
        mode_row.setSpacing(8)
        mode_row.addStretch()

        self.shuffle_btn = _icon_btn("fa5s.random", color=TEXT_FAINT, size=16,
                                     fixed=(36, 36), tooltip="Shuffle (S)", obj_name="modeBtn")
        self.shuffle_btn.setFocusPolicy(Qt.NoFocus)
        self.repeat_btn  = _icon_btn("fa5s.sync",   color=TEXT_FAINT, size=16,
                                     fixed=(36, 36), tooltip="Repeat (R)",  obj_name="modeBtn")
        self.repeat_btn.setFocusPolicy(Qt.NoFocus)
        mode_row.addWidget(self.shuffle_btn)
        mode_row.addWidget(self.repeat_btn)
        mode_row.addStretch()
        card_layout.addLayout(mode_row)

        # Playback Controls
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(12)
        ctrl_row.addStretch()

        self.prev_btn = _icon_btn("fa5s.step-backward", color=TEXT_PRIMARY, size=22,
                                  fixed=(52, 52), tooltip="Previous (←)", obj_name="controlBtn")
        self.prev_btn.setEnabled(False)
        self.prev_btn.setFocusPolicy(Qt.NoFocus)

        self.play_btn = _icon_btn("fa5s.play", color=TEXT_PRIMARY, size=28,
                                  fixed=(72, 72), tooltip="Play / Pause (Space)", obj_name="playBtn")
        self.play_btn.setEnabled(False)
        self.play_btn.setFocusPolicy(Qt.NoFocus)

        self.next_btn = _icon_btn("fa5s.step-forward", color=TEXT_PRIMARY, size=22,
                                  fixed=(52, 52), tooltip="Next (→)", obj_name="controlBtn")
        self.next_btn.setEnabled(False)
        self.next_btn.setFocusPolicy(Qt.NoFocus)

        ctrl_row.addWidget(self.prev_btn)
        ctrl_row.addWidget(self.play_btn)
        ctrl_row.addWidget(self.next_btn)
        ctrl_row.addStretch()
        card_layout.addLayout(ctrl_row)

        # Volume
        vol_row = QHBoxLayout()
        vol_row.setSpacing(10)

        self.volume_icon_btn = QPushButton()
        self.volume_icon_btn.setFixedSize(28, 28)
        self.volume_icon_btn.setIcon(qta.icon("fa5s.volume-up", color=TEXT_MUTED, size=14))
        self.volume_icon_btn.setIconSize(QSize(14, 14))
        self.volume_icon_btn.setToolTip("Volume (↑ / ↓)")
        self.volume_icon_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; border-radius: 4px; }}
            QPushButton:hover {{ background: {BG_ELEVATED}; }}
        """)
        self.volume_icon_btn.setFocusPolicy(Qt.NoFocus)
        vol_row.addWidget(self.volume_icon_btn)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setStyleSheet(VOLUME_SLIDER_STYLE)
        self.volume_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        vol_row.addWidget(self.volume_slider)

        self.volume_label = _label("70%", font_size=10, color=TEXT_FAINT)
        self.volume_label.setFixedWidth(32)
        self.volume_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        vol_row.addWidget(self.volume_label)
        card_layout.addLayout(vol_row)

        layout.addWidget(card)
        layout.addSpacing(12)

        # Status
        self.status_label = _label("", font_size=11, color=TEXT_MUTED, align=Qt.AlignCenter)
        self.status_label.setObjectName("statusLabel")
        eff = QGraphicsOpacityEffect()
        eff.setOpacity(0.9)
        self.status_label.setGraphicsEffect(eff)
        layout.addWidget(self.status_label)

        # Keyboard hint
        hint = _label(
            "Space: Play  ·  ← →: Track  ·  ↑ ↓: Vol  ·  Ctrl+Q: Quit  ·  Esc: Minimize",
            font_size=10, color=TEXT_FAINT, align=Qt.AlignCenter
        )
        hint.setContentsMargins(0, 4, 0, 0)
        layout.addWidget(hint)

        layout.addStretch()
        return layout

    # ── Right panel ──────────────────────────────────────────────────────────

    def _build_right_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Section header: Search
        layout.addLayout(self._section_header("fa5s.search", "Cari Lagu"))

        # Search row
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Judul lagu atau artis…")
        self.search_box.setFixedHeight(40)
        self.search_box.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
                color: {TEXT_PRIMARY};
                font-size: 13px;
                padding: 0 12px;
            }}
            QLineEdit:focus {{
                border-color: {GREEN};
            }}
            QLineEdit::placeholder {{
                color: {TEXT_FAINT};
            }}
        """)
        search_row.addWidget(self.search_box)

        self.search_btn = QPushButton("Cari")
        self.search_btn.setIcon(qta.icon("fa5s.search", color=TEXT_PRIMARY, size=14))
        self.search_btn.setIconSize(QSize(14, 14))
        self.search_btn.setFixedSize(80, 40)
        self.search_btn.setToolTip("Cari (Enter)")
        self.search_btn.setStyleSheet(f"""
            QPushButton {{
                background: {GREEN};
                color: {TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {GREEN_LIGHT}; }}
            QPushButton:pressed {{ background: {GREEN_DARK}; }}
        """)
        search_row.addWidget(self.search_btn)
        layout.addLayout(search_row)

        # Loading label
        self.loading_label = _label("", font_size=11, color=GREEN)
        layout.addWidget(self.loading_label)

        layout.addWidget(_divider())

        # Section header: Daftar Lagu
        hdr_row = QHBoxLayout()
        hdr_row.addLayout(self._section_header("fa5s.list", "Daftar Lagu"))
        hdr_row.addStretch()
        self.song_count_label = _label("", font_size=11, color=TEXT_FAINT, align=Qt.AlignRight)
        hdr_row.addWidget(self.song_count_label)
        layout.addLayout(hdr_row)

        # Song List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {BG_PANEL};
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 6px;
                color: {TEXT_PRIMARY};
                outline: none;
                font-size: 13px;
            }}
            QListWidget::item {{
                background-color: {BG_CARD};
                padding: 11px 14px;
                border-radius: 6px;
                margin: 2px 0;
                border-left: 3px solid transparent;
                color: {TEXT_MUTED};
            }}
            QListWidget::item:selected {{
                background-color: {BG_ELEVATED};
                border-left: 3px solid {GREEN};
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {BG_ELEVATED};
                color: {TEXT_PRIMARY};
            }}
        """)
        layout.addWidget(self.list_widget)

        return layout

    def _section_header(self, icon_name, text):
        """Returns a QHBoxLayout with an icon + bold label."""
        row = QHBoxLayout()
        row.setSpacing(8)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon(icon_name, color=GREEN, size=16).pixmap(16, 16))
        row.addWidget(icon_lbl)
        row.addWidget(_label(text, font_size=14, bold=True))
        row.addStretch()
        return row

    # ── System Tray ──────────────────────────────────────────────────────────

    def setup_tray_icon(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = None
            return

        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png"
        )
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(qta.icon("fa5s.music", color=GREEN, size=32))

        self.tray_icon.setToolTip("Music Player Pro")

        menu = QMenu()
        self.tray_play_action = QAction("▶  Play");      menu.addAction(self.tray_play_action)
        self.tray_next_action = QAction("⏭  Next");      menu.addAction(self.tray_next_action)
        self.tray_prev_action = QAction("⏮  Previous");  menu.addAction(self.tray_prev_action)
        menu.addSeparator()
        self.tray_show_action = QAction("👁  Show");      menu.addAction(self.tray_show_action)
        self.tray_quit_action = QAction("✕  Quit");      menu.addAction(self.tray_quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self._on_tray_activated)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_from_tray()

    def show_from_tray(self):
        self.show()
        self.showNormal()
        self.activateWindow()

    # ── Status helpers ───────────────────────────────────────────────────────

    def show_status_message(self, message, timeout=3000):
        self.status_label.setText(message)
        self._status_timer.start(timeout)

    def _clear_status(self):
        self.status_label.setText("")

    # ── Window close ─────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self._force_quit:
            self._force_quit = False
            if hasattr(self, "tray_icon") and self.tray_icon:
                self.tray_icon.hide()
            event.accept()
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Keluar Aplikasi")
        msg.setIcon(QMessageBox.Question)
        msg.setText("<b style='font-size:14px;'>Apa yang ingin Anda lakukan?</b>")
        msg.setInformativeText(
            f"<span style='color:{TEXT_MUTED}; font-size:12px;'>"
            "Minimize agar aplikasi tetap berjalan di background,<br>"
            "atau Quit untuk keluar sepenuhnya."
            "</span>"
        )

        btn_minimize = msg.addButton("📍  Minimize", QMessageBox.AcceptRole)
        btn_quit     = msg.addButton("✕  Quit",     QMessageBox.DestructiveRole)
        btn_cancel   = msg.addButton("Batal",        QMessageBox.RejectRole)

        msg.setDefaultButton(btn_minimize)
        msg.setStyleSheet(DIALOG_STYLE)
        msg.exec_()

        clicked = msg.clickedButton()

        if clicked == btn_quit:
            self._force_quit = True
            self.close()
        elif clicked == btn_minimize:
            if hasattr(self, "tray_icon") and self.tray_icon and self.tray_icon.isVisible():
                self.hide()
                self.tray_icon.showMessage(
                    "Music Player Pro",
                    "Aplikasi berjalan di background.\nKlik kanan ikon tray untuk menu.",
                    QSystemTrayIcon.Information,
                    2000,
                )
                event.ignore()
            else:
                self._force_quit = True
                self.close()
        else:
            event.ignore()

    # ── Cleanup ──────────────────────────────────────────────────────────────

    def cleanup(self):
        if hasattr(self, "_status_timer"):
            self._status_timer.stop()