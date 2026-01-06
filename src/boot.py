import sys
import os
import subprocess
import time
import psutil
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QThread

# Path to python interpreter
PYTHON_EXE = sys.executable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ProcessManager(QThread):
    def __init__(self):
        super().__init__()
        self.server_process = None
        self.client_process = None

    def run(self):
        # 1. Start Server
        server_script = os.path.join(BASE_DIR, "src", "server", "app.py")
        print(f"Booting Server: {server_script}")
        # Use pythonw.exe (or creationflags) to hide console if desired, 
        # but for now we keep it visible for debugging or hide via CREATE_NO_WINDOW
        
        # CREATE_NO_WINDOW = 0x08000000
        self.server_process = subprocess.Popen(
            [PYTHON_EXE, server_script],
            cwd=BASE_DIR
            # creationflags=subprocess.CREATE_NO_WINDOW 
        )
        
        # Wait for server to warm up
        time.sleep(2)
        
        # 2. Start Client
        client_script = os.path.join(BASE_DIR, "src", "client_desktop.py")
        print(f"Booting Client: {client_script}")
        self.client_process = subprocess.Popen(
            [PYTHON_EXE, client_script],
            cwd=BASE_DIR
            # creationflags=subprocess.CREATE_NO_WINDOW
        )
        
    def stop_all(self):
        if self.client_process:
            self.client_process.terminate()
        if self.server_process:
            self.server_process.terminate()
        
        # Force kill if needed
        time.sleep(1)
        if self.client_process and self.client_process.poll() is None:
            self.client_process.kill()
        if self.server_process and self.server_process.poll() is None:
            self.server_process.kill()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # System Tray Setup
    icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
    else:
        # Fallback to system icon if icon.png is missing
        icon = app.style().standardIcon(app.style().StandardPixmap.SP_ComputerIcon)
    
    tray_icon = QSystemTrayIcon(icon, app)
    
    menu = QMenu()
    
    action_status = QAction("Cherry is Active")
    action_status.setEnabled(False)
    menu.addAction(action_status)
    
    menu.addSeparator()
    
    action_quit = QAction("Quit Cherry")
    action_quit.triggered.connect(app.quit)
    menu.addAction(action_quit)
    
    tray_icon.setContextMenu(menu)
    tray_icon.setToolTip("Cherry Voice Assistant")
    tray_icon.show()

    # Start Processes
    manager = ProcessManager()
    manager.start()
    
    # Handle Exit
    app.aboutToQuit.connect(manager.stop_all)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
