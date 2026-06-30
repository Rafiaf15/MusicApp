import sys
import os
import time
import subprocess
import threading
import json
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox, QShortcut
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtNetwork import QNetworkRequest
import qtawesome as qta

from ui.main_window import MainWindow
from core.player import MusicPlayer
from services.search_service import SearchService
from services.url_fetch_service import URLFetchService


class CacheManager:
    """Cache manager untuk URL agar tidak perlu fetch ulang"""
    
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            cache_dir = Path.home() / '.musicplayer_cache'
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.url_cache_file = self.cache_dir / 'url_cache.json'
        self.url_cache = self._load_cache()
    
    def _load_cache(self):
        """Load cache dari file"""
        if self.url_cache_file.exists():
            try:
                with open(self.url_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self):
        """Save cache ke file"""
        try:
            with open(self.url_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.url_cache, f)
        except:
            pass
    
    def get_url(self, video_id):
        """Get URL dari cache"""
        return self.url_cache.get(video_id)
    
    def set_url(self, video_id, url):
        """Set URL ke cache"""
        self.url_cache[video_id] = url
        self.save_cache()
    
    def clear_cache(self):
        """Clear semua cache"""
        self.url_cache = {}
        if self.url_cache_file.exists():
            self.url_cache_file.unlink()


class MusicAppController:
    """Optimized controller dengan lazy loading, caching, dan better performance"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        
        # Initialize components
        self.window = MainWindow()
        self.player = MusicPlayer()
        self.search_service = SearchService()
        self.url_fetch_service = None
        
        # Data
        self.songs = []
        self.audio_urls = {}
        self._fetching_indices = set()
        self._fetch_timers = {}
        
        # Initialize cache manager
        self.cache = CacheManager()
        
        # Connect signals
        self.connect_signals()
        
        # Setup UI connections
        self.setup_ui_connections()
        
        print("✅ Music Player Pro initialized")
    
    def connect_signals(self):
        """Connect player signals to UI slots"""
        self.player.state_changed.connect(self.on_player_state_changed)
        self.player.position_changed.connect(self.on_position_changed)
        self.player.volume_changed.connect(self.on_volume_changed)
        self.player.song_ended.connect(self.on_song_ended)
        self.player.error_occurred.connect(self.on_player_error)
    
    def setup_ui_connections(self):
        """Setup UI signal connections"""
        # Search
        self.window.search_btn.clicked.connect(self.on_search_clicked)
        self.window.search_box.returnPressed.connect(self.on_search_clicked)
        
        # Playback controls
        self.window.play_btn.clicked.connect(self.on_play_clicked)
        self.window.next_btn.clicked.connect(self.on_next_clicked)
        self.window.prev_btn.clicked.connect(self.on_prev_clicked)
        
        # Volume
        self.window.volume_slider.valueChanged.connect(self.on_volume_slider_changed)
        
        # Seek
        self.window.progress_slider.sliderMoved.connect(self.on_seek)
        
        # Mode buttons
        self.window.shuffle_btn.clicked.connect(self.on_shuffle_clicked)
        self.window.repeat_btn.clicked.connect(self.on_repeat_clicked)
        
        # Song selection - LAZY LOADING
        self.window.list_widget.itemClicked.connect(self.on_song_selected)
        
        # Tray connections
        if self.window.tray_icon:
            self.window.tray_play_action.triggered.connect(self.on_play_clicked)
            self.window.tray_next_action.triggered.connect(self.on_next_clicked)
            self.window.tray_prev_action.triggered.connect(self.on_prev_clicked)
            self.window.tray_show_action.triggered.connect(self.window.show_from_tray)
            self.window.tray_quit_action.triggered.connect(self.quit_app)
        
        # Keyboard shortcuts
        self.setup_keyboard_shortcuts()
        # Connect playback speed dropdown
        self.window.speed_combo.currentTextChanged.connect(self.on_speed_changed)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts menggunakan QShortcut"""
        QShortcut(QKeySequence(Qt.Key_Space), self.window).activated.connect(self.on_play_clicked)
        QShortcut(QKeySequence(Qt.Key_Left), self.window).activated.connect(self.on_prev_clicked)
        QShortcut(QKeySequence(Qt.Key_Right), self.window).activated.connect(self.on_next_clicked)
        QShortcut(QKeySequence(Qt.Key_Up), self.window).activated.connect(lambda: self.change_volume(5))
        QShortcut(QKeySequence(Qt.Key_Down), self.window).activated.connect(lambda: self.change_volume(-5))
        QShortcut(QKeySequence(Qt.Key_M), self.window).activated.connect(self.toggle_mute)
        QShortcut(QKeySequence(Qt.Key_S), self.window).activated.connect(self.on_shuffle_clicked)
        QShortcut(QKeySequence(Qt.Key_R), self.window).activated.connect(self.on_repeat_clicked)
        QShortcut(QKeySequence("Ctrl+Q"), self.window).activated.connect(self.quit_app)
        QShortcut(QKeySequence(Qt.Key_Escape), self.window).activated.connect(self.minimize_to_tray)
        # Playback speed shortcuts
        QShortcut(QKeySequence("Ctrl+1"), self.window).activated.connect(lambda: self.change_playback_rate(0.5))
        QShortcut(QKeySequence("Ctrl+2"), self.window).activated.connect(lambda: self.change_playback_rate(1.0))
        QShortcut(QKeySequence("Ctrl+3"), self.window).activated.connect(lambda: self.change_playback_rate(1.2))
        QShortcut(QKeySequence("Ctrl+4"), self.window).activated.connect(lambda: self.change_playback_rate(1.5))
        QShortcut(QKeySequence("Ctrl+5"), self.window).activated.connect(lambda: self.change_playback_rate(2.0))
    
    # ==================== SEARCH ====================
    
    def change_playback_rate(self, rate):
        """Change playback speed via player"""
        self.player.set_playback_rate(rate)
        self.window.show_status_message(f"Kecepatan pemutaran: {rate}x", 3000)

    def on_search_clicked(self):
        query = self.window.search_box.text().strip()
        if not query:
            return
        
        print(f"🔍 Searching: {query}")
        start_time = time.time()
        
        self.window.search_btn.setEnabled(False)
        self.window.list_widget.clear()
        self.window.list_widget.addItem("🔍 Mencari lagu...")
        self.window.loading_label.setText("⏳ Sedang mencari...")
        self.window.show_status_message("")
        self.audio_urls.clear()
        self._fetching_indices.clear()
        self.window.fetch_progress.setVisible(False)
        
        self.search_service.search(query, 
                                   lambda results: self.on_search_finished(results, start_time), 
                                   self.on_search_error)
    
    def on_search_finished(self, results, start_time=None):
        elapsed = time.time() - start_time if start_time else 0
        print(f"✅ Search completed in {elapsed:.2f}s - Found {len(results)} results")
        
        self.window.search_btn.setEnabled(True)
        self.songs = results
        self.player.set_total_songs(len(self.songs))
        self.window.list_widget.clear()
        
        if not self.songs:
            self.window.list_widget.addItem("❌ Tidak ada hasil ditemukan")
            self.window.loading_label.setText("")
            self.window.song_count_label.setText("")
            return
        
        # Tampilkan lagu TANPA fetch URL (INSTANT!)
        for i, song in enumerate(self.songs):
            title = song.get('title', 'Unknown')
            artists = song.get('artists', [])
            artist = artists[0].get('name', 'Unknown') if artists else 'Unknown'
            duration = song.get('duration', '')
            
            item_text = f"{i+1}. {title} - {artist}"
            if duration:
                item_text += f" ({duration})"
            
            self.window.list_widget.addItem(item_text)
        
        self.window.song_count_label.setText(f"({len(self.songs)} lagu)")
        self.window.loading_label.setText("✅ Klik lagu untuk memutar")
        self.window.show_status_message(f"✅ {len(self.songs)} lagu ditemukan dalam {elapsed:.2f}s")
        
        # Pre-fetch lagu dari cache
        self._prefetch_from_cache()
        # Pre-fetch URLs for first few songs to reduce wait on click
        self._prefetch_initial_songs(count=5)
    
    def _prefetch_from_cache(self):
        """Pre-fetch URLs dari cache untuk lagu yang sudah pernah di-fetch"""
        cached_count = 0
        for i, song in enumerate(self.songs):
            video_id = song.get("videoId")
            if video_id:
                cached_url = self.cache.get_url(video_id)
                if cached_url:
                    self.audio_urls[i] = cached_url
                    cached_count += 1

        if cached_count > 0:
            print(f"📦 Loaded {cached_count} URLs from cache")
            self.window.show_status_message(f"📦 {cached_count} lagu dari cache")

    def _prefetch_initial_songs(self, count=5):
        """Fetch URLs for the first *count* songs in background to reduce click latency."""
        if not self.songs:
            return
        for idx in range(min(count, len(self.songs))):
            if idx not in self.audio_urls and idx not in self._fetching_indices:
                threading.Thread(target=lambda i=idx: self._background_fetch(i), daemon=True).start()
    def on_search_error(self, error_msg):
        print(f"❌ Search error: {error_msg}")
        self.window.search_btn.setEnabled(True)
        self.window.list_widget.clear()
        self.window.list_widget.addItem("❌ Gagal mencari lagu")
        self.window.loading_label.setText("")
        self.window.song_count_label.setText("")
        self.window.show_status_message(f"❌ Error: {error_msg}", 5000)
    
    # ==================== SONG SELECTION & FETCHING ====================
    
    def on_song_selected(self, item):
        """INSTANT PLAY: Prioritaskan lagu yang diklik"""
        # Use the clicked item's row directly instead of currentRow which may be outdated
        index = self.window.list_widget.row(item)
        if 0 <= index < len(self.songs):
            print(f"🎵 Song selected: {index + 1}")

            # Save to history
            if self.player.current_index >= 0 and self.player.current_index != index:
                self.player.play_history.append(self.player.current_index)
                if len(self.player.play_history) > 50:
                    self.player.play_history.pop(0)

            self.player.current_index = index
            self.window.list_widget.setCurrentRow(index)

            # PRIORITAS: Cek cache dulu
            if index in self.audio_urls:
                print(f"⚡ URL already cached for song {index + 1}")
                self.load_and_play()
                # Pre-fetch lagu berikutnya
                self._prefetch_next_songs(index)
            else:
                # Fetch dengan PRIORITAS TINGGI
                self._fetch_priority_url(index)
    
    def _fetch_priority_url(self, index):
        """Fetch URL dengan prioritas tinggi untuk instant play"""
        if index in self._fetching_indices:
            print(f"⏳ Already fetching song {index + 1}")
            return
        
        self._fetching_indices.add(index)
        self._fetch_timers[index] = time.time()
        
        song = self.songs[index]
        video_id = song.get("videoId")
        
        if not video_id:
            print(f"❌ No video ID for song {index + 1}")
            self.window.show_status_message("❌ Video ID tidak ditemukan", 3000)
            self._fetching_indices.discard(index)
            return
        
        # Update UI
        original_text = self.window.list_widget.item(index).text()
        self.window.list_widget.item(index).setText(original_text + " ⏳ LOADING...")
        self.window.show_status_message("⚡ Memuat URL...")
        
        print(f"🚀 Fetching URL for song {index + 1}...")
        
        # Fetch di thread dengan prioritas tinggi
        def priority_fetch():
            try:
                cmd = [
                    'yt-dlp',
                    '-f', 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio',
                    '--get-url',
                    '--no-warnings',
                    '--socket-timeout', '5',
                    '--extractor-retries', '1',
                    f'https://www.youtube.com/watch?v={video_id}'
                ]
                
                start_time = time.time()
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=8,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                elapsed = time.time() - start_time
                
                if result.returncode == 0 and result.stdout.strip():
                    url = result.stdout.strip()
                    print(f"✅ URL fetched in {elapsed:.2f}s for song {index + 1}")
                    QTimer.singleShot(0, lambda: self._on_priority_url_ready(index, url, original_text, elapsed))
                else:
                    print(f"❌ Failed to fetch URL for song {index + 1}")
                    QTimer.singleShot(0, lambda: self._on_fetch_failed(index, original_text))
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout fetching URL for song {index + 1}")
                QTimer.singleShot(0, lambda: self._on_fetch_timeout(index, original_text))
            except Exception as e:
                print(f"❌ Error fetching URL for song {index + 1}: {e}")
                QTimer.singleShot(0, lambda: self._on_fetch_failed(index, original_text, str(e)))
            finally:
                self._fetching_indices.discard(index)
        
        thread = threading.Thread(target=priority_fetch, daemon=True)
        thread.start()
    
    def _on_priority_url_ready(self, index, url, original_text, elapsed):
        """Callback saat URL prioritas siap"""
        self.audio_urls[index] = url
        
        # Save to cache
        video_id = self.songs[index].get("videoId")
        if video_id:
            self.cache.set_url(video_id, url)
        
        # Update UI
        item = self.window.list_widget.item(index)
        if item:
            item.setText(original_text + " ✅")
        
        self.window.show_status_message(f"⚡ Siap dalam {elapsed:.2f}s!")
        self.load_and_play()
        
        # AGGRESSIVE PRE-FETCH: Fetch 3 lagu berikutnya
        self._prefetch_next_songs(index, count=3)
    
    def _on_fetch_failed(self, index, original_text, error_msg=None):
        """Callback saat fetch gagal"""
        item = self.window.list_widget.item(index)
        if item:
            item.setText(original_text + " ❌")
        
        msg = error_msg if error_msg else "Gagal memuat URL"
        self.window.show_status_message(f"❌ {msg}", 5000)
    
    def _on_fetch_timeout(self, index, original_text):
        """Callback saat timeout"""
        item = self.window.list_widget.item(index)
        if item:
            item.setText(original_text + " ⏰ Timeout")
        
        self.window.show_status_message("⏰ Timeout - coba lagu lain", 3000)
    
    def _prefetch_next_songs(self, current_index, count=3):
        """Pre-fetch lagu berikutnya di background"""
        print(f"🔄 Pre-fetching {count} next songs...")
        for i in range(1, count + 1):
            next_idx = (current_index + i) % len(self.songs)
            if next_idx not in self.audio_urls and next_idx not in self._fetching_indices:
                threading.Thread(
                    target=lambda idx=next_idx: self._background_fetch(idx),
                    daemon=True
                ).start()
    
    def _background_fetch(self, index):
        """Background fetch tanpa UI update"""
        if index in self._fetching_indices or index in self.audio_urls:
            return
        
        self._fetching_indices.add(index)
        song = self.songs[index]
        video_id = song.get("videoId")
        
        if not video_id:
            self._fetching_indices.discard(index)
            return
        
        try:
            cmd = [
                'yt-dlp',
                '-f', 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio',
                '--get-url',
                '--no-warnings',
                '--socket-timeout', '5',
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=8,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            elapsed = time.time() - start_time
            
            if result.returncode == 0 and result.stdout.strip():
                url = result.stdout.strip()
                self.audio_urls[index] = url
                self.cache.set_url(video_id, url)
                print(f"✅ Pre-fetched song {index + 1} in {elapsed:.2f}s")
                
        except:
            pass
        finally:
            self._fetching_indices.discard(index)
    
    def fetch_single_url(self, index):
        """Fetch URL untuk satu lagu saja (LAZY LOADING)"""
        self._fetch_priority_url(index)
    
    def on_single_url_fetched(self, index, url):
        """Callback saat URL single lagu berhasil di-fetch"""
        self.audio_urls[index] = url
        
        video_id = self.songs[index].get("videoId")
        if video_id:
            self.cache.set_url(video_id, url)
        
        item_text = self.window.list_widget.item(index).text()
        item_text = item_text.replace(" ⏳", " ✅")
        self.window.list_widget.item(index).setText(item_text)
        
        self.window.show_status_message("✅ URL siap, memutar...")
        self.load_and_play()
        
        next_idx = self.player.get_next_index()
        if next_idx >= 0 and next_idx not in self.audio_urls and next_idx not in self._fetching_indices:
            threading.Thread(target=lambda: self.fetch_single_url(next_idx), daemon=True).start()
    
    def on_single_url_error(self, index, error_msg=None):
        """Callback saat fetch URL gagal"""
        item_text = self.window.list_widget.item(index).text()
        item_text = item_text.replace(" ⏳", " ❌")
        self.window.list_widget.item(index).setText(item_text)
        
        msg = error_msg if error_msg else "Gagal memuat URL"
        self.window.show_status_message(f"❌ {msg}", 5000)
    
    # ==================== PLAYBACK CONTROLS ====================
    
    def on_play_clicked(self):
        if self.player.is_playing:
            self.player.pause()
        else:
            if self.player.audio_url:
                self.player.play()
            elif self.player.current_index >= 0:
                self.load_and_play()
    
    def on_next_clicked(self):
        if self.player._is_transitioning:
            return
        self.player._is_transitioning = True
        
        next_idx = self.player.get_next_index()
        
        if next_idx >= 0:
            if self.player.repeat_mode != 2 and self.player.current_index >= 0:
                self.player.play_history.append(self.player.current_index)
                if len(self.player.play_history) > 50:
                    self.player.play_history.pop(0)
            
            self.player.current_index = next_idx
            self.window.list_widget.setCurrentRow(next_idx)
            self.load_and_play()
        else:
            self.player.stop()
            self.player._is_transitioning = False
    
    def on_prev_clicked(self):
        prev_idx = self.player.get_previous_index()
        if prev_idx >= 0:
            self.player.current_index = prev_idx
            self.window.list_widget.setCurrentRow(prev_idx)
            self.load_and_play()
    
    def on_volume_slider_changed(self, value):
        self.player.set_volume(value)
        self.window.volume_label.setText(f"{value}%")
        
        if value == 0:
            self.window.volume_icon_btn.setIcon(qta.icon('fa5s.volume-mute', color='white', size=16))
        elif value < 50:
            self.window.volume_icon_btn.setIcon(qta.icon('fa5s.volume-down', color='white', size=16))
        else:
            self.window.volume_icon_btn.setIcon(qta.icon('fa5s.volume-up', color='white', size=16))
    
    def on_seek(self, position):
        if self.player.duration_ms > 0:
            seek_ms = int((position / 1000.0) * self.player.duration_ms)
            self.player.seek(seek_ms)
    
    def on_shuffle_clicked(self):
        is_shuffled = self.player.toggle_shuffle(len(self.songs))
        
        if is_shuffled:
            self.window.shuffle_btn.setIcon(qta.icon('fa5s.random', color='#1DB954', size=18))
            self.window.show_status_message("🔀 Shuffle ON")
        else:
            self.window.shuffle_btn.setIcon(qta.icon('fa5s.random', color='#B3B3B3', size=18))
            self.window.show_status_message("🔀 Shuffle OFF")
        
        self.update_button_states()
    
    def on_speed_changed(self, text):
        """Handle speed dropdown change"""
        # text format like "1.2x"
        try:
            rate = float(text.rstrip('x'))
        except ValueError:
            self.window.show_status_message(f"Kecepatan tidak valid: {text}", 3000)
            return
        self.player.set_playback_rate(rate)
        self.window.show_status_message(f"Kecepatan pemutaran: {rate}x", 3000)

    def on_repeat_clicked(self):
        mode = self.player.toggle_repeat()
        
        if mode == 0:
            self.window.repeat_btn.setIcon(qta.icon('fa5s.sync', color='#B3B3B3', size=18))
            self.window.show_status_message("🔁 Repeat OFF")
        elif mode == 1:
            self.window.repeat_btn.setIcon(qta.icon('fa5s.sync', color='#1DB954', size=18))
            self.window.show_status_message("🔁 Repeat ALL")
        elif mode == 2:
            self.window.repeat_btn.setIcon(qta.icon('fa5s.redo', color='#1DB954', size=18))
            self.window.show_status_message("🔂 Repeat ONE")
        
        self.update_button_states()
    
    # ==================== PLAYER SIGNAL HANDLERS ====================
    
    def on_player_state_changed(self, state):
        if state == 'playing':
            self.window.play_btn.setIcon(qta.icon('fa5s.pause', color='white', size=32))
            self.window.show_status_message("▶ Sedang memutar...")
            if hasattr(self.window, 'tray_play_action'):
                self.window.tray_play_action.setText("⏸ Pause")
        elif state == 'paused':
            self.window.play_btn.setIcon(qta.icon('fa5s.play', color='white', size=32))
            self.window.show_status_message("⏸ Dijeda")
            if hasattr(self.window, 'tray_play_action'):
                self.window.tray_play_action.setText("▶ Play")
        elif state == 'stopped':
            self.window.play_btn.setIcon(qta.icon('fa5s.play', color='white', size=32))
            self.window.show_status_message("⏹ Selesai")
    
    def on_position_changed(self, current, total):
        progress = int((current / total) * 1000)
        self.window.progress_slider.setValue(progress)
        self.window.current_time_label.setText(self.format_time(current))
        self.window.duration_label.setText(self.format_time(total))
    
    def on_volume_changed(self, volume):
        self.window.volume_slider.setValue(volume)
        self.window.volume_label.setText(f"{volume}%")
    
    def on_song_ended(self):
        """Auto-next saat lagu selesai"""
        self.on_next_clicked()
    
    def on_player_error(self, error_msg):
        """Handle player error"""
        self.window.show_status_message(f"❌ Player error: {error_msg}", 5000)
    
    # ==================== UTILITY METHODS ====================
    
    def change_volume(self, delta):
        """Change volume by delta"""
        current = self.window.volume_slider.value()
        new_volume = max(0, min(100, current + delta))
        self.window.volume_slider.setValue(new_volume)
    
    def toggle_mute(self):
        """Toggle mute/unmute"""
        if self.player.get_volume() > 0:
            self.player.set_mute(True)
            self.window.show_status_message("🔇 Muted")
        else:
            self.player.set_mute(False)
            self.window.show_status_message("🔊 Unmuted")
    
    def minimize_to_tray(self):
        """Minimize window ke tray"""
        if hasattr(self.window, 'tray_icon') and self.window.tray_icon and self.window.tray_icon.isVisible():
            self.window.hide()
    
    def load_and_play(self):
        if self.player.current_index < 0 or self.player.current_index >= len(self.songs):
            return
        
        if self.player.current_index in self.audio_urls:
            self.play_from_url(self.audio_urls[self.player.current_index])
        else:
            self.window.show_status_message("⏳ URL belum siap...")
            self.window.play_btn.setEnabled(False)
            self.window.play_btn.setIcon(qta.icon('fa5s.spinner', color='white', size=32, spin=True))
            
            QTimer.singleShot(1000, self.load_and_play)
    
    def play_from_url(self, url):
        song = self.songs[self.player.current_index]
        title = song.get('title', 'Unknown')
        artists = song.get('artists', [])
        artist = artists[0].get('name', 'Unknown') if artists else 'Unknown'
        thumbnail = song.get('thumbnails', [{}])[-1].get('url', '')
        
        self.window.now_playing_label.setText(f"🎵 {title}\n{artist}")
        
        if hasattr(self.window, 'tray_icon') and self.window.tray_icon:
            self.window.tray_icon.setToolTip(f"🎵 {title} - {artist}")
        
        if thumbnail:
            self.load_album_art(thumbnail)
        
        # Stop dulu sebelum load media baru (penting untuk repeat one!)
        self.player.stop()
        self.player.load_media(url)
        self.player.play()
        
        self.player._is_transitioning = False
        self.window.play_btn.setEnabled(True)
        
        self.update_button_states()
        self.highlight_current_song()
    
    def load_album_art(self, url):
        try:
            request = QNetworkRequest(QUrl(url))
            reply = self.window.nam.get(request)
            reply.finished.connect(lambda: self.on_album_art_loaded(reply))
        except:
            pass
    
    def on_album_art_loaded(self, reply):
        try:
            data = reply.readAll()
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.window.album_art.setPixmap(scaled_pixmap)
        except:
            pass
    
    def highlight_current_song(self):
        for i in range(self.window.list_widget.count()):
            item = self.window.list_widget.item(i)
            if item:
                text = item.text()
                text = text.replace("▶ ", "").replace("  ", " ")
                if i == self.player.current_index:
                    text = "▶ " + text
                item.setText(text)
    
    def update_button_states(self):
        self.window.prev_btn.setEnabled(self.player.can_go_previous())
        self.window.next_btn.setEnabled(self.player.can_go_next())
    
    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def quit_app(self):
        print("👋 Quitting application...")
        self.window._force_quit = True
        if hasattr(self.window, 'tray_icon'):
            self.window.tray_icon.hide()
        self.player.cleanup()
        self.window.cleanup()
        self.window.close()
        self.app.quit()
    
    def run(self):
        print("🚀 Starting Music Player Pro...")
        self.window.show()
        sys.exit(self.app.exec_())


def main():
    print("=" * 50)
    print("🎵 Music Player Pro - Starting...")
    print("=" * 50)
    
    # Check dependencies
    missing = []
    
    try:
        import vlc
        print("✅ VLC found")
    except ImportError:
        missing.append("python-vlc")
        print("❌ VLC not found")
    
    try:
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True, creationflags=creation_flags)
        print(f"✅ yt-dlp found: {result.stdout.decode().strip()}")
    except:
        missing.append("yt-dlp")
        print("❌ yt-dlp not found")
    
    if missing:
        app = QApplication([])
        msg = QMessageBox()
        msg.critical(None, "Missing Dependencies", 
                    f"Library yang belum terinstall:\n{', '.join(missing)}\n\n"
                    f"Install dengan:\n   pip install python-vlc yt-dlp ytmusicapi PyQt5")
        sys.exit(1)
    
    # Run app
    controller = MusicAppController()
    controller.run()


if __name__ == "__main__":
    main()