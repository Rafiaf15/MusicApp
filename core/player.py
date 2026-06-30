import vlc
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import random
import time


class MusicPlayer(QObject):
    """Optimized music player dengan semua attribute yang diperlukan"""
    
    # Signals
    state_changed = pyqtSignal(str)
    position_changed = pyqtSignal(int, int)
    duration_changed = pyqtSignal(int)
    volume_changed = pyqtSignal(int)
    song_ended = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # ✅ PENTING: Inisialisasi SEMUA attribute yang dibutuhkan
        self.current_index = -1
        self.play_history = []
        self.is_playing = False
        self.audio_url = None
        self.duration_ms = 0
        self.total_songs = 0
        
        # Playback modes
        self.shuffle_mode = False
        self.repeat_mode = 0  # 0=off, 1=all, 2=one
        self.shuffled_indices = []
        
        # Guards
        self._is_transitioning = False
        self._last_auto_next_time = 0
        self._last_position = 0
        
        # VLC Instance dengan konfigurasi optimal
        try:
            self.vlc_instance = vlc.Instance(
                '--no-xlib',
                '--quiet',
                '--no-video-title-show',
                '--no-snapshot-preview',
                '--no-stats',
                '--no-osd',
                '--no-loop',
                '--network-caching=500',
                '--file-caching=500',
                '--live-caching=500',
            )
            self.player = self.vlc_instance.media_player_new()
        except Exception as e:
            self.error_occurred.emit(f"VLC initialization error: {e}")
            raise
        
        # Timer untuk update progress
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_tick)
        self.timer.start(250)
        
        # Set volume default
        self.player.audio_set_volume(70)
        
        print("✅ MusicPlayer initialized with all attributes")
    
    # ==================== PLAYBACK CONTROLS ====================
    
    def load_media(self, url):
        """Load media dari URL"""
        try:
            self.audio_url = url
            media = self.vlc_instance.media_new(url)
            media.add_option(':network-caching=500')
            media.add_option(':file-caching=500')
            self.player.set_media(media)
        except Exception as e:
            self.error_occurred.emit(f"Error loading media: {e}")
    
    def play(self):
        """Start playback"""
        try:
            if self.player.play() == -1:
                self.error_occurred.emit("Cannot start playback")
                return
            self.is_playing = True
            self.state_changed.emit('playing')
        except Exception as e:
            self.error_occurred.emit(f"Play error: {e}")
    
    def pause(self):
        """Pause playback"""
        self.player.pause()
        self.is_playing = False
        self.state_changed.emit('paused')
    
    def stop(self):
        """Stop playback"""
        self.player.stop()
        self.is_playing = False
        self.state_changed.emit('stopped')
    
    def toggle_playback(self):
        """Toggle play/pause"""
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    # ==================== VOLUME CONTROLS ====================
    
    def set_volume(self, value):
        """Set volume (0-100)"""
        self.player.audio_set_volume(value)
        self.volume_changed.emit(value)

    def set_playback_rate(self, rate: float):
        """Set playback speed. Accepted values: 0.5, 1.0, 1.2, 1.5, 2.0"""
        # VLC expects a float rate; clamp to allowed values
        allowed = {0.5, 1.0, 1.2, 1.5, 2.0}
        if rate not in allowed:
            # Emit error but keep current rate
            self.error_occurred.emit(f"Unsupported playback rate: {rate}")
            return
        try:
            self.player.set_rate(rate)
        except Exception as e:
            self.error_occurred.emit(f"Failed to set playback rate: {e}")
    
    def get_volume(self):
        """Get current volume"""
        return self.player.audio_get_volume()
    
    def set_mute(self, mute):
        """Mute/unmute"""
        self.player.audio_set_mute(mute)
    
    # ==================== SEEK & POSITION ====================
    
    def seek(self, position_ms):
        """Seek to position (ms)"""
        if self.duration_ms > 0:
            self.player.set_time(position_ms)
    
    def get_position(self):
        """Get current position (ms)"""
        return self.player.get_time()
    
    def get_duration(self):
        """Get total duration (ms)"""
        return self.player.get_length()
    
    # ==================== TIMER ====================
    
    def _on_timer_tick(self):
        """Timer tick - update progress dengan debouncing"""
        if not self.is_playing:
            return
        
        try:
            current = self.get_position()
            total = self.get_duration()
            
            # Debouncing - skip jika nilai tidak berubah
            if current == self._last_position:
                return
            self._last_position = current
            
            if total > 0 and current > 0:
                self.duration_ms = total
                self.position_changed.emit(current, total)
                
                # Auto-next dengan guard yang ketat
                if current >= total - 500:
                    current_time = time.time()
                    if current_time - self._last_auto_next_time > 3:
                        self._last_auto_next_time = current_time
                        self.song_ended.emit()
        except Exception as e:
            # Jangan crash aplikasi karena timer error
            pass
    
    # ==================== PLAYBACK MODES ====================
    
    def set_total_songs(self, total):
        """Set total songs untuk perhitungan index"""
        self.total_songs = total
    
    def toggle_shuffle(self, total_songs):
        """Toggle shuffle mode"""
        self.shuffle_mode = not self.shuffle_mode
        
        if self.shuffle_mode:
            self.shuffled_indices = list(range(total_songs))
            random.shuffle(self.shuffled_indices)
            
            if self.current_index >= 0 and self.current_index in self.shuffled_indices:
                self.shuffled_indices.remove(self.current_index)
                self.shuffled_indices.insert(0, self.current_index)
        else:
            self.shuffled_indices = []
        
        return self.shuffle_mode
    
    def toggle_repeat(self):
        """Toggle repeat mode: 0→1→2→0"""
        self.repeat_mode = (self.repeat_mode + 1) % 3
        return self.repeat_mode
    
    def get_next_index(self):
        """Get next index berdasarkan mode"""
        if self.total_songs == 0:
            return -1
        
        # Repeat one
        if self.repeat_mode == 2:
            return self.current_index
        
        # Shuffle mode
        if self.shuffle_mode and self.shuffled_indices:
            try:
                current_pos = self.shuffled_indices.index(self.current_index)
                if current_pos + 1 < len(self.shuffled_indices):
                    return self.shuffled_indices[current_pos + 1]
                elif self.repeat_mode == 1:
                    random.shuffle(self.shuffled_indices)
                    return self.shuffled_indices[0]
                else:
                    return -1
            except ValueError:
                return self.shuffled_indices[0] if self.shuffled_indices else -1
        
        # Normal mode
        next_idx = self.current_index + 1
        if next_idx < self.total_songs:
            return next_idx
        elif self.repeat_mode == 1:
            return 0
        else:
            return -1
    
    def get_previous_index(self):
        """Get previous index"""
        if self.total_songs == 0:
            return -1
        
        if self.shuffle_mode and self.play_history:
            return self.play_history.pop()
        
        prev_idx = self.current_index - 1
        if prev_idx >= 0:
            return prev_idx
        elif self.repeat_mode == 1:
            return self.total_songs - 1
        else:
            return -1
    
    def can_go_previous(self):
        """Check if can go previous"""
        if self.repeat_mode > 0:
            return True
        if self.shuffle_mode and self.play_history:
            return True
        return self.current_index > 0
    
    def can_go_next(self):
        """Check if can go next"""
        if self.repeat_mode > 0:
            return True
        if self.shuffle_mode and self.shuffled_indices:
            try:
                current_pos = self.shuffled_indices.index(self.current_index)
                return current_pos + 1 < len(self.shuffled_indices)
            except ValueError:
                return True
        return self.current_index < self.total_songs - 1
    
    # ==================== CLEANUP ====================
    
    def cleanup(self):
        """Cleanup resources dengan proper"""
        try:
            self.timer.stop()
            self.stop()
            if hasattr(self, 'vlc_instance'):
                self.vlc_instance.release()
            print("✅ MusicPlayer cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")