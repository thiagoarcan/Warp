"""
Streaming Controls - Widget PyQt6 para controle de streaming temporal

Features:
- Controles de play/pause/stop
- Slider de tempo
- Controle de velocidade
- Configuração de filtros
- Sincronização multi-view
"""

from __future__ import annotations

import time
from datetime import timedelta
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from platform_base.desktop.widgets.base import UiLoaderMixin
from platform_base.utils.logging import get_logger
from platform_base.viz.streaming import (
    StreamFilters,
    StreamingEngine,
    StreamingState,
    TickUpdate,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from platform_base.core.models import Dataset


logger = get_logger(__name__)


class StreamingControlWidget(QWidget, UiLoaderMixin):
    """
    Widget de controle para streaming temporal conforme seção 11.4

    Features:
    - Play/pause/stop controls
    - Time slider com preview
    - Speed control
    - Window size control
    - Filtros de qualidade
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "streamingControlWidget.ui"

    # Signals
    tick_update = pyqtSignal(object)  # TickUpdate
    playback_started = pyqtSignal()
    playback_paused = pyqtSignal()
    playback_stopped = pyqtSignal()
    time_seeked = pyqtSignal(float)  # time_seconds

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.streaming_engine: StreamingEngine | None = None
        self.current_dataset: Dataset | None = None

        # Timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._on_timer_tick)
        self.update_timer.setSingleShot(False)

        # Carrega interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()
        
        self._setup_connections()
        logger.debug("streaming_control_widget_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Playback controls
        self.play_pause_btn = self.findChild(QPushButton, "playPauseBtn")
        self.stop_btn = self.findChild(QPushButton, "stopBtn")
        self.loop_checkbox = self.findChild(QCheckBox, "loopCheckbox")
        
        # Time controls
        self.time_label_start = self.findChild(QLabel, "timeLabelStart")
        self.time_slider = self.findChild(QSlider, "timeSlider")
        self.time_label_end = self.findChild(QLabel, "timeLabelEnd")
        self.current_time_label = self.findChild(QLabel, "currentTimeLabel")
        self.progress_bar = self.findChild(QProgressBar, "progressBar")
        
        # Settings controls
        self.speed_spinbox = self.findChild(QDoubleSpinBox, "speedSpinbox")
        self.window_size_spinbox = self.findChild(QSpinBox, "windowSizeSpinbox")
        self.interval_spinbox = self.findChild(QSpinBox, "intervalSpinbox")
        self.hide_nan_checkbox = self.findChild(QCheckBox, "hideNanCheckbox")
        self.hide_interpolated_checkbox = self.findChild(QCheckBox, "hideInterpolatedCheckbox")
        
        # Status labels
        self.total_points_label = self.findChild(QLabel, "totalPointsLabel")
        self.eligible_points_label = self.findChild(QLabel, "eligiblePointsLabel")
        self.window_points_label = self.findChild(QLabel, "windowPointsLabel")
        self.fps_label = self.findChild(QLabel, "fpsLabel")
        
        # Validação de widgets essenciais
        self._validate_widgets()

    def _validate_widgets(self):
        """Valida que todos os widgets essenciais foram encontrados no .ui"""
        required_widgets = {
            "playPauseBtn": self.play_pause_btn,
            "stopBtn": self.stop_btn,
            "loopCheckbox": self.loop_checkbox,
            "timeSlider": self.time_slider,
            "timeLabelStart": self.time_label_start,
            "timeLabelEnd": self.time_label_end,
            "currentTimeLabel": self.current_time_label,
            "progressBar": self.progress_bar,
            "speedSpinbox": self.speed_spinbox,
            "windowSizeSpinbox": self.window_size_spinbox,
            "intervalSpinbox": self.interval_spinbox,
            "hideNanCheckbox": self.hide_nan_checkbox,
            "totalPointsLabel": self.total_points_label,
            "eligiblePointsLabel": self.eligible_points_label,
            "windowPointsLabel": self.window_points_label,
            "fpsLabel": self.fps_label,
        }
        
        missing = [name for name, widget in required_widgets.items() if widget is None]
        
        if missing:
            raise RuntimeError(
                f"Widgets ausentes no arquivo .ui: {', '.join(missing)}. "
                f"Verifique se {self.UI_FILE} está completo."
            )

    def _setup_connections(self):
        """Configura conexões de sinais"""
        # Playback controls
        self.play_pause_btn.clicked.connect(self._toggle_playback)
        self.stop_btn.clicked.connect(self._stop_playback)
        self.loop_checkbox.stateChanged.connect(self._on_loop_changed)
        
        # Time controls
        self.time_slider.valueChanged.connect(self._on_slider_changed)
        
        # Settings controls
        self.speed_spinbox.valueChanged.connect(self._on_speed_changed)
        self.window_size_spinbox.valueChanged.connect(self._on_window_size_changed)
        self.interval_spinbox.valueChanged.connect(self._on_interval_changed)
        
        # Filter controls
        self.hide_nan_checkbox.stateChanged.connect(self._on_filters_changed)
        if self.hide_interpolated_checkbox:
            self.hide_interpolated_checkbox.stateChanged.connect(self._on_filters_changed)

    def set_dataset(self, dataset: Dataset):
        """Define dataset para streaming"""
        self.current_dataset = dataset

        if dataset is None:
            self._clear_controls()
            return

        # Create streaming state
        streaming_state = StreamingState()
        streaming_state.window_size = timedelta(seconds=self.window_size_spinbox.value())
        streaming_state.speed = self.speed_spinbox.value()
        streaming_state.loop = self.loop_checkbox.isChecked()

        # Update filters
        self._update_filters(streaming_state)

        # Create streaming engine
        self.streaming_engine = StreamingEngine(streaming_state, dataset.dataset_id)

        # Setup data
        series_data = {series_id: series.values for series_id, series in dataset.series.items()}
        self.streaming_engine.setup_data(
            time_points=dataset.t_seconds,
            series_data=series_data,
        )

        # Update UI
        self._update_time_controls()
        self._update_status()

        logger.info("streaming_dataset_set",
                   dataset_id=dataset.dataset_id,
                   n_series=len(dataset.series),
                   n_points=len(dataset.t_seconds))

    def _clear_controls(self):
        """Limpa controles quando não há dataset"""
        self.streaming_engine = None
        self.time_slider.setMaximum(0)
        self.time_label_start.setText("00:00")
        self.time_label_end.setText("00:00")
        self.current_time_label.setText("Current: 00:00")
        self.progress_bar.setValue(0)

        self.total_points_label.setText("0")
        self.eligible_points_label.setText("0")
        self.window_points_label.setText("0")
        self.fps_label.setText("0.0")

    def _update_time_controls(self):
        """Atualiza controles de tempo baseado no dataset"""
        if not self.streaming_engine or len(self.streaming_engine.eligible_indices) == 0:
            return

        max_index = len(self.streaming_engine.eligible_indices) - 1
        self.time_slider.setMaximum(max_index)

        # Time labels
        start_time = self.streaming_engine.time_points[self.streaming_engine.eligible_indices[0]]
        end_time = self.streaming_engine.time_points[self.streaming_engine.eligible_indices[-1]]

        self.time_label_start.setText(self._format_time(start_time))
        self.time_label_end.setText(self._format_time(end_time))

        # Progress bar
        self.progress_bar.setMaximum(max_index)

    def _update_status(self):
        """Atualiza display de status"""
        if not self.streaming_engine:
            return

        self.total_points_label.setText(str(self.streaming_engine.total_points))
        self.eligible_points_label.setText(str(len(self.streaming_engine.eligible_indices)))

        # Window points will be updated in timer

    def _update_filters(self, streaming_state: StreamingState):
        """Atualiza filtros do streaming state"""
        filters = StreamFilters()
        filters.hide_nan = self.hide_nan_checkbox.isChecked()
        filters.hide_interpolated = self.hide_interpolated_checkbox.isChecked()
        streaming_state.filters = filters

    def _format_time(self, seconds: float) -> str:
        """Formata tempo em MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    @pyqtSlot()
    def _toggle_playback(self):
        """Toggle entre play e pause"""
        if not self.streaming_engine:
            return

        if self.streaming_engine.state.play_state.is_playing:
            self._pause_playback()
        else:
            self._start_playback()

    def _start_playback(self):
        """Inicia playback"""
        if not self.streaming_engine:
            return

        self.streaming_engine.play()
        self.play_pause_btn.setText("Pause")

        # Start timer
        interval_ms = self.interval_spinbox.value()
        self.update_timer.start(interval_ms)

        self.playback_started.emit()
        logger.debug("streaming_playback_started")

    def _pause_playback(self):
        """Pausa playback"""
        if not self.streaming_engine:
            return

        self.streaming_engine.pause()
        self.play_pause_btn.setText("Play")

        # Stop timer
        self.update_timer.stop()

        self.playback_paused.emit()
        logger.debug("streaming_playback_paused")

    @pyqtSlot()
    def _stop_playback(self):
        """Para playback"""
        if not self.streaming_engine:
            return

        self.streaming_engine.stop()
        self.play_pause_btn.setText("Play")

        # Stop timer
        self.update_timer.stop()

        # Reset UI
        self.time_slider.setValue(0)
        self.progress_bar.setValue(0)

        self.playback_stopped.emit()
        logger.debug("streaming_playback_stopped")

    @pyqtSlot(int)
    def _on_slider_changed(self, value: int):
        """Slider de tempo foi movido"""
        if not self.streaming_engine or len(self.streaming_engine.eligible_indices) == 0:
            return

        # Don't update during playback unless user is dragging
        if self.streaming_engine.state.play_state.is_playing:
            return

        # Seek to new position
        self.streaming_engine.state.current_time_index = value

        # Update display
        current_time = self.streaming_engine._current_time()
        self.current_time_label.setText(f"Current: {self._format_time(current_time)}")
        self.progress_bar.setValue(value)

        # Emit seek signal
        self.time_seeked.emit(current_time)

        # Send manual update
        update = self.streaming_engine._current_update()
        self.tick_update.emit(update)

    @pyqtSlot(float)
    def _on_speed_changed(self, speed: float):
        """Velocidade foi alterada"""
        if self.streaming_engine:
            self.streaming_engine.state.speed = speed
            logger.debug("streaming_speed_changed", speed=speed)

    @pyqtSlot(int)
    def _on_window_size_changed(self, size_seconds: int):
        """Tamanho da janela foi alterado"""
        if self.streaming_engine:
            self.streaming_engine.state.window_size = timedelta(seconds=size_seconds)
            logger.debug("streaming_window_size_changed", size_seconds=size_seconds)

    @pyqtSlot(int)
    def _on_interval_changed(self, interval_ms: int):
        """Intervalo de atualização foi alterado"""
        if self.update_timer.isActive():
            self.update_timer.stop()
            self.update_timer.start(interval_ms)
        logger.debug("streaming_interval_changed", interval_ms=interval_ms)

    @pyqtSlot(int)
    def _on_loop_changed(self, state: int):
        """Loop foi ativado/desativado"""
        if self.streaming_engine:
            self.streaming_engine.state.loop = state == Qt.CheckState.Checked.value

    @pyqtSlot()
    def _on_filters_changed(self):
        """Filtros foram alterados"""
        if not self.streaming_engine:
            return

        # Update filters
        self._update_filters(self.streaming_engine.state)

        # Reapply filters
        self.streaming_engine.eligible_indices = self.streaming_engine._apply_eligibility_filters()

        # Update UI
        self._update_time_controls()
        self._update_status()

        logger.debug("streaming_filters_changed")

    @pyqtSlot()
    def _on_timer_tick(self):
        """Timer tick - avança streaming"""
        if not self.streaming_engine:
            return

        start_time = time.perf_counter()

        # Advance streaming
        update = self.streaming_engine.tick()

        # Update UI
        self.time_slider.setValue(self.streaming_engine.state.current_time_index)
        self.progress_bar.setValue(self.streaming_engine.state.current_time_index)

        current_time = self.streaming_engine._current_time()
        self.current_time_label.setText(f"Current: {self._format_time(current_time)}")

        # Update window points count
        total_window_points = sum(len(data) for data in update.window_data.values())
        self.window_points_label.setText(str(total_window_points))

        # Calculate and display FPS
        duration_ms = (time.perf_counter() - start_time) * 1000
        fps = 1000.0 / max(duration_ms, 1.0)
        self.fps_label.setText(f"{fps:.1f} Hz")

        # Emit update
        self.tick_update.emit(update)

        # Stop if reached end and not looping
        if update.reached_end and not self.streaming_engine.state.loop:
            self._pause_playback()

    def add_callback(self, callback: Callable[[TickUpdate], None]):
        """Adiciona callback para receber updates"""
        if self.streaming_engine:
            self.streaming_engine.add_sync_callback(callback)

    def get_current_update(self) -> TickUpdate | None:
        """Retorna update atual"""
        if self.streaming_engine:
            return self.streaming_engine._current_update()
        return None

# =============================================================================
# StreamingControls - Alias simplificado para StreamingControlWidget
# =============================================================================

# Available playback speeds
AVAILABLE_SPEEDS = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]

# Available window presets
WINDOW_PRESETS = {
    "1 second": 1.0,
    "5 seconds": 5.0,
    "10 seconds": 10.0,
    "30 seconds": 30.0,
    "1 minute": 60.0,
    "5 minutes": 300.0,
}


def get_available_speeds() -> list[float]:
    """Return list of available playback speeds."""
    return AVAILABLE_SPEEDS.copy()


def get_window_presets() -> dict[str, float]:
    """Return dictionary of window size presets."""
    return WINDOW_PRESETS.copy()


class StreamingControls(QWidget, UiLoaderMixin):
    """
    Simplified streaming controls widget.
    
    Provides basic play/pause/stop functionality and timeline control.
    For more advanced features, use StreamingControlWidget.
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "streamingControls.ui"

    # Signals
    playback_started = pyqtSignal()
    playback_paused = pyqtSignal()
    playback_stopped = pyqtSignal()
    position_changed = pyqtSignal(float)  # position in seconds
    speed_changed = pyqtSignal(float)     # speed multiplier
    window_size_changed = pyqtSignal(float)  # window size in seconds

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._is_playing = False
        self._current_position = 0.0
        self._total_duration = 0.0
        self._playback_speed = 1.0
        self._window_size = 10.0

        # Timer for playback
        self._timer = QTimer()
        self._timer.timeout.connect(self._on_tick)

        # Carrega interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()
        
        logger.debug("streaming_controls_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Playback buttons
        self.play_btn = self.findChild(QPushButton, "playBtn")
        self.pause_btn = self.findChild(QPushButton, "pauseBtn")
        self.stop_btn = self.findChild(QPushButton, "stopBtn")
        
        # Timeline
        self.timeline = self.findChild(QSlider, "timeline")
        self.position_label = self.findChild(QLabel, "positionLabel")
        self.duration_label = self.findChild(QLabel, "durationLabel")
        
        # Speed and window controls
        self.speed_spinbox = self.findChild(QDoubleSpinBox, "speedSpinbox")
        self.window_spinbox = self.findChild(QDoubleSpinBox, "windowSpinbox")
        
        # Conecta sinais
        if self.play_btn:
            self.play_btn.clicked.connect(self.play)
        if self.pause_btn:
            self.pause_btn.setEnabled(False)
            self.pause_btn.clicked.connect(self.pause)
        if self.stop_btn:
            self.stop_btn.clicked.connect(self.stop)
        if self.timeline:
            self.timeline.valueChanged.connect(self._on_timeline_changed)
        if self.speed_spinbox:
            self.speed_spinbox.valueChanged.connect(self.set_speed)
        if self.window_spinbox:
            self.window_spinbox.valueChanged.connect(self.set_window_size)

    def _on_tick(self):
        """Timer tick - advance playback."""
        if not self._is_playing:
            return

        # Advance position based on speed
        step = (self._timer.interval() / 1000.0) * self._playback_speed
        new_position = self._current_position + step

        if new_position >= self._total_duration:
            new_position = self._total_duration
            self.stop()

        self.seek(new_position)

    def _on_timeline_changed(self, value: int):
        """Handle timeline slider change."""
        if self._total_duration > 0:
            position = (value / 1000.0) * self._total_duration
            self._current_position = position
            self._update_position_label()
            self.position_changed.emit(position)

    def _update_position_label(self):
        """Update the position label."""
        self.position_label.setText(self._format_time(self._current_position))

    def _update_timeline(self):
        """Update timeline slider position."""
        if self._total_duration > 0:
            value = int((self._current_position / self._total_duration) * 1000)
            self.timeline.blockSignals(True)
            self.timeline.setValue(value)
            self.timeline.blockSignals(False)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds as M:SS.s"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}:{secs:04.1f}"

    def play(self):
        """Start playback."""
        if not self._is_playing:
            self._is_playing = True
            self._timer.start(33)  # ~30 fps
            self.play_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.playback_started.emit()
            logger.debug("streaming_play")

    def pause(self):
        """Pause playback."""
        if self._is_playing:
            self._is_playing = False
            self._timer.stop()
            self.play_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.playback_paused.emit()
            logger.debug("streaming_pause")

    def stop(self):
        """Stop playback and reset position."""
        self._is_playing = False
        self._timer.stop()
        self._current_position = 0.0
        self._update_position_label()
        self._update_timeline()
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.playback_stopped.emit()
        logger.debug("streaming_stop")

    def is_playing(self) -> bool:
        """Check if playback is active."""
        return self._is_playing

    def seek(self, position: float):
        """
        Seek to a specific position.
        
        Args:
            position: Position in seconds
        """
        self._current_position = max(0.0, min(position, self._total_duration))
        self._update_position_label()
        self._update_timeline()
        self.position_changed.emit(self._current_position)

    def get_position(self) -> float:
        """Get current position in seconds."""
        return self._current_position

    def set_duration(self, duration: float):
        """
        Set total duration.
        
        Args:
            duration: Duration in seconds
        """
        self._total_duration = max(0.0, duration)
        self.duration_label.setText(f"/ {self._format_time(self._total_duration)}")
        logger.debug("streaming_duration_set", duration=duration)

    def get_duration(self) -> float:
        """Get total duration in seconds."""
        return self._total_duration

    def set_speed(self, speed: float):
        """
        Set playback speed.
        
        Args:
            speed: Speed multiplier (1.0 = normal)
        """
        self._playback_speed = max(0.1, min(16.0, speed))
        self.speed_spinbox.blockSignals(True)
        self.speed_spinbox.setValue(self._playback_speed)
        self.speed_spinbox.blockSignals(False)
        self.speed_changed.emit(self._playback_speed)
        logger.debug("streaming_speed_set", speed=self._playback_speed)

    def get_speed(self) -> float:
        """Get current playback speed."""
        return self._playback_speed

    def set_window_size(self, size: float):
        """
        Set visualization window size.
        
        Args:
            size: Window size in seconds
        """
        self._window_size = max(0.1, size)
        self.window_spinbox.blockSignals(True)
        self.window_spinbox.setValue(self._window_size)
        self.window_spinbox.blockSignals(False)
        self.window_size_changed.emit(self._window_size)
        logger.debug("streaming_window_size_set", size=self._window_size)

    def get_window_size(self) -> float:
        """Get current window size in seconds."""
        return self._window_size

    def step_forward(self, step: float = 1.0):
        """
        Step forward by given amount.
        
        Args:
            step: Step size in seconds
        """
        self.seek(self._current_position + step)

    def step_backward(self, step: float = 1.0):
        """
        Step backward by given amount.
        
        Args:
            step: Step size in seconds
        """
        self.seek(self._current_position - step)

    def set_range(self, start: float, end: float):
        """
        Set playback range.
        
        Args:
            start: Start position in seconds
            end: End position in seconds
        """
        self._total_duration = end - start
        self.duration_label.setText(f"/ {self._format_time(self._total_duration)}")