"""
Comprehensive Context Menu System for Plot Interactions
Original implementation for Platform Base v2.0
"""

from typing import TYPE_CHECKING, Optional, Dict, Any
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QMenu, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QLabel,
    QCheckBox, QLineEdit, QTextEdit, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QAction

import numpy as np

from platform_base.viz.computation_engine import ComputationEngine
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.desktop.session_state import SessionState
    from platform_base.desktop.signal_hub import SignalHub

logger = get_logger(__name__)


class CalculationDialog(QDialog):
    """Dialog for configuring calculation parameters"""
    
    calculation_confirmed = pyqtSignal(dict)  # parameters dict
    
    def __init__(self, calc_type: str, parent=None):
        super().__init__(parent)
        self.calc_type = calc_type
        self.setWindowTitle(f"Configurar {calc_type}")
        self.setModal(True)
        self.resize(400, 300)
        
        self._build_ui()
        
    def _build_ui(self):
        """Build dialog UI based on calculation type"""
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.param_widgets = {}
        
        if self.calc_type == "Derivada":
            # Order selector
            order_spin = QSpinBox()
            order_spin.setRange(1, 3)
            order_spin.setValue(1)
            form.addRow("Ordem:", order_spin)
            self.param_widgets['order'] = order_spin
            
            # Smoothing option
            smooth_check = QCheckBox("Aplicar suavização")
            form.addRow("", smooth_check)
            self.param_widgets['smoothing'] = smooth_check
            
            smooth_window = QSpinBox()
            smooth_window.setRange(3, 51)
            smooth_window.setValue(5)
            smooth_window.setSingleStep(2)
            form.addRow("Janela de suavização:", smooth_window)
            self.param_widgets['smooth_window'] = smooth_window
            
        elif self.calc_type == "Regressão":
            # Regression type
            regress_combo = QComboBox()
            regress_combo.addItems([
                "Linear", "Polinomial", "Exponencial",
                "Logarítmica", "Potência"
            ])
            form.addRow("Tipo:", regress_combo)
            self.param_widgets['regression_type'] = regress_combo
            
            # Polynomial order (for polynomial regression)
            poly_order = QSpinBox()
            poly_order.setRange(2, 10)
            poly_order.setValue(2)
            form.addRow("Ordem do polinômio:", poly_order)
            self.param_widgets['poly_order'] = poly_order
            
        elif self.calc_type == "Interpolação":
            # Interpolation type
            interp_combo = QComboBox()
            interp_combo.addItems([
                "Linear", "Cúbica", "Quadrática",
                "Mais próximo", "Spline linear"
            ])
            form.addRow("Tipo:", interp_combo)
            self.param_widgets['interp_type'] = interp_combo
            
            # Target interval
            interval_spin = QDoubleSpinBox()
            interval_spin.setRange(0.1, 3600)
            interval_spin.setValue(15.0)
            interval_spin.setSuffix(" s")
            form.addRow("Intervalo alvo:", interval_spin)
            self.param_widgets['interval'] = interval_spin
            
        elif self.calc_type == "Desvio Padrão":
            # Multiplier
            mult_spin = QDoubleSpinBox()
            mult_spin.setRange(0.5, 5.0)
            mult_spin.setValue(1.0)
            mult_spin.setSingleStep(0.5)
            form.addRow("Multiplicador:", mult_spin)
            self.param_widgets['multiplier'] = mult_spin
            
        elif self.calc_type == "Taxa de Variação":
            # Window size
            window_spin = QSpinBox()
            window_spin.setRange(1, 50)
            window_spin.setValue(1)
            form.addRow("Tamanho da janela:", window_spin)
            self.param_widgets['window'] = window_spin
            
        elif self.calc_type == "Área Entre Curvas":
            # Second curve selector (populated externally)
            curve_combo = QComboBox()
            form.addRow("Segunda curva:", curve_combo)
            self.param_widgets['second_curve'] = curve_combo
            
        elif self.calc_type == "Anotar Ponto":
            # Annotation text
            text_edit = QTextEdit()
            text_edit.setMaximumHeight(100)
            form.addRow("Comentário:", text_edit)
            self.param_widgets['comment'] = text_edit
            
            # X coordinate
            x_spin = QDoubleSpinBox()
            x_spin.setRange(-1e10, 1e10)
            x_spin.setDecimals(4)
            form.addRow("Coordenada X:", x_spin)
            self.param_widgets['x_coord'] = x_spin
            
            # Y coordinate
            y_spin = QDoubleSpinBox()
            y_spin.setRange(-1e10, 1e10)
            y_spin.setDecimals(4)
            form.addRow("Coordenada Y:", y_spin)
            self.param_widgets['y_coord'] = y_spin
            
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        confirm_btn = QPushButton("Confirmar")
        confirm_btn.clicked.connect(self._on_confirm)
        button_layout.addWidget(confirm_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def _on_confirm(self):
        """Collect parameters and emit signal"""
        params = {'calc_type': self.calc_type}
        
        for key, widget in self.param_widgets.items():
            if isinstance(widget, QSpinBox):
                params[key] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                params[key] = widget.value()
            elif isinstance(widget, QComboBox):
                params[key] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                params[key] = widget.isChecked()
            elif isinstance(widget, QTextEdit):
                params[key] = widget.toPlainText()
                
        self.calculation_confirmed.emit(params)
        self.accept()
        
    def set_available_curves(self, curve_names: list):
        """Set available curves for selection (for area between curves)"""
        if 'second_curve' in self.param_widgets:
            combo = self.param_widgets['second_curve']
            combo.clear()
            combo.addItems(curve_names)


class ComprehensiveContextMenu(QMenu):
    """
    Comprehensive context menu for series with all required calculations
    """
    
    calculation_requested = pyqtSignal(str, str, dict)  # series_id, calc_type, params
    series_property_changed = pyqtSignal(str, str, object)  # series_id, property, value
    export_requested = pyqtSignal(str, str)  # series_id, format
    
    def __init__(self, session_state: 'SessionState', signal_hub: 'SignalHub', parent=None):
        super().__init__(parent)
        self.session_state = session_state
        self.signal_hub = signal_hub
        
        self.current_series_id: Optional[str] = None
        self.available_series: Dict[str, Any] = {}
        
        self._build_menu()
        
    def _build_menu(self):
        """Build comprehensive menu structure"""
        
        # Mathematical Operations Section
        math_menu = self.addMenu("📐 Operações Matemáticas")
        
        # Derivatives
        deriv_menu = math_menu.addMenu("Derivadas")
        for order in [1, 2, 3]:
            action = deriv_menu.addAction(f"{order}ª Derivada")
            action.triggered.connect(lambda checked, o=order: self._request_derivative(o))
        
        # Integrals
        integral_menu = math_menu.addMenu("Integrais")
        action = integral_menu.addAction("Área sob a curva")
        action.triggered.connect(self._request_area_under_curve)
        
        action = integral_menu.addAction("Área entre curvas...")
        action.triggered.connect(self._request_area_between_curves)
        
        # Statistics
        stats_menu = math_menu.addMenu("Estatísticas")
        
        stat_actions = [
            ("Média", "mean"),
            ("Mediana", "median"),
            ("Moda", "mode"),
            ("Mínimo", "min"),
            ("Máximo", "max"),
            ("Todas as estatísticas", "all")
        ]
        
        for label, stat_type in stat_actions:
            action = stats_menu.addAction(label)
            action.triggered.connect(lambda checked, s=stat_type: self._request_statistics(s))
        
        # Standard deviation
        std_menu = math_menu.addMenu("Desvio Padrão")
        for mult in [1.0, 1.5, 2.0, 2.5, 3.0]:
            action = std_menu.addAction(f"±{mult}σ")
            action.triggered.connect(lambda checked, m=mult: self._request_std_bands(m))
        
        # Trend and regression
        trend_menu = math_menu.addMenu("Tendência e Regressão")
        
        action = trend_menu.addAction("Linha de tendência linear")
        action.triggered.connect(lambda: self._request_trend(1))
        
        action = trend_menu.addAction("Linha de tendência polinomial...")
        action.triggered.connect(lambda: self._request_trend(2))
        
        trend_menu.addSeparator()
        
        regress_types = [
            ("Regressão Linear", "linear"),
            ("Regressão Polinomial...", "polynomial"),
            ("Regressão Exponencial", "exponential"),
            ("Regressão Logarítmica", "logarithmic"),
            ("Regressão de Potência", "power")
        ]
        
        for label, reg_type in regress_types:
            action = trend_menu.addAction(label)
            action.triggered.connect(lambda checked, r=reg_type: self._request_regression(r))
        
        # Interpolation
        interp_menu = math_menu.addMenu("Interpolação")
        
        interp_types = [
            ("Linear", "linear"),
            ("Cúbica", "cubic"),
            ("Quadrática", "quadratic"),
            ("Mais próximo", "nearest"),
            ("Spline", "slinear")
        ]
        
        for label, interp_type in interp_types:
            action = interp_menu.addAction(label)
            action.triggered.connect(lambda checked, i=interp_type: self._request_interpolation(i))
        
        # Rate of change
        action = math_menu.addAction("Taxa de variação")
        action.triggered.connect(self._request_rate_of_change)
        
        self.addSeparator()
        
        # Axis Management Section
        axis_menu = self.addMenu("📊 Eixos")
        
        action = axis_menu.addAction("Alternar para eixo primário")
        action.triggered.connect(lambda: self._change_axis(0))
        
        action = axis_menu.addAction("Alternar para eixo secundário")
        action.triggered.connect(lambda: self._change_axis(1))
        
        action = axis_menu.addAction("Criar novo eixo Y...")
        action.triggered.connect(self._create_new_y_axis)
        
        self.addSeparator()
        
        # Visual Properties Section
        visual_menu = self.addMenu("🎨 Propriedades Visuais")
        
        line_menu = visual_menu.addMenu("Estilo de linha")
        
        line_styles = [
            ("Sólida", Qt.PenStyle.SolidLine),
            ("Tracejada", Qt.PenStyle.DashLine),
            ("Pontilhada", Qt.PenStyle.DotLine),
            ("Traço-Ponto", Qt.PenStyle.DashDotLine)
        ]
        
        for label, style in line_styles:
            action = line_menu.addAction(label)
            action.triggered.connect(lambda checked, s=style: self._change_line_style(s))
        
        width_menu = visual_menu.addMenu("Espessura da linha")
        for width in [1, 2, 3, 4, 5]:
            action = width_menu.addAction(f"{width}px")
            action.triggered.connect(lambda checked, w=width: self._change_line_width(w))
        
        self.addSeparator()
        
        # Annotation Section
        action = self.addAction("📝 Anotar ponto...")
        action.triggered.connect(self._annotate_point)
        
        self.addSeparator()
        
        # Export Section
        export_menu = self.addMenu("💾 Exportar")
        
        export_formats = [
            ("Exportar para XLSX", "xlsx"),
            ("Exportar para CSV", "csv"),
            ("Exportar com anotações", "xlsx_annotated")
        ]
        
        for label, fmt in export_formats:
            action = export_menu.addAction(label)
            action.triggered.connect(lambda checked, f=fmt: self._export_series(f))
        
        self.addSeparator()
        
        # Remove action
        action = self.addAction("🗑️ Remover série")
        action.triggered.connect(self._remove_series)
        
    def show_for_series(self, series_id: str, available_series: Dict[str, Any]):
        """Show menu for specific series"""
        self.current_series_id = series_id
        self.available_series = available_series
        
    def _request_derivative(self, order: int):
        """Request derivative calculation"""
        if not self.current_series_id:
            return
            
        dialog = CalculationDialog("Derivada", self)
        if 'order' in dialog.param_widgets:
            dialog.param_widgets['order'].setValue(order)
            
        # Connect signal before exec
        dialog.calculation_confirmed.connect(
            lambda params: self.calculation_requested.emit(
                self.current_series_id, "derivative", params
            )
        )
        
        dialog.exec()
        
    def _request_area_under_curve(self):
        """Request area under curve calculation"""
        if not self.current_series_id:
            return
        self.calculation_requested.emit(self.current_series_id, "area_under_curve", {})
        
    def _request_area_between_curves(self):
        """Request area between curves calculation"""
        if not self.current_series_id:
            return
            
        dialog = CalculationDialog("Área Entre Curvas", self)
        
        # Populate available curves
        curve_names = [s for s in self.available_series.keys() if s != self.current_series_id]
        dialog.set_available_curves(curve_names)
        
        dialog.calculation_confirmed.connect(
            lambda params: self.calculation_requested.emit(
                self.current_series_id, "area_between_curves", params
            )
        )
        
        dialog.exec()
        
    def _request_statistics(self, stat_type: str):
        """Request statistical calculation"""
        if not self.current_series_id:
            return
        self.calculation_requested.emit(
            self.current_series_id, "statistics", {'stat_type': stat_type}
        )
        
    def _request_std_bands(self, multiplier: float):
        """Request standard deviation bands"""
        if not self.current_series_id:
            return
        self.calculation_requested.emit(
            self.current_series_id, "std_bands", {'multiplier': multiplier}
        )
        
    def _request_trend(self, degree: int):
        """Request trend line"""
        if not self.current_series_id:
            return
        self.calculation_requested.emit(
            self.current_series_id, "trend", {'degree': degree}
        )
        
    def _request_regression(self, regression_type: str):
        """Request regression calculation"""
        if not self.current_series_id:
            return
            
        if regression_type == "polynomial":
            dialog = CalculationDialog("Regressão", self)
            dialog.calculation_confirmed.connect(
                lambda params: self.calculation_requested.emit(
                    self.current_series_id, "regression", params
                )
            )
            dialog.exec()
        else:
            self.calculation_requested.emit(
                self.current_series_id, "regression",
                {'regression_type': regression_type, 'poly_order': 2}
            )
        
    def _request_interpolation(self, interp_type: str):
        """Request interpolation"""
        if not self.current_series_id:
            return
            
        dialog = CalculationDialog("Interpolação", self)
        if 'interp_type' in dialog.param_widgets:
            # Set default type
            combo = dialog.param_widgets['interp_type']
            idx = combo.findText(interp_type.capitalize())
            if idx >= 0:
                combo.setCurrentIndex(idx)
                
        dialog.calculation_confirmed.connect(
            lambda params: self.calculation_requested.emit(
                self.current_series_id, "interpolation", params
            )
        )
        
        dialog.exec()
        
    def _request_rate_of_change(self):
        """Request rate of change calculation"""
        if not self.current_series_id:
            return
            
        dialog = CalculationDialog("Taxa de Variação", self)
        dialog.calculation_confirmed.connect(
            lambda params: self.calculation_requested.emit(
                self.current_series_id, "rate_of_change", params
            )
        )
        dialog.exec()
        
    def _change_axis(self, axis_index: int):
        """Change series to different axis"""
        if not self.current_series_id:
            return
        self.series_property_changed.emit(self.current_series_id, "axis", axis_index)
        
    def _create_new_y_axis(self):
        """Create new Y axis"""
        if not self.current_series_id:
            return
        self.series_property_changed.emit(self.current_series_id, "create_axis", None)
        
    def _change_line_style(self, style):
        """Change line style"""
        if not self.current_series_id:
            return
        self.series_property_changed.emit(self.current_series_id, "line_style", style)
        
    def _change_line_width(self, width: int):
        """Change line width"""
        if not self.current_series_id:
            return
        self.series_property_changed.emit(self.current_series_id, "line_width", width)
        
    def _annotate_point(self):
        """Add annotation to point"""
        if not self.current_series_id:
            return
            
        dialog = CalculationDialog("Anotar Ponto", self)
        dialog.calculation_confirmed.connect(
            lambda params: self.calculation_requested.emit(
                self.current_series_id, "annotate", params
            )
        )
        dialog.exec()
        
    def _export_series(self, format_type: str):
        """Export series data"""
        if not self.current_series_id:
            return
        self.export_requested.emit(self.current_series_id, format_type)
        
    def _remove_series(self):
        """Remove series from plot"""
        if not self.current_series_id:
            return
        self.series_property_changed.emit(self.current_series_id, "remove", None)
