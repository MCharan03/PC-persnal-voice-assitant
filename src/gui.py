import sys
import math
import random
import psutil
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QSize
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QRadialGradient, QFont, QPainterPath, QConicalGradient

class ModernHUD(QWidget):
    def __init__(self):
        super().__init__()
        # Window Setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Dimensions (Focused on the Orb)
        self.orb_size = 300
        self.width = self.orb_size + 200 # Extra space for text
        self.height = self.orb_size + 150
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() - self.width - 50, 
            screen.height() - self.height - 50, 
            self.width, 
            self.height
        )
        
        # State Data
        self.state = "IDLE" 
        self.user_text = ""
        self.ai_text = "Cherry Online"
        self.cpu_percent = 0
        self.ram_percent = 0
        
        # Animation
        self.angle_1 = 0
        self.angle_2 = 0
        self.angle_3 = 0
        self.pulse = 0
        self.pulse_dir = 1
        self.glow_intensity = 0
        
        # Timers
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(16)
        
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(2000)

    def update_stats(self):
        self.cpu_percent = psutil.cpu_percent()
        self.ram_percent = psutil.virtual_memory().percent

    def set_state(self, state):
        self.state = state
        
    def set_text(self, user, ai):
        self.user_text = user
        self.ai_text = ai

    def animate(self):
        # Rotation speeds based on state
        speed_mult = 1.0
        if self.state == "THINKING": speed_mult = 4.0
        elif self.state == "LISTENING": speed_mult = 2.0
        
        self.angle_1 = (self.angle_1 + 1 * speed_mult) % 360
        self.angle_2 = (self.angle_2 - 1.5 * speed_mult) % 360
        self.angle_3 = (self.angle_3 + 0.5 * speed_mult) % 360
        
        # Pulse Logic
        if self.state in ["LISTENING", "SPEAKING"]:
            p_speed = 0.05 if self.state == "LISTENING" else 0.08
            self.pulse += p_speed * self.pulse_dir
            if self.pulse > 1 or self.pulse < 0:
                self.pulse_dir *= -1
        else:
            self.pulse = math.sin(time.time() * 2) * 0.5 + 0.5
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Center of the orb area
        cx = self.width / 2
        cy = self.orb_size / 2 + 20
        
        # 1. Background Glow (The 'Aura')
        glow_radius = (self.orb_size / 2) * (1.2 + 0.1 * self.pulse)
        aura = QRadialGradient(cx, cy, glow_radius)
        
        base_cyan = QColor(0, 255, 255)
        if self.state == "LISTENING":
            base_cyan = QColor(255, 50, 50)
        elif self.state == "THINKING":
            base_cyan = QColor(255, 255, 0)
        
        aura.setColorAt(0, QColor(base_cyan.red(), base_cyan.green(), base_cyan.blue(), 100))
        aura.setColorAt(0.5, QColor(base_cyan.red(), base_cyan.green(), base_cyan.blue(), 30))
        aura.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.setBrush(QBrush(aura))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), glow_radius, glow_radius)
        
        # 2. Tech Rings
        self.draw_tech_ring(painter, cx, cy, 100, self.angle_1, base_cyan, 3)
        self.draw_tech_ring(painter, cx, cy, 120, self.angle_2, base_cyan.darker(150), 2)
        self.draw_tech_ring(painter, cx, cy, 140, self.angle_3, base_cyan, 1)
        
        # 3. The Core Orb
        core_radius = 60 + (5 * self.pulse)
        core_grad = QRadialGradient(cx - 10, cy - 10, core_radius)
        core_grad.setColorAt(0, QColor(255, 255, 255, 255))
        core_grad.setColorAt(0.2, base_cyan)
        core_grad.setColorAt(1, base_cyan.darker(300))
        
        painter.setBrush(QBrush(core_grad))
        painter.drawEllipse(QPointF(cx, cy), core_radius, core_radius)
        
        # 4. Floating Text
        self.draw_floating_text(painter)

    def draw_tech_ring(self, painter, cx, cy, radius, angle, color, width):
        pen = QPen(color)
        pen.setWidth(width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
        # Dynamic gaps
        painter.drawArc(rect, int((angle) * 16), int(60 * 16))
        painter.drawArc(rect, int((angle + 120) * 16), int(30 * 16))
        painter.drawArc(rect, int((angle + 200) * 16), int(90 * 16))

    def draw_floating_text(self, painter):
        # AI Response below orb
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.setPen(QColor(0, 255, 255))
        
        # Wrap text logic or just simple clip
        ai_rect = QRectF(50, self.orb_size + 40, self.width - 100, 60)
        painter.drawText(ai_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self.ai_text)
        
        # User input above or small
        if self.user_text:
            painter.setFont(QFont("Segoe UI", 10))
            painter.setPen(QColor(200, 200, 200))
            user_rect = QRectF(50, self.orb_size + 100, self.width - 100, 30)
            painter.drawText(user_rect, Qt.AlignmentFlag.AlignCenter, f"\"{self.user_text}\"")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = ModernHUD()
    hud.show()
    sys.exit(app.exec())