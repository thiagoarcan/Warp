"""
Enhanced VizPanel with Multi-Canvas Support and Comprehensive Features
Original implementation for Platform Base v2.0
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from pathlib import Path

import numpy as np
import pandas as pd
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QToolBar, QFileDialog, QMessageBox, QLabel
)

from platform_base.viz.multi_canvas_plot import MultiCanvasPlotWidget, IndependentPlotCanvas
from platform_base.viz.comprehensive_context_menu import ComprehensiveContextMenu
from platform_base.viz.computation_engine import ComputationEngine
from platform_base.viz.hue_coordinator import get_hue_coordinator
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub

logger = get_logger(__name__)


class EnhancedVizPanel(QWidget):
    """
    Enhanced visualization panel with:
    - Multi-canvas support (up to 4 plots per tab)
    - Comprehensive context menu with calculations
    - DateTime X-axis support
    - Global color coordination
    - Responsive design for ultrawide monitors
    """
    
    def __init__(self, session_state: SessionState, signal_hub: SignalHub, parent=None):
        super().__init__(parent)
        
        self.session_state = session_state
        self.signal_hub = signal_hub
        self.hue_coordinator = get_hue_coordinator()
        self.computation_engine = ComputationEngine()
        
        # Tab management
        self.tab_counter = 0
        self.active_tabs: Dict[int, MultiCanvasPlotWidget] = {}
        
        # Series tracking
        self.series_data_cache: Dict[str, Dict[str, np.ndarray]] = {}
        self.calculated_series: Dict[str, Dict[str, Any]] = {}
        
        self._build_interface()
        self._connect_internal_signals()
        
        logger.info("EnhancedVizPanel initialized with multi-canvas support")
        
    def _build_interface(self):
        """Build the panel interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Toolbar
        toolbar = self._create_toolbar()
        layout.addLayout(toolbar)
        
        # Main tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        layout.addWidget(self.tab_widget)
        
        # Add initial tab
        self._add_new_tab()
        
    def _create_toolbar(self) -> QHBoxLayout:
        """Create toolbar with controls"""
        toolbar = QHBoxLayout()
        
        self.add_tab_btn = QPushButton("➕ Nova Aba")
        self.add_tab_btn.clicked.connect(self._add_new_tab)
        self.add_tab_btn.setToolTip("Adicionar nova aba de visualização")
        toolbar.addWidget(self.add_tab_btn)
        
        self.datetime_axis_btn = QPushButton("📅 Eixo DateTime")
        self.datetime_axis_btn.setCheckable(True)
        self.datetime_axis_btn.clicked.connect(self._toggle_datetime_axis)
        self.datetime_axis_btn.setToolTip("Ativar formato de data/hora no eixo X")
        toolbar.addWidget(self.datetime_axis_btn)
        
        self.export_all_btn = QPushButton("💾 Exportar Tudo")
        self.export_all_btn.clicked.connect(self._export_all_data)
        self.export_all_btn.setToolTip("Exportar todos os dados e cálculos")
        toolbar.addWidget(self.export_all_btn)
        
        toolbar.addStretch()
        
        self.status_label = QLabel("Pronto")
        toolbar.addWidget(self.status_label)
        
        return toolbar
        
    def _add_new_tab(self):
        """Add new tab with multi-canvas widget"""
        self.tab_counter += 1
        tab_id = self.tab_counter
        
        # Create multi-canvas widget
        multi_canvas = MultiCanvasPlotWidget()
        
        # Setup context menus for all canvases
        for canvas in multi_canvas.get_all_canvases():
            self._setup_canvas_context_menu(canvas)
        
        # Listen for new canvases
        multi_canvas.canvas_added.connect(
            lambda cid: self._setup_canvas_context_menu(
                multi_canvas.get_canvas(cid)
            )
        )
        
        # Add tab
        tab_name = f"Visualização {tab_id}"
        self.tab_widget.addTab(multi_canvas, tab_name)
        self.tab_widget.setCurrentWidget(multi_canvas)
        
        # Store reference
        self.active_tabs[tab_id] = multi_canvas
        
        logger.debug(f"New tab added: {tab_name}")
        
    def _close_tab(self, index: int):
        """Close tab at index"""
        if self.tab_widget.count() <= 1:
            QMessageBox.warning(self, "Aviso", "Não é possível fechar a última aba")
            return
            
        # Find tab_id
        widget = self.tab_widget.widget(index)
        tab_id_to_remove = None
        
        for tab_id, tab_widget in self.active_tabs.items():
            if tab_widget == widget:
                tab_id_to_remove = tab_id
                break
                
        if tab_id_to_remove:
            del self.active_tabs[tab_id_to_remove]
            
        self.tab_widget.removeTab(index)
        
    def _setup_canvas_context_menu(self, canvas: IndependentPlotCanvas):
        """Setup comprehensive context menu for a canvas"""
        context_menu = ComprehensiveContextMenu(
            self.session_state, self.signal_hub, canvas
        )
        
        # Connect signals
        context_menu.calculation_requested.connect(
            lambda sid, ctype, params: self._handle_calculation_request(
                canvas, sid, ctype, params
            )
        )
        
        context_menu.series_property_changed.connect(
            lambda sid, prop, val: self._handle_series_property_change(
                canvas, sid, prop, val
            )
        )
        
        context_menu.export_requested.connect(
            lambda sid, fmt: self._handle_export_request(canvas, sid, fmt)
        )
        
        # Store menu reference
        canvas.context_menu = context_menu
        
        # Connect context menu trigger
        canvas.context_menu_requested.connect(
            lambda event, series_id: self._show_context_menu(
                canvas, event, series_id
            )
        )
        
    def _show_context_menu(self, canvas: IndependentPlotCanvas, event, series_id: str):
        """Show context menu for series"""
        if not hasattr(canvas, 'context_menu'):
            return
            
        # Get available series for this canvas
        available_series = canvas._series_registry
        
        canvas.context_menu.show_for_series(series_id, available_series)
        canvas.context_menu.exec(event.screenPos().toPoint())
        
    def _handle_calculation_request(self, canvas: IndependentPlotCanvas,
                                   series_id: str, calc_type: str, params: Dict):
        """Handle calculation request from context menu"""
        logger.info(f"Calculation requested: {calc_type} for {series_id}")
        
        # Get series data
        if series_id not in canvas._series_registry:
            logger.error(f"Series {series_id} not found in canvas")
            return
            
        series_info = canvas._series_registry[series_id]
        x_data = series_info['x_data']
        y_data = series_info['y_data']
        
        try:
            if calc_type == "derivative":
                self._calculate_derivative(canvas, series_id, x_data, y_data, params)
                
            elif calc_type == "area_under_curve":
                self._calculate_area_under_curve(canvas, series_id, x_data, y_data)
                
            elif calc_type == "area_between_curves":
                self._calculate_area_between_curves(canvas, series_id, params)
                
            elif calc_type == "statistics":
                self._calculate_statistics(canvas, series_id, y_data, params)
                
            elif calc_type == "std_bands":
                self._calculate_std_bands(canvas, series_id, x_data, y_data, params)
                
            elif calc_type == "trend":
                self._calculate_trend(canvas, series_id, x_data, y_data, params)
                
            elif calc_type == "regression":
                self._calculate_regression(canvas, series_id, x_data, y_data, params)
                
            elif calc_type == "interpolation":
                self._calculate_interpolation(canvas, series_id, x_data, y_data, params)
                
            elif calc_type == "rate_of_change":
                self._calculate_rate_of_change(canvas, series_id, x_data, y_data, params)
                
            elif calc_type == "annotate":
                self._add_annotation(canvas, series_id, params)
                
            self.status_label.setText(f"Cálculo concluído: {calc_type}")
            
        except Exception as e:
            logger.exception(f"Calculation failed: {calc_type}", error=str(e))
            QMessageBox.critical(self, "Erro", f"Falha no cálculo: {str(e)}")
            
    def _calculate_derivative(self, canvas, series_id, x_data, y_data, params):
        """Calculate derivative"""
        order = params.get('order', 1)
        apply_smooth = params.get('smoothing', False)
        smooth_window = params.get('smooth_window', 5)
        
        new_x, new_y = self.computation_engine.compute_derivative(
            x_data, y_data, order, apply_smooth, smooth_window
        )
        
        # Create new series
        new_series_id = f"{series_id}_deriv{order}"
        new_series_name = f"{series_id} - Derivada {order}"
        
        canvas.add_series_to_canvas(new_series_id, new_x, new_y, new_series_name)
        
        # Store calculation info
        self.calculated_series[new_series_id] = {
            'source': series_id,
            'type': 'derivative',
            'params': params,
            'x_data': new_x,
            'y_data': new_y
        }
        
    def _calculate_area_under_curve(self, canvas, series_id, x_data, y_data):
        """Calculate area under curve"""
        area = self.computation_engine.compute_area_under_curve(x_data, y_data)
        
        msg = f"Área sob a curva '{series_id}':\n{area:.6f}"
        QMessageBox.information(self, "Área sob a curva", msg)
        
        # Store result
        self.calculated_series[f"{series_id}_area"] = {
            'source': series_id,
            'type': 'area',
            'value': area
        }
        
    def _calculate_area_between_curves(self, canvas, series_id, params):
        """Calculate area between two curves"""
        second_curve_id = params.get('second_curve', '')
        
        if second_curve_id not in canvas._series_registry:
            QMessageBox.warning(self, "Erro", f"Curva '{second_curve_id}' não encontrada")
            return
            
        series1 = canvas._series_registry[series_id]
        series2 = canvas._series_registry[second_curve_id]
        
        area = self.computation_engine.compute_area_between_curves(
            series1['x_data'], series1['y_data'],
            series2['x_data'], series2['y_data']
        )
        
        msg = f"Área entre '{series_id}' e '{second_curve_id}':\n{area:.6f}"
        QMessageBox.information(self, "Área entre curvas", msg)
        
        # Store result
        result_id = f"{series_id}_vs_{second_curve_id}_area"
        self.calculated_series[result_id] = {
            'source': [series_id, second_curve_id],
            'type': 'area_between',
            'value': area
        }
        
    def _calculate_statistics(self, canvas, series_id, y_data, params):
        """Calculate statistics"""
        stat_type = params.get('stat_type', 'all')
        
        stats = self.computation_engine.compute_statistics(y_data)
        
        if stat_type == 'all':
            msg = f"Estatísticas para '{series_id}':\n"
            msg += f"Média: {stats['mean']:.6f}\n"
            msg += f"Mediana: {stats['median']:.6f}\n"
            msg += f"Moda: {stats['mode']:.6f}\n"
            msg += f"Mínimo: {stats['min']:.6f}\n"
            msg += f"Máximo: {stats['max']:.6f}\n"
            msg += f"Desvio Padrão: {stats['std']:.6f}\n"
            msg += f"Variância: {stats['variance']:.6f}"
        else:
            value = stats.get(stat_type, 'N/A')
            msg = f"{stat_type.capitalize()} de '{series_id}': {value:.6f}"
            
        QMessageBox.information(self, "Estatísticas", msg)
        
        # Store results
        self.calculated_series[f"{series_id}_stats"] = {
            'source': series_id,
            'type': 'statistics',
            'values': stats
        }
        
    def _calculate_std_bands(self, canvas, series_id, x_data, y_data, params):
        """Calculate standard deviation bands"""
        multiplier = params.get('multiplier', 1.0)
        
        bands = self.computation_engine.compute_std_deviation_bands(y_data, multiplier)
        
        # Add mean line
        mean_id = f"{series_id}_mean"
        canvas.add_series_to_canvas(mean_id, x_data, bands['mean'], f"{series_id} - Média")
        
        # Add upper band
        upper_id = f"{series_id}_std+{multiplier}"
        canvas.add_series_to_canvas(upper_id, x_data, bands['upper_band'],
                                   f"{series_id} - +{multiplier}σ")
        
        # Add lower band
        lower_id = f"{series_id}_std-{multiplier}"
        canvas.add_series_to_canvas(lower_id, x_data, bands['lower_band'],
                                   f"{series_id} - -{multiplier}σ")
        
    def _calculate_trend(self, canvas, series_id, x_data, y_data, params):
        """Calculate trend line"""
        degree = params.get('degree', 1)
        
        trend_x, trend_y = self.computation_engine.compute_trend_line(
            x_data, y_data, degree
        )
        
        new_series_id = f"{series_id}_trend{degree}"
        new_series_name = f"{series_id} - Tendência (grau {degree})"
        
        canvas.add_series_to_canvas(new_series_id, trend_x, trend_y, new_series_name)
        
    def _calculate_regression(self, canvas, series_id, x_data, y_data, params):
        """Calculate regression"""
        reg_type = params.get('regression_type', 'Linear').lower()
        poly_order = params.get('poly_order', 2)
        
        reg_x, reg_y = self.computation_engine.compute_regression(
            x_data, y_data, reg_type, poly_order
        )
        
        new_series_id = f"{series_id}_reg_{reg_type}"
        new_series_name = f"{series_id} - Regressão {reg_type.capitalize()}"
        
        canvas.add_series_to_canvas(new_series_id, reg_x, reg_y, new_series_name)
        
    def _calculate_interpolation(self, canvas, series_id, x_data, y_data, params):
        """Calculate interpolation"""
        interp_type = params.get('interp_type', 'Linear').lower()
        interval = params.get('interval', 15.0)
        
        interp_x, interp_y = self.computation_engine.compute_interpolation(
            x_data, y_data, interval, interp_type
        )
        
        new_series_id = f"{series_id}_interp_{interp_type}"
        new_series_name = f"{series_id} - Interpolação {interp_type.capitalize()}"
        
        canvas.add_series_to_canvas(new_series_id, interp_x, interp_y, new_series_name)
        
    def _calculate_rate_of_change(self, canvas, series_id, x_data, y_data, params):
        """Calculate rate of change"""
        window = params.get('window', 1)
        
        roc_x, roc_y = self.computation_engine.compute_rate_of_change(
            x_data, y_data, window
        )
        
        new_series_id = f"{series_id}_roc"
        new_series_name = f"{series_id} - Taxa de Variação"
        
        canvas.add_series_to_canvas(new_series_id, roc_x, roc_y, new_series_name)
        
    def _add_annotation(self, canvas, series_id, params):
        """Add annotation to canvas"""
        comment = params.get('comment', '')
        x_coord = params.get('x_coord', 0)
        y_coord = params.get('y_coord', 0)
        
        # Create text annotation
        from pyqtgraph import TextItem
        
        text_item = TextItem(comment, anchor=(0.5, 1))
        text_item.setPos(x_coord, y_coord)
        canvas.addItem(text_item)
        
        logger.info(f"Annotation added at ({x_coord}, {y_coord}): {comment}")
        
    def _handle_series_property_change(self, canvas, series_id, property_name, value):
        """Handle series property changes"""
        if series_id not in canvas._series_registry:
            return
            
        if property_name == "remove":
            canvas.remove_series_from_canvas(series_id)
            
        elif property_name == "axis":
            # Move to different axis
            logger.info(f"Moving {series_id} to axis {value}")
            
        elif property_name == "create_axis":
            canvas.create_secondary_y_axis()
            
        elif property_name == "line_style":
            series_info = canvas._series_registry[series_id]
            curve = series_info['curve_item']
            pen = curve.opts['pen']
            pen.setStyle(value)
            curve.setPen(pen)
            
        elif property_name == "line_width":
            series_info = canvas._series_registry[series_id]
            curve = series_info['curve_item']
            pen = curve.opts['pen']
            pen.setWidth(value)
            curve.setPen(pen)
            
    def _handle_export_request(self, canvas, series_id, format_type):
        """Handle export request"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Dados",
            f"{series_id}.{format_type}",
            f"Arquivos {format_type.upper()} (*.{format_type})"
        )
        
        if not file_path:
            return
            
        try:
            self._export_series_data(canvas, series_id, file_path, format_type)
            QMessageBox.information(self, "Sucesso", f"Dados exportados para {file_path}")
        except Exception as e:
            logger.exception("Export failed", error=str(e))
            QMessageBox.critical(self, "Erro", f"Falha na exportação: {str(e)}")
            
    def _export_series_data(self, canvas, series_id, file_path, format_type):
        """Export series data to file"""
        series_info = canvas._series_registry[series_id]
        x_data = series_info['x_data']
        y_data = series_info['y_data']
        
        df = pd.DataFrame({
            'tempo': x_data,
            'valor': y_data
        })
        
        if format_type == 'xlsx' or format_type == 'xlsx_annotated':
            df.to_excel(file_path, index=False)
        elif format_type == 'csv':
            df.to_csv(file_path, index=False)
            
    def _toggle_datetime_axis(self, checked: bool):
        """Toggle datetime axis for all canvases"""
        for tab_widget in self.active_tabs.values():
            for canvas in tab_widget.get_all_canvases():
                canvas.set_datetime_x_axis(checked)
                
        self.status_label.setText(
            "Eixo DateTime ativado" if checked else "Eixo numérico ativado"
        )
        
    def _export_all_data(self):
        """Export all series and calculations"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Todos os Dados",
            "export_completo.xlsx",
            "Arquivos Excel (*.xlsx)"
        )
        
        if not file_path:
            return
            
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                sheet_counter = 0
                
                # Export all series from all canvases
                for tab_id, tab_widget in self.active_tabs.items():
                    for canvas in tab_widget.get_all_canvases():
                        for series_id, series_info in canvas._series_registry.items():
                            df = pd.DataFrame({
                                'tempo': series_info['x_data'],
                                'valor': series_info['y_data']
                            })
                            
                            sheet_name = f"{series_id[:25]}"  # Excel limit is 31 chars
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                            sheet_counter += 1
                            
                # Export calculated results
                if self.calculated_series:
                    results_data = []
                    for calc_id, calc_info in self.calculated_series.items():
                        if calc_info['type'] in ['area', 'area_between']:
                            results_data.append({
                                'id': calc_id,
                                'tipo': calc_info['type'],
                                'valor': calc_info['value']
                            })
                            
                    if results_data:
                        df_results = pd.DataFrame(results_data)
                        df_results.to_excel(writer, sheet_name='Resultados', index=False)
                        
            QMessageBox.information(
                self, "Sucesso",
                f"Dados exportados com sucesso!\n{sheet_counter} séries exportadas."
            )
            
        except Exception as e:
            logger.exception("Export all failed", error=str(e))
            QMessageBox.critical(self, "Erro", f"Falha na exportação: {str(e)}")
            
    def _connect_internal_signals(self):
        """Connect internal signals"""
        if self.signal_hub:
            self.signal_hub.series_selected.connect(self._on_series_selected)
            
    @pyqtSlot(str, str)
    def _on_series_selected(self, dataset_id: str, series_id: str):
        """Handle series selection from data panel"""
        # Get current tab's first canvas
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, MultiCanvasPlotWidget):
            canvases = current_widget.get_all_canvases()
            if canvases:
                canvas = canvases[0]
                
                # Load and plot series
                self._load_and_plot_series(canvas, dataset_id, series_id)
                
    def _load_and_plot_series(self, canvas: IndependentPlotCanvas,
                              dataset_id: str, series_id: str):
        """Load series data and plot it"""
        # Get data from session state
        dataset = self.session_state.dataset_store.get_dataset(dataset_id)
        if not dataset:
            logger.warning(f"Dataset {dataset_id} not found")
            return
            
        # Extract time and value data
        # This depends on your dataset structure
        # Placeholder implementation:
        x_data = np.arange(100)
        y_data = np.random.randn(100)
        
        # Plot on canvas
        full_series_id = f"{dataset_id}_{series_id}"
        canvas.add_series_to_canvas(full_series_id, x_data, y_data, series_id)
        
        # Cache data
        self.series_data_cache[full_series_id] = {
            'x_data': x_data,
            'y_data': y_data,
            'dataset_id': dataset_id,
            'series_id': series_id
        }
        
        logger.info(f"Series plotted: {full_series_id}")
