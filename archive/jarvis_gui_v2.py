import sys
import threading
import speech_recognition as sr
from pathlib import Path
from datetime import datetime
import json

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLineEdit, QLabel, QScrollArea, QFrame, QComboBox,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QTextCursor
import traceback

# Import the main JARVIS functions
import importlib.util

# Load the main JARVIS functions defensively so import errors don't silently
# prevent the GUI from starting. If the core module fails to load we provide
# simple fallbacks so the UI can start and display the error.
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

    # Fallback stubs so the GUI can still run for debugging.
    def speak(text):
        print("[stub speak]", text,)

    def open_program(name):
        print("[stub open_program]", name)

    def route_command(cmd):
        # Minimal parsing: allow 'shutdown' and 'open <name>' patterns
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
        # Guard against missing microphone/recognizer from failed core import
        if not self.mic or not self.recognizer:
            self.status_changed.emit("✗ Mic/Recognizer unavailable")
            return

        while self.is_listening:
            try:
                with self.mic as source:
                    self.status_changed.emit("🔴 Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=6)
                
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    self.text_received.emit(text)
                    self.status_changed.emit("✓ Processed")
                except sr.UnknownValueError:
                    self.status_changed.emit("⚠ Couldn't understand")
                except Exception as e:
                    self.status_changed.emit(f"✗ Error: {str(e)[:20]}")
            except Exception as e:
                self.status_changed.emit(f"✗ Mic Error")
                break

class JARVISChatMessage(QFrame):
    """Custom widget for chat messages"""
    def __init__(self, text, is_jarvis=False):
        super().__init__()
        self.is_jarvis = is_jarvis
        self.setup_ui(text)
    
    def setup_ui(self, text):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        if self.is_jarvis:
            # JARVIS message - cyan/blue with Matrix green accent
            label.setFont(QFont("Segoe UI", 10, QFont.Bold))
            label.setStyleSheet("""
                color: #D6F7FF;
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(14,38,60,220), stop:1 rgba(6,20,34,220));
                padding: 10px;
                border: 1px solid rgba(255,255,255,0.03);
                border-left: 4px solid #4fc3ff;
                border-radius: 12px;
            """)
            self.setStyleSheet("background-color: transparent; border: none;")
        else:
            # User message - darker blue
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("""
                color: #E8F6FF;
                background-color: rgba(28,32,36,220);
                padding: 10px;
                border: 1px solid rgba(255,255,255,0.02);
                border-left: 4px solid #6aa6ff;
                border-radius: 12px;
            """)
            self.setStyleSheet("background-color: transparent; border: none;")
        
        layout.addWidget(label)
        self.setLayout(layout)

class JARVISGui(QMainWindow):
    program_launched = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.voice_thread = None
        self.scroll_area = None
        self.chat_layout = None
        self.chat_container = None
        self.init_ui()
        self.program_launched.connect(self.on_program_launched)
    
    def init_ui(self):
        self.setWindowTitle("J.A.R.V.I.S - AI Assistant")
        self.setGeometry(100, 100, 900, 700)
        
        # Modern dark theme (cleaner, rounded, subtle accents)
        self.setStyleSheet("""
            * { font-family: 'Segoe UI', Roboto, Arial; }
            QMainWindow, QWidget {
                background-color: #0f1216;
                color: #D7E9FF;
            }
            /* Inputs */
            QLineEdit, QTextEdit, QComboBox {
                background-color: #13161a;
                color: #E6F3FF;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 8px;
                padding: 8px;
                font-size: 10pt;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid rgba(80,160,255,0.9);
                background-color: #0f171d;
            }
            /* Buttons */
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #1f6fb3, stop:1 #1a57a0);
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 8px 14px;
                font-weight: 600;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #2a7fcd, stop:1 #2168b0);
            }
            QPushButton:pressed { /* transform: translateY(1px); */ }
            /* Flat small buttons */
            QPushButton#flat {
                background: transparent;
                border: 1px solid rgba(255,255,255,0.03);
                color: #BFDFFF;
            }
            /* Labels */
            QLabel { color: #CFE9FF; }
            /* Scroll area and chat */
            QScrollArea { background-color: transparent; border: none; }
            /* Scrollbar */
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: rgba(150,200,255,0.12);
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover { background: rgba(150,200,255,0.2); }
            /* Combo box popup */
            QComboBox QAbstractItemView { background-color: #0f161a; color: #DFF; selection-background-color: #234f7a; }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Modern header
        header_frame = QFrame()
        header_frame.setObjectName('header')
        header_frame.setStyleSheet('QFrame#header { background: transparent; }')
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(6, 6, 6, 6)

        icon_label = QLabel("🤖")
        icon_label.setFont(QFont('Segoe UI Emoji', 18))
        header_layout.addWidget(icon_label)

        jarvis_title = QLabel("J.A.R.V.I.S — Assistant")
        jarvis_title.setFont(QFont("Segoe UI", 14, QFont.DemiBold))
        jarvis_title.setStyleSheet("color: #E6FBFF;")
        header_layout.addWidget(jarvis_title)

        header_layout.addStretch()

        # small settings / close placeholders
        help_btn = QPushButton("?")
        help_btn.setObjectName('flat')
        help_btn.setFixedSize(28, 28)
        header_layout.addWidget(help_btn)

        main_layout.addWidget(header_frame)
        
        # Chat display
        chat_label = QLabel("[ SYSTEM LOG ]")
        chat_label.setFont(QFont("Consolas", 9, QFont.Bold))
        chat_label.setStyleSheet("color: #00FF00;")
        main_layout.addWidget(chat_label)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #0f1f2f;
                border: 2px solid #00D9FF;
                border-radius: 5px;
            }
        """)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(8)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.addStretch()
        
        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area, 1)
        
        # Status indicator
        status_layout = QHBoxLayout()
        self.status_label = QLabel("● System Ready")
        self.status_label.setFont(QFont("Consolas", 10, QFont.Bold))
        self.status_label.setStyleSheet("color: #00FF00;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        main_layout.addLayout(status_layout)
        
        # Voice input section
        voice_layout = QHBoxLayout()
        self.voice_btn = QPushButton("🎤 VOICE INPUT")
        self.voice_btn.setMinimumHeight(40)
        self.voice_btn.clicked.connect(self.toggle_voice_listening)
        voice_layout.addWidget(self.voice_btn)
        main_layout.addLayout(voice_layout)
        
        # Text input section
        input_label = QLabel("[ USER INPUT ]")
        input_label.setFont(QFont("Consolas", 9, QFont.Bold))
        input_label.setStyleSheet("color: #00FF00;")
        main_layout.addWidget(input_label)
        
        input_layout = QHBoxLayout()
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type command or message...")
        self.text_input.setMinimumHeight(35)
        self.text_input.returnPressed.connect(self.send_text_command)
        input_layout.addWidget(self.text_input)
        
        send_btn = QPushButton("SEND")
        send_btn.setMinimumHeight(35)
        send_btn.setMinimumWidth(100)
        send_btn.clicked.connect(self.send_text_command)
        input_layout.addWidget(send_btn)
        
        main_layout.addLayout(input_layout)
        
        # Quick launch section
        quick_label = QLabel("[ QUICK PROGRAMS ]")
        quick_label.setFont(QFont("Consolas", 9, QFont.Bold))
        quick_label.setStyleSheet("color: #00FF00;")
        main_layout.addWidget(quick_label)
        
        programs_layout = QHBoxLayout()
        for program_name in list(PROGRAM_PATHS.keys())[:5]:
            btn = QPushButton(program_name.upper())
            btn.setMinimumHeight(30)
            btn.clicked.connect(lambda checked, p=program_name: self.quick_launch(p))
            programs_layout.addWidget(btn)
        
        programs_layout.addStretch()
        main_layout.addLayout(programs_layout)
        
        # Voice selector
        voice_layout_selector = QHBoxLayout()
        voice_label = QLabel("VOICE:")
        voice_label.setFont(QFont("Consolas", 9, QFont.Bold))
        voice_layout_selector.addWidget(voice_label)
        
        self.voice_combo = QComboBox()
        self.voice_combo.addItems([
            "en_GB-vctk-medium",
            "en_US-hfc-male",
            "en_US-hfc-female"
        ])
        self.voice_combo.setMinimumWidth(150)
        voice_layout_selector.addWidget(self.voice_combo)
        voice_layout_selector.addStretch()
        
        main_layout.addLayout(voice_layout_selector)
        
        # Add initial system message
        self.add_system_message("System initialized. Standing by for commands.")
    
    def add_chat_message(self, text, is_jarvis=False):
        """Add a message to the chat"""
        msg = JARVISChatMessage(text, is_jarvis)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg)
        
        # Scroll to bottom
        QTimer.singleShot(10, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
    
    def add_system_message(self, text):
        """Add a system message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        system_text = f"[{timestamp}] {text}"
        self.add_chat_message(system_text, is_jarvis=False)
    
    def toggle_voice_listening(self):
        """Start/stop voice listening"""
        if self.voice_thread is None or not self.voice_thread.is_listening:
            self.voice_thread = VoiceListeningThread()
            self.voice_thread.is_listening = True
            self.voice_thread.text_received.connect(self.process_voice_input)
            self.voice_thread.status_changed.connect(self.update_status)
            self.voice_thread.start()
            
            self.voice_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF3333;
                    color: #FFFFFF;
                    border: 2px solid #FF0000;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
            """)
            self.voice_btn.setText("⏹ STOP LISTENING")
            self.update_status("🔴 Voice input active...")
        else:
            self.voice_thread.is_listening = False
            self.voice_btn.setStyleSheet("")  # Reset to default
            self.voice_btn.setText("🎤 VOICE INPUT")
            self.update_status("● System Ready")
    
    def process_voice_input(self, text):
        """Process voice input"""
        self.add_chat_message(f"USER: {text}", is_jarvis=False)
        self.process_command(text)
    
    def send_text_command(self):
        """Send text command"""
        text = self.text_input.text().strip()
        if text:
            self.add_chat_message(f"USER: {text}", is_jarvis=False)
            self.text_input.clear()
            self.process_command(text)
    
    def process_command(self, command):
        """Process a command"""
        action, payload = route_command(command)
        
        if action == "shutdown":
            self.add_chat_message("JARVIS: Powering down. Goodbye.", is_jarvis=True)
            speak("Goodbye.")
            self.close()
        elif action == "help":
            help_text = "Commands: 'open [program]' to launch programs, 'shutdown' to exit."
            self.add_chat_message(f"JARVIS: {help_text}", is_jarvis=True)
        elif action == "open" and payload:
            self.add_chat_message(f"JARVIS: Opening {payload}...", is_jarvis=True)
            threading.Thread(
                target=lambda: (
                    open_program(payload),
                    self.add_chat_message(f"JARVIS: {payload} has been launched.", is_jarvis=True)
                ),
                daemon=True
            ).start()
        else:
            self.add_chat_message("JARVIS: Command not recognized.", is_jarvis=True)
    
    def quick_launch(self, program):
        """Quick launch a program"""
        self.add_chat_message(f"USER: open {program}", is_jarvis=False)
        self.add_chat_message(f"JARVIS: Opening {program}...", is_jarvis=True)
        def launch():
            open_program(program)
            self.program_launched.emit(program)
        threading.Thread(target=launch, daemon=True).start()

    def on_program_launched(self, program):
        self.add_chat_message(f"JARVIS: {program} has been launched.", is_jarvis=True)
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.voice_thread and self.voice_thread.is_listening:
            self.voice_thread.is_listening = False
        event.accept()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = JARVISGui()
        window.show()
        sys.exit(app.exec_())
    except Exception:
        tb = traceback.format_exc()
        print(tb)
        try:
            # Attempt to show an error dialog with details
            app = QApplication.instance() or QApplication(sys.argv)
            msg = QMessageBox()
            msg.setWindowTitle("JARVIS - Startup Error")
            msg.setText("An error occurred while starting JARVIS. See Details.")
            msg.setDetailedText(tb)
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
        except Exception:
            pass
        sys.exit(1)
