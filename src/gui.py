import sys
import math
import random
import psutil
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QRadialGradient, QFont, QPainterPath

class ModernHUD(QWidget):
    def __init__(self):
        super().__init__()
        # Window Setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Dimensions
        screen = QApplication.primaryScreen().geometry()
        self.width = 600
        self.height = 400
        self.setGeometry(
            (screen.width() - self.width) // 2, 
            (screen.height() - self.height) // 2, 
            self.width, 
            self.height
        )
        
        # State Data
        self.state = "IDLE" # IDLE, LISTENING, THINKING, SPEAKING
        self.user_text = "System Online"
        self.ai_text = "Waiting for command..."
        self.cpu_percent = 0
        self.ram_percent = 0
        
        # Animation Variables
        self.angle_1 = 0
        self.angle_2 = 0
        self.angle_3 = 0
        self.pulse = 0
        self.pulse_dir = 1
        self.particles = [] # For background effect
        
        # Timers
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(16) # ~60 FPS
        
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(1000) # Every 1 sec
        
        self.update_stats()

    def update_stats(self):
        self.cpu_percent = psutil.cpu_percent()
        self.ram_percent = psutil.virtual_memory().percent

    def set_state(self, state):
        self.state = state
        
    def set_text(self, user, ai):
        self.user_text = user
        self.ai_text = ai

    def animate(self):
        # Rotate Rings
        self.angle_1 = (self.angle_1 + 2) % 360
        self.angle_2 = (self.angle_2 - 1.5) % 360
        self.angle_3 = (self.angle_3 + 0.5) % 360
        
        # Pulse Core
        if self.state in ["LISTENING", "SPEAKING"]:
            speed = 0.05 if self.state == "LISTENING" else 0.1
            self.pulse += speed * self.pulse_dir
            if self.pulse > 1 or self.pulse < 0:
                self.pulse_dir *= -1
        else:
            self.pulse = 0
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width / 2
        center_y = self.height / 2
        
        # 1. Draw Background (Tech Card Style)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 20, 20)
        
        bg_color = QColor(10, 15, 30, 200) # Dark Blue translucent
        painter.fillPath(path, bg_color)
        
        # Border
        pen = QPen(QColor(0, 255, 255, 100))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # 2. Draw Central Arc Reactor (Rings)
        self.draw_arc_ring(painter, center_x, center_y, 80, self.angle_1, QColor(0, 255, 255))
        self.draw_arc_ring(painter, center_x, center_y, 100, self.angle_2, QColor(0, 200, 255))
        self.draw_arc_ring(painter, center_x, center_y, 120, self.angle_3, QColor(0, 150, 255))
        
        # 3. Draw Core (Pulsing Orb)
        core_radius = 50 + (10 * self.pulse)
        gradient = QRadialGradient(center_x, center_y, core_radius)
        if self.state == "LISTENING":
            gradient.setColorAt(0, QColor(255, 50, 50)) # Red when listening
        elif self.state == "THINKING":
            gradient.setColorAt(0, QColor(255, 255, 0)) # Yellow when thinking
        else:
            gradient.setColorAt(0, QColor(0, 255, 255)) # Cyan otherwise
            
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(center_x, center_y), core_radius, core_radius)
        
        # 4. Draw Stats (CPU/RAM)
        self.draw_stat_bar(painter, 40, 60, "CPU", self.cpu_percent)
        self.draw_stat_bar(painter, self.width - 80, 60, "RAM", self.ram_percent)
        
        # 5. Draw Text (Conversation)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Consolas", 10))
        
        # User Text
        painter.drawText(QRectF(20, self.height - 80, self.width - 40, 30), Qt.AlignmentFlag.AlignLeft, f"USER: {self.user_text}")
        
        # AI Text (Larger)
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(0, 255, 255))
        painter.drawText(QRectF(20, self.height - 50, self.width - 40, 40), Qt.AlignmentFlag.AlignLeft, f"CHERRY: {self.ai_text}")

    def draw_arc_ring(self, painter, cx, cy, radius, angle, color):
        pen = QPen(color)
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Draw 3 segments
        rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
        start_angles = [0, 120, 240]
        for start in start_angles:
            painter.drawArc(rect, int((start + angle) * 16), int(90 * 16))

    def draw_stat_bar(self, painter, x, y, label, value):
        painter.save() # Save state to isolate changes
        try:
            # Label
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 8))
            # Explicit int casting to avoid ambiguity in C++ overloads
            painter.drawText(int(x), int(y) - 10, label)
            
            # Background Bar
            painter.setBrush(QColor(50, 50, 50))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(int(x), int(y), 40, 100)
            
            # Fill Bar
            # Ensure value is valid
            if value is None: value = 0
            if value > 100: value = 100
            
            fill_height = int((value / 100) * 100)
            painter.setBrush(QColor(0, 255, 255))
            painter.drawRect(int(x), int(y) + (100 - fill_height), 40, fill_height)
        except Exception as e:
            print(f"GUI Error: {e}")
        finally:
            painter.restore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = ModernHUD()
    hud.show()
    sys.exit(app.exec())