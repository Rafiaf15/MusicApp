import sys
import subprocess
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui import MusicApp

def check_dependencies():
    """Cek apakah semua dependencies terinstall"""
    missing = []
    
    try:
        import vlc
    except ImportError:
        missing.append("python-vlc")
    
    try:
        # ✅ Tambahkan creationflags
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        subprocess.run(
            ['yt-dlp', '--version'], 
            capture_output=True, 
            check=True,
            creationflags=creation_flags
        )
    except:
        missing.append("yt-dlp")
    
    if missing:
        from PyQt5.QtWidgets import QMessageBox
        app = QApplication([])
        msg = QMessageBox()
        msg.critical(None, "Missing Dependencies", 
                    f"Library yang belum terinstall:\n{', '.join(missing)}\n\n"
                    f"Install dengan:\n   pip install python-vlc yt-dlp ytmusicapi PyQt5")
        return False
    
    return True

def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setStyle("Fusion")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Music Player Pro")
    
    if not check_dependencies():
        sys.exit(1)
    
    window = MusicApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()