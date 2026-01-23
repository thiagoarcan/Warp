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


class DraggableSeriesTree(QWidget):
    """Tree widget que permite drag de séries"""
    
    def __init__(self, data_panel):
        super().__init__()
        self.data_panel = data_panel
        
        # Enable drag
        if hasattr(data_panel, '_series_tree'):
            data_panel._series_tree.setDragEnabled(True)
            data_panel._series_tree.setDragDropMode(data_panel._series_tree.DragDropMode.DragOnly)


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
    
    def _create_drop_zones_tab(self):\n        \"\"\"Cria tab com zonas de drop para criar gráficos\"\"\"\n        drop_widget = QWidget()\n        drop_layout = QVBoxLayout(drop_widget)\n        drop_layout.setContentsMargins(16, 16, 16, 16)\n        drop_layout.setSpacing(12)\n        \n        # Instruções\n        instructions = QLabel(\n            \"🎯 <b>Como criar gráficos:</b><br>\"\n            \"1. Clique com botão direito em uma série no painel de dados<br>\"\n            \"2. Ou arraste a série para uma das zonas abaixo\"\n        )\n        instructions.setStyleSheet(\"\"\"\n            background-color: #e3f2fd;\n            border: 1px solid #90caf9;\n            border-radius: 6px;\n            padding: 12px;\n            color: #1565c0;\n            font-size: 12px;\n        \"\"\")\n        instructions.setWordWrap(True)\n        drop_layout.addWidget(instructions)\n        \n        # Grid de zonas de drop\n        zones_frame = QFrame()\n        zones_layout = QGridLayout(zones_frame)\n        zones_layout.setSpacing(16)\n        \n        # Zona 2D\n        zone_2d = DropZone(\n            \"📊 Gráfico 2D\",\n            \"Arraste série aqui para\\ncriar gráfico de linha 2D\",\n            \"2d\"\n        )\n        zone_2d.series_dropped.connect(self._on_series_dropped_2d)\n        zones_layout.addWidget(zone_2d, 0, 0)\n        \n        # Zona 3D\n        zone_3d = DropZone(\n            \"📈 Gráfico 3D\",\n            \"Arraste série aqui para\\ncriar visualização 3D\",\n            \"3d\"\n        )\n        zone_3d.series_dropped.connect(self._on_series_dropped_3d)\n        zones_layout.addWidget(zone_3d, 0, 1)\n        \n        # Zona Heatmap\n        zone_heatmap = DropZone(\n            \"🔥 Heatmap\",\n            \"Arraste série aqui para\\ncriar mapa de calor\",\n            \"heatmap\"\n        )\n        zone_heatmap.series_dropped.connect(self._on_series_dropped_heatmap)\n        zones_layout.addWidget(zone_heatmap, 1, 0)\n        \n        # Zona Scatter\n        zone_scatter = DropZone(\n            \"🔵 Scatter Plot\",\n            \"Arraste série aqui para\\ncriar gráfico de dispersão\",\n            \"scatter\"\n        )\n        zone_scatter.series_dropped.connect(self._on_series_dropped_scatter)\n        zones_layout.addWidget(zone_scatter, 1, 1)\n        \n        drop_layout.addWidget(zones_frame)\n        drop_layout.addStretch()\n        \n        self._viz_tabs.addTab(drop_widget, \"➕ Nova Visualização\")\n    \n    def _setup_connections(self):\n        \"\"\"Configuração de conexões\"\"\"\n        # Session state connections\n        self.session_state.dataset_changed.connect(self._on_dataset_changed)\n    \n    @pyqtSlot(str)\n    def _on_dataset_changed(self, dataset_id: str):\n        \"\"\"Handler para mudança de dataset\"\"\"\n        # Update UI quando dataset mudar\n        logger.debug(\"viz_panel_dataset_changed\", dataset_id=dataset_id)\n    \n    # Handlers para drop de séries\n    @pyqtSlot(str, str)\n    def _on_series_dropped_2d(self, dataset_id: str, series_id: str):\n        \"\"\"Série dropada para gráfico 2D\"\"\"\n        self._create_plot(dataset_id, series_id, \"2d\")\n    \n    @pyqtSlot(str, str)\n    def _on_series_dropped_3d(self, dataset_id: str, series_id: str):\n        \"\"\"Série dropada para gráfico 3D\"\"\"\n        self._create_plot(dataset_id, series_id, \"3d\")\n    \n    @pyqtSlot(str, str)\n    def _on_series_dropped_heatmap(self, dataset_id: str, series_id: str):\n        \"\"\"Série dropada para heatmap\"\"\"\n        self._create_plot(dataset_id, series_id, \"heatmap\")\n    \n    @pyqtSlot(str, str)\n    def _on_series_dropped_scatter(self, dataset_id: str, series_id: str):\n        \"\"\"Série dropada para scatter plot\"\"\"\n        self._create_plot(dataset_id, series_id, \"scatter\")\n    \n    def _create_plot(self, dataset_id: str, series_id: str, plot_type: str):\n        \"\"\"Cria novo gráfico\"\"\"\n        try:\n            # Get series data\n            dataset = self.session_state.get_dataset(dataset_id)\n            if not dataset or series_id not in dataset.series:\n                return\n            \n            series = dataset.series[series_id]\n            \n            # Create plot widget (placeholder por enquanto)\n            plot_widget = self._create_plot_widget(series, plot_type)\n            \n            # Add as new tab\n            tab_title = f\"{series.name} ({plot_type.upper()})\"\n            tab_index = self._viz_tabs.addTab(plot_widget, tab_title)\n            self._viz_tabs.setCurrentIndex(tab_index)\n            \n            # Store plot info\n            self._plots.append({\n                'widget': plot_widget,\n                'series': series,\n                'type': plot_type,\n                'tab_index': tab_index\n            })\n            \n            logger.info(\"plot_created\", \n                       series_id=series_id, \n                       plot_type=plot_type, \n                       tab_index=tab_index)\n            \n        except Exception as e:\n            logger.error(\"plot_creation_failed\", \n                        series_id=series_id, \n                        plot_type=plot_type, \n                        error=str(e))\n    \n    def _create_plot_widget(self, series, plot_type: str) -> QWidget:\n        \"\"\"Cria widget de gráfico (placeholder)\"\"\"\n        widget = QFrame()\n        layout = QVBoxLayout(widget)\n        \n        # Placeholder content\n        content = QLabel(\n            f\"📊 Gráfico {plot_type.upper()}\\n\\n\"\n            f\"Série: {series.name}\\n\"\n            f\"Pontos: {len(series.values):,}\\n\"\n            f\"Unidade: {series.unit}\\n\\n\"\n            \"🚧 Integração com pyqtgraph/PyVista\\nem desenvolvimento\"\n        )\n        content.setAlignment(Qt.AlignmentFlag.AlignCenter)\n        content.setStyleSheet(\"\"\"\n            background-color: #f8f9fa;\n            border: 2px dashed #ced4da;\n            border-radius: 8px;\n            padding: 24px;\n            color: #6c757d;\n            font-size: 12px;\n            line-height: 1.4;\n        \"\"\")\n        \n        layout.addWidget(content)\n        \n        return widget\n    \n    @pyqtSlot(int)\n    def _close_tab(self, index: int):\n        \"\"\"Fecha tab de visualização\"\"\"\n        if index == 0:  # Não fechar a tab principal\n            return\n        \n        # Remove from plots list\n        plot_to_remove = None\n        for plot in self._plots:\n            if plot['tab_index'] == index:\n                plot_to_remove = plot\n                break\n        \n        if plot_to_remove:\n            self._plots.remove(plot_to_remove)\n        \n        # Remove tab\n        self._viz_tabs.removeTab(index)\n        \n        # Update tab indices\n        for plot in self._plots:\n            if plot['tab_index'] > index:\n                plot['tab_index'] -= 1\n        \n        logger.debug(\"plot_tab_closed\", index=index)\n    \n    # Public methods para toolbar\n    def create_2d_plot(self):\n        \"\"\"Cria novo gráfico 2D vazio\"\"\"\n        # Por enquanto, apenas foca na tab de drop\n        self._viz_tabs.setCurrentIndex(0)\n        logger.debug(\"2d_plot_creation_requested\")\n    \n    def create_3d_plot(self):\n        \"\"\"Cria novo gráfico 3D vazio\"\"\"\n        # Por enquanto, apenas foca na tab de drop\n        self._viz_tabs.setCurrentIndex(0)\n        logger.debug(\"3d_plot_creation_requested\")\n\n\n# Alias para compatibilidade\nVizPanel = ModernVizPanel