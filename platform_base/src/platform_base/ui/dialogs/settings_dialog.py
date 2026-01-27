"""
Settings Dialog - Configurações da aplicação

Dialog completo para gerenciar preferências do usuário:
- Aparência (tema, cores, fontes)
- Visualização (crosshair, grid, legenda padrão)
- Performance (downsampling, buffer size)
- Caminhos (diretório padrão)
- Atalhos de teclado
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from PyQt6.QtCore import QSettings, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFontComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
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


@dataclass
class AppSettings:
    """Estrutura de configurações da aplicação"""
    
    # Aparência
    theme: str = "light"  # light, dark, system
    font_family: str = "Segoe UI"
    font_size: int = 10
    accent_color: str = "#0d6efd"
    
    # Visualização
    default_grid: bool = True
    default_legend: bool = True
    default_crosshair: bool = False
    auto_zoom_fit: bool = True
    plot_line_width: float = 2.0
    marker_size: int = 3
    
    # Performance
    lttb_threshold: int = 10000  # Pontos para ativar downsampling
    max_render_points: int = 100000
    buffer_size_mb: int = 512
    opengl_enabled: bool = False
    
    # Caminhos
    default_data_dir: str = ""
    default_export_dir: str = ""
    recent_files_max: int = 10
    
    # Comportamento
    confirm_on_exit: bool = True
    auto_save_layout: bool = True
    remember_window_size: bool = True
    check_updates: bool = False
    
    # Streaming
    default_fps: int = 30
    default_window_size: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'theme': self.theme,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'accent_color': self.accent_color,
            'default_grid': self.default_grid,
            'default_legend': self.default_legend,
            'default_crosshair': self.default_crosshair,
            'auto_zoom_fit': self.auto_zoom_fit,
            'plot_line_width': self.plot_line_width,
            'marker_size': self.marker_size,
            'lttb_threshold': self.lttb_threshold,
            'max_render_points': self.max_render_points,
            'buffer_size_mb': self.buffer_size_mb,
            'opengl_enabled': self.opengl_enabled,
            'default_data_dir': self.default_data_dir,
            'default_export_dir': self.default_export_dir,
            'recent_files_max': self.recent_files_max,
            'confirm_on_exit': self.confirm_on_exit,
            'auto_save_layout': self.auto_save_layout,
            'remember_window_size': self.remember_window_size,
            'check_updates': self.check_updates,
            'default_fps': self.default_fps,
            'default_window_size': self.default_window_size,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        """Cria a partir de dicionário"""
        settings = cls()
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        return settings


class SettingsDialog(QDialog):
    """
    Diálogo de configurações da aplicação
    
    Recursos:
    - Abas organizadas por categoria
    - Persistência via QSettings
    - Preview de alterações
    - Reset para padrões
    """
    
    # Signals
    settings_changed = pyqtSignal(object)  # AppSettings
    theme_changed = pyqtSignal(str)
    
    SETTINGS_ORG = "TRANSPETRO"
    SETTINGS_APP = "PlatformBase"
    
    def __init__(self, parent=None, current_settings: Optional[AppSettings] = None):
        super().__init__(parent)
        
        self.setWindowTitle("⚙️ Configurações")
        self.setMinimumSize(700, 550)
        self.setModal(True)
        
        # Carregar configurações atuais ou padrões
        self._original_settings = current_settings or self._load_settings()
        self._current_settings = AppSettings(**self._original_settings.to_dict())
        
        self._setup_ui()
        self._load_values()
        self._setup_connections()
        
        self._apply_dialog_style()
    
    def _setup_ui(self):
        """Configura a interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Tab Widget principal
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background-color: #ffffff;
                padding: 12px;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 10px 20px;
                margin-right: 4px;
                border-radius: 6px 6px 0 0;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
                color: #0d6efd;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Criar abas
        self._tabs.addTab(self._create_appearance_tab(), "🎨 Aparência")
        self._tabs.addTab(self._create_visualization_tab(), "📊 Visualização")
        self._tabs.addTab(self._create_performance_tab(), "⚡ Performance")
        self._tabs.addTab(self._create_paths_tab(), "📁 Caminhos")
        self._tabs.addTab(self._create_behavior_tab(), "🔧 Comportamento")
        
        layout.addWidget(self._tabs)
        
        # Botões
        self._create_buttons(layout)
    
    def _create_appearance_tab(self) -> QWidget:
        """Aba de aparência"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Grupo: Tema
        theme_group = QGroupBox("🌗 Tema")
        theme_layout = QFormLayout(theme_group)
        
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["Claro (Light)", "Escuro (Dark)", "Sistema"])
        self._theme_combo.setToolTip("Selecione o tema visual da aplicação")
        theme_layout.addRow("Tema:", self._theme_combo)
        
        # Cor de destaque
        self._accent_btn = QPushButton()
        self._accent_btn.setFixedSize(100, 30)
        self._accent_btn.setToolTip("Clique para escolher a cor de destaque")
        self._accent_btn.clicked.connect(self._choose_accent_color)
        theme_layout.addRow("Cor de Destaque:", self._accent_btn)
        
        layout.addWidget(theme_group)
        
        # Grupo: Fonte
        font_group = QGroupBox("🔤 Fonte")
        font_layout = QFormLayout(font_group)
        
        self._font_combo = QFontComboBox()
        self._font_combo.setToolTip("Fonte da interface")
        font_layout.addRow("Família:", self._font_combo)
        
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(8, 18)
        self._font_size_spin.setSuffix(" pt")
        self._font_size_spin.setToolTip("Tamanho da fonte (8-18 pt)")
        font_layout.addRow("Tamanho:", self._font_size_spin)
        
        layout.addWidget(font_group)
        
        layout.addStretch()
        return widget
    
    def _create_visualization_tab(self) -> QWidget:
        """Aba de visualização"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Grupo: Padrões de Gráfico
        defaults_group = QGroupBox("📈 Padrões de Gráfico")
        defaults_layout = QVBoxLayout(defaults_group)
        
        self._grid_check = QCheckBox("Mostrar grid por padrão")
        self._grid_check.setToolTip("Exibir linhas de grade nos gráficos automaticamente")
        defaults_layout.addWidget(self._grid_check)
        
        self._legend_check = QCheckBox("Mostrar legenda por padrão")
        self._legend_check.setToolTip("Exibir legenda nos gráficos automaticamente")
        defaults_layout.addWidget(self._legend_check)
        
        self._crosshair_check = QCheckBox("Crosshair ativo por padrão")
        self._crosshair_check.setToolTip("Ativar cursor em cruz com coordenadas automaticamente")
        defaults_layout.addWidget(self._crosshair_check)
        
        self._autozoom_check = QCheckBox("Auto-ajustar zoom ao carregar")
        self._autozoom_check.setToolTip("Ajustar automaticamente o zoom para mostrar todos os dados")
        defaults_layout.addWidget(self._autozoom_check)
        
        layout.addWidget(defaults_group)
        
        # Grupo: Estilo de Linha
        style_group = QGroupBox("✏️ Estilo de Linha")
        style_layout = QFormLayout(style_group)
        
        self._line_width_spin = QDoubleSpinBox()
        self._line_width_spin.setRange(0.5, 5.0)
        self._line_width_spin.setSingleStep(0.5)
        self._line_width_spin.setSuffix(" px")
        self._line_width_spin.setToolTip("Espessura das linhas nos gráficos")
        style_layout.addRow("Largura da linha:", self._line_width_spin)
        
        self._marker_size_spin = QSpinBox()
        self._marker_size_spin.setRange(1, 10)
        self._marker_size_spin.setSuffix(" px")
        self._marker_size_spin.setToolTip("Tamanho dos marcadores de pontos")
        style_layout.addRow("Tamanho do marcador:", self._marker_size_spin)
        
        layout.addWidget(style_group)
        
        layout.addStretch()
        return widget
    
    def _create_performance_tab(self) -> QWidget:
        """Aba de performance"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Grupo: Downsampling
        ds_group = QGroupBox("📉 Downsampling (LTTB)")
        ds_layout = QFormLayout(ds_group)
        
        self._lttb_spin = QSpinBox()
        self._lttb_spin.setRange(1000, 1000000)
        self._lttb_spin.setSingleStep(5000)
        self._lttb_spin.setSuffix(" pontos")
        self._lttb_spin.setToolTip("Número de pontos a partir do qual o LTTB é ativado")
        ds_layout.addRow("Limite para LTTB:", self._lttb_spin)
        
        self._max_points_spin = QSpinBox()
        self._max_points_spin.setRange(10000, 10000000)
        self._max_points_spin.setSingleStep(10000)
        self._max_points_spin.setSuffix(" pontos")
        self._max_points_spin.setToolTip("Máximo de pontos renderizados por série")
        ds_layout.addRow("Máx. pontos render:", self._max_points_spin)
        
        layout.addWidget(ds_group)
        
        # Grupo: Memória
        mem_group = QGroupBox("💾 Memória")
        mem_layout = QFormLayout(mem_group)
        
        self._buffer_spin = QSpinBox()
        self._buffer_spin.setRange(128, 4096)
        self._buffer_spin.setSingleStep(128)
        self._buffer_spin.setSuffix(" MB")
        self._buffer_spin.setToolTip("Tamanho do buffer de dados em memória")
        mem_layout.addRow("Buffer de dados:", self._buffer_spin)
        
        layout.addWidget(mem_group)
        
        # Grupo: Aceleração
        accel_group = QGroupBox("🚀 Aceleração")
        accel_layout = QVBoxLayout(accel_group)
        
        self._opengl_check = QCheckBox("Usar aceleração OpenGL (experimental)")
        self._opengl_check.setToolTip("Habilitar renderização por GPU (pode melhorar performance)")
        accel_layout.addWidget(self._opengl_check)
        
        warning_label = QLabel("⚠️ OpenGL pode causar instabilidade em alguns sistemas")
        warning_label.setStyleSheet("color: #fd7e14; font-size: 11px;")
        accel_layout.addWidget(warning_label)
        
        layout.addWidget(accel_group)
        
        layout.addStretch()
        return widget
    
    def _create_paths_tab(self) -> QWidget:
        """Aba de caminhos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Grupo: Diretórios
        dirs_group = QGroupBox("📂 Diretórios Padrão")
        dirs_layout = QFormLayout(dirs_group)
        
        # Diretório de dados
        data_layout = QHBoxLayout()
        self._data_dir_edit = QLineEdit()
        self._data_dir_edit.setPlaceholderText("Diretório padrão para abrir arquivos")
        self._data_dir_edit.setReadOnly(True)
        data_layout.addWidget(self._data_dir_edit)
        
        data_btn = QPushButton("📁")
        data_btn.setFixedWidth(40)
        data_btn.clicked.connect(lambda: self._choose_directory(self._data_dir_edit))
        data_layout.addWidget(data_btn)
        
        dirs_layout.addRow("Dados:", data_layout)
        
        # Diretório de exportação
        export_layout = QHBoxLayout()
        self._export_dir_edit = QLineEdit()
        self._export_dir_edit.setPlaceholderText("Diretório padrão para exportar arquivos")
        self._export_dir_edit.setReadOnly(True)
        export_layout.addWidget(self._export_dir_edit)
        
        export_btn = QPushButton("📁")
        export_btn.setFixedWidth(40)
        export_btn.clicked.connect(lambda: self._choose_directory(self._export_dir_edit))
        export_layout.addWidget(export_btn)
        
        dirs_layout.addRow("Exportação:", export_layout)
        
        layout.addWidget(dirs_group)
        
        # Grupo: Arquivos Recentes
        recent_group = QGroupBox("📋 Arquivos Recentes")
        recent_layout = QFormLayout(recent_group)
        
        self._recent_max_spin = QSpinBox()
        self._recent_max_spin.setRange(5, 50)
        self._recent_max_spin.setToolTip("Número máximo de arquivos recentes a lembrar")
        recent_layout.addRow("Máximo de recentes:", self._recent_max_spin)
        
        clear_recent_btn = QPushButton("🗑️ Limpar Recentes")
        clear_recent_btn.clicked.connect(self._clear_recent_files)
        recent_layout.addRow("", clear_recent_btn)
        
        layout.addWidget(recent_group)
        
        layout.addStretch()
        return widget
    
    def _create_behavior_tab(self) -> QWidget:
        """Aba de comportamento"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # Grupo: Aplicação
        app_group = QGroupBox("🖥️ Aplicação")
        app_layout = QVBoxLayout(app_group)
        
        self._confirm_exit_check = QCheckBox("Confirmar antes de sair")
        self._confirm_exit_check.setToolTip("Exibir confirmação ao fechar a aplicação")
        app_layout.addWidget(self._confirm_exit_check)
        
        self._auto_save_layout_check = QCheckBox("Salvar layout automaticamente")
        self._auto_save_layout_check.setToolTip("Restaurar posição e tamanho dos painéis ao reabrir")
        app_layout.addWidget(self._auto_save_layout_check)
        
        self._remember_size_check = QCheckBox("Lembrar tamanho da janela")
        self._remember_size_check.setToolTip("Restaurar tamanho da janela ao reabrir")
        app_layout.addWidget(self._remember_size_check)
        
        self._check_updates_check = QCheckBox("Verificar atualizações ao iniciar")
        self._check_updates_check.setToolTip("Verificar novas versões automaticamente")
        app_layout.addWidget(self._check_updates_check)
        
        layout.addWidget(app_group)
        
        # Grupo: Streaming
        streaming_group = QGroupBox("▶️ Streaming")
        streaming_layout = QFormLayout(streaming_group)
        
        self._fps_spin = QSpinBox()
        self._fps_spin.setRange(1, 60)
        self._fps_spin.setSuffix(" fps")
        self._fps_spin.setToolTip("Taxa de quadros padrão para streaming")
        streaming_layout.addRow("FPS padrão:", self._fps_spin)
        
        self._window_size_spin = QSpinBox()
        self._window_size_spin.setRange(100, 10000)
        self._window_size_spin.setSingleStep(100)
        self._window_size_spin.setSuffix(" pontos")
        self._window_size_spin.setToolTip("Janela de visualização padrão")
        streaming_layout.addRow("Janela padrão:", self._window_size_spin)
        
        layout.addWidget(streaming_group)
        
        layout.addStretch()
        return widget
    
    def _create_buttons(self, layout: QVBoxLayout):
        """Cria botões de ação"""
        button_layout = QHBoxLayout()
        
        # Reset para padrões
        reset_btn = QPushButton("🔄 Restaurar Padrões")
        reset_btn.setToolTip("Restaurar todas as configurações para valores padrão")
        reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        # Cancel
        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Apply
        apply_btn = QPushButton("✓ Aplicar")
        apply_btn.clicked.connect(self._apply_settings)
        button_layout.addWidget(apply_btn)
        
        # OK
        ok_btn = QPushButton("✓ OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self._accept_and_save)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """Configura conexões de signals"""
        # Notificar mudança de tema
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
    
    def _load_values(self):
        """Carrega valores nas widgets"""
        s = self._current_settings
        
        # Aparência
        theme_map = {"light": 0, "dark": 1, "system": 2}
        self._theme_combo.setCurrentIndex(theme_map.get(s.theme, 0))
        self._update_accent_button(s.accent_color)
        self._font_combo.setCurrentFont(QFont(s.font_family))
        self._font_size_spin.setValue(s.font_size)
        
        # Visualização
        self._grid_check.setChecked(s.default_grid)
        self._legend_check.setChecked(s.default_legend)
        self._crosshair_check.setChecked(s.default_crosshair)
        self._autozoom_check.setChecked(s.auto_zoom_fit)
        self._line_width_spin.setValue(s.plot_line_width)
        self._marker_size_spin.setValue(s.marker_size)
        
        # Performance
        self._lttb_spin.setValue(s.lttb_threshold)
        self._max_points_spin.setValue(s.max_render_points)
        self._buffer_spin.setValue(s.buffer_size_mb)
        self._opengl_check.setChecked(s.opengl_enabled)
        
        # Caminhos
        self._data_dir_edit.setText(s.default_data_dir)
        self._export_dir_edit.setText(s.default_export_dir)
        self._recent_max_spin.setValue(s.recent_files_max)
        
        # Comportamento
        self._confirm_exit_check.setChecked(s.confirm_on_exit)
        self._auto_save_layout_check.setChecked(s.auto_save_layout)
        self._remember_size_check.setChecked(s.remember_window_size)
        self._check_updates_check.setChecked(s.check_updates)
        self._fps_spin.setValue(s.default_fps)
        self._window_size_spin.setValue(s.default_window_size)
    
    def _collect_values(self) -> AppSettings:
        """Coleta valores das widgets"""
        theme_map = {0: "light", 1: "dark", 2: "system"}
        
        return AppSettings(
            # Aparência
            theme=theme_map.get(self._theme_combo.currentIndex(), "light"),
            font_family=self._font_combo.currentFont().family(),
            font_size=self._font_size_spin.value(),
            accent_color=self._current_settings.accent_color,
            
            # Visualização
            default_grid=self._grid_check.isChecked(),
            default_legend=self._legend_check.isChecked(),
            default_crosshair=self._crosshair_check.isChecked(),
            auto_zoom_fit=self._autozoom_check.isChecked(),
            plot_line_width=self._line_width_spin.value(),
            marker_size=self._marker_size_spin.value(),
            
            # Performance
            lttb_threshold=self._lttb_spin.value(),
            max_render_points=self._max_points_spin.value(),
            buffer_size_mb=self._buffer_spin.value(),
            opengl_enabled=self._opengl_check.isChecked(),
            
            # Caminhos
            default_data_dir=self._data_dir_edit.text(),
            default_export_dir=self._export_dir_edit.text(),
            recent_files_max=self._recent_max_spin.value(),
            
            # Comportamento
            confirm_on_exit=self._confirm_exit_check.isChecked(),
            auto_save_layout=self._auto_save_layout_check.isChecked(),
            remember_window_size=self._remember_size_check.isChecked(),
            check_updates=self._check_updates_check.isChecked(),
            default_fps=self._fps_spin.value(),
            default_window_size=self._window_size_spin.value(),
        )
    
    def _choose_accent_color(self):
        """Abre diálogo de seleção de cor"""
        current = QColor(self._current_settings.accent_color)
        color = QColorDialog.getColor(current, self, "Escolher Cor de Destaque")
        
        if color.isValid():
            self._current_settings.accent_color = color.name()
            self._update_accent_button(color.name())
    
    def _update_accent_button(self, color: str):
        """Atualiza visual do botão de cor"""
        self._accent_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid #dee2e6;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                border-color: #0d6efd;
            }}
        """)
    
    def _choose_directory(self, line_edit: QLineEdit):
        """Abre diálogo de seleção de diretório"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Diretório",
            line_edit.text() or ""
        )
        if directory:
            line_edit.setText(directory)
    
    def _clear_recent_files(self):
        """Limpa lista de arquivos recentes"""
        reply = QMessageBox.question(
            self,
            "Limpar Recentes",
            "Deseja limpar a lista de arquivos recentes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
            settings.remove("recent_files")
            QMessageBox.information(self, "Sucesso", "Lista de recentes limpa!")
    
    def _reset_to_defaults(self):
        """Restaura configurações padrão"""
        reply = QMessageBox.question(
            self,
            "Restaurar Padrões",
            "Deseja restaurar todas as configurações para os valores padrão?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._current_settings = AppSettings()
            self._load_values()
    
    def _on_theme_changed(self, index: int):
        """Handler para mudança de tema"""
        theme_map = {0: "light", 1: "dark", 2: "system"}
        theme = theme_map.get(index, "light")
        self.theme_changed.emit(theme)
    
    def _apply_settings(self):
        """Aplica configurações sem fechar"""
        self._current_settings = self._collect_values()
        self._save_settings(self._current_settings)
        self.settings_changed.emit(self._current_settings)
        logger.info("Settings applied")
    
    def _accept_and_save(self):
        """Aceita e salva configurações"""
        self._apply_settings()
        self.accept()
    
    def _save_settings(self, settings: AppSettings):
        """Salva configurações via QSettings"""
        qsettings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        
        for key, value in settings.to_dict().items():
            qsettings.setValue(f"settings/{key}", value)
        
        qsettings.sync()
    
    def _load_settings(self) -> AppSettings:
        """Carrega configurações via QSettings"""
        qsettings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        default_settings = AppSettings()
        data = {}
        
        for key in default_settings.to_dict().keys():
            value = qsettings.value(f"settings/{key}")
            if value is not None:
                # Converter tipos
                default_value = getattr(default_settings, key)
                if isinstance(default_value, bool):
                    data[key] = value == "true" if isinstance(value, str) else bool(value)
                elif isinstance(default_value, int):
                    data[key] = int(value)
                elif isinstance(default_value, float):
                    data[key] = float(value)
                else:
                    data[key] = value
        
        return AppSettings.from_dict(data)
    
    def _apply_dialog_style(self):
        """Aplica estilos ao diálogo"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #0d6efd;
            }
            QCheckBox {
                spacing: 8px;
                padding: 4px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
                padding: 6px 10px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                background-color: #ffffff;
                min-height: 24px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border-color: #0d6efd;
            }
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                background-color: #ffffff;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #0d6efd;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            QPushButton:default {
                background-color: #0d6efd;
                color: white;
                border-color: #0d6efd;
            }
            QPushButton:default:hover {
                background-color: #0b5ed7;
            }
        """)
    
    def get_settings(self) -> AppSettings:
        """Retorna as configurações atuais"""
        return self._collect_values()


def show_settings_dialog(parent=None, current_settings: Optional[AppSettings] = None) -> Optional[AppSettings]:
    """
    Função de conveniência para mostrar o diálogo de configurações
    
    Args:
        parent: Widget pai
        current_settings: Configurações atuais (opcional)
    
    Returns:
        AppSettings se aceito, None se cancelado
    """
    dialog = SettingsDialog(parent, current_settings)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_settings()
    
    return None


def load_app_settings() -> AppSettings:
    """
    Carrega configurações da aplicação do QSettings
    
    Returns:
        AppSettings com as configurações salvas ou padrões
    """
    qsettings = QSettings(SettingsDialog.SETTINGS_ORG, SettingsDialog.SETTINGS_APP)
    default_settings = AppSettings()
    data = {}
    
    for key in default_settings.to_dict().keys():
        value = qsettings.value(f"settings/{key}")
        if value is not None:
            default_value = getattr(default_settings, key)
            if isinstance(default_value, bool):
                data[key] = value == "true" if isinstance(value, str) else bool(value)
            elif isinstance(default_value, int):
                data[key] = int(value)
            elif isinstance(default_value, float):
                data[key] = float(value)
            else:
                data[key] = value
    
    return AppSettings.from_dict(data)
