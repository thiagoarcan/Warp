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
    QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QRect
from PyQt6.QtGui import QPainter, QPen, QBrush, QFont, QColor

from platform_base.ui.state import SessionState
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


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
        
        # Estilo da zona de drop
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
        
        # Instruções
        instructions = QLabel(
            "🎯 <b>Como criar gráficos:</b><br>"
            "1. Clique com botão direito em uma série no painel de dados<br>"
            "2. Ou arraste a série para uma das zonas abaixo"
        )
        instructions.setStyleSheet("""
            background-color: #e3f2fd;
            border: 1px solid #90caf9;
            border-radius: 6px;
            padding: 12px;
            color: #1565c0;
            font-size: 12px;
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
        """Cria widget de gráfico (placeholder)"""
        widget = QFrame()
        layout = QVBoxLayout(widget)
        
        # Placeholder content
        content = QLabel(
            f"📊 Gráfico {plot_type.upper()}\n\n"
            f"Série: {series.name}\n"
            f"Pontos: {len(series.values):,}\n"
            f"Unidade: {series.unit}\n\n"
            "🚧 Integração com pyqtgraph/PyVista\nem desenvolvimento"
        )
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.setStyleSheet("""
            background-color: #f8f9fa;
            border: 2px dashed #ced4da;
            border-radius: 8px;
            padding: 24px;
            color: #6c757d;
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