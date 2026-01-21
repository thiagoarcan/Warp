from __future__ import annotations

from typing import Optional, Callable
import numpy as np

from PyQt6.QtWidgets import QMenu, QMessageBox, QFileDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from platform_base.ui.state import SessionState
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class PlotContextMenu(QMenu):
    """
    Menu contextual para plots PyQt6.
    
    Implementa ações conforme PRD seção 12.6:
    - Zoom/Pan/Reset
    - Seleção de região
    - Estatísticas
    - Filtros visuais
    - Exportação
    """
    
    def __init__(self, plot_widget, session_state: Optional[SessionState] = None, 
                 parent=None):
        super().__init__(parent)
        self.plot_widget = plot_widget
        self.session_state = session_state
        
        self._create_actions()
        logger.debug("plot_context_menu_initialized")
    
    def _create_actions(self):
        """Cria todas as ações do menu"""
        
        # ========== ZOOM/PAN ==========
        zoom_menu = self.addMenu("Zoom")
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("+")
        zoom_in_action.triggered.connect(self._zoom_in)
        zoom_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("-")
        zoom_out_action.triggered.connect(self._zoom_out)
        zoom_menu.addAction(zoom_out_action)
        
        reset_view_action = QAction("Reset View", self)
        reset_view_action.setShortcut("R")
        reset_view_action.triggered.connect(self._reset_view)
        zoom_menu.addAction(reset_view_action)
        
        self.addSeparator()
        
        # ========== SELEÇÃO ==========
        select_region_action = QAction("Select Region", self)
        select_region_action.triggered.connect(self._select_region)
        self.addAction(select_region_action)
        
        extract_action = QAction("Extract Selection", self)
        extract_action.triggered.connect(self._extract_selection)
        self.addAction(extract_action)
        
        self.addSeparator()
        
        # ========== ANÁLISE ==========
        stats_action = QAction("Statistics on Selection", self)
        stats_action.triggered.connect(self._show_stats)
        self.addAction(stats_action)
        
        compare_action = QAction("Compare Series...", self)
        compare_action.triggered.connect(self._compare_series)
        self.addAction(compare_action)
        
        self.addSeparator()
        
        # ========== FILTROS VISUAIS ==========
        filter_menu = self.addMenu("Visual Filters")
        
        hide_interp_action = QAction("Hide Interpolated Points", self, checkable=True)
        hide_interp_action.triggered.connect(self._toggle_hide_interpolated)
        filter_menu.addAction(hide_interp_action)
        
        smooth_action = QAction("Apply Visual Smoothing...", self)
        smooth_action.triggered.connect(self._apply_visual_smoothing)
        filter_menu.addAction(smooth_action)
        
        self.addSeparator()
        
        # ========== EXPORT ==========
        export_plot_action = QAction("Export Plot Image...", self)
        export_plot_action.triggered.connect(self._export_plot)
        self.addAction(export_plot_action)
        
        export_data_action = QAction("Export Selection Data...", self)
        export_data_action.triggered.connect(self._export_selection_data)
        self.addAction(export_data_action)
        
        self.addSeparator()
        
        # ========== ANOTAÇÕES ==========
        add_annotation_action = QAction("Add Annotation...", self)
        add_annotation_action.triggered.connect(self._add_annotation)
        self.addAction(add_annotation_action)
    
    # ========== HANDLERS ==========
    
    def _zoom_in(self):
        """Zoom in no plot"""
        if hasattr(self.plot_widget, 'plotItem'):
            vb = self.plot_widget.plotItem.vb
            vb.scaleBy((0.5, 0.5))
    
    def _zoom_out(self):
        """Zoom out no plot"""
        if hasattr(self.plot_widget, 'plotItem'):
            vb = self.plot_widget.plotItem.vb
            vb.scaleBy((2, 2))
    
    def _reset_view(self):
        """Reseta visualização"""
        if hasattr(self.plot_widget, 'autoRange'):
            self.plot_widget.autoRange()
    
    def _select_region(self):
        """Habilita seleção de região"""
        if hasattr(self.plot_widget, 'enable_selection'):
            self.plot_widget.enable_selection(True)
    
    def _extract_selection(self):
        """Extrai dados da seleção"""
        # TODO: Implementar extração de subsérie
        pass
    
    def _show_stats(self):
        """Mostra estatísticas da seleção"""
        if self.session_state and self.session_state.selection:
            view_data = self.session_state.get_current_view()
            if view_data:
                stats = {}
                for series_id, values in view_data.series.items():
                    stats[series_id] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values)
                    }
                
                msg = "\n".join(
                    f"{sid}: μ={s['mean']:.3f}, σ={s['std']:.3f}"
                    for sid, s in stats.items()
                )
                QMessageBox.information(self, "Statistics", msg)
            else:
                QMessageBox.warning(self, "Statistics", "No view data available")
        else:
            QMessageBox.warning(self, "Statistics", "No selection active")
    
    def _compare_series(self):
        """Abre diálogo de comparação"""
        pass
    
    def _toggle_hide_interpolated(self, checked: bool):
        """Alterna visibilidade de pontos interpolados"""
        pass
    
    def _apply_visual_smoothing(self):
        """Aplica suavização visual"""
        pass
    
    def _export_plot(self):
        """Exporta plot como imagem"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Plot", "",
            "PNG (*.png);;SVG (*.svg);;PDF (*.pdf)"
        )
        
        if path:
            if hasattr(self.plot_widget, 'export_image'):
                # Usa método do wrapper Plot2DWidget
                self.plot_widget.export_image(path)
            elif hasattr(self.plot_widget, 'plotItem'):
                # Fallback para pyqtgraph direto
                import pyqtgraph.exporters as exp
                exporter = exp.ImageExporter(self.plot_widget.plotItem)
                exporter.export(path)
    
    def _export_selection_data(self):
        """Exporta dados da seleção"""
        pass
    
    def _add_annotation(self):
        """Adiciona anotação"""
        pass
