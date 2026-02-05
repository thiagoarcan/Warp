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
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
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

from platform_base.desktop.widgets.base import UiLoaderMixin
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

    def __init__(self, parent: QWidget | None = None):
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

    def __init__(self, parent: QWidget | None = None):
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

    def set_data_preview(self, data: np.ndarray):
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
        from PyQt6.QtGui import QColor, QPainter, QPen

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


class StreamingPanel(QWidget, UiLoaderMixin):
    """
    Painel de controle de streaming/playback

    Signals:
        position_changed: Posição atual mudou (index ou timestamp)
        state_changed: Estado de playback mudou
        speed_changed: Velocidade mudou
    
    Interface carregada do arquivo streamingPanel.ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface (Fase 0: Migração UI - sem fallback)
    UI_FILE = "streamingPanel.ui"

    position_changed = pyqtSignal(int)  # Índice atual
    state_changed = pyqtSignal(PlaybackState)
    speed_changed = pyqtSignal(float)

    def __init__(self, parent: QWidget | None = None):
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

        # Carregar interface do arquivo .ui (obrigatório, sem fallback)
        if not self._load_ui():
            raise RuntimeError(
                f"Falha ao carregar arquivo UI: {self.UI_FILE}. "
                "Verifique se o arquivo existe em desktop/ui_files/"
            )
        
        self._setup_ui_from_file()
        self._connect_signals()
        self._update_ui_state()
        logger.debug("streaming_panel_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """
        Configura widgets carregados do arquivo streamingPanel.ui
        
        Mapeia os widgets do arquivo .ui para os atributos da classe,
        mantendo compatibilidade com os métodos existentes.
        
        IMPORTANTE: Todos os widgets são carregados do arquivo .ui.
        Não há fallback - se o widget não existir, será None.
        """
        from PyQt6.QtWidgets import QProgressBar, QLineEdit
        
        # === WIDGETS DE STATUS ===
        self._status_icon_label = self.findChild(QLabel, "statusIconLabel")
        self._status_text_label = self.findChild(QLabel, "statusTextLabel")
        self._rate_value_label = self.findChild(QLabel, "rateValueLabel")
        self._buffer_progress = self.findChild(QProgressBar, "bufferProgress")
        
        # === WIDGETS DE CONTROLE DE PLAYBACK ===
        # Botões principais
        self._btn_play = self.findChild(QPushButton, "playBtn")
        self._btn_pause = self.findChild(QPushButton, "pauseBtn")
        self._btn_stop = self.findChild(QPushButton, "stopBtn")
        
        # Para compatibilidade com código legado
        self._btn_start = None  # Não existe no novo .ui
        self._btn_prev = None   # Não existe no novo .ui
        self._btn_next = None   # Não existe no novo .ui
        self._btn_end = None    # Não existe no novo .ui
        
        # Slider de posição
        self._timeline = self.findChild(QSlider, "positionSlider")
        self._current_time = self.findChild(QLabel, "positionLabel")
        self._total_time = self.findChild(QLabel, "durationLabel")
        
        # Controle de velocidade
        self._speed_slider = self.findChild(QSlider, "speedSlider")
        self._speed_value_label = self.findChild(QLabel, "speedValueLabel")
        
        # === WIDGETS DE FONTE DE DADOS ===
        self._source_type_combo = self.findChild(QComboBox, "sourceTypeCombo")
        self._source_path_edit = self.findChild(QLineEdit, "sourcePathEdit")
        self._btn_browse = self.findChild(QPushButton, "browseBtn")
        self._btn_connect = self.findChild(QPushButton, "connectBtn")
        self._btn_disconnect = self.findChild(QPushButton, "disconnectBtn")
        
        # === WIDGETS DE CONFIGURAÇÃO ===
        self._buffer_size_spin = self.findChild(QSpinBox, "bufferSizeSpin")
        self._update_rate_spin = self.findChild(QSpinBox, "updateRateSpin")
        self._auto_scroll_check = self.findChild(QCheckBox, "autoScrollCheck")
        self._record_check = self.findChild(QCheckBox, "recordCheck")
        
        # === STATUS (para compatibilidade) ===
        # Criamos um label de status se não existir no .ui
        self._status_label = self._status_text_label or QLabel("⏹ Parado")
        self._frame_info = QLabel("Frame: 0 / 0")  # Label auxiliar para info de frames
        
        # === MINIMAP (widget customizado - criar se necessário) ===
        self._minimap = MinimapWidget()
        self._minimap.position_changed.connect(self._on_minimap_position)
        
        # Configurar timeline
        if self._timeline:
            self._timeline.setMinimum(0)
            self._timeline.setMaximum(100)
            self._timeline.valueChanged.connect(self._on_timeline_changed)
        
        # Configurar speed slider
        if self._speed_slider:
            self._speed_slider.valueChanged.connect(self._on_speed_slider_changed)
        
        # Conectar botões de controle
        if self._btn_play:
            self._btn_play.clicked.connect(self._play)
        if self._btn_pause:
            self._btn_pause.clicked.connect(self._pause)
        if self._btn_stop:
            self._btn_stop.clicked.connect(self._stop)
        
        # Conectar botões de conexão
        if self._btn_connect:
            self._btn_connect.clicked.connect(self._on_connect)
        if self._btn_disconnect:
            self._btn_disconnect.clicked.connect(self._on_disconnect)

    def _connect_signals(self):
        """Conecta signals internos"""

    def _on_speed_slider_changed(self, value: int):
        """Handler para mudança no slider de velocidade"""
        self._speed = value / 100.0  # Slider vai de 25 a 400 (0.25x a 4x)
        if self._speed_value_label:
            self._speed_value_label.setText(f"{self._speed:.1f}x")
        
        # Atualiza timer se estiver reproduzindo
        if self._state == PlaybackState.PLAYING:
            base_interval = 33  # ~30 fps
            interval = int(base_interval / self._speed)
            interval = max(1, interval)
            self._timer.setInterval(interval)
        
        self.speed_changed.emit(self._speed)
        logger.debug(f"streaming_speed_changed: speed={self._speed}")
    
    def _on_connect(self):
        """Handler para botão de conectar"""
        if self._btn_connect:
            self._btn_connect.setEnabled(False)
        if self._btn_disconnect:
            self._btn_disconnect.setEnabled(True)
        if self._status_icon_label:
            self._status_icon_label.setText("🟢")
        if self._status_text_label:
            self._status_text_label.setText("Conectado")
        logger.info("streaming_connected")
    
    def _on_disconnect(self):
        """Handler para botão de desconectar"""
        self._stop()
        if self._btn_connect:
            self._btn_connect.setEnabled(True)
        if self._btn_disconnect:
            self._btn_disconnect.setEnabled(False)
        if self._status_icon_label:
            self._status_icon_label.setText("⚪")
        if self._status_text_label:
            self._status_text_label.setText("Desconectado")
        logger.info("streaming_disconnected")

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

    def set_data_preview(self, data: np.ndarray):
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

        elif self._mode == PlaybackMode.REVERSE and new_pos < 0:
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
    "MinimapWidget",
    "PlaybackMode",
    "PlaybackState",
    "StreamingPanel",
    "TimelineSlider",
]
