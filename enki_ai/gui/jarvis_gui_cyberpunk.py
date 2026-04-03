"""
JARVIS Cyberpunk GUI — PyQt5 graphical interface with neon theme.

Run:
    python -m enki_ai.gui.jarvis_gui_cyberpunk
"""

import logging
import sys
import threading

from PyQt5.QtCore import (  # type: ignore[import]
    QEasingCurve,
    QPropertyAnimation,
    QThread,
    QTimer,
    Qt,
    pyqtSignal,
)
from PyQt5.QtGui import QColor, QFont, QIcon, QRegion  # type: ignore[import]
from PyQt5.QtWidgets import (  # type: ignore[import]
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

# ---------------------------------------------------------------------------
# Import JARVIS core from package (replaces the old hardcoded path import)
# ---------------------------------------------------------------------------
try:
    import speech_recognition as sr  # type: ignore[import]
    from enki_ai.core.jarvis_core import (
        FILE_INDEX,
        PROGRAM_PATHS,  # noqa: F401
        build_file_index,
        normalize_text,
        open_program,
        route_command,
        speak,
    )
    from enki_ai.core.jarvis_core import _setup_mic as _setup_mic_fn

    _recognizer, _mic = _setup_mic_fn()
    recognizer = _recognizer
    mic = _mic
    _CORE_AVAILABLE = True
except Exception as _exc:
    logging.getLogger(__name__).warning("JARVIS core unavailable: %s", _exc)
    _CORE_AVAILABLE = False

    def speak(text: str) -> None:  # type: ignore[misc]
        print(f"[stub speak] {text}")

    def open_program(name: str) -> bool:  # type: ignore[misc]
        print(f"[stub open_program] {name}")
        return False

    def route_command(cmd: str):  # type: ignore[misc]
        t = cmd.strip().lower()
        if t == "shutdown":
            return ("shutdown", None)
        if t.startswith("open "):
            return ("open", t.split(" ", 1)[1])
        return ("unknown", None)

    def normalize_text(t: str) -> str:  # type: ignore[misc]
        return t

    def build_file_index() -> None:  # type: ignore[misc]
        pass

    mic = None
    recognizer = None
    FILE_INDEX: dict = {}  # type: ignore[assignment]

log = logging.getLogger("jarvis.gui")


# ---------------------------------------------------------------------------
# Custom widgets
# ---------------------------------------------------------------------------


class NeonButton(QPushButton):
    """Button with a pulsing neon glow on hover."""

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self._glow_timer = QTimer()
        self._glow_intensity = 0
        self._glow_increasing = True
        self._glow_timer.timeout.connect(self._update_glow)

    def enterEvent(self, event) -> None:
        self._glow_timer.start(30)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._glow_timer.stop()
        self._glow_intensity = 0
        self._apply_shadow()
        super().leaveEvent(event)

    def _update_glow(self) -> None:
        if self._glow_increasing:
            self._glow_intensity = min(100, self._glow_intensity + 5)
            if self._glow_intensity >= 100:
                self._glow_increasing = False
        else:
            self._glow_intensity = max(0, self._glow_intensity - 5)
            if self._glow_intensity <= 0:
                self._glow_increasing = True
        self._apply_shadow()

    def _apply_shadow(self) -> None:
        blur = 8 + self._glow_intensity // 10
        alpha = int(255 * (0.3 + self._glow_intensity / 100 * 0.7))
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setColor(QColor(0, 217, 255, alpha))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)


class NeonChatMessage(QFrame):
    """Styled chat bubble for JARVIS messages and user input."""

    def __init__(self, text: str, is_jarvis: bool = False) -> None:
        super().__init__()
        self._is_jarvis = is_jarvis
        self._build(text)

    def _build(self, text: str) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if self._is_jarvis:
            label.setFont(QFont("Consolas", 10, QFont.Bold))
            label.setStyleSheet(
                "color:#00FFFF; background:rgba(0,60,80,180); padding:10px;"
                "border:2px solid #00D9FF; border-radius:8px;"
            )
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(12)
            shadow.setColor(QColor(0, 217, 255, 100))
            shadow.setOffset(0, 0)
            label.setGraphicsEffect(shadow)
        else:
            label.setFont(QFont("Consolas", 10))
            label.setStyleSheet(
                "color:#00EEFF; background:rgba(20,60,100,180); padding:10px;"
                "border:2px solid #0088FF; border-radius:8px;"
            )
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 136, 255, 80))
            shadow.setOffset(0, 0)
            label.setGraphicsEffect(shadow)

        layout.addWidget(label)
        self.setLayout(layout)
        self.setStyleSheet("background-color:transparent; border:none;")


# ---------------------------------------------------------------------------
# Voice listening thread
# ---------------------------------------------------------------------------


class VoiceListeningThread(QThread):
    """Non-blocking voice recognition thread."""

    text_received = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.is_listening = False

    def run(self) -> None:
        if mic is None or recognizer is None:
            self.status_changed.emit("✗ Mic / Recognizer unavailable")
            return

        try:
            import speech_recognition as _sr  # type: ignore[import]
        except ImportError:
            self.status_changed.emit("✗ speech_recognition not installed")
            return

        while self.is_listening:
            try:
                with mic as source:
                    self.status_changed.emit("🔴 LISTENING…")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
                try:
                    text = recognizer.recognize_google(audio).lower()
                    self.text_received.emit(text)
                    self.status_changed.emit("✓ PROCESSED")
                except _sr.UnknownValueError:
                    self.status_changed.emit("⚠ UNCLEAR INPUT")
                except Exception as exc:
                    self.status_changed.emit(f"✗ ERROR: {str(exc)[:20]}")
            except Exception:
                self.status_changed.emit("✗ MIC ERROR")
                break


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

_DARK_CSS = """
* { font-family: 'Consolas', 'Courier New', monospace; }
QMainWindow, QWidget { background-color: #0a0e27; color: #00D9FF; }
QLineEdit, QTextEdit {
    background:rgba(0,30,60,200); color:#00FFFF;
    border:2px solid #0088FF; border-radius:6px; padding:6px; font-size:10pt;
}
QLineEdit:focus, QTextEdit:focus { border:2px solid #00FFFF; background:rgba(0,50,100,220); }
QPushButton {
    background:qlineargradient(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 rgba(0,150,255,200),stop:1 rgba(0,100,200,200));
    color:#FFF; border:2px solid #00FFFF; border-radius:8px; padding:8px 16px;
    font-weight:bold; font-size:10pt; min-height:30px;
}
QPushButton:hover {
    background:qlineargradient(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 rgba(0,200,255,220),stop:1 rgba(0,150,220,220));
}
QPushButton:pressed { background:qlineargradient(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 rgba(0,100,200,200),stop:1 rgba(0,80,180,200)); }
QLabel { color:#00D9FF; }
QScrollArea { background-color:transparent; border:none; }
QScrollBar:vertical { background:transparent; width:10px; }
QScrollBar::handle:vertical { background:#00D9FF; min-height:20px; border-radius:5px; }
QScrollBar::handle:vertical:hover { background:#00FFFF; }
"""

_LIGHT_CSS = """
* { font-family: 'Segoe UI', Arial, sans-serif; }
QMainWindow, QWidget { background-color:#F5F7FA; color:#1A1A1A; }
QLineEdit, QTextEdit {
    background:#FFF; color:#0066CC; border:2px solid #0088FF;
    border-radius:6px; padding:6px; font-size:10pt;
}
QLineEdit:focus, QTextEdit:focus { border:2px solid #0066CC; background:#F0F8FF; }
QPushButton {
    background:qlineargradient(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 #0088FF,stop:1 #0055CC);
    color:#FFF; border:none; border-radius:8px; padding:8px 16px;
    font-weight:bold; font-size:10pt; min-height:30px;
}
QPushButton:hover { background:qlineargradient(spread:pad,x1:0,y1:0,x2:0,y2:1,stop:0 #00AAFF,stop:1 #0077DD); }
QPushButton:pressed { background:#0055CC; }
QLabel { color:#1A1A1A; }
QScrollArea { background-color:transparent; border:none; }
"""


class CyberpunkJARVISGui(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.voice_thread: VoiceListeningThread | None = None
        self.dark_mode = True
        self.setMinimumSize(600, 500)
        self._init_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        self.setWindowTitle("J.A.R.V.I.S – NEON EDITION")
        self.setGeometry(100, 100, 1000, 750)
        self.setWindowIcon(QIcon())
        self.setStyleSheet(_DARK_CSS)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet(
            "QFrame{background:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,"
            "stop:0 rgba(0,50,100,100),stop:0.5 rgba(0,80,120,100),stop:1 rgba(0,50,100,100));"
            "border:2px solid #0088FF; border-radius:10px;}"
        )
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 12, 12, 12)

        title = QLabel("⚡ J.A.R.V.I.S ⚡")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color:#00FFFF;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 255, 255, 150))
        shadow.setOffset(0, 0)
        title.setGraphicsEffect(shadow)
        header_layout.addWidget(title)

        subtitle = QLabel("NEON CYBERPUNK EDITION")
        subtitle.setFont(QFont("Arial", 9, QFont.Bold))
        subtitle.setStyleSheet("color:#00D9FF;")
        header_layout.addWidget(subtitle)
        header_layout.addStretch()

        self.theme_btn = NeonButton("🌙 DARK")
        self.theme_btn.setFixedWidth(100)
        self.theme_btn.clicked.connect(self._toggle_theme)
        header_layout.addWidget(self.theme_btn)
        main_layout.addWidget(header_frame)

        # Status bar
        status_frame = QFrame()
        status_frame.setStyleSheet(
            "QFrame{background:rgba(0,30,60,150);border:2px solid #00FF88;border-radius:8px;}"
        )
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 6, 10, 6)

        dot = QLabel("●")
        dot.setFont(QFont("Arial", 14))
        dot.setStyleSheet("color:#00FF88;")
        status_layout.addWidget(dot)

        self.status_label = QLabel("[ SYSTEM ONLINE ]")
        self.status_label.setFont(QFont("Consolas", 10, QFont.Bold))
        self.status_label.setStyleSheet("color:#00FF88;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        main_layout.addWidget(status_frame)

        # Chat area
        chat_heading = QLabel("[ ▧ NEURAL INTERFACE ▧ ]")
        chat_heading.setFont(QFont("Consolas", 11, QFont.Bold))
        chat_heading.setStyleSheet("color:#00D9FF;")
        main_layout.addWidget(chat_heading)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            "QScrollArea{background:rgba(0,20,50,200);border:3px solid #0088FF;border-radius:5px;}"
        )
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(8, 8, 8, 8)
        self.chat_layout.addStretch()
        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area, 1)

        # Voice button
        voice_heading = QLabel("[ VOICE RECOGNITION ]")
        voice_heading.setFont(QFont("Consolas", 10, QFont.Bold))
        voice_heading.setStyleSheet("color:#FF00FF;")
        main_layout.addWidget(voice_heading)

        self.voice_btn = NeonButton("🎤 ACTIVATE VOCAL INPUT")
        self.voice_btn.setMinimumHeight(45)
        self.voice_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.voice_btn.clicked.connect(self._toggle_voice)
        main_layout.addWidget(self.voice_btn)

        # Text input
        input_heading = QLabel("[ COMMAND INPUT ]")
        input_heading.setFont(QFont("Consolas", 10, QFont.Bold))
        input_heading.setStyleSheet("color:#FF00FF;")
        main_layout.addWidget(input_heading)

        input_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command or query…")
        self.input_field.setMinimumHeight(40)
        self.input_field.setFont(QFont("Consolas", 10))
        self.input_field.returnPressed.connect(self._submit_text)
        input_row.addWidget(self.input_field)

        send_btn = NeonButton("→ TRANSMIT")
        send_btn.setFixedWidth(120)
        send_btn.setMinimumHeight(40)
        send_btn.setFont(QFont("Arial", 10, QFont.Bold))
        send_btn.clicked.connect(self._submit_text)
        input_row.addWidget(send_btn)
        main_layout.addLayout(input_row)

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def _toggle_theme(self) -> None:
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet(_DARK_CSS)
            self.theme_btn.setText("🌙 DARK")
            self.add_message("[ Theme: NEON CYBERPUNK ]", is_jarvis=True)
        else:
            self.setStyleSheet(_LIGHT_CSS)
            self.theme_btn.setText("☀️ LIGHT")
            self.add_message("[ Theme: LIGHT MODE ]", is_jarvis=True)

    # ------------------------------------------------------------------
    # Chat helpers
    # ------------------------------------------------------------------

    def add_message(self, text: str, is_jarvis: bool = False) -> None:
        """Append a message bubble to the chat area with a fade-in animation."""
        msg = NeonChatMessage(text, is_jarvis=is_jarvis)
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(0.0)
        msg.setGraphicsEffect(effect)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()
        # Keep reference so it isn't GC'd before finishing
        msg._anim = anim  # type: ignore[attr-defined]

        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    # ------------------------------------------------------------------
    # Voice
    # ------------------------------------------------------------------

    def _toggle_voice(self) -> None:
        if self.voice_thread and self.voice_thread.is_listening:
            self.voice_thread.is_listening = False
            self.voice_btn.setText("🎤 ACTIVATE VOCAL INPUT")
            self.add_message("[ Voice input DEACTIVATED ]", is_jarvis=True)
        else:
            self.voice_thread = VoiceListeningThread()
            self.voice_thread.is_listening = True
            self.voice_thread.text_received.connect(self._on_voice_text)
            self.voice_thread.status_changed.connect(self._on_voice_status)
            self.voice_thread.start()
            self.voice_btn.setText("⏹ STOP LISTENING")
            self.add_message("[ Voice input ACTIVATED ]", is_jarvis=True)

    def _on_voice_text(self, text: str) -> None:
        self.add_message(text, is_jarvis=False)
        self._process_command(text)

    def _on_voice_status(self, status: str) -> None:
        self.status_label.setText(f"[ {status} ]")

    # ------------------------------------------------------------------
    # Command processing
    # ------------------------------------------------------------------

    def _submit_text(self) -> None:
        text = self.input_field.text().strip()
        if not text:
            return
        self.add_message(text, is_jarvis=False)
        self.input_field.clear()
        self._process_command(text)

    def _process_command(self, command: str) -> None:
        try:
            action, param = route_command(command)
            if action == "open":
                self.add_message(f"▹ Opening: {param}…", is_jarvis=True)
                threading.Thread(target=open_program, args=(param,), daemon=True).start()
            elif action == "shutdown":
                self.add_message("[ INITIATING SHUTDOWN ]", is_jarvis=True)
                speak("Shutting down. Goodbye!")
                self.close()
            elif action in ("volume_set", "volume_up", "volume_down", "mute", "unmute"):
                from enki_ai.core.jarvis_core import (
                    change_volume,
                    extract_volume_number,
                    mute_system,
                    set_system_volume,
                )
                if action == "volume_set" and param:
                    ok = set_system_volume(int(param))
                    self.add_message(f"▹ Volume {'set to ' + param + '%' if ok else 'error'}.", is_jarvis=True)
                elif action == "volume_up":
                    ok, lvl = change_volume(int(param) if param else 10)
                    self.add_message(f"▹ Volume {lvl}%." if ok and lvl is not None else "▹ Volume error.", is_jarvis=True)
                elif action == "volume_down":
                    ok, lvl = change_volume(-(int(param) if param else 10))
                    self.add_message(f"▹ Volume {lvl}%." if ok and lvl is not None else "▹ Volume error.", is_jarvis=True)
                elif action == "mute":
                    mute_system(True)
                    self.add_message("▹ Muted.", is_jarvis=True)
                elif action == "unmute":
                    mute_system(False)
                    self.add_message("▹ Unmuted.", is_jarvis=True)
            else:
                self.add_message(f"▹ Command: {command}", is_jarvis=True)
        except Exception as exc:
            log.error("process_command error: %s", exc)
            self.add_message(f"✗ Error: {str(exc)[:60]}", is_jarvis=True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    app = QApplication(sys.argv)
    gui = CyberpunkJARVISGui()
    gui.show()
    gui.add_message("[ ▧ NEURAL INTERFACE ONLINE ▧ ]", is_jarvis=True)
    gui.add_message("[ ALL SYSTEMS NOMINAL ]", is_jarvis=True)
    if not _CORE_AVAILABLE:
        gui.add_message("[ ⚠ JARVIS core unavailable – running in stub mode ]", is_jarvis=True)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
