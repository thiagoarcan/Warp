"""
StreamingPanel - Painel de controle de streaming (versão UI)

Interface carregada de: desktop/ui_files/streamingPanel.ui

Características:
- Controles de play/pause/stop
- Velocidade ajustável (0.1x a 10x)
- Navegação temporal (seek)
- Loop e modo reverso
- Timeline com minimap

Este módulo usa UiLoaderMixin para carregar a interface do arquivo .ui.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub


logger = get_logger(__name__)


class PlaybackState(Enum):
    """Estados de playback"""
    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()


class PlaybackMode(Enum):
    """Modos de playback"""
    NORMAL = auto()      # Play uma vez
    LOOP = auto()        # Loop infinito
    PING_PONG = auto()   # Vai e volta
    REVERSE = auto()     # Reverso


class StreamingPanel(QWidget, UiLoaderMixin):
    """
    Painel de controle de streaming/playback.

    Interface carregada do arquivo .ui via UiLoaderMixin.

    Signals:
        position_changed: Posição atual mudou (index ou timestamp)
        state_changed: Estado de playback mudou
        speed_changed: Velocidade mudou
    """

    # Arquivo .ui que define a interface
    UI_FILE = "streamingPanel.ui"

    # Signals
    position_changed = pyqtSignal(int)  # Índice atual
    state_changed = pyqtSignal(PlaybackState)
    speed_changed = pyqtSignal(float)

    def __init__(
        self,
        session_state: "SessionState | None" = None,
        signal_hub: "SignalHub | None" = None,
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        self.session_state = session_state
        self.signal_hub = signal_hub

        # Estado
        self._state = PlaybackState.STOPPED
        self._mode = PlaybackMode.NORMAL
        self._speed = 1.0
        self._position = 0
        self._total_frames = 0
        self._direction = 1  # 1 = forward, -1 = reverse

        # Timer para playback
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_tick)

        # Tentar carregar UI do arquivo .ui
        if not self._load_ui():
            logger.warning("streaming_panel_ui_load_failed_using_fallback")
            self._setup_ui_fallback()
        else:
            self._setup_ui_from_file()

        self._connect_signals()
        self._update_ui_state()
        logger.debug("streaming_panel_initialized")

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Buscar widgets do .ui
        self._timeline_slider = self.findChild(QSlider, "timelineSlider")
        self._current_time_label = self.findChild(QLabel, "currentTimeLabel")
        self._total_time_label = self.findChild(QLabel, "totalTimeLabel")
        self._frame_info_label = self.findChild(QLabel, "frameInfoLabel")
        
        # Botões de controle
        self._btn_start = self.findChild(QPushButton, "btnStart")
        self._btn_prev = self.findChild(QPushButton, "btnPrev")
        self._btn_play = self.findChild(QPushButton, "btnPlay")
        self._btn_stop = self.findChild(QPushButton, "btnStop")
        self._btn_next = self.findChild(QPushButton, "btnNext")
        self._btn_end = self.findChild(QPushButton, "btnEnd")
        
        # Combos de configuração
        self._speed_combo = self.findChild(QComboBox, "speedCombo")
        self._mode_combo = self.findChild(QComboBox, "modeCombo")
        self._step_spin = self.findChild(QSpinBox, "stepSpin")
        
        # Configurar timeline
        if self._timeline_slider:
            self._timeline_slider.setMinimum(0)
            self._timeline_slider.setMaximum(100)
        
        # Configurar speed combo
        if self._speed_combo and self._speed_combo.count() == 0:
            self._speed_combo.addItems(["0.1x", "0.25x", "0.5x", "1x", "2x", "5x", "10x"])
            self._speed_combo.setCurrentText("1x")
        
        # Configurar mode combo
        if self._mode_combo and self._mode_combo.count() == 0:
            self._mode_combo.addItem("Normal", PlaybackMode.NORMAL)
            self._mode_combo.addItem("Loop ♻️", PlaybackMode.LOOP)
            self._mode_combo.addItem("Ping-Pong ↔️", PlaybackMode.PING_PONG)
            self._mode_combo.addItem("Reverso ⏪", PlaybackMode.REVERSE)
        
        logger.debug("streaming_panel_ui_loaded_from_file")

    def _connect_signals(self):
        """Conecta signals dos widgets"""
        # Timeline
        if self._timeline_slider:
            self._timeline_slider.valueChanged.connect(self._on_timeline_changed)
        
        # Botões de navegação
        if self._btn_start:
            self._btn_start.clicked.connect(self._go_to_start)
        if self._btn_prev:
            self._btn_prev.clicked.connect(self._step_backward)
        if self._btn_play:
            self._btn_play.clicked.connect(self._toggle_play)
        if self._btn_stop:
            self._btn_stop.clicked.connect(self._stop)
        if self._btn_next:
            self._btn_next.clicked.connect(self._step_forward)
        if self._btn_end:
            self._btn_end.clicked.connect(self._go_to_end)
        
        # Configurações
        if self._speed_combo:
            self._speed_combo.currentTextChanged.connect(self._on_speed_changed)
        if self._mode_combo:
            self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)

    def _setup_ui_fallback(self):
        """Fallback: Setup UI programaticamente se arquivo .ui não carregar"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header = QLabel("🎬 Controle de Streaming")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #212529;")
        layout.addWidget(header)

        # Timeline
        timeline_group = QGroupBox("⏱️ Timeline")
        timeline_layout = QVBoxLayout(timeline_group)

        self._timeline_slider = QSlider(Qt.Orientation.Horizontal)
        self._timeline_slider.setMinimum(0)
        self._timeline_slider.setMaximum(100)
        timeline_layout.addWidget(self._timeline_slider)

        # Labels de tempo
        time_layout = QHBoxLayout()
        self._current_time_label = QLabel("00:00:00")
        self._current_time_label.setStyleSheet("font-family: monospace;")
        time_layout.addWidget(self._current_time_label)

        time_layout.addStretch()

        self._frame_info_label = QLabel("Frame: 0 / 0")
        self._frame_info_label.setStyleSheet("color: #6c757d;")
        time_layout.addWidget(self._frame_info_label)

        time_layout.addStretch()

        self._total_time_label = QLabel("00:00:00")
        self._total_time_label.setStyleSheet("font-family: monospace;")
        time_layout.addWidget(self._total_time_label)

        timeline_layout.addLayout(time_layout)
        layout.addWidget(timeline_group)

        # Controles
        controls_group = QGroupBox("🎮 Controles")
        controls_layout = QVBoxLayout(controls_group)

        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(4)

        self._btn_start = QPushButton("⏮")
        self._btn_start.setToolTip("Ir para início")
        self._btn_start.setFixedSize(36, 36)
        buttons_layout.addWidget(self._btn_start)

        self._btn_prev = QPushButton("⏪")
        self._btn_prev.setToolTip("Frame anterior")
        self._btn_prev.setFixedSize(36, 36)
        buttons_layout.addWidget(self._btn_prev)

        self._btn_play = QPushButton("▶")
        self._btn_play.setToolTip("Play/Pause")
        self._btn_play.setFixedSize(48, 48)
        buttons_layout.addWidget(self._btn_play)

        self._btn_stop = QPushButton("⏹")
        self._btn_stop.setToolTip("Stop")
        self._btn_stop.setFixedSize(36, 36)
        buttons_layout.addWidget(self._btn_stop)

        self._btn_next = QPushButton("⏩")
        self._btn_next.setToolTip("Próximo frame")
        self._btn_next.setFixedSize(36, 36)
        buttons_layout.addWidget(self._btn_next)

        self._btn_end = QPushButton("⏭")
        self._btn_end.setToolTip("Ir para fim")
        self._btn_end.setFixedSize(36, 36)
        buttons_layout.addWidget(self._btn_end)

        controls_layout.addLayout(buttons_layout)

        # Configurações
        config_layout = QHBoxLayout()

        config_layout.addWidget(QLabel("Velocidade:"))
        self._speed_combo = QComboBox()
        self._speed_combo.addItems(["0.1x", "0.25x", "0.5x", "1x", "2x", "5x", "10x"])
        self._speed_combo.setCurrentText("1x")
        config_layout.addWidget(self._speed_combo)

        config_layout.addWidget(QLabel("Modo:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("Normal", PlaybackMode.NORMAL)
        self._mode_combo.addItem("Loop ♻️", PlaybackMode.LOOP)
        self._mode_combo.addItem("Ping-Pong ↔️", PlaybackMode.PING_PONG)
        self._mode_combo.addItem("Reverso ⏪", PlaybackMode.REVERSE)
        config_layout.addWidget(self._mode_combo)

        config_layout.addWidget(QLabel("Step:"))
        self._step_spin = QSpinBox()
        self._step_spin.setRange(1, 100)
        self._step_spin.setValue(1)
        config_layout.addWidget(self._step_spin)

        controls_layout.addLayout(config_layout)
        layout.addWidget(controls_group)

        layout.addStretch()
        logger.debug("streaming_panel_ui_fallback_created")

    # ========================
    # Controles de playback
    # ========================

    @pyqtSlot()
    def _toggle_play(self):
        """Alterna entre play e pause"""
        if self._state == PlaybackState.PLAYING:
            self._pause()
        else:
            self._play()

    def _play(self):
        """Inicia playback"""
        if self._total_frames == 0:
            return

        self._state = PlaybackState.PLAYING
        interval = int(1000 / (30 * self._speed))  # 30 FPS base
        self._timer.start(max(1, interval))
        self._update_ui_state()
        self.state_changed.emit(self._state)

    def _pause(self):
        """Pausa playback"""
        self._state = PlaybackState.PAUSED
        self._timer.stop()
        self._update_ui_state()
        self.state_changed.emit(self._state)

    @pyqtSlot()
    def _stop(self):
        """Para playback e volta ao início"""
        self._state = PlaybackState.STOPPED
        self._timer.stop()
        self._position = 0
        self._direction = 1
        self._update_position_display()
        self._update_ui_state()
        self.state_changed.emit(self._state)
        self.position_changed.emit(self._position)

    @pyqtSlot()
    def _go_to_start(self):
        """Vai para o início"""
        self._position = 0
        self._update_position_display()
        self.position_changed.emit(self._position)

    @pyqtSlot()
    def _go_to_end(self):
        """Vai para o fim"""
        self._position = max(0, self._total_frames - 1)
        self._update_position_display()
        self.position_changed.emit(self._position)

    @pyqtSlot()
    def _step_forward(self):
        """Avança um step"""
        step = self._step_spin.value() if self._step_spin else 1
        self._position = min(self._total_frames - 1, self._position + step)
        self._update_position_display()
        self.position_changed.emit(self._position)

    @pyqtSlot()
    def _step_backward(self):
        """Retrocede um step"""
        step = self._step_spin.value() if self._step_spin else 1
        self._position = max(0, self._position - step)
        self._update_position_display()
        self.position_changed.emit(self._position)

    @pyqtSlot()
    def _on_timer_tick(self):
        """Callback do timer - avança frame"""
        step = self._step_spin.value() if self._step_spin else 1
        new_pos = self._position + (step * self._direction)

        # Verificar limites baseado no modo
        if self._mode == PlaybackMode.NORMAL:
            if new_pos >= self._total_frames:
                self._stop()
                return
        elif self._mode == PlaybackMode.LOOP:
            new_pos = new_pos % self._total_frames
        elif self._mode == PlaybackMode.PING_PONG:
            if new_pos >= self._total_frames or new_pos < 0:
                self._direction *= -1
                new_pos = self._position + (step * self._direction)
        elif self._mode == PlaybackMode.REVERSE:
            if new_pos < 0:
                self._stop()
                return

        self._position = max(0, min(self._total_frames - 1, new_pos))
        self._update_position_display()
        self.position_changed.emit(self._position)

    @pyqtSlot(int)
    def _on_timeline_changed(self, value: int):
        """Callback quando timeline muda"""
        if self._total_frames > 0:
            self._position = int(value * self._total_frames / 100)
            self._update_position_display()
            self.position_changed.emit(self._position)

    @pyqtSlot(str)
    def _on_speed_changed(self, text: str):
        """Callback quando velocidade muda"""
        try:
            self._speed = float(text.replace("x", ""))
            if self._state == PlaybackState.PLAYING:
                interval = int(1000 / (30 * self._speed))
                self._timer.setInterval(max(1, interval))
            self.speed_changed.emit(self._speed)
        except ValueError:
            pass

    @pyqtSlot(int)
    def _on_mode_changed(self, index: int):
        """Callback quando modo muda"""
        if self._mode_combo:
            self._mode = self._mode_combo.itemData(index)
            if self._mode == PlaybackMode.REVERSE:
                self._direction = -1
            else:
                self._direction = 1

    # ========================
    # UI Updates
    # ========================

    def _update_ui_state(self):
        """Atualiza estado visual dos controles"""
        is_playing = self._state == PlaybackState.PLAYING

        if self._btn_play:
            self._btn_play.setText("⏸" if is_playing else "▶")
            self._btn_play.setToolTip("Pause" if is_playing else "Play")

    def _update_position_display(self):
        """Atualiza displays de posição"""
        if self._timeline_slider and self._total_frames > 0:
            progress = int(self._position * 100 / self._total_frames)
            self._timeline_slider.blockSignals(True)
            self._timeline_slider.setValue(progress)
            self._timeline_slider.blockSignals(False)

        # Atualizar labels de tempo
        current_time = self._format_time(self._position)
        total_time = self._format_time(self._total_frames)

        if self._current_time_label:
            self._current_time_label.setText(current_time)
        if self._total_time_label:
            self._total_time_label.setText(total_time)
        if self._frame_info_label:
            self._frame_info_label.setText(f"Frame: {self._position} / {self._total_frames}")

    def _format_time(self, frames: int, fps: float = 30.0) -> str:
        """Formata frames como tempo HH:MM:SS"""
        seconds = int(frames / fps)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    # ========================
    # API pública
    # ========================

    def set_total_frames(self, total: int):
        """Define o total de frames"""
        self._total_frames = total
        self._update_position_display()

    def set_position(self, position: int):
        """Define posição atual"""
        self._position = max(0, min(self._total_frames - 1, position))
        self._update_position_display()

    def get_position(self) -> int:
        """Retorna posição atual"""
        return self._position

    def get_state(self) -> PlaybackState:
        """Retorna estado atual"""
        return self._state

    def get_speed(self) -> float:
        """Retorna velocidade atual"""
        return self._speed
