"""
StreamingPanel - Painel de controle de playback para streaming de dados

Características:
- Controles de play/pause/stop
- Velocidade ajustável (0.1x a 10x)
- Navegação temporal (seek)
- Loop e modo reverso
- Minimap para navegação rápida

Autor: Platform Base Team
Versão: 2.0.0
"""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    import numpy as np

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


class TimelineSlider(QSlider):
    """Slider customizado para timeline"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._apply_style()
    
    def _apply_style(self):
        """Aplica estilo ao slider"""
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                margin: -4px 0;
                background: #0d6efd;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #0b5ed7;
            }
            QSlider::sub-page:horizontal {
                background: #0d6efd;
                border-radius: 4px;
            }
        """)


class MinimapWidget(QWidget):
    """Widget minimap para visualização geral e navegação rápida"""
    
    position_changed = pyqtSignal(float)  # Posição normalizada 0-1
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self._position = 0.0
        self._window_size = 0.1  # 10% do total
        self._data_preview = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
    
    def set_data_preview(self, data: "np.ndarray"):
        """Define preview dos dados para desenhar no minimap"""
        self._data_preview = data
        self.update()
    
    def set_position(self, position: float):
        """Define posição atual (0-1)"""
        self._position = max(0.0, min(1.0, position))
        self.update()
    
    def set_window_size(self, size: float):
        """Define tamanho da janela visível (0-1)"""
        self._window_size = max(0.01, min(1.0, size))
        self.update()
    
    def mousePressEvent(self, a0):
        """Clique para navegar"""
        if a0 is None:
            return
        if a0.button() == Qt.MouseButton.LeftButton:
            pos = a0.position().x() / self.width()
            self._position = pos
            self.position_changed.emit(pos)
            self.update()
    
    def paintEvent(self, a0):
        """Desenha o minimap"""
        from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Background
        painter.fillRect(0, 0, w, h, QColor("#f8f9fa"))
        
        # Desenha preview dos dados se disponível
        if self._data_preview is not None and len(self._data_preview) > 0:
            import numpy as np
            data = self._data_preview
            
            # Normaliza dados
            min_val = np.min(data)
            max_val = np.max(data)
            if max_val > min_val:
                normalized = (data - min_val) / (max_val - min_val)
            else:
                normalized = np.zeros_like(data)
            
            # Reduz para largura do widget
            step = max(1, len(data) // w)
            sampled = normalized[::step]
            
            # Desenha linha
            pen = QPen(QColor("#0d6efd"), 1)
            painter.setPen(pen)
            
            for i in range(len(sampled) - 1):
                x1 = int(i * w / len(sampled))
                y1 = int(h - sampled[i] * (h - 4) - 2)
                x2 = int((i + 1) * w / len(sampled))
                y2 = int(h - sampled[i + 1] * (h - 4) - 2)
                painter.drawLine(x1, y1, x2, y2)
        
        # Desenha janela de visualização atual
        window_x = int(self._position * w - self._window_size * w / 2)
        window_w = int(self._window_size * w)
        
        painter.fillRect(window_x, 0, window_w, h, QColor(13, 110, 253, 40))
        painter.setPen(QPen(QColor("#0d6efd"), 2))
        painter.drawRect(window_x, 0, window_w, h)
        
        # Marca posição atual
        pos_x = int(self._position * w)
        painter.setPen(QPen(QColor("#dc3545"), 2))
        painter.drawLine(pos_x, 0, pos_x, h)


class StreamingPanel(QWidget):
    """
    Painel de controle de streaming/playback
    
    Signals:
        position_changed: Posição atual mudou (index ou timestamp)
        state_changed: Estado de playback mudou
        speed_changed: Velocidade mudou
    """
    
    position_changed = pyqtSignal(int)  # Índice atual
    state_changed = pyqtSignal(PlaybackState)
    speed_changed = pyqtSignal(float)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
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
        
        self._setup_ui()
        self._connect_signals()
        self._update_ui_state()
    
    def _setup_ui(self):
        """Configura interface principal"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("🎬 Controle de Streaming")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #212529;
        """)
        layout.addWidget(header)
        
        # Minimap
        minimap_group = QGroupBox("📊 Navegação")
        minimap_layout = QVBoxLayout(minimap_group)
        self._minimap = MinimapWidget()
        self._minimap.position_changed.connect(self._on_minimap_position)
        minimap_layout.addWidget(self._minimap)
        layout.addWidget(minimap_group)
        
        # Timeline slider
        timeline_group = QGroupBox("⏱️ Timeline")
        timeline_layout = QVBoxLayout(timeline_group)
        
        self._timeline = TimelineSlider()
        self._timeline.setMinimum(0)
        self._timeline.setMaximum(100)
        self._timeline.valueChanged.connect(self._on_timeline_changed)
        timeline_layout.addWidget(self._timeline)
        
        # Labels de tempo
        time_layout = QHBoxLayout()
        self._current_time = QLabel("00:00:00")
        self._current_time.setStyleSheet("font-family: monospace; font-size: 12px;")
        time_layout.addWidget(self._current_time)
        
        time_layout.addStretch()
        
        self._frame_info = QLabel("Frame: 0 / 0")
        self._frame_info.setStyleSheet("color: #6c757d; font-size: 11px;")
        time_layout.addWidget(self._frame_info)
        
        time_layout.addStretch()
        
        self._total_time = QLabel("00:00:00")
        self._total_time.setStyleSheet("font-family: monospace; font-size: 12px;")
        time_layout.addWidget(self._total_time)
        
        timeline_layout.addLayout(time_layout)
        layout.addWidget(timeline_group)
        
        # Controles de playback
        controls_group = QGroupBox("🎮 Controles")
        controls_layout = QVBoxLayout(controls_group)
        
        # Botões principais
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        # Botões de navegação
        self._btn_start = self._create_control_button("⏮", "Ir para início")
        self._btn_start.clicked.connect(self._go_to_start)
        buttons_layout.addWidget(self._btn_start)
        
        self._btn_prev = self._create_control_button("⏪", "Frame anterior")
        self._btn_prev.clicked.connect(self._step_backward)
        buttons_layout.addWidget(self._btn_prev)
        
        # Play/Pause (maior)
        self._btn_play = self._create_control_button("▶", "Play/Pause", large=True)
        self._btn_play.clicked.connect(self._toggle_play)
        buttons_layout.addWidget(self._btn_play)
        
        # Stop
        self._btn_stop = self._create_control_button("⏹", "Stop")
        self._btn_stop.clicked.connect(self._stop)
        buttons_layout.addWidget(self._btn_stop)
        
        self._btn_next = self._create_control_button("⏩", "Próximo frame")
        self._btn_next.clicked.connect(self._step_forward)
        buttons_layout.addWidget(self._btn_next)
        
        self._btn_end = self._create_control_button("⏭", "Ir para fim")
        self._btn_end.clicked.connect(self._go_to_end)
        buttons_layout.addWidget(self._btn_end)
        
        controls_layout.addLayout(buttons_layout)
        
        # Linha de configurações
        config_layout = QHBoxLayout()
        config_layout.setSpacing(16)
        
        # Velocidade
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Velocidade:"))
        
        self._speed_combo = QComboBox()
        self._speed_combo.addItems(["0.1x", "0.25x", "0.5x", "1x", "2x", "5x", "10x"])
        self._speed_combo.setCurrentText("1x")
        self._speed_combo.currentTextChanged.connect(self._on_speed_changed)
        speed_layout.addWidget(self._speed_combo)
        
        config_layout.addLayout(speed_layout)
        
        # Modo
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Modo:"))
        
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("Normal", PlaybackMode.NORMAL)
        self._mode_combo.addItem("Loop ♻️", PlaybackMode.LOOP)
        self._mode_combo.addItem("Ping-Pong ↔️", PlaybackMode.PING_PONG)
        self._mode_combo.addItem("Reverso ⏪", PlaybackMode.REVERSE)
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self._mode_combo)
        
        config_layout.addLayout(mode_layout)
        
        # Step size
        step_layout = QHBoxLayout()
        step_layout.addWidget(QLabel("Step:"))
        
        self._step_spin = QSpinBox()
        self._step_spin.setMinimum(1)
        self._step_spin.setMaximum(1000)
        self._step_spin.setValue(1)
        self._step_spin.setToolTip("Frames por step")
        step_layout.addWidget(self._step_spin)
        
        config_layout.addLayout(step_layout)
        
        config_layout.addStretch()
        
        controls_layout.addLayout(config_layout)
        layout.addWidget(controls_group)
        
        # Status
        self._status_label = QLabel("⏹ Parado")
        self._status_label.setStyleSheet("""
            padding: 8px;
            background-color: #f8f9fa;
            border-radius: 4px;
            color: #6c757d;
        """)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)
        
        layout.addStretch()
    
    def _create_control_button(
        self,
        text: str,
        tooltip: str,
        large: bool = False
    ) -> QPushButton:
        """Cria botão de controle estilizado"""
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        
        size = 48 if large else 36
        btn.setFixedSize(size, size)
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: {size // 2}px;
                font-size: {16 if large else 14}px;
            }}
            QPushButton:hover {{
                background-color: #e9ecef;
                border-color: #adb5bd;
            }}
            QPushButton:pressed {{
                background-color: #dee2e6;
            }}
        """)
        
        return btn
    
    def _connect_signals(self):
        """Conecta signals internos"""
        pass
    
    def _update_ui_state(self):
        """Atualiza estado visual da UI"""
        # Atualiza botão play
        if self._state == PlaybackState.PLAYING:
            self._btn_play.setText("⏸")
            self._status_label.setText(f"▶ Reproduzindo ({self._speed}x)")
            self._status_label.setStyleSheet("""
                padding: 8px;
                background-color: #d1e7dd;
                border-radius: 4px;
                color: #0f5132;
            """)
        elif self._state == PlaybackState.PAUSED:
            self._btn_play.setText("▶")
            self._status_label.setText("⏸ Pausado")
            self._status_label.setStyleSheet("""
                padding: 8px;
                background-color: #fff3cd;
                border-radius: 4px;
                color: #664d03;
            """)
        else:
            self._btn_play.setText("▶")
            self._status_label.setText("⏹ Parado")
            self._status_label.setStyleSheet("""
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                color: #6c757d;
            """)
        
        # Atualiza labels de tempo
        self._frame_info.setText(f"Frame: {self._position:,} / {self._total_frames:,}")
        
        # Atualiza timeline
        if self._total_frames > 0:
            self._timeline.blockSignals(True)
            self._timeline.setValue(int(self._position * 100 / self._total_frames))
            self._timeline.blockSignals(False)
        
        # Atualiza minimap
        if self._total_frames > 0:
            self._minimap.set_position(self._position / self._total_frames)
    
    def set_total_frames(self, total: int):
        """Define número total de frames"""
        self._total_frames = max(0, total)
        self._position = 0
        self._update_ui_state()
        logger.info(f"streaming_total_set: total={total}")
    
    def set_data_preview(self, data: "np.ndarray"):
        """Define preview dos dados para o minimap"""
        self._minimap.set_data_preview(data)
    
    def set_position(self, position: int):
        """Define posição atual"""
        self._position = max(0, min(self._total_frames - 1, position))
        self._update_ui_state()
        self.position_changed.emit(self._position)
    
    def get_position(self) -> int:
        """Retorna posição atual"""
        return self._position
    
    def get_state(self) -> PlaybackState:
        """Retorna estado atual"""
        return self._state
    
    def _toggle_play(self):
        """Alterna play/pause"""
        if self._state == PlaybackState.PLAYING:
            self._pause()
        else:
            self._play()
    
    def _play(self):
        """Inicia playback"""
        if self._total_frames <= 0:
            return
        
        self._state = PlaybackState.PLAYING
        
        # Calcula intervalo baseado na velocidade
        base_interval = 33  # ~30 fps
        interval = int(base_interval / self._speed)
        interval = max(1, interval)
        
        self._timer.start(interval)
        self._update_ui_state()
        self.state_changed.emit(self._state)
        logger.info(f"streaming_play: speed={self._speed}, interval={interval}ms")
    
    def _pause(self):
        """Pausa playback"""
        self._state = PlaybackState.PAUSED
        self._timer.stop()
        self._update_ui_state()
        self.state_changed.emit(self._state)
        logger.info("streaming_pause")
    
    def _stop(self):
        """Para playback e volta ao início"""
        self._state = PlaybackState.STOPPED
        self._timer.stop()
        self._position = 0
        self._direction = 1
        self._update_ui_state()
        self.state_changed.emit(self._state)
        self.position_changed.emit(0)
        logger.info("streaming_stop")
    
    def _step_forward(self):
        """Avança um step"""
        step = self._step_spin.value()
        self.set_position(self._position + step)
    
    def _step_backward(self):
        """Volta um step"""
        step = self._step_spin.value()
        self.set_position(self._position - step)
    
    def _go_to_start(self):
        """Vai para o início"""
        self.set_position(0)
    
    def _go_to_end(self):
        """Vai para o fim"""
        self.set_position(self._total_frames - 1)
    
    def _on_timer_tick(self):
        """Callback do timer de playback"""
        step = self._step_spin.value() * self._direction
        new_pos = self._position + step
        
        # Verifica limites baseado no modo
        if self._mode == PlaybackMode.NORMAL:
            if new_pos >= self._total_frames:
                self._stop()
                return
        
        elif self._mode == PlaybackMode.LOOP:
            if new_pos >= self._total_frames:
                new_pos = 0
            elif new_pos < 0:
                new_pos = self._total_frames - 1
        
        elif self._mode == PlaybackMode.PING_PONG:
            if new_pos >= self._total_frames:
                self._direction = -1
                new_pos = self._total_frames - 2
            elif new_pos < 0:
                self._direction = 1
                new_pos = 1
        
        elif self._mode == PlaybackMode.REVERSE:
            if new_pos < 0:
                self._stop()
                return
        
        self._position = max(0, min(self._total_frames - 1, new_pos))
        self._update_ui_state()
        self.position_changed.emit(self._position)
    
    def _on_timeline_changed(self, value: int):
        """Callback quando timeline é movida"""
        if self._total_frames > 0:
            new_pos = int(value * self._total_frames / 100)
            self.set_position(new_pos)
    
    def _on_minimap_position(self, pos: float):
        """Callback quando posição do minimap muda"""
        if self._total_frames > 0:
            new_pos = int(pos * self._total_frames)
            self.set_position(new_pos)
    
    def _on_speed_changed(self, text: str):
        """Callback quando velocidade muda"""
        speed_map = {
            "0.1x": 0.1,
            "0.25x": 0.25,
            "0.5x": 0.5,
            "1x": 1.0,
            "2x": 2.0,
            "5x": 5.0,
            "10x": 10.0,
        }
        self._speed = speed_map.get(text, 1.0)
        
        # Reinicia timer se estiver rodando
        if self._state == PlaybackState.PLAYING:
            self._timer.stop()
            base_interval = 33
            interval = max(1, int(base_interval / self._speed))
            self._timer.start(interval)
        
        self.speed_changed.emit(self._speed)
        self._update_ui_state()
        logger.info(f"streaming_speed_changed: speed={self._speed}")
    
    def _on_mode_changed(self, index: int):
        """Callback quando modo muda"""
        self._mode = self._mode_combo.itemData(index)
        
        # Ajusta direção para modo reverso
        if self._mode == PlaybackMode.REVERSE:
            self._direction = -1
        else:
            self._direction = 1
        
        logger.info(f"streaming_mode_changed: mode={self._mode.name}")


# Exports
__all__ = [
    "StreamingPanel",
    "PlaybackState",
    "PlaybackMode",
    "TimelineSlider",
    "MinimapWidget",
]
