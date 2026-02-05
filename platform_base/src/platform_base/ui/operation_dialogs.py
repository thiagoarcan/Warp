"""
Operation Dialogs - Diálogos avançados de configuração para operações

Features:
- Diálogos especializados para cada tipo de operação
- Configuração visual interativa
- Preview em tempo real
- Validação de parâmetros
- Presets e templates
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from platform_base.desktop.widgets.base import UiLoaderMixin
from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class ParameterWidget(QFrame):
    """Widget base para parâmetros configuráveis"""

    value_changed = pyqtSignal(str, object)  # parameter_name, value

    def __init__(self, name: str, description: str = "", parent: QWidget | None = None):
        super().__init__(parent)

        self.parameter_name = name
        self.description = description

        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)

        self._setup_base_ui()

    def _setup_base_ui(self):
        """Setup básico do widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        header_layout = QHBoxLayout()

        name_label = QLabel(self.parameter_name)
        name_label.setFont(QFont("", 9, QFont.Weight.Bold))
        header_layout.addWidget(name_label)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Description
        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: gray; font-size: 8pt;")
            layout.addWidget(desc_label)

        # Control widget (to be implemented by subclasses)
        self.control_widget = self._create_control()
        if self.control_widget:
            layout.addWidget(self.control_widget)

    def _create_control(self) -> QWidget | None:
        """Override para criar controle específico"""
        return None

    def get_value(self) -> Any:
        """Override para retornar valor atual"""
        return None

    def set_value(self, value: Any):
        """Override para definir valor"""

    def _emit_value_changed(self):
        """Emite sinal de mudança de valor"""
        self.value_changed.emit(self.parameter_name, self.get_value())


class NumericParameterWidget(ParameterWidget):
    """Widget para parâmetros numéricos"""

    def __init__(self, name: str, min_val: float = 0.0, max_val: float = 100.0,
                 step: float = 1.0, decimals: int = 0, default: float = 0.0,
                 description: str = "", parent: QWidget | None = None):

        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.decimals = decimals
        self.default = default

        super().__init__(name, description, parent)

        self.set_value(default)

    def _create_control(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Spinbox
        if self.decimals > 0:
            self.spinbox = QDoubleSpinBox()
            self.spinbox.setDecimals(self.decimals)
        else:
            self.spinbox = QSpinBox()

        self.spinbox.setRange(self.min_val, self.max_val)
        self.spinbox.setSingleStep(self.step)
        self.spinbox.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.spinbox)

        # Slider (for better UX)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)

        return widget

    def _on_value_changed(self):
        # Update slider position
        normalized = (self.spinbox.value() - self.min_val) / (self.max_val - self.min_val)
        self.slider.setValue(int(normalized * 100))
        self._emit_value_changed()

    def _on_slider_changed(self, value):
        # Update spinbox value
        normalized = value / 100.0
        actual_value = self.min_val + normalized * (self.max_val - self.min_val)

        if self.decimals == 0:
            actual_value = int(actual_value)

        self.spinbox.setValue(actual_value)

    def get_value(self) -> float:
        return self.spinbox.value()

    def set_value(self, value: float):
        self.spinbox.setValue(value)


class ChoiceParameterWidget(ParameterWidget):
    """Widget para parâmetros de escolha"""

    def __init__(self, name: str, choices: list[str], default: str = "",
                 description: str = "", parent: QWidget | None = None):

        self.choices = choices
        self.default = default or (choices[0] if choices else "")

        super().__init__(name, description, parent)

        self.set_value(self.default)

    def _create_control(self) -> QWidget:
        self.combo = QComboBox()
        self.combo.addItems(self.choices)
        self.combo.currentTextChanged.connect(self._emit_value_changed)
        return self.combo

    def get_value(self) -> str:
        return self.combo.currentText()

    def set_value(self, value: str):
        index = self.combo.findText(value)
        if index >= 0:
            self.combo.setCurrentIndex(index)


class BooleanParameterWidget(ParameterWidget):
    """Widget para parâmetros booleanos"""

    def __init__(self, name: str, default: bool = False,
                 description: str = "", parent: QWidget | None = None):

        self.default = default
        super().__init__(name, description, parent)
        self.set_value(default)

    def _create_control(self) -> QWidget:
        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self._emit_value_changed)
        return self.checkbox

    def get_value(self) -> bool:
        return self.checkbox.isChecked()

    def set_value(self, value: bool):
        self.checkbox.setChecked(value)


class PreviewWidget(QWidget, UiLoaderMixin):
    """
    Widget de preview para operações
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "desktop/ui_files/previewWidget.ui"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.figure = None
        self.canvas = None

        # Tenta carregar do arquivo .ui, senão usa fallback
        if not self._load_ui():
            self._setup_ui_fallback()
        else:
            self._setup_ui_from_file()

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # O matplotlib precisa ser adicionado programaticamente
        content_layout = self.findChild(QVBoxLayout, "contentLayout")
        if content_layout is None:
            content_layout = self.layout()
        
        if MATPLOTLIB_AVAILABLE and content_layout:
            self.figure = Figure(figsize=(8, 6))
            self.canvas = FigureCanvas(self.figure)
            content_layout.addWidget(self.canvas)
        elif content_layout:
            label = QLabel("Preview not available\n(matplotlib required)")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: gray; font-size: 14px;")
            content_layout.addWidget(label)

    def _setup_ui_fallback(self):
        layout = QVBoxLayout(self)

        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(8, 6))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
        else:
            # Fallback if matplotlib not available
            label = QLabel("Preview not available\n(matplotlib required)")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: gray; font-size: 14px;")
            layout.addWidget(label)

    def update_preview(self, data: dict[str, Any]):
        """Atualiza preview com novos dados"""
        if not MATPLOTLIB_AVAILABLE or not self.figure:
            return

        self.figure.clear()

        # Create sample preview plot
        ax = self.figure.add_subplot(111)

        if "x" in data and "y" in data:
            ax.plot(data["x"], data["y"], "b-", label="Original")

            if "y_processed" in data:
                ax.plot(data["x"], data["y_processed"], "r--", label="Processed")

            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_xlabel("Time")
            ax.set_ylabel("Value")

        else:
            ax.text(0.5, 0.5, "No data to preview",
                   ha="center", va="center", transform=ax.transAxes)

        self.canvas.draw()


class BaseOperationDialog(QDialog, UiLoaderMixin):
    """
    Diálogo base para operações
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "desktop/ui_files/baseOperationDialog.ui"

    # Signals
    parameters_changed = pyqtSignal(dict)  # parameters
    preview_requested = pyqtSignal(dict)   # parameters
    operation_accepted = pyqtSignal(dict)  # final parameters

    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(900, 700)

        # Parameter widgets
        self.parameter_widgets: dict[str, ParameterWidget] = {}

        # Preview timer (for real-time updates)
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._update_preview)

        # Tenta carregar do arquivo .ui, senão usa fallback
        if not self._load_ui():
            self._setup_ui_fallback()
        else:
            self._setup_ui_from_file()
        
        self._setup_connections()

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Splitter e painéis
        self.splitter = self.findChild(QSplitter, "splitter")
        
        # Botões
        self.reset_btn = self.findChild(QPushButton, "resetBtn")
        self.preview_btn = self.findChild(QPushButton, "previewBtn")
        self.cancel_btn = self.findChild(QPushButton, "cancelBtn")
        self.apply_btn = self.findChild(QPushButton, "applyBtn")
        
        # Preview widget - precisa ser criado programaticamente
        preview_container = self.findChild(QWidget, "previewContainer")
        if preview_container:
            preview_layout = preview_container.layout()
            if preview_layout is None:
                preview_layout = QVBoxLayout(preview_container)
            self.preview_widget = PreviewWidget()
            preview_layout.addWidget(self.preview_widget)
            
            self.preview_status = self.findChild(QLabel, "previewStatus")
            if not self.preview_status:
                self.preview_status = QLabel("Ready")
                preview_layout.addWidget(self.preview_status)
        else:
            self.preview_widget = PreviewWidget()
            self.preview_status = QLabel("Ready")
        
        # Conecta sinais
        if self.reset_btn:
            self.reset_btn.clicked.connect(self._reset_parameters)
        if self.preview_btn:
            self.preview_btn.clicked.connect(self._manual_preview)
        if self.cancel_btn:
            self.cancel_btn.clicked.connect(self.reject)
        if self.apply_btn:
            self.apply_btn.clicked.connect(self._apply_operation)
            self.apply_btn.setDefault(True)

    def _setup_ui_fallback(self):
        """Setup da UI base"""
        layout = QVBoxLayout(self)

        # Create splitter for parameters and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Parameters panel
        params_widget = self._create_parameters_panel()
        splitter.addWidget(params_widget)

        # Preview panel
        preview_widget = self._create_preview_panel()
        splitter.addWidget(preview_widget)

        # Set splitter proportions
        splitter.setSizes([400, 500])

        layout.addWidget(splitter)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self._reset_parameters)
        buttons_layout.addWidget(self.reset_btn)

        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self._manual_preview)
        buttons_layout.addWidget(self.preview_btn)

        buttons_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_operation)
        self.apply_btn.setDefault(True)
        buttons_layout.addWidget(self.apply_btn)

        layout.addLayout(buttons_layout)

    def _create_parameters_panel(self) -> QWidget:
        """Cria painel de parâmetros - override em subclasses"""
        widget = QScrollArea()
        widget.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        # Placeholder
        label = QLabel("Override _create_parameters_panel in subclass")
        layout.addWidget(label)

        widget.setWidget(content)
        return widget

    def _create_preview_panel(self) -> QWidget:
        """Cria painel de preview"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = QLabel("Preview")
        header.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(header)

        # Preview widget
        self.preview_widget = PreviewWidget()
        layout.addWidget(self.preview_widget)

        # Status
        self.preview_status = QLabel("Ready")
        self.preview_status.setStyleSheet("color: gray; font-size: 9px;")
        layout.addWidget(self.preview_status)

        return widget

    def _setup_connections(self):
        """Setup de conexões"""

    def add_parameter(self, widget: ParameterWidget):
        """Adiciona widget de parâmetro"""
        self.parameter_widgets[widget.parameter_name] = widget
        widget.value_changed.connect(self._on_parameter_changed)

    @pyqtSlot(str, object)
    def _on_parameter_changed(self, name: str, value: Any):
        """Callback quando parâmetro muda"""
        # Trigger delayed preview update
        self.preview_timer.start(500)  # 500ms delay

    def _get_current_parameters(self) -> dict[str, Any]:
        """Coleta parâmetros atuais"""
        params = {}
        for name, widget in self.parameter_widgets.items():
            params[name] = widget.get_value()
        return params

    @pyqtSlot()
    def _update_preview(self):
        """Atualiza preview com parâmetros atuais"""
        params = self._get_current_parameters()
        self.parameters_changed.emit(params)
        self.preview_requested.emit(params)

        # Mock preview data
        self._generate_mock_preview(params)

    def _generate_mock_preview(self, params: dict[str, Any]):
        """Gera preview mock - override em subclasses"""
        # Create sample data for preview
        x = np.linspace(0, 10, 100)
        y = np.sin(x) + 0.1 * np.random.randn(100)

        preview_data = {
            "x": x,
            "y": y,
            "parameters": params,
        }

        self.preview_widget.update_preview(preview_data)
        self.preview_status.setText(f"Preview updated with {len(params)} parameters")

    @pyqtSlot()
    def _manual_preview(self):
        """Preview manual (botão)"""
        self._update_preview()

    @pyqtSlot()
    def _reset_parameters(self):
        """Reset parâmetros para valores padrão"""
        for widget in self.parameter_widgets.values():
            # Each widget should implement its own default reset
            if hasattr(widget, "default"):
                widget.set_value(widget.default)

    @pyqtSlot()
    def _apply_operation(self):
        """Aplica operação com parâmetros atuais"""
        params = self._get_current_parameters()

        # Validate parameters
        if self._validate_parameters(params):
            self.operation_accepted.emit(params)
            self.accept()
        else:
            QMessageBox.warning(self, "Invalid Parameters",
                              "Please check the parameters and try again.")

    def _validate_parameters(self, params: dict[str, Any]) -> bool:
        """Valida parâmetros - override em subclasses"""
        return True


class InterpolationDialog(BaseOperationDialog):
    """Diálogo para configuração de interpolação"""

    def __init__(self, available_series: list[tuple[str, str]], parent: QWidget | None = None):
        self.available_series = available_series
        super().__init__("Interpolation Configuration", parent)

    def _create_parameters_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        # Method selection
        method_widget = ChoiceParameterWidget(
            "method",
            ["linear", "cubic_spline", "akima", "pchip", "polynomial"],
            "cubic_spline",
            "Interpolation method to use",
        )
        layout.addWidget(method_widget)
        self.add_parameter(method_widget)

        # Polynomial degree
        degree_widget = NumericParameterWidget(
            "degree", 1, 10, 1, 0, 3,
            "Degree for polynomial interpolation",
        )
        layout.addWidget(degree_widget)
        self.add_parameter(degree_widget)

        # Smoothing factor
        smooth_widget = NumericParameterWidget(
            "smoothing", 0.0, 1.0, 0.001, 3, 0.0,
            "Smoothing factor (0 = no smoothing, 1 = maximum smoothing)",
        )
        layout.addWidget(smooth_widget)
        self.add_parameter(smooth_widget)

        # Number of output points
        points_widget = NumericParameterWidget(
            "num_points", 10, 10000, 10, 0, 1000,
            "Number of points in interpolated output",
        )
        layout.addWidget(points_widget)
        self.add_parameter(points_widget)

        # Extrapolation
        extrap_widget = BooleanParameterWidget(
            "extrapolate", False,
            "Allow extrapolation beyond data range",
        )
        layout.addWidget(extrap_widget)
        self.add_parameter(extrap_widget)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll


class SynchronizationDialog(BaseOperationDialog):
    """Diálogo para configuração de sincronização"""

    def __init__(self, available_series: list[tuple[str, str]], parent: QWidget | None = None):
        self.available_series = available_series
        super().__init__("Synchronization Configuration", parent)

    def _create_parameters_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        # Sync method
        method_widget = ChoiceParameterWidget(
            "method",
            ["common_grid", "cross_correlation", "dtw", "phase_alignment"],
            "common_grid",
            "Synchronization method",
        )
        layout.addWidget(method_widget)
        self.add_parameter(method_widget)

        # Time tolerance
        tolerance_widget = NumericParameterWidget(
            "tolerance", 0.001, 10.0, 0.001, 3, 0.1,
            "Time tolerance for synchronization (seconds)",
        )
        layout.addWidget(tolerance_widget)
        self.add_parameter(tolerance_widget)

        # Output sample rate
        rate_widget = NumericParameterWidget(
            "sample_rate", 0.1, 1000.0, 0.1, 1, 1.0,
            "Output sample rate (Hz)",
        )
        layout.addWidget(rate_widget)
        self.add_parameter(rate_widget)

        # Window size for cross-correlation
        window_widget = NumericParameterWidget(
            "window_size", 10, 1000, 10, 0, 100,
            "Window size for correlation analysis",
        )
        layout.addWidget(window_widget)
        self.add_parameter(window_widget)

        # Create new dataset
        new_dataset_widget = BooleanParameterWidget(
            "create_new_dataset", True,
            "Create new synchronized dataset",
        )
        layout.addWidget(new_dataset_widget)
        self.add_parameter(new_dataset_widget)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll


class DerivativeDialog(BaseOperationDialog):
    """Diálogo para configuração de derivadas 1ª/2ª/3ª ordem"""

    def __init__(self, available_series: list[tuple[str, str]] | None = None, parent: QWidget | None = None):
        self.available_series = available_series or []
        super().__init__("Configuração de Derivada", parent)

    def _create_parameters_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        # Ordem da derivada
        order_widget = ChoiceParameterWidget(
            "order",
            ["1ª Ordem (velocidade)", "2ª Ordem (aceleração)", "3ª Ordem (jerk)"],
            "1ª Ordem (velocidade)",
            "Ordem da derivada a calcular",
        )
        layout.addWidget(order_widget)
        self.add_parameter(order_widget)

        # Método de cálculo
        method_widget = ChoiceParameterWidget(
            "method",
            ["finite_diff", "savitzky_golay", "spline_derivative"],
            "finite_diff",
            "Método numérico para cálculo da derivada",
        )
        layout.addWidget(method_widget)
        self.add_parameter(method_widget)

        # Tamanho da janela (Savitzky-Golay)
        window_widget = NumericParameterWidget(
            "window_length", 3, 51, 2, 0, 7,
            "Tamanho da janela para Savitzky-Golay (deve ser ímpar)",
        )
        layout.addWidget(window_widget)
        self.add_parameter(window_widget)

        # Ordem do polinômio
        polyorder_widget = NumericParameterWidget(
            "polyorder", 1, 6, 1, 0, 3,
            "Ordem do polinômio para Savitzky-Golay",
        )
        layout.addWidget(polyorder_widget)
        self.add_parameter(polyorder_widget)

        # Suavização pré-derivada
        smooth_widget = BooleanParameterWidget(
            "pre_smooth", False,
            "Aplicar suavização antes de derivar (reduz ruído)",
        )
        layout.addWidget(smooth_widget)
        self.add_parameter(smooth_widget)

        # Fator de suavização
        smooth_factor_widget = NumericParameterWidget(
            "smooth_factor", 0.0, 1.0, 0.01, 3, 0.1,
            "Fator de suavização pré-derivada (0=nenhuma)",
        )
        layout.addWidget(smooth_factor_widget)
        self.add_parameter(smooth_factor_widget)

        # Criar nova série
        new_series_widget = BooleanParameterWidget(
            "create_new_series", True,
            "Criar nova série com resultado (preserva original)",
        )
        layout.addWidget(new_series_widget)
        self.add_parameter(new_series_widget)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def _generate_mock_preview(self, params: dict[str, Any]):
        """Gera preview com derivada simulada"""
        import numpy as np

        x = np.linspace(0, 4*np.pi, 200)
        y = np.sin(x)

        # Derivada analítica para demonstração
        order_text = params.get("order", "1ª Ordem")
        if "1ª" in order_text:
            y_deriv = np.cos(x)  # d/dx(sin) = cos
            label = "dy/dx"
        elif "2ª" in order_text:
            y_deriv = -np.sin(x)  # d²/dx²(sin) = -sin
            label = "d²y/dx²"
        else:
            y_deriv = -np.cos(x)  # d³/dx³(sin) = -cos
            label = "d³y/dx³"

        preview_data = {
            "x": x,
            "y": y,
            "y_processed": y_deriv,
            "label_original": "sin(x)",
            "label_processed": label,
        }

        self.preview_widget.update_preview(preview_data)
        self.preview_status.setText(f"Preview: {order_text} - Método: {params.get('method', 'N/A')}")


class IntegralDialog(BaseOperationDialog):
    """Diálogo para configuração de integrais"""

    def __init__(self, available_series: list[tuple[str, str]] | None = None, parent: QWidget | None = None):
        self.available_series = available_series or []
        super().__init__("Configuração de Integral", parent)

    def _create_parameters_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        # Método de integração
        method_widget = ChoiceParameterWidget(
            "method",
            ["trapezoid", "simpson", "cumulative"],
            "trapezoid",
            "Método de integração numérica",
        )
        layout.addWidget(method_widget)
        self.add_parameter(method_widget)

        # Tipo de resultado
        result_type_widget = ChoiceParameterWidget(
            "result_type",
            ["Valor escalar (área total)", "Integral cumulativa (série)"],
            "Valor escalar (área total)",
            "Tipo de resultado desejado",
        )
        layout.addWidget(result_type_widget)
        self.add_parameter(result_type_widget)

        # Limites de integração
        use_limits_widget = BooleanParameterWidget(
            "use_limits", False,
            "Definir limites de integração (default: todo o intervalo)",
        )
        layout.addWidget(use_limits_widget)
        self.add_parameter(use_limits_widget)

        # Limite inferior
        lower_limit_widget = NumericParameterWidget(
            "lower_limit", -1e10, 1e10, 0.1, 6, 0.0,
            "Limite inferior de integração",
        )
        layout.addWidget(lower_limit_widget)
        self.add_parameter(lower_limit_widget)

        # Limite superior
        upper_limit_widget = NumericParameterWidget(
            "upper_limit", -1e10, 1e10, 0.1, 6, 1.0,
            "Limite superior de integração",
        )
        layout.addWidget(upper_limit_widget)
        self.add_parameter(upper_limit_widget)

        # Constante de integração
        constant_widget = NumericParameterWidget(
            "integration_constant", -1e10, 1e10, 0.1, 6, 0.0,
            "Constante de integração (para integral cumulativa)",
        )
        layout.addWidget(constant_widget)
        self.add_parameter(constant_widget)

        # Criar nova série
        new_series_widget = BooleanParameterWidget(
            "create_new_series", True,
            "Criar nova série com resultado",
        )
        layout.addWidget(new_series_widget)
        self.add_parameter(new_series_widget)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def _generate_mock_preview(self, params: dict[str, Any]):
        """Gera preview com integral simulada"""
        import numpy as np

        x = np.linspace(0, 4*np.pi, 200)
        y = np.sin(x)

        method = params.get("method", "trapezoid")
        result_type = params.get("result_type", "Valor escalar")

        if "cumulativa" in result_type.lower() or method == "cumulative":
            # Integral cumulativa: ∫sin = -cos + C
            y_integral = -np.cos(x) + 1  # +1 como constante
            label = "∫y dx (cumulativa)"
        else:
            # Área total sob a curva
            y_integral = np.cumsum(y) * (x[1] - x[0])
            label = f"Área = {np.trapz(y, x):.4f}"

        preview_data = {
            "x": x,
            "y": y,
            "y_processed": y_integral,
            "label_original": "sin(x)",
            "label_processed": label,
        }

        self.preview_widget.update_preview(preview_data)
        self.preview_status.setText(f"Preview: {method} - {result_type}")


class FilterDialog(BaseOperationDialog):
    """Diálogo para configuração de filtros digitais"""

    def __init__(self, available_series: list[tuple[str, str]] | None = None, parent: QWidget | None = None):
        self.available_series = available_series or []
        super().__init__("Configuração de Filtro", parent)

    def _create_parameters_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        # Tipo de filtro
        filter_type_widget = ChoiceParameterWidget(
            "filter_type",
            ["butterworth_lowpass", "butterworth_highpass", "butterworth_bandpass",
             "gaussian", "median", "outlier_removal"],
            "butterworth_lowpass",
            "Tipo de filtro a aplicar",
        )
        layout.addWidget(filter_type_widget)
        self.add_parameter(filter_type_widget)

        # Ordem do filtro
        order_widget = NumericParameterWidget(
            "order", 1, 10, 1, 0, 4,
            "Ordem do filtro Butterworth",
        )
        layout.addWidget(order_widget)
        self.add_parameter(order_widget)

        # Frequência de corte
        cutoff_widget = NumericParameterWidget(
            "cutoff_freq", 0.001, 0.999, 0.001, 3, 0.1,
            "Frequência de corte normalizada (0-1)",
        )
        layout.addWidget(cutoff_widget)
        self.add_parameter(cutoff_widget)

        # Frequência de corte alta (para bandpass)
        cutoff_high_widget = NumericParameterWidget(
            "cutoff_freq_high", 0.001, 0.999, 0.001, 3, 0.3,
            "Frequência de corte alta (para bandpass)",
        )
        layout.addWidget(cutoff_high_widget)
        self.add_parameter(cutoff_high_widget)

        # Tamanho da janela (para filtros de janela)
        window_widget = NumericParameterWidget(
            "window_size", 3, 101, 2, 0, 5,
            "Tamanho da janela para filtros de média/mediana",
        )
        layout.addWidget(window_widget)
        self.add_parameter(window_widget)

        # Limiar para remoção de outliers
        threshold_widget = NumericParameterWidget(
            "outlier_threshold", 1.0, 10.0, 0.1, 1, 3.0,
            "Limiar em desvios padrão para detecção de outliers",
        )
        layout.addWidget(threshold_widget)
        self.add_parameter(threshold_widget)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll


class SmoothingDialog(BaseOperationDialog):
    """Diálogo para configuração de suavização"""

    def __init__(self, available_series: list[tuple[str, str]] | None = None, parent: QWidget | None = None):
        self.available_series = available_series or []
        super().__init__("Configuração de Suavização", parent)

    def _create_parameters_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        # Método de suavização
        method_widget = ChoiceParameterWidget(
            "method",
            ["gaussian", "moving_average", "savitzky_golay", "exponential", "median"],
            "gaussian",
            "Método de suavização",
        )
        layout.addWidget(method_widget)
        self.add_parameter(method_widget)

        # Tamanho da janela
        window_widget = NumericParameterWidget(
            "window_size", 3, 101, 2, 0, 5,
            "Tamanho da janela de suavização (deve ser ímpar)",
        )
        layout.addWidget(window_widget)
        self.add_parameter(window_widget)

        # Sigma (para Gaussiano)
        sigma_widget = NumericParameterWidget(
            "sigma", 0.1, 10.0, 0.1, 2, 1.0,
            "Desvio padrão para filtro Gaussiano",
        )
        layout.addWidget(sigma_widget)
        self.add_parameter(sigma_widget)

        # Ordem do polinômio (para Savitzky-Golay)
        polyorder_widget = NumericParameterWidget(
            "polyorder", 1, 6, 1, 0, 3,
            "Ordem do polinômio para Savitzky-Golay",
        )
        layout.addWidget(polyorder_widget)
        self.add_parameter(polyorder_widget)

        # Fator de decaimento (para exponencial)
        alpha_widget = NumericParameterWidget(
            "alpha", 0.01, 1.0, 0.01, 2, 0.3,
            "Fator de decaimento para média móvel exponencial",
        )
        layout.addWidget(alpha_widget)
        self.add_parameter(alpha_widget)

        # Preservar bordas
        preserve_edges_widget = BooleanParameterWidget(
            "preserve_edges", True,
            "Preservar valores nas bordas (evita redução do tamanho)",
        )
        layout.addWidget(preserve_edges_widget)
        self.add_parameter(preserve_edges_widget)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll


class CalculusDialog(BaseOperationDialog):
    """Diálogo para configuração de cálculos matemáticos"""

    def __init__(self, available_series: list[tuple[str, str]] | None = None, parent: QWidget | None = None):
        self.available_series = available_series or []
        super().__init__("Calculus Configuration", parent)

    def _create_parameters_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        # Operation type
        operation_widget = ChoiceParameterWidget(
            "operation",
            ["derivative", "second_derivative", "integral", "moving_average", "fft"],
            "derivative",
            "Mathematical operation to perform",
        )
        layout.addWidget(operation_widget)
        self.add_parameter(operation_widget)

        # Differentiation method
        diff_method_widget = ChoiceParameterWidget(
            "diff_method",
            ["forward", "backward", "central", "savitzky_golay"],
            "central",
            "Differentiation method",
        )
        layout.addWidget(diff_method_widget)
        self.add_parameter(diff_method_widget)

        # Window size
        window_widget = NumericParameterWidget(
            "window_size", 3, 101, 2, 0, 5,
            "Window size for smoothing operations (odd numbers only)",
        )
        layout.addWidget(window_widget)
        self.add_parameter(window_widget)

        # Polynomial order (for Savitzky-Golay)
        order_widget = NumericParameterWidget(
            "poly_order", 1, 10, 1, 0, 3,
            "Polynomial order for Savitzky-Golay filter",
        )
        layout.addWidget(order_widget)
        self.add_parameter(order_widget)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll


class OperationDialogManager:
    """Manager para diálogos de operação"""

    def __init__(self):
        self.dialog_registry = {
            "interpolation": InterpolationDialog,
            "synchronization": SynchronizationDialog,
            "calculus": CalculusDialog,
            "derivative": DerivativeDialog,
            "integral": IntegralDialog,
            "filter": FilterDialog,
            "smoothing": SmoothingDialog,
        }

    def show_dialog(self, operation_type: str, available_series: list[tuple[str, str]] | None = None,
                   parent: QWidget | None = None) -> dict[str, Any] | None:
        """Mostra diálogo para tipo de operação e retorna parâmetros"""

        dialog_class = self.dialog_registry.get(operation_type)
        if not dialog_class:
            logger.warning("unknown_operation_dialog", operation_type=operation_type)
            return None

        dialog = dialog_class(available_series or [], parent)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog._get_current_parameters()

        return None

    def register_dialog(self, operation_type: str, dialog_class):
        """Registra novo tipo de diálogo"""
        self.dialog_registry[operation_type] = dialog_class


# Global dialog manager instance
_dialog_manager = OperationDialogManager()


def get_operation_dialog_manager() -> OperationDialogManager:
    """Retorna manager global de diálogos"""
    return _dialog_manager


def show_interpolation_dialog(available_series: list[tuple[str, str]] | None = None,
                            parent: QWidget | None = None) -> dict[str, Any] | None:
    """Conveniência para mostrar diálogo de interpolação"""
    return _dialog_manager.show_dialog("interpolation", available_series, parent)


def show_synchronization_dialog(available_series: list[tuple[str, str]] | None = None,
                               parent: QWidget | None = None) -> dict[str, Any] | None:
    """Conveniência para mostrar diálogo de sincronização"""
    return _dialog_manager.show_dialog("synchronization", available_series, parent)


def show_calculus_dialog(available_series: list[tuple[str, str]] | None = None,
                        parent: QWidget | None = None) -> dict[str, Any] | None:
    """Conveniência para mostrar diálogo de cálculo"""
    return _dialog_manager.show_dialog("calculus", available_series, parent)


def show_derivative_dialog(available_series: list[tuple[str, str]] | None = None,
                          parent: QWidget | None = None) -> dict[str, Any] | None:
    """Conveniência para mostrar diálogo de derivada"""
    return _dialog_manager.show_dialog("derivative", available_series, parent)


def show_integral_dialog(available_series: list[tuple[str, str]] | None = None,
                        parent: QWidget | None = None) -> dict[str, Any] | None:
    """Conveniência para mostrar diálogo de integral"""
    return _dialog_manager.show_dialog("integral", available_series, parent)


def show_filter_dialog(available_series: list[tuple[str, str]] | None = None,
                      parent: QWidget | None = None) -> dict[str, Any] | None:
    """Conveniência para mostrar diálogo de filtro"""
    return _dialog_manager.show_dialog("filter", available_series, parent)


def show_smoothing_dialog(available_series: list[tuple[str, str]] | None = None,
                         parent: QWidget | None = None) -> dict[str, Any] | None:
    """Conveniência para mostrar diálogo de suavização"""
    return _dialog_manager.show_dialog("smoothing", available_series, parent)
