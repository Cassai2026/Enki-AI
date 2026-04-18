import sys
import threading
import speech_recognition as sr
from pathlib import Path
from datetime import datetime
import json
import time

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLineEdit, QLabel, QScrollArea, QFrame, 
    QComboBox, QMessageBox, QGraphicsOpacityEffect, QStackedWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPolygon, QRegion, QFont, QColor, QIcon
from PyQt5.QtCore import QPoint, QThread, pyqtSignal, QTimer, QEasingCurve, Qt
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtCore import QThread
import traceback

# Import the main JARVIS functions
import importlib.util

# Load the main JARVIS functions defensively
try:
    spec = importlib.util.spec_from_file_location("jarvis_core", r"d:\\JARVIS AI\\AI_Assistant\\Jarvis V 0.03.py")
    jarvis_core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(jarvis_core)

    speak = jarvis_core.speak
    open_program = jarvis_core.open_program
    route_command = jarvis_core.route_command
    normalize_text = jarvis_core.normalize_text
    build_file_index = jarvis_core.build_file_index
    mic = jarvis_core.mic
    recognizer = jarvis_core.recognizer
    PROGRAM_PATHS = jarvis_core.PROGRAM_PATHS
    FILE_INDEX = jarvis_core.FILE_INDEX
except Exception as e:
    print("Failed to load Jarvis core module:", e)
    traceback.print_exc()
    jarvis_core = None

    # Fallback stubs
    def speak(text):
        print("[stub speak]", text)

    def open_program(name):
        print("[stub open_program]", name)

    def route_command(cmd):
        try:
            t = cmd.strip().lower()
            if t == "shutdown":
                return ("shutdown", None)
            if t.startswith("open "):
                return ("open", t.split(" ", 1)[1])
        except Exception:
            pass
        return ("unknown", None)

    def normalize_text(t):
        return t

    def build_file_index():
        return {}

    mic = None
    recognizer = None
    PROGRAM_PATHS = {}
    FILE_INDEX = {}


class VoiceListeningThread(QThread):
    """Thread to handle voice listening without blocking UI"""
    text_received = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.recognizer = recognizer
        self.mic = mic
        self.is_listening = False
    
    def run(self):
        if not self.mic or not self.recognizer:
            self.status_changed.emit("✗ Mic/Recognizer unavailable")
            return

        while self.is_listening:
            try:
                with self.mic as source:
                    self.status_changed.emit("🔴 LISTENING...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=6)
                
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    self.text_received.emit(text)
                    self.status_changed.emit("✓ PROCESSED")
                except sr.UnknownValueError:
                    self.status_changed.emit("⚠ UNCLEAR INPUT")
                except Exception as e:
                    self.status_changed.emit(f"✗ ERROR: {str(e)[:20]}")
            except Exception as e:
                self.status_changed.emit("✗ MIC ERROR")
                break


class GlowingLabel(QLabel):
    """Label with neon glow effect"""
    def __init__(self, text, glow_color="#00D9FF"):
        super().__init__(text)
        self.setFont(QFont("Arial", 10, QFont.Bold))
        self.glow_color = glow_color
        
        # Apply glow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(glow_color))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)


class NeonButton(QPushButton):
    """Button with neon glow animation"""
    def __init__(self, text):
        super().__init__(text)
        self.glow_timer = QTimer()
        self.glow_intensity = 0
        self.glow_increasing = True
        self.glow_timer.timeout.connect(self.update_glow)
        
    def enterEvent(self, event):
        self.glow_timer.start(30)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.glow_timer.stop()
        self.glow_intensity = 0
        self.update_style()
        super().leaveEvent(event)
    
    def update_glow(self):
        if self.glow_increasing:
            self.glow_intensity += 5
            if self.glow_intensity >= 100:
                self.glow_increasing = False
        else:
            self.glow_intensity -= 5
            if self.glow_intensity <= 0:
                self.glow_increasing = True
        self.update_style()
    
    def update_style(self):
        shadow_blur = 8 + (self.glow_intensity // 10)
        glow_opacity = 0.3 + (self.glow_intensity / 100) * 0.7
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(shadow_blur)
        shadow.setColor(QColor(0, 217, 255, int(255 * glow_opacity)))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)


class NeonChatMessage(QFrame):
    """Neon styled chat message"""
    def __init__(self, text, is_jarvis=False):
        super().__init__()
        self.is_jarvis = is_jarvis
        self.setup_ui(text)
    
    def setup_ui(self, text):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        if self.is_jarvis:
            # JARVIS message - Cyan neon
            label.setFont(QFont("Consolas", 10, QFont.Bold))
            label.setStyleSheet("""
                color: #00FFFF;
                background-color: rgba(0, 60, 80, 180);
                padding: 10px;
                border: 2px solid #00D9FF;
                border-radius: 8px;
            """)
            # Add glow
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(12)
            shadow.setColor(QColor(0, 217, 255, 100))
            shadow.setOffset(0, 0)
            label.setGraphicsEffect(shadow)
        else:
            # User message - Blue neon
            label.setFont(QFont("Consolas", 10))
            label.setStyleSheet("""
                color: #00EEFF;
                background-color: rgba(20, 60, 100, 180);
                padding: 10px;
                border: 2px solid #0088FF;
                border-radius: 8px;
            """)
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 136, 255, 80))
            shadow.setOffset(0, 0)
            label.setGraphicsEffect(shadow)
        
        layout.addWidget(label)
        self.setLayout(layout)
        self.setStyleSheet("background-color: transparent; border: none;")


class CyberpunkJARVISGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.voice_thread = None
        self.scroll_area = None
        self.chat_layout = None
        self.chat_container = None
        self.dark_mode = True  # Start with dark mode
        self.setMinimumSize(600, 500)
        self.init_ui()
        
        QTimer.singleShot(0, self.set_triangular_shape)
def set_spherical_shape(self):
    """Set the window shape to a sphere (circle)"""
    size = min(self.width(), self.height())
    region = QRegion(self.width() // 2 - size // 2, self.height() // 2 - size // 2, size, size, QRegion.Ellipse)
    self.setMask(region)
    
    def init_ui(self):
        self.setWindowTitle("J.A.R.V.I.S - NEON EDITION")
        self.setGeometry(100, 100, 1000, 750)
        self.setWindowIcon(QIcon())
        
        # Apply cyberpunk dark theme
        self.apply_cyberpunk_theme()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # HEADER WITH ANIMATED ELEMENTS
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(0,50,100,100), stop:0.5 rgba(0,80,120,100), stop:1 rgba(0,50,100,100));
                border: 2px solid #0088FF;
                border-radius: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 12, 12, 12)
        header_layout.setSpacing(10)

        # Animated title
        title_label = QLabel("⚡ J.A.R.V.I.S ⚡")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #00FFFF;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 255, 255, 150))
        shadow.setOffset(0, 0)
        title_label.setGraphicsEffect(shadow)
        header_layout.addWidget(title_label)

        subtitle = QLabel("NEON CYBERPUNK EDITION")
        subtitle.setFont(QFont("Arial", 9, QFont.Bold))
        subtitle.setStyleSheet("color: #00D9FF;")
        header_layout.addWidget(subtitle)

        header_layout.addStretch()

        # Dark mode toggle button
        self.theme_btn = NeonButton("🌙 DARK")
        self.theme_btn.setFixedWidth(100)
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)

        main_layout.addWidget(header_frame)
        
        # SYSTEM STATUS PANEL
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 30, 60, 150);
                border: 2px solid #00FF88;
                border-radius: 8px;
            }
        """)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 6, 10, 6)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 14))
        self.status_indicator.setStyleSheet("color: #00FF88;")
        status_layout.addWidget(self.status_indicator)
        
        self.status_label = QLabel("[ SYSTEM ONLINE ]")
        self.status_label.setFont(QFont("Consolas", 10, QFont.Bold))
        self.status_label.setStyleSheet("color: #00FF88;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setFont(QFont("Consolas", 9))
        self.cpu_label.setStyleSheet("color: #00FFFF;")
        status_layout.addWidget(self.cpu_label)
        
        main_layout.addWidget(status_frame)
        
        # CHAT DISPLAY WITH NEON BORDER
        chat_label = QLabel("[ ▧ NEURAL INTERFACE ▧ ]")
        chat_label.setFont(QFont("Consolas", 11, QFont.Bold))
        chat_label.setStyleSheet("color: #00D9FF;")
        main_layout.addWidget(chat_label)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: rgba(0, 20, 50, 200);
                border: 3px solid #0088FF;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #00D9FF;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00FFFF;
            }
        """)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(8, 8, 8, 8)
        self.chat_layout.addStretch()
        
        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area, 1)
        
        # VOICE INPUT SECTION
        voice_label = QLabel("[ VOICE RECOGNITION ]")
        voice_label.setFont(QFont("Consolas", 10, QFont.Bold))
        voice_label.setStyleSheet("color: #FF00FF;")
        main_layout.addWidget(voice_label)
        
        voice_layout = QHBoxLayout()
        self.voice_btn = NeonButton("🎤 ACTIVATE VOCAL INPUT")
        self.voice_btn.setMinimumHeight(45)
        self.voice_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.voice_btn.clicked.connect(self.toggle_voice_listening)
        voice_layout.addWidget(self.voice_btn)
        main_layout.addLayout(voice_layout)
        
        # TEXT INPUT SECTION
        input_label = QLabel("[ COMMAND INPUT ]")
        input_label.setFont(QFont("Consolas", 10, QFont.Bold))
        input_label.setStyleSheet("color: #FF00FF;")
        main_layout.addWidget(input_label)
        
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command or query...")
        self.input_field.setMinimumHeight(40)
        self.input_field.setFont(QFont("Consolas", 10))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 30, 60, 200);
                color: #00FFFF;
                border: 2px solid #00D9FF;
                border-radius: 8px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #00FFFF;
                background-color: rgba(0, 50, 100, 200);
            }
        """)
        self.input_field.returnPressed.connect(self.submit_text_command)
        input_layout.addWidget(self.input_field)
        
        self.submit_btn = NeonButton("→ TRANSMIT")
        self.submit_btn.setFixedWidth(120)
        self.submit_btn.setMinimumHeight(40)
        self.submit_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.submit_btn.clicked.connect(self.submit_text_command)
        input_layout.addWidget(self.submit_btn)
        
        main_layout.addLayout(input_layout)
    
    def apply_cyberpunk_theme(self):
        """Apply neon cyberpunk theme"""
        self.setStyleSheet("""
            * { font-family: 'Consolas', 'Courier New', monospace; }
            QMainWindow, QWidget {
                background-color: #0a0e27;
                color: #00D9FF;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: rgba(0, 30, 60, 200);
                color: #00FFFF;
                border: 2px solid #0088FF;
                border-radius: 6px;
                padding: 6px;
                font-size: 10pt;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #00FFFF;
                background-color: rgba(0, 50, 100, 220);
            }
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(0, 150, 255, 200), stop:1 rgba(0, 100, 200, 200));
                color: #FFFFFF;
                border: 2px solid #00FFFF;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 30px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(0, 200, 255, 220), stop:1 rgba(0, 150, 220, 220));
                border: 2px solid #00FFFF;
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(0, 100, 200, 200), stop:1 rgba(0, 80, 180, 200));
            }
            QLabel { color: #00D9FF; }
            QScrollArea { background-color: transparent; border: none; }
            QComboBox QAbstractItemView { 
                background-color: rgba(0, 30, 60, 220); 
                color: #00FFFF; 
                selection-background-color: #0088FF; 
            }
        """)
    
    def apply_light_theme(self):
        """Apply light theme"""
        self.setStyleSheet("""
            * { font-family: 'Segoe UI', Arial, sans-serif; }
            QMainWindow, QWidget {
                background-color: #F5F7FA;
                color: #1A1A1A;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #FFFFFF;
                color: #0066CC;
                border: 2px solid #0088FF;
                border-radius: 6px;
                padding: 6px;
                font-size: 10pt;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #0066CC;
                background-color: #F0F8FF;
            }
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #0088FF, stop:1 #0055CC);
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 30px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #00AAFF, stop:1 #0077DD);
            }
            QPushButton:pressed {
                background: #0055CC;
            }
            QLabel { color: #1A1A1A; }
            QScrollArea { background-color: transparent; border: none; }
            QComboBox QAbstractItemView { 
                background-color: #FFFFFF; 
                color: #0066CC; 
                selection-background-color: #0088FF; 
            }
        """)
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_cyberpunk_theme()
            self.theme_btn.setText("🌙 DARK")
            self.add_chat_message("[ Theme switched to NEON CYBERPUNK ]", is_jarvis=True)
        else:
            self.apply_light_theme()
            self.theme_btn.setText("☀️ LIGHT")
            self.add_chat_message("[ Theme switched to LIGHT MODE ]", is_jarvis=True)
    
    def add_chat_message(self, text, is_jarvis=False):
        """Add a message to the chat display with smooth animation"""
        message = NeonChatMessage(text, is_jarvis=is_jarvis)
        
        # Add fade-in animation
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0)
        message.setGraphicsEffect(opacity_effect)
        
        # Insert before the stretch
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, message)
        
        # Animate in
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
        
        # Auto-scroll to bottom
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
    
    def toggle_voice_listening(self):
        """Toggle voice listening"""
        if self.voice_thread and self.voice_thread.is_listening:
            self.voice_thread.is_listening = False
            self.voice_btn.setText("🎤 ACTIVATE VOCAL INPUT")
            self.add_chat_message("[ Voice input DEACTIVATED ]", is_jarvis=True)
        else:
            self.voice_thread = VoiceListeningThread()
            self.voice_thread.is_listening = True
            self.voice_thread.text_received.connect(self.on_voice_text)
            self.voice_thread.status_changed.connect(self.on_voice_status)
            self.voice_thread.start()
            self.voice_btn.setText("⏹ STOP LISTENING")
            self.add_chat_message("[ Voice input ACTIVATED ]", is_jarvis=True)
    
    def on_voice_text(self, text):
        """Handle voice input"""
        self.add_chat_message(text, is_jarvis=False)
        self.process_command(text)
    
    def on_voice_status(self, status):
        """Update voice status"""
        self.status_label.setText(f"[ {status} ]")
    
    def submit_text_command(self):
        """Submit text command"""
        text = self.input_field.text().strip()
        if not text:
            return
        
        self.add_chat_message(text, is_jarvis=False)
        self.input_field.clear()
        self.process_command(text)
    
    def process_command(self, command):
        """Process a command"""
        try:
            action, param = route_command(command)
            
            if action == "open":
                self.add_chat_message(f"▹ Opening: {param}...", is_jarvis=True)
                open_program(param)
            elif action == "shutdown":
                self.add_chat_message("[ INITIATING SHUTDOWN ]", is_jarvis=True)
                speak("Shutting down. Goodbye!")
                self.close()
            else:
                self.add_chat_message(f"▹ Command registered: {command}", is_jarvis=True)
                speak(f"Processed command: {command}")
        except Exception as e:
            self.add_chat_message(f"✗ Error: {str(e)[:50]}", is_jarvis=True)


def main():
    app = QApplication(sys.argv)
    gui = CyberpunkJARVISGui()
    gui.show()
    
    # Show welcome message
    gui.add_chat_message("[ ▧ NEURAL INTERFACE ONLINE ▧ ]", is_jarvis=True)
    gui.add_chat_message("[ INITIATING SYSTEM BOOT SEQUENCE ]", is_jarvis=True)
    gui.add_chat_message("[ ALL SYSTEMS NOMINAL ]", is_jarvis=True)
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
