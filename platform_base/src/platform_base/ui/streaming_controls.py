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


class StreamingControlWidget(QWidget):
    """
    Widget de controle para streaming temporal conforme seção 11.4

    Features:
    - Play/pause/stop controls
    - Time slider com preview
    - Speed control
    - Window size control
    - Filtros de qualidade
    """

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

        self._setup_ui()
        self._setup_connections()

        logger.debug("streaming_control_widget_initialized")

    def _setup_ui(self):
        """Configura interface do widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Playback Controls
        self._create_playback_controls(layout)

        # Time Controls
        self._create_time_controls(layout)

        # Settings
        self._create_settings_controls(layout)

        # Status
        self._create_status_display(layout)

    def _create_playback_controls(self, parent_layout):
        """Cria controles de playback"""
        group = QGroupBox("Playback")
        layout = QHBoxLayout(group)

        # Play/Pause button
        self.play_pause_btn = QPushButton("Play")
        self.play_pause_btn.setMinimumSize(80, 32)
        self.play_pause_btn.clicked.connect(self._toggle_playback)
        layout.addWidget(self.play_pause_btn)

        # Stop button
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setMinimumSize(80, 32)
        self.stop_btn.clicked.connect(self._stop_playback)
        layout.addWidget(self.stop_btn)

        layout.addStretch()

        # Loop checkbox
        self.loop_checkbox = QCheckBox("Loop")
        layout.addWidget(self.loop_checkbox)

        parent_layout.addWidget(group)

    def _create_time_controls(self, parent_layout):
        """Cria controles de tempo"""
        group = QGroupBox("Time Navigation")
        layout = QVBoxLayout(group)

        # Time slider
        slider_layout = QHBoxLayout()

        self.time_label_start = QLabel("00:00")
        self.time_label_start.setMinimumWidth(40)
        slider_layout.addWidget(self.time_label_start)

        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(100)
        self.time_slider.valueChanged.connect(self._on_slider_changed)
        slider_layout.addWidget(self.time_slider)

        self.time_label_end = QLabel("00:00")
        self.time_label_end.setMinimumWidth(40)
        slider_layout.addWidget(self.time_label_end)

        layout.addLayout(slider_layout)

        # Current time display
        time_info_layout = QHBoxLayout()

        self.current_time_label = QLabel("Current: 00:00")
        self.current_time_label.setFont(QFont("", 10, QFont.Weight.Bold))
        time_info_layout.addWidget(self.current_time_label)

        time_info_layout.addStretch()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumWidth(100)
        time_info_layout.addWidget(self.progress_bar)

        layout.addLayout(time_info_layout)

        parent_layout.addWidget(group)

    def _create_settings_controls(self, parent_layout):
        """Cria controles de configuração"""
        group = QGroupBox("Settings")
        layout = QFormLayout(group)

        # Speed control
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setRange(0.1, 10.0)
        self.speed_spinbox.setValue(1.0)
        self.speed_spinbox.setSingleStep(0.1)
        self.speed_spinbox.setSuffix("x")
        self.speed_spinbox.valueChanged.connect(self._on_speed_changed)
        layout.addRow("Speed:", self.speed_spinbox)

        # Window size
        self.window_size_spinbox = QSpinBox()
        self.window_size_spinbox.setRange(1, 3600)
        self.window_size_spinbox.setValue(60)
        self.window_size_spinbox.setSuffix(" sec")
        self.window_size_spinbox.valueChanged.connect(self._on_window_size_changed)
        layout.addRow("Window Size:", self.window_size_spinbox)

        # Update interval
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(10, 1000)
        self.interval_spinbox.setValue(100)
        self.interval_spinbox.setSuffix(" ms")
        self.interval_spinbox.valueChanged.connect(self._on_interval_changed)
        layout.addRow("Update Interval:", self.interval_spinbox)

        # Quality filters
        self.hide_nan_checkbox = QCheckBox("Hide NaN values")
        self.hide_nan_checkbox.setChecked(True)
        self.hide_nan_checkbox.stateChanged.connect(self._on_filters_changed)
        layout.addRow("Filters:", self.hide_nan_checkbox)

        self.hide_interpolated_checkbox = QCheckBox("Hide interpolated")
        self.hide_interpolated_checkbox.stateChanged.connect(self._on_filters_changed)
        layout.addRow("", self.hide_interpolated_checkbox)

        parent_layout.addWidget(group)

    def _create_status_display(self, parent_layout):
        """Cria display de status"""
        group = QGroupBox("Status")
        layout = QFormLayout(group)

        self.total_points_label = QLabel("0")
        layout.addRow("Total Points:", self.total_points_label)

        self.eligible_points_label = QLabel("0")
        layout.addRow("Eligible Points:", self.eligible_points_label)

        self.window_points_label = QLabel("0")
        layout.addRow("Window Points:", self.window_points_label)

        self.fps_label = QLabel("0.0")
        layout.addRow("Update Rate:", self.fps_label)

        parent_layout.addWidget(group)

    def _setup_connections(self):
        """Configura conexões de sinais"""
        # Connect loop checkbox
        self.loop_checkbox.stateChanged.connect(self._on_loop_changed)

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
