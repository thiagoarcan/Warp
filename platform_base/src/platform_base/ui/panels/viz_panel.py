"""
VizPanel - Painel moderno de visualização com drag-and-drop

Características:
- Sistema drag-and-drop para criar gráficos
- Área de plotagem com zonas definidas
- Interface intuitiva e moderna
- Suporte para múltiplas visualizações
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QFrame, QScrollArea, QSplitter, QPushButton, QGroupBox,
    QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QRect
from PyQt6.QtGui import QPainter, QPen, QBrush, QFont, QColor

# Matplotlib imports para visualização real
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from platform_base.ui.state import SessionState
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class MatplotlibWidget(QWidget):
    """Widget real de matplotlib para visualização de dados"""
    
    def __init__(self, series, plot_type: str = "2d", parent=None):
        super().__init__(parent)
        
        self.series = series
        self.plot_type = plot_type
        
        # Configurar matplotlib com estilo moderno
        plt.style.use('default')
        
        # Criar figura matplotlib com design moderno
        self.figure = Figure(figsize=(12, 8), dpi=100, tight_layout=True, 
                            facecolor='white', edgecolor='none')
        self.canvas = FigureCanvas(self.figure)
        
        # Configurar cores modernas
        self.colors = ['#0d6efd', '#198754', '#dc3545', '#fd7e14', '#6f42c1', '#20c997']
        self.current_color_idx = 0
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        
        # Enable context menu
        self.canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self._show_context_menu)
        
        # Criar o gráfico
        self._create_plot()
    
    def _create_plot(self):
        """Cria o gráfico com base no tipo"""
        self.figure.clear()
        
        try:
            if self.plot_type == "2d":
                self._create_2d_plot()
            elif self.plot_type == "3d":
                self._create_3d_plot()
            elif self.plot_type == "heatmap":
                self._create_heatmap()
            elif self.plot_type == "scatter":
                self._create_scatter_plot()
            else:
                self._create_2d_plot()  # Default
                
            self.canvas.draw()
            
        except Exception as e:
            logger.error("plot_creation_error", error=str(e), plot_type=self.plot_type)
            self._create_error_plot(str(e))
    
    def _create_2d_plot(self):
        """Cria gráfico 2D de linha com design moderno"""
        ax = self.figure.add_subplot(111)
        
        # Dados da série
        values = self.series.values
        n_points = len(values)
        x_data = np.arange(n_points)
        
        # Cor moderna baseada no índice
        color = self.colors[self.current_color_idx % len(self.colors)]
        
        # Plot principal com linha mais moderna
        line = ax.plot(x_data, values, linewidth=2.0, color=color, alpha=0.9,
                      label=f"{self.series.name} ({self.series.unit})",
                      markevery=max(1, n_points//50), marker='o', markersize=3,
                      markerfacecolor=color, markeredgecolor='white', markeredgewidth=0.5)
        
        # Personalização moderna
        ax.set_title(f"📊 {self.series.name} - Análise Temporal", 
                    fontsize=16, fontweight='bold', color='#212529', pad=20)
        ax.set_xlabel("🔢 Índice da Amostra", fontsize=13, color='#495057', fontweight='500')
        ax.set_ylabel(f"📈 Valor ({self.series.unit})", fontsize=13, color='#495057', fontweight='500')
        
        # Grid moderno
        ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.8, color='#dee2e6')
        ax.set_axisbelow(True)
        ax.set_facecolor('#fafbfc')
        
        # Bordas mais modernas
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#dee2e6')
        ax.spines['bottom'].set_color('#dee2e6')
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_linewidth(1.2)
        
        # Legenda moderna
        legend = ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=False,
                          facecolor='white', edgecolor='#e9ecef', framealpha=0.98,
                          fontsize=11)
        legend.get_frame().set_linewidth(1.5)
        legend.get_frame().set_boxstyle("round,pad=0.3")
        
        # Estatísticas no canto com design moderno
        std_val = np.std(values)
        stats_text = f"📊 ESTATÍSTICAS\n" \
                    f"Pontos: {n_points:,}\n" \
                    f"Min: {np.min(values):.3f}\n" \
                    f"Max: {np.max(values):.3f}\n" \
                    f"Média: {np.mean(values):.3f}\n" \
                    f"Desvio: {std_val:.3f}"
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               verticalalignment='top', fontsize=9, fontweight='500',
               bbox=dict(boxstyle='round,pad=0.6', facecolor='white', 
                        edgecolor='#e9ecef', alpha=0.95, linewidth=1.2))
    
    def _create_3d_plot(self):
        """Cria visualização 3D (superfície)"""
        ax = self.figure.add_subplot(111, projection='3d')
        
        values = self.series.values
        n_points = len(values)
        
        # Criar dados 3D simulados baseados na série
        # Grid para superfície
        grid_size = min(50, int(np.sqrt(n_points)))
        if grid_size < 5:
            grid_size = 5
            
        x = np.linspace(0, 1, grid_size)
        y = np.linspace(0, 1, grid_size)
        X, Y = np.meshgrid(x, y)
        
        # Interpolar dados para grid 2D
        indices = np.linspace(0, n_points-1, grid_size*grid_size).astype(int)
        z_data = values[indices].reshape(grid_size, grid_size)
        
        # Surface plot
        surf = ax.plot_surface(X, Y, z_data, cmap='viridis', alpha=0.8, 
                              linewidth=0, antialiased=True, 
                              label=f"{self.series.name}")
        
        # Personalização
        ax.set_title(f"{self.series.name} - Visualização 3D", 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel("X normalizado")
        ax.set_ylabel("Y normalizado") 
        ax.set_zlabel(f"Valor ({self.series.unit})")
        
        # Colorbar com label
        cbar = self.figure.colorbar(surf, shrink=0.5, aspect=20)
        cbar.set_label(f"{self.series.name} ({self.series.unit})", rotation=270, labelpad=15)
    
    def _create_heatmap(self):
        """Cria heatmap dos dados"""
        ax = self.figure.add_subplot(111)
        
        values = self.series.values
        n_points = len(values)
        
        # Reorganizar dados em matriz 2D
        grid_size = int(np.sqrt(n_points))
        if grid_size < 10:
            grid_size = 10
            
        # Preencher com zeros se necessário
        matrix_size = grid_size * grid_size
        if matrix_size > n_points:
            padded_values = np.pad(values, (0, matrix_size - n_points), 'constant')
        else:
            padded_values = values[:matrix_size]
            
        heat_data = padded_values.reshape(grid_size, grid_size)
        
        # Heatmap
        im = ax.imshow(heat_data, cmap='plasma', aspect='auto', interpolation='bilinear')
        
        # Personalização
        ax.set_title(f"{self.series.name} - Heatmap", fontsize=14, fontweight='bold')
        ax.set_xlabel("Coluna")
        ax.set_ylabel("Linha")
        
        # Colorbar com label
        cbar = self.figure.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label(f"{self.series.name} ({self.series.unit})", rotation=270, labelpad=15)
    
    def _create_scatter_plot(self):
        """Cria gráfico de dispersão"""
        ax = self.figure.add_subplot(111)
        
        values = self.series.values
        n_points = len(values)
        x_data = np.arange(n_points)
        
        # Scatter plot com cores baseadas no valor
        scatter = ax.scatter(x_data, values, c=values, cmap='viridis', 
                           alpha=0.7, s=20, edgecolors='black', linewidth=0.5,
                           label=f"{self.series.name}")
        
        # Personalização
        ax.set_title(f"{self.series.name} - Scatter Plot", 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel("Índice da Amostra")
        ax.set_ylabel(f"Valor ({self.series.unit})")
        
        # Grid, legenda e colorbar
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        
        # Legenda
        legend = ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True,
                          facecolor='white', edgecolor='#dee2e6', framealpha=0.95)
        legend.get_frame().set_linewidth(1)
        
        # Colorbar com label
        cbar = self.figure.colorbar(scatter, ax=ax)
        cbar.set_label(f"Intensidade - {self.series.name} ({self.series.unit})", 
                      rotation=270, labelpad=15)
    
    def _create_error_plot(self, error_msg: str):
        """Cria plot de erro quando algo falha"""
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, f"Erro na visualização:\n{error_msg}", 
               transform=ax.transAxes, ha='center', va='center',
               fontsize=12, color='red',
               bbox=dict(boxstyle='round', facecolor='#ffe6e6', alpha=0.8))
        ax.set_title("Erro na Visualização", fontsize=14, color='red')
        ax.axis('off')
    
    def _show_context_menu(self, position):
        """Mostra menu de contexto moderno para o gráfico"""
        try:
            from PyQt6.QtCore import QPoint
            from PyQt6.QtWidgets import QMenu
            from PyQt6.QtGui import QAction
            
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: #ffffff;
                    border: 2px solid #0d6efd;
                    border-radius: 8px;
                    padding: 6px;
                    font-size: 13px;
                }
                QMenu::item {
                    padding: 10px 20px;
                    border-radius: 6px;
                    margin: 2px;
                }
                QMenu::item:selected {
                    background-color: #0d6efd;
                    color: white;
                }
                QMenu::separator {
                    height: 2px;
                    background-color: #e9ecef;
                    margin: 6px 10px;
                }
            """)
            
            # Título
            title_action = QAction(f"📊 Gráfico {self.plot_type.upper()}", self)
            title_action.setEnabled(False)
            title_action.setStyleSheet("font-weight: bold; color: #0d6efd;")
            menu.addAction(title_action)
            menu.addSeparator()
            
            # Exportar
            export_png_action = QAction("💾 Exportar como PNG", self)
            export_png_action.triggered.connect(self._export_png)
            menu.addAction(export_png_action)
            
            export_pdf_action = QAction("📄 Exportar como PDF", self)
            export_pdf_action.triggered.connect(self._export_pdf)
            menu.addAction(export_pdf_action)
            
            menu.addSeparator()
            
            # Visualização
            zoom_action = QAction("🔍 Zoom para Ajustar", self)
            zoom_action.triggered.connect(self._zoom_to_fit)
            menu.addAction(zoom_action)
            
            grid_action = QAction("⚏ Alternar Grid", self)
            grid_action.triggered.connect(self._toggle_grid)
            menu.addAction(grid_action)
            
            legend_action = QAction("📋 Alternar Legenda", self)
            legend_action.triggered.connect(self._toggle_legend)
            menu.addAction(legend_action)
            
            menu.addSeparator()
            
            # Propriedades
            props_action = QAction("⚙️ Propriedades do Gráfico", self)
            props_action.triggered.connect(self._show_properties)
            menu.addAction(props_action)
            
            # Mostrar menu
            menu.exec(self.mapToGlobal(position))
            
        except Exception as e:
            logger.error("context_menu_error", error=str(e))
    
    def _export_png(self):
        """Exporta gráfico como PNG"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Salvar Gráfico", f"{self.series.name}_{self.plot_type}.png",
                "PNG files (*.png);;All files (*.*)"
            )
            
            if filename:
                self.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
                logger.info("plot_exported_png", filename=filename)
                
        except Exception as e:
            logger.error("export_png_error", error=str(e))
    
    def _export_pdf(self):
        """Exporta gráfico como PDF"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Salvar Gráfico", f"{self.series.name}_{self.plot_type}.pdf",
                "PDF files (*.pdf);;All files (*.*)"
            )
            
            if filename:
                self.figure.savefig(filename, format='pdf', bbox_inches='tight', facecolor='white')
                logger.info("plot_exported_pdf", filename=filename)
                
        except Exception as e:
            logger.error("export_pdf_error", error=str(e))
    
    def _zoom_to_fit(self):
        """Ajusta zoom para mostrar todos os dados"""
        try:
            for ax in self.figure.get_axes():
                ax.relim()
                ax.autoscale()
            self.canvas.draw()
            
        except Exception as e:
            logger.error("zoom_fit_error", error=str(e))
    
    def _toggle_grid(self):
        """Alterna exibição do grid"""
        try:
            for ax in self.figure.get_axes():
                ax.grid(not ax.get_gridlines()[0].get_visible() if ax.get_gridlines() else True)
            self.canvas.draw()
            
        except Exception as e:
            logger.error("toggle_grid_error", error=str(e))
    
    def _toggle_legend(self):
        """Alterna exibição da legenda"""
        try:
            for ax in self.figure.get_axes():
                legend = ax.get_legend()
                if legend:
                    legend.set_visible(not legend.get_visible())
                else:
                    ax.legend([f"{self.series.name} ({self.series.unit})"])
            self.canvas.draw()
            
        except Exception as e:
            logger.error("toggle_legend_error", error=str(e))
    
    def _show_properties(self):
        """Mostra dialog de propriedades do gráfico"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            props_text = f"""
Gráfico: {self.plot_type.upper()}
Série: {self.series.name}
Unidade: {self.series.unit}
Pontos: {len(self.series.values):,}
Min: {np.min(self.series.values):.6f}
Max: {np.max(self.series.values):.6f}
Média: {np.mean(self.series.values):.6f}
Desvio Padrão: {np.std(self.series.values):.6f}
            """
            
            QMessageBox.information(self, f"Propriedades - {self.series.name}", props_text)
            
        except Exception as e:
            logger.error("show_properties_error", error=str(e))


class DropZone(QFrame):
    """Zona de drop para criar gráficos"""
    
    series_dropped = pyqtSignal(str, str)  # dataset_id, series_id
    
    def __init__(self, title: str, description: str, plot_type: str):
        super().__init__()
        
        self.title = title
        self.description = description
        self.plot_type = plot_type
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura zona de drop"""
        self.setMinimumSize(200, 150)
        self.setAcceptDrops(True)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Título
        title_label = QLabel(self.title)
        title_label.setFont(QFont("", 11, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #0d6efd; font-size: 13px;")
        layout.addWidget(title_label)
        
        # Descrição
        desc_label = QLabel(self.description)
        desc_label.setFont(QFont("", 9))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #6c757d; line-height: 1.4;")
        layout.addWidget(desc_label)
        
        # Estilo moderno da zona de drop
        self.setStyleSheet(f"""
            DropZone {{
                border: 3px dashed #dee2e6;
                border-radius: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                font-weight: 600;
            }}
            DropZone:hover {{
                border: 3px dashed #0d6efd;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #e3f2fd, stop: 1 #f3e5f5);
            }}
        """)
    
    def dragEnterEvent(self, event):
        """Handler para entrada de drag"""
        if event.mimeData().hasText():
            # Verificar se é uma série
            data = event.mimeData().text().split("|")
            if len(data) == 2:
                event.acceptProposedAction()
                self.setStyleSheet("""
                    DropZone {
                        border: 2px solid #198754;
                        border-radius: 8px;
                        background-color: #d4edda;
                    }
                """)
    
    def dragLeaveEvent(self, event):
        """Handler para saída de drag"""
        self.setStyleSheet("""
            DropZone {
                border: 2px dashed #ced4da;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
            DropZone:hover {
                border-color: #0d6efd;
                background-color: #e9f3ff;
            }
        """)
    
    def dropEvent(self, event):
        """Handler para drop"""
        if event.mimeData().hasText():
            data = event.mimeData().text().split("|")
            if len(data) == 2:
                dataset_id, series_id = data
                self.series_dropped.emit(dataset_id, series_id)
                event.acceptProposedAction()
                
                # Reset visual
                self.dragLeaveEvent(event)
                
                logger.info("series_dropped", 
                          dataset_id=dataset_id, 
                          series_id=series_id, 
                          plot_type=self.plot_type)


class ModernVizPanel(QWidget):
    """
    Painel de visualização moderno com drag-and-drop
    
    Funcionalidades:
    - Zonas de drop para gráficos 2D/3D
    - Sistema intuitivo de drag-and-drop
    - Múltiplas visualizações em abas
    - Interface moderna e responsiva
    """
    
    # Signals
    plot_requested = pyqtSignal(str, str, str)  # dataset_id, series_id, plot_type
    
    def __init__(self, session_state: SessionState):
        super().__init__()
        
        self.session_state = session_state
        self._plots = []  # Lista de gráficos ativos
        
        self._setup_modern_ui()
        self._setup_connections()
        
        logger.debug("modern_viz_panel_initialized")
    
    def _setup_modern_ui(self):
        """Interface moderna com zonas de drop"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Header
        self._create_header(layout)
        
        # Main content area
        self._create_main_area(layout)
    
    def _create_header(self, layout: QVBoxLayout):
        """Cabeçalho do painel"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(4, 4, 4, 4)
        
        # Título
        title_label = QLabel("📊 Visualizações")
        title_label.setFont(QFont("", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #0d6efd; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botões de ação rápida
        new_2d_btn = QPushButton("📊 Novo 2D")
        new_2d_btn.setToolTip("Criar novo gráfico 2D")
        new_2d_btn.clicked.connect(self.create_2d_plot)
        header_layout.addWidget(new_2d_btn)
        
        new_3d_btn = QPushButton("📈 Novo 3D")
        new_3d_btn.setToolTip("Criar novo gráfico 3D")
        new_3d_btn.clicked.connect(self.create_3d_plot)
        header_layout.addWidget(new_3d_btn)
        
        layout.addWidget(header_frame)
    
    def _create_main_area(self, layout: QVBoxLayout):
        """Área principal com zonas de drop"""
        # Tab widget para múltiplas visualizações
        self._viz_tabs = QTabWidget()
        self._viz_tabs.setTabsClosable(True)
        self._viz_tabs.tabCloseRequested.connect(self._close_tab)
        
        # Styling moderno para tabs
        self._viz_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e9ecef;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Tab inicial com zonas de drop
        self._create_drop_zones_tab()
        
        layout.addWidget(self._viz_tabs)
    
    def _create_drop_zones_tab(self):
        """Cria tab com zonas de drop para criar gráficos"""
        drop_widget = QWidget()
        drop_layout = QVBoxLayout(drop_widget)
        drop_layout.setContentsMargins(16, 16, 16, 16)
        drop_layout.setSpacing(12)
        
        # Instruções modernas
        instructions = QLabel(
            "🎯 <b>Como Criar Visualizações</b><br>"
            "✨ <b>Método 1:</b> Clique com botão direito em uma série<br>"
            "🎨 <b>Método 2:</b> Arraste a série para as zonas abaixo<br>"
            "📊 Suporte para gráficos 2D, 3D, Heatmap e Scatter"
        )
        instructions.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #e3f2fd, stop: 1 #f3e5f5);
                border: 2px solid #0d6efd;
                border-radius: 10px;
                padding: 16px;
                color: #1565c0;
                font-size: 13px;
                font-weight: 500;
                line-height: 1.4;
            }
        """)
        instructions.setWordWrap(True)
        drop_layout.addWidget(instructions)
        
        # Grid de zonas de drop
        zones_frame = QFrame()
        zones_layout = QGridLayout(zones_frame)
        zones_layout.setSpacing(16)
        
        # Zona 2D
        zone_2d = DropZone(
            "📊 Gráfico 2D",
            "Arraste série aqui para\ncriar gráfico de linha 2D",
            "2d"
        )
        zone_2d.series_dropped.connect(self._on_series_dropped_2d)
        zones_layout.addWidget(zone_2d, 0, 0)
        
        # Zona 3D
        zone_3d = DropZone(
            "📈 Gráfico 3D",
            "Arraste série aqui para\ncriar visualização 3D",
            "3d"
        )
        zone_3d.series_dropped.connect(self._on_series_dropped_3d)
        zones_layout.addWidget(zone_3d, 0, 1)
        
        # Zona Heatmap
        zone_heatmap = DropZone(
            "🔥 Heatmap",
            "Arraste série aqui para\ncriar mapa de calor",
            "heatmap"
        )
        zone_heatmap.series_dropped.connect(self._on_series_dropped_heatmap)
        zones_layout.addWidget(zone_heatmap, 1, 0)
        
        # Zona Scatter
        zone_scatter = DropZone(
            "🔵 Scatter Plot",
            "Arraste série aqui para\ncriar gráfico de dispersão",
            "scatter"
        )
        zone_scatter.series_dropped.connect(self._on_series_dropped_scatter)
        zones_layout.addWidget(zone_scatter, 1, 1)
        
        drop_layout.addWidget(zones_frame)
        drop_layout.addStretch()
        
        self._viz_tabs.addTab(drop_widget, "➕ Nova Visualização")
    
    def _setup_connections(self):
        """Configuração de conexões"""
        # Session state connections
        self.session_state.dataset_changed.connect(self._on_dataset_changed)
    
    @pyqtSlot(str)
    def _on_dataset_changed(self, dataset_id: str):
        """Handler para mudança de dataset"""
        # Update UI quando dataset mudar
        logger.debug("viz_panel_dataset_changed", dataset_id=dataset_id)
    
    # Handlers para drop de séries
    @pyqtSlot(str, str)
    def _on_series_dropped_2d(self, dataset_id: str, series_id: str):
        """Série dropada para gráfico 2D"""
        self._create_plot(dataset_id, series_id, "2d")
    
    @pyqtSlot(str, str)
    def _on_series_dropped_3d(self, dataset_id: str, series_id: str):
        """Série dropada para gráfico 3D"""
        self._create_plot(dataset_id, series_id, "3d")
    
    @pyqtSlot(str, str)
    def _on_series_dropped_heatmap(self, dataset_id: str, series_id: str):
        """Série dropada para heatmap"""
        self._create_plot(dataset_id, series_id, "heatmap")
    
    @pyqtSlot(str, str)
    def _on_series_dropped_scatter(self, dataset_id: str, series_id: str):
        """Série dropada para scatter plot"""
        self._create_plot(dataset_id, series_id, "scatter")
    
    def _create_plot(self, dataset_id: str, series_id: str, plot_type: str):
        """Cria novo gráfico"""
        try:
            # Get series data
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                return
            
            series = dataset.series[series_id]
            
            # Create plot widget (placeholder por enquanto)
            plot_widget = self._create_plot_widget(series, plot_type)
            
            # Add as new tab
            tab_title = f"{series.name} ({plot_type.upper()})"
            tab_index = self._viz_tabs.addTab(plot_widget, tab_title)
            self._viz_tabs.setCurrentIndex(tab_index)
            
            # Store plot info
            self._plots.append({
                'widget': plot_widget,
                'series': series,
                'type': plot_type,
                'tab_index': tab_index
            })
            
            logger.info("plot_created", 
                       series_id=series_id, 
                       plot_type=plot_type, 
                       tab_index=tab_index)
            
        except Exception as e:
            logger.error("plot_creation_failed", 
                        series_id=series_id, 
                        plot_type=plot_type, 
                        error=str(e))
    
    def _create_plot_widget(self, series, plot_type: str) -> QWidget:
        """Cria widget de gráfico REAL usando matplotlib"""
        try:
            # Criar widget matplotlib real
            plot_widget = MatplotlibWidget(series, plot_type)
            return plot_widget
            
        except Exception as e:
            logger.error("matplotlib_widget_creation_failed", error=str(e), plot_type=plot_type)
            
            # Fallback para widget de erro
            widget = QFrame()
            layout = QVBoxLayout(widget)
            
            content = QLabel(
                f"❌ Erro na Visualização\n\n"
                f"Série: {series.name}\n"
                f"Tipo: {plot_type.upper()}\n"
                f"Erro: {str(e)}\n\n"
                "Verifique se matplotlib está instalado corretamente."
            )
            content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content.setStyleSheet("""
                background-color: #ffe6e6;
                border: 2px solid #dc3545;
                border-radius: 8px;
                padding: 24px;
                color: #dc3545;
                font-size: 12px;
                line-height: 1.4;
            """)
            
            layout.addWidget(content)
            return widget
    
    @pyqtSlot(int)
    def _close_tab(self, index: int):
        """Fecha tab de visualização"""
        if index == 0:  # Não fechar a tab principal
            return
        
        # Remove from plots list
        plot_to_remove = None
        for plot in self._plots:
            if plot['tab_index'] == index:
                plot_to_remove = plot
                break
        
        if plot_to_remove:
            self._plots.remove(plot_to_remove)
        
        # Remove tab
        self._viz_tabs.removeTab(index)
        
        # Update tab indices
        for plot in self._plots:
            if plot['tab_index'] > index:
                plot['tab_index'] -= 1
        
        logger.debug("plot_tab_closed", index=index)
    
    # Public methods para toolbar
    def create_2d_plot(self):
        """Cria novo gráfico 2D vazio"""
        # Por enquanto, apenas foca na tab de drop
        self._viz_tabs.setCurrentIndex(0)
        logger.debug("2d_plot_creation_requested")
    
    def create_3d_plot(self):
        """Cria novo gráfico 3D vazio"""
        # Por enquanto, apenas foca na tab de drop
        self._viz_tabs.setCurrentIndex(0)
        logger.debug("3d_plot_creation_requested")


# Alias para compatibilidade
VizPanel = ModernVizPanel