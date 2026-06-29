from PyQt5.QtCore import QThread, pyqtSignal
import locale
# Ensure a default locale to avoid gettext translation errors
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C')
import gettext
gettext.translation = lambda *args, **kwargs: gettext.NullTranslations()
from ytmusicapi import YTMusic

# Initialize YTMusic lazily to avoid translation file errors on import
def get_ytmusic():
    try:
        return YTMusic()
    except Exception:
        # Fallback: initialize without authentication; may have limited features
        return YTMusic()


class SearchService(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.query = ""
        self.callback = None
        self.error_callback = None
    
    def search(self, query, callback, error_callback):
        self.query = query
        self.callback = callback
        self.error_callback = error_callback
        self.start()
    
    def run(self):
        try:
            ytmusic = get_ytmusic()
            results = ytmusic.search(self.query, filter='songs', limit=10)
            
            if not results:
                results = ytmusic.search(self.query, limit=10)
            
            self.callback(results[:10])
        except Exception as e:
            self.error_callback(str(e))