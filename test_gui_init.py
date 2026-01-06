try:
    from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
    from PyQt6.QtGui import QIcon
    import sys
    
    app = QApplication(sys.argv)
    print("SUCCESS: PyQt6 and SystemTray modules loaded correctly.")
    sys.exit(0)
except Exception as e:
    print(f"FAILURE: {e}")
    sys.exit(1)
