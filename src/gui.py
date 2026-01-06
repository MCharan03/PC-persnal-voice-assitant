import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Screen dimensions
        screen = QApplication.primaryScreen().geometry()
        self.width = 400
        self.height = 100
        self.setGeometry(
            (screen.width() - self.width) // 2, 
            screen.height() - self.height - 50, 
            self.width, 
            self.height
        )
        
        # State
        self.is_active = False
        self.color = QColor(0, 255, 255, 100) # Cyan glow
        self.pulse_size = 0
        self.pulse_dir = 1
        
        # Animation Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)
        
        self.hide() # Start hidden

    def animate(self):
        if self.is_active:
            self.pulse_size += 0.5 * self.pulse_dir
            if self.pulse_size > 10 or self.pulse_size < 0:
                self.pulse_dir *= -1
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.is_active:
            # Draw glowing orb/bar
            painter.setBrush(QBrush(self.color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            center_x = self.width // 2
            center_y = self.height // 2
            radius = 30 + self.pulse_size
            
            painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius*2), int(radius*2))
            
            # Draw Status Text
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Listening...")

    def show_overlay(self):
        self.is_active = True
        self.show()
    
    def hide_overlay(self):
        self.is_active = False
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = Overlay()
    overlay.show_overlay() # Show for testing
    sys.exit(app.exec())
