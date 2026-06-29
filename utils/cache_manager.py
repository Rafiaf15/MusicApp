import os
import json
import hashlib
from pathlib import Path


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
                with open(self.url_cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self):
        """Save cache ke file"""
        try:
            with open(self.url_cache_file, 'w') as f:
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