"""
ConfigPanel - Painel de configurações da aplicação

Características:
- Configurações de visualização
- Preferências de usuário
- Opções de performance
- Temas e aparência
- Persistência via QSettings

Autor: Platform Base Team
Versão: 2.0.0
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from PyQt6.QtCore import QSettings, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class ColorButton(QPushButton):
    """Botão para seleção de cor"""
    
    color_changed = pyqtSignal(str)  # Hex color
    
    def __init__(self, color: str = "#0d6efd", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(32, 32)
        self._update_style()
        self.clicked.connect(self._pick_color)
    
    def _update_style(self):
        """Atualiza estilo com a cor atual"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 2px solid #dee2e6;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: #0d6efd;
            }}
        """)
    
    def _pick_color(self):
        """Abre diálogo de seleção de cor"""
        from PyQt6.QtGui import QColor
        
        color = QColorDialog.getColor(QColor(self._color), self, "Selecionar Cor")
        if color.isValid():
            self._color = color.name()
            self._update_style()
            self.color_changed.emit(self._color)
    
    def get_color(self) -> str:
        """Retorna cor atual em hex"""
        return self._color
    
    def set_color(self, color: str):
        """Define cor atual"""
        self._color = color
        self._update_style()


class ConfigPanel(QWidget):
    """
    Painel de configurações da aplicação
    
    Signals:
        config_changed: Emitido quando qualquer configuração muda
        theme_changed: Emitido quando tema muda
        performance_changed: Emitido quando config de performance muda
    """
    
    config_changed = pyqtSignal(str, object)  # key, value
    theme_changed = pyqtSignal(str)  # theme name
    performance_changed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._settings = QSettings("PlatformBase", "Desktop")
        self._config: Dict[str, Any] = {}
        
        self._setup_ui()
        self._load_settings()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura interface principal"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("⚙️ Configurações")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #212529;
        """)
        layout.addWidget(header)
        
        # Tabs de configuração
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e9ecef;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border: 1px solid #e9ecef;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
            }
        """)
        
        # Tab Visualização
        viz_tab = self._create_visualization_tab()
        tabs.addTab(viz_tab, "🎨 Visualização")
        
        # Tab Performance
        perf_tab = self._create_performance_tab()
        tabs.addTab(perf_tab, "⚡ Performance")
        
        # Tab Geral
        general_tab = self._create_general_tab()
        tabs.addTab(general_tab, "📋 Geral")
        
        # Tab Atalhos
        shortcuts_tab = self._create_shortcuts_tab()
        tabs.addTab(shortcuts_tab, "⌨️ Atalhos")
        
        layout.addWidget(tabs)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        reset_btn = QPushButton("🔄 Restaurar Padrões")
        reset_btn.clicked.connect(self._reset_defaults)
        buttons_layout.addWidget(reset_btn)
        
        apply_btn = QPushButton("✅ Aplicar")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
        apply_btn.clicked.connect(self._apply_settings)
        buttons_layout.addWidget(apply_btn)
        
        layout.addLayout(buttons_layout)
    
    def _create_visualization_tab(self) -> QWidget:
        """Cria tab de configurações de visualização"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Tema
        theme_group = QGroupBox("🎨 Tema e Cores")
        theme_layout = QFormLayout(theme_group)
        
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["Claro", "Escuro", "Sistema"])
        theme_layout.addRow("Tema:", self._theme_combo)
        
        self._primary_color = ColorButton("#0d6efd")
        theme_layout.addRow("Cor primária:", self._primary_color)
        
        self._accent_color = ColorButton("#198754")
        theme_layout.addRow("Cor de destaque:", self._accent_color)
        
        layout.addWidget(theme_group)
        
        # Gráficos
        plot_group = QGroupBox("📊 Gráficos")
        plot_layout = QFormLayout(plot_group)
        
        self._line_width = QDoubleSpinBox()
        self._line_width.setRange(0.5, 5.0)
        self._line_width.setValue(2.0)
        self._line_width.setSingleStep(0.5)
        plot_layout.addRow("Espessura de linha:", self._line_width)
        
        self._marker_size = QSpinBox()
        self._marker_size.setRange(0, 20)
        self._marker_size.setValue(3)
        plot_layout.addRow("Tamanho do marcador:", self._marker_size)
        
        self._show_grid = QCheckBox()
        self._show_grid.setChecked(True)
        plot_layout.addRow("Mostrar grid:", self._show_grid)
        
        self._show_legend = QCheckBox()
        self._show_legend.setChecked(True)
        plot_layout.addRow("Mostrar legenda:", self._show_legend)
        
        self._antialiasing = QCheckBox()
        self._antialiasing.setChecked(True)
        plot_layout.addRow("Antialiasing:", self._antialiasing)
        
        layout.addWidget(plot_group)
        
        # Interface
        ui_group = QGroupBox("🖥️ Interface")
        ui_layout = QFormLayout(ui_group)
        
        self._font_size = QSpinBox()
        self._font_size.setRange(8, 24)
        self._font_size.setValue(12)
        ui_layout.addRow("Tamanho da fonte:", self._font_size)
        
        self._toolbar_icons = QComboBox()
        self._toolbar_icons.addItems(["Pequeno", "Médio", "Grande"])
        self._toolbar_icons.setCurrentText("Médio")
        ui_layout.addRow("Ícones da toolbar:", self._toolbar_icons)
        
        layout.addWidget(ui_group)
        
        layout.addStretch()
        return widget
    
    def _create_performance_tab(self) -> QWidget:
        """Cria tab de configurações de performance"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Decimação
        decimation_group = QGroupBox("📉 Decimação de Dados")
        dec_layout = QFormLayout(decimation_group)
        
        self._direct_limit = QSpinBox()
        self._direct_limit.setRange(1000, 100000)
        self._direct_limit.setValue(10000)
        self._direct_limit.setSingleStep(1000)
        dec_layout.addRow("Limite render direto:", self._direct_limit)
        
        self._target_points = QSpinBox()
        self._target_points.setRange(1000, 50000)
        self._target_points.setValue(5000)
        self._target_points.setSingleStep(500)
        dec_layout.addRow("Pontos alvo:", self._target_points)
        
        self._decimation_method = QComboBox()
        self._decimation_method.addItems([
            "MinMax (preserva picos)",
            "LTTB (visual)",
            "Amostragem aleatória",
            "Cada N pontos",
            "Média por bucket"
        ])
        dec_layout.addRow("Método:", self._decimation_method)
        
        layout.addWidget(decimation_group)
        
        # Cache
        cache_group = QGroupBox("💾 Cache")
        cache_layout = QFormLayout(cache_group)
        
        self._cache_enabled = QCheckBox()
        self._cache_enabled.setChecked(True)
        cache_layout.addRow("Habilitar cache:", self._cache_enabled)
        
        self._cache_size = QSpinBox()
        self._cache_size.setRange(10, 1000)
        self._cache_size.setValue(100)
        cache_layout.addRow("Tamanho do cache:", self._cache_size)
        
        layout.addWidget(cache_group)
        
        # Streaming
        streaming_group = QGroupBox("📡 Streaming")
        stream_layout = QFormLayout(streaming_group)
        
        self._chunk_size = QSpinBox()
        self._chunk_size.setRange(10000, 1000000)
        self._chunk_size.setValue(100000)
        self._chunk_size.setSingleStep(10000)
        stream_layout.addRow("Tamanho do chunk:", self._chunk_size)
        
        self._preload_chunks = QSpinBox()
        self._preload_chunks.setRange(1, 10)
        self._preload_chunks.setValue(2)
        stream_layout.addRow("Chunks pré-carregados:", self._preload_chunks)
        
        layout.addWidget(streaming_group)
        
        layout.addStretch()
        return widget
    
    def _create_general_tab(self) -> QWidget:
        """Cria tab de configurações gerais"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Arquivos
        files_group = QGroupBox("📁 Arquivos")
        files_layout = QFormLayout(files_group)
        
        self._default_encoding = QComboBox()
        self._default_encoding.addItems(["auto", "utf-8", "latin-1", "cp1252"])
        self._default_encoding.setCurrentText("auto")
        files_layout.addRow("Encoding padrão:", self._default_encoding)
        
        self._auto_backup = QCheckBox()
        self._auto_backup.setChecked(True)
        files_layout.addRow("Backup automático:", self._auto_backup)
        
        self._recent_files_limit = QSpinBox()
        self._recent_files_limit.setRange(5, 50)
        self._recent_files_limit.setValue(10)
        files_layout.addRow("Arquivos recentes:", self._recent_files_limit)
        
        layout.addWidget(files_group)
        
        # Histórico
        history_group = QGroupBox("📜 Histórico")
        history_layout = QFormLayout(history_group)
        
        self._undo_limit = QSpinBox()
        self._undo_limit.setRange(10, 500)
        self._undo_limit.setValue(100)
        history_layout.addRow("Limite de undo:", self._undo_limit)
        
        self._save_session = QCheckBox()
        self._save_session.setChecked(True)
        history_layout.addRow("Salvar sessão:", self._save_session)
        
        layout.addWidget(history_group)
        
        # Notificações
        notify_group = QGroupBox("🔔 Notificações")
        notify_layout = QFormLayout(notify_group)
        
        self._show_notifications = QCheckBox()
        self._show_notifications.setChecked(True)
        notify_layout.addRow("Mostrar notificações:", self._show_notifications)
        
        self._play_sounds = QCheckBox()
        self._play_sounds.setChecked(False)
        notify_layout.addRow("Tocar sons:", self._play_sounds)
        
        layout.addWidget(notify_group)
        
        layout.addStretch()
        return widget
    
    def _create_shortcuts_tab(self) -> QWidget:
        """Cria tab de atalhos de teclado"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info = QLabel(
            "⌨️ Atalhos de Teclado\n\n"
            "Ctrl+O  -  Abrir arquivo\n"
            "Ctrl+S  -  Salvar\n"
            "Ctrl+Shift+S  -  Salvar como\n"
            "Ctrl+Z  -  Desfazer\n"
            "Ctrl+Y  -  Refazer\n"
            "Ctrl+C  -  Copiar\n"
            "Ctrl+V  -  Colar\n"
            "Delete  -  Excluir seleção\n"
            "Ctrl++  -  Zoom in\n"
            "Ctrl+-  -  Zoom out\n"
            "Ctrl+0  -  Reset zoom\n"
            "F11  -  Tela cheia\n"
            "Esc  -  Cancelar operação\n"
        )
        info.setStyleSheet("""
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            padding: 16px;
            background-color: #f8f9fa;
            border-radius: 4px;
        """)
        layout.addWidget(info)
        
        layout.addStretch()
        return widget
    
    def _connect_signals(self):
        """Conecta signals para detecção de mudanças"""
        # Conecta todos os widgets para emitir config_changed
        self._theme_combo.currentTextChanged.connect(
            lambda v: self._on_config_change("theme", v)
        )
        self._show_grid.stateChanged.connect(
            lambda v: self._on_config_change("show_grid", bool(v))
        )
        self._show_legend.stateChanged.connect(
            lambda v: self._on_config_change("show_legend", bool(v))
        )
    
    def _on_config_change(self, key: str, value: Any):
        """Handler para mudança de configuração"""
        self._config[key] = value
        self.config_changed.emit(key, value)
    
    def _load_settings(self):
        """Carrega configurações salvas"""
        # Visualização
        self._theme_combo.setCurrentText(
            self._settings.value("viz/theme", "Claro")
        )
        self._line_width.setValue(
            float(self._settings.value("viz/line_width", 2.0))
        )
        self._marker_size.setValue(
            int(self._settings.value("viz/marker_size", 3))
        )
        self._show_grid.setChecked(
            self._settings.value("viz/show_grid", True, type=bool)
        )
        self._show_legend.setChecked(
            self._settings.value("viz/show_legend", True, type=bool)
        )
        
        # Performance
        self._direct_limit.setValue(
            int(self._settings.value("perf/direct_limit", 10000))
        )
        self._target_points.setValue(
            int(self._settings.value("perf/target_points", 5000))
        )
        self._cache_enabled.setChecked(
            self._settings.value("perf/cache_enabled", True, type=bool)
        )
        
        # Geral
        self._default_encoding.setCurrentText(
            self._settings.value("general/encoding", "auto")
        )
        self._undo_limit.setValue(
            int(self._settings.value("general/undo_limit", 100))
        )
        
        logger.info("settings_loaded")
    
    def _apply_settings(self):
        """Salva configurações"""
        # Visualização
        self._settings.setValue("viz/theme", self._theme_combo.currentText())
        self._settings.setValue("viz/line_width", self._line_width.value())
        self._settings.setValue("viz/marker_size", self._marker_size.value())
        self._settings.setValue("viz/show_grid", self._show_grid.isChecked())
        self._settings.setValue("viz/show_legend", self._show_legend.isChecked())
        self._settings.setValue("viz/antialiasing", self._antialiasing.isChecked())
        self._settings.setValue("viz/font_size", self._font_size.value())
        
        # Performance
        self._settings.setValue("perf/direct_limit", self._direct_limit.value())
        self._settings.setValue("perf/target_points", self._target_points.value())
        self._settings.setValue("perf/decimation_method", self._decimation_method.currentIndex())
        self._settings.setValue("perf/cache_enabled", self._cache_enabled.isChecked())
        self._settings.setValue("perf/cache_size", self._cache_size.value())
        self._settings.setValue("perf/chunk_size", self._chunk_size.value())
        self._settings.setValue("perf/preload_chunks", self._preload_chunks.value())
        
        # Geral
        self._settings.setValue("general/encoding", self._default_encoding.currentText())
        self._settings.setValue("general/auto_backup", self._auto_backup.isChecked())
        self._settings.setValue("general/recent_files_limit", self._recent_files_limit.value())
        self._settings.setValue("general/undo_limit", self._undo_limit.value())
        self._settings.setValue("general/save_session", self._save_session.isChecked())
        self._settings.setValue("general/show_notifications", self._show_notifications.isChecked())
        
        self._settings.sync()
        
        # Emite signals
        self.theme_changed.emit(self._theme_combo.currentText())
        self.performance_changed.emit()
        
        logger.info("settings_saved")
    
    def _reset_defaults(self):
        """Restaura configurações padrão"""
        # Visualização
        self._theme_combo.setCurrentText("Claro")
        self._line_width.setValue(2.0)
        self._marker_size.setValue(3)
        self._show_grid.setChecked(True)
        self._show_legend.setChecked(True)
        self._antialiasing.setChecked(True)
        self._font_size.setValue(12)
        self._toolbar_icons.setCurrentText("Médio")
        
        # Performance
        self._direct_limit.setValue(10000)
        self._target_points.setValue(5000)
        self._decimation_method.setCurrentIndex(0)
        self._cache_enabled.setChecked(True)
        self._cache_size.setValue(100)
        self._chunk_size.setValue(100000)
        self._preload_chunks.setValue(2)
        
        # Geral
        self._default_encoding.setCurrentText("auto")
        self._auto_backup.setChecked(True)
        self._recent_files_limit.setValue(10)
        self._undo_limit.setValue(100)
        self._save_session.setChecked(True)
        self._show_notifications.setChecked(True)
        self._play_sounds.setChecked(False)
        
        logger.info("settings_reset_to_defaults")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        return self._settings.value(key, default)
    
    def set_config(self, key: str, value: Any):
        """Define valor de configuração"""
        self._settings.setValue(key, value)
        self._settings.sync()


# Exports
__all__ = [
    "ConfigPanel",
    "ColorButton",
]
