from PyQt5.QtCore import QThread, pyqtSignal
from ytmusicapi import YTMusic

ytmusic = YTMusic()


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
            results = ytmusic.search(self.query, filter='songs', limit=10)
            
            if not results:
                results = ytmusic.search(self.query, limit=10)
            
            self.callback(results[:10])
        except Exception as e:
            self.error_callback(str(e))