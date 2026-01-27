"""
SmoothingDialog - Diálogo de configuração de suavização

Métodos disponíveis:
- Gaussian: Suavização com kernel Gaussiano
- Moving Average: Média móvel simples/ponderada
- Savitzky-Golay: Suavização polinomial
- Exponential: Suavização exponencial
- Median: Filtro mediana
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class SmoothingDialog(QDialog):
    """
    Diálogo para configuração de suavização de dados
    
    Métodos suportados:
    - Gaussian: Filtro Gaussiano
    - Moving Average: Média móvel
    - Savitzky-Golay: Suavização polinomial local
    - Exponential: Suavização exponencial
    - Median: Filtro mediana
    """
    
    smoothing_applied = pyqtSignal(dict)  # config
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.setWindowTitle("〰️ Configurar Suavização")
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        
        self._setup_ui()
        self._setup_connections()
        
        logger.debug("smoothing_dialog_initialized")
    
    def _setup_ui(self):
        """Configura interface do diálogo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 2px 8px;
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton[objectName="secondary"] {
                background-color: #6c757d;
            }
            QPushButton[objectName="success"] {
                background-color: #198754;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                min-width: 150px;
            }
            QSlider {
                margin: 10px 0;
            }
            QSlider::groove:horizontal {
                border: 1px solid #ced4da;
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0d6efd;
                border: none;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        
        # Header
        header = QLabel("〰️ Configurar Suavização de Dados")
        header.setFont(QFont("", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #0d6efd; padding: 10px;")
        layout.addWidget(header)
        
        # Método de suavização
        method_group = QGroupBox("📊 Método de Suavização")
        method_layout = QFormLayout(method_group)
        
        self._method = QComboBox()
        self._method.addItems([
            "gaussian", "moving_average", "savitzky_golay",
            "exponential", "median"
        ])
        self._method.setToolTip(
            "Método de suavização:\n"
            "• Gaussian: Kernel gaussiano (smooth)\n"
            "• Moving Average: Média móvel simples\n"
            "• Savitzky-Golay: Preserva picos\n"
            "• Exponential: Peso decai exponencialmente\n"
            "• Median: Remove ruído impulsivo"
        )
        method_layout.addRow("Método:", self._method)
        
        layout.addWidget(method_group)
        
        # Parâmetros comuns
        common_group = QGroupBox("🔧 Parâmetros")
        common_layout = QFormLayout(common_group)
        
        # Janela com slider
        window_container = QWidget()
        window_layout = QHBoxLayout(window_container)
        window_layout.setContentsMargins(0, 0, 0, 0)
        
        self._window = QSpinBox()
        self._window.setRange(3, 101)
        self._window.setValue(7)
        self._window.setSingleStep(2)
        self._window.setToolTip(
            "Tamanho da janela de suavização (ímpar).\n"
            "Valores maiores = mais suavização."
        )
        
        self._window_slider = QSlider(Qt.Orientation.Horizontal)
        self._window_slider.setRange(3, 101)
        self._window_slider.setValue(7)
        self._window_slider.setSingleStep(2)
        
        window_layout.addWidget(self._window)
        window_layout.addWidget(self._window_slider, stretch=1)
        
        common_layout.addRow("Janela:", window_container)
        
        # Sigma (para Gaussian)
        sigma_container = QWidget()
        sigma_layout = QHBoxLayout(sigma_container)
        sigma_layout.setContentsMargins(0, 0, 0, 0)
        
        self._sigma = QDoubleSpinBox()
        self._sigma.setRange(0.1, 20.0)
        self._sigma.setValue(1.5)
        self._sigma.setDecimals(2)
        self._sigma.setSingleStep(0.1)
        self._sigma.setToolTip(
            "Desvio padrão do kernel Gaussiano.\n"
            "Valores maiores = mais suavização."
        )
        
        self._sigma_slider = QSlider(Qt.Orientation.Horizontal)
        self._sigma_slider.setRange(1, 200)  # 0.1 to 20.0 * 10
        self._sigma_slider.setValue(15)
        
        sigma_layout.addWidget(self._sigma)
        sigma_layout.addWidget(self._sigma_slider, stretch=1)
        
        common_layout.addRow("Sigma:", sigma_container)
        
        layout.addWidget(common_group)
        
        # Parâmetros específicos de Savitzky-Golay
        self._savgol_group = QGroupBox("📐 Savitzky-Golay")
        savgol_layout = QFormLayout(self._savgol_group)
        
        self._polyorder = QSpinBox()
        self._polyorder.setRange(1, 10)
        self._polyorder.setValue(3)
        self._polyorder.setToolTip(
            "Ordem do polinômio de ajuste.\n"
            "Deve ser menor que o tamanho da janela."
        )
        savgol_layout.addRow("Ordem Polinômio:", self._polyorder)
        
        self._deriv = QSpinBox()
        self._deriv.setRange(0, 3)
        self._deriv.setValue(0)
        self._deriv.setToolTip(
            "Ordem da derivada a calcular.\n"
            "0 = apenas suavização."
        )
        savgol_layout.addRow("Derivada:", self._deriv)
        
        self._delta = QDoubleSpinBox()
        self._delta.setRange(0.001, 100.0)
        self._delta.setValue(1.0)
        self._delta.setDecimals(3)
        self._delta.setToolTip(
            "Espaçamento entre amostras (para derivadas)."
        )
        savgol_layout.addRow("Delta:", self._delta)
        
        layout.addWidget(self._savgol_group)
        
        # Parâmetros específicos de Exponential
        self._exp_group = QGroupBox("📉 Exponencial")
        exp_layout = QFormLayout(self._exp_group)
        
        self._alpha = QDoubleSpinBox()
        self._alpha.setRange(0.01, 1.0)
        self._alpha.setValue(0.3)
        self._alpha.setDecimals(2)
        self._alpha.setSingleStep(0.05)
        self._alpha.setToolTip(
            "Fator de suavização (0-1).\n"
            "Valores menores = mais suavização.\n"
            "0.1 = muito suave, 0.9 = menos suave."
        )
        exp_layout.addRow("Alpha:", self._alpha)
        
        self._adjust = QCheckBox("Ajustar para bias inicial")
        self._adjust.setChecked(True)
        self._adjust.setToolTip(
            "Corrige o bias introduzido nos primeiros valores."
        )
        exp_layout.addRow(self._adjust)
        
        layout.addWidget(self._exp_group)
        
        # Opções adicionais
        options_group = QGroupBox("⚙️ Opções")
        options_layout = QFormLayout(options_group)
        
        self._preserve_nan = QCheckBox("Preservar NaN")
        self._preserve_nan.setChecked(True)
        self._preserve_nan.setToolTip(
            "Se marcado, valores NaN são preservados.\n"
            "Se desmarcado, NaN pode ser interpolado."
        )
        options_layout.addRow(self._preserve_nan)
        
        self._boundary_mode = QComboBox()
        self._boundary_mode.addItems(["nearest", "wrap", "reflect", "constant"])
        self._boundary_mode.setToolTip(
            "Como tratar bordas dos dados:\n"
            "• nearest: Repete valor mais próximo\n"
            "• wrap: Circular\n"
            "• reflect: Espelhado\n"
            "• constant: Usa valor fixo"
        )
        options_layout.addRow("Modo Borda:", self._boundary_mode)
        
        layout.addWidget(options_group)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        preview_btn = QPushButton("👁️ Preview")
        preview_btn.clicked.connect(self._preview_smoothing)
        btn_layout.addWidget(preview_btn)
        
        apply_btn = QPushButton("✅ Aplicar")
        apply_btn.setObjectName("success")
        apply_btn.clicked.connect(self._apply_smoothing)
        btn_layout.addWidget(apply_btn)
        
        layout.addLayout(btn_layout)
    
    def _setup_connections(self):
        """Configura conexões de sinais"""
        # Sincronizar sliders com spinboxes
        self._window_slider.valueChanged.connect(self._on_window_slider_changed)
        self._window.valueChanged.connect(self._window_slider.setValue)
        
        self._sigma_slider.valueChanged.connect(self._on_sigma_slider_changed)
        self._sigma.valueChanged.connect(lambda v: self._sigma_slider.setValue(int(v * 10)))
        
        # Mostrar/ocultar grupos baseado no método
        self._method.currentTextChanged.connect(self._on_method_changed)
        
        # Inicializar estado
        self._on_method_changed(self._method.currentText())
    
    def _on_window_slider_changed(self, value: int):
        """Handler para slider de janela"""
        # Garantir valor ímpar
        if value % 2 == 0:
            value += 1
        self._window.setValue(value)
    
    def _on_sigma_slider_changed(self, value: int):
        """Handler para slider de sigma"""
        self._sigma.setValue(value / 10.0)
    
    def _on_method_changed(self, method: str):
        """Handler para mudança de método"""
        # Mostrar/ocultar grupos específicos
        self._savgol_group.setVisible(method == "savitzky_golay")
        self._exp_group.setVisible(method == "exponential")
        
        # Habilitar/desabilitar sigma
        self._sigma.setEnabled(method == "gaussian")
        self._sigma_slider.setEnabled(method == "gaussian")
        
        # Ajustar janela padrão conforme método
        if method == "gaussian":
            self._window.setValue(7)
        elif method == "moving_average":
            self._window.setValue(5)
        elif method == "savitzky_golay":
            self._window.setValue(11)
        elif method == "median":
            self._window.setValue(3)
        
        # Validar polyorder < window
        if method == "savitzky_golay":
            self._validate_polyorder()
    
    def _validate_polyorder(self):
        """Garante que polyorder < window"""
        max_order = self._window.value() - 1
        self._polyorder.setMaximum(max_order)
        if self._polyorder.value() >= max_order:
            self._polyorder.setValue(max_order - 1)
    
    def _get_smoothing_config(self) -> Dict[str, Any]:
        """Obtém configuração de suavização"""
        method = self._method.currentText()
        
        config = {
            'method': method,
            'window': self._window.value(),
            'preserve_nan': self._preserve_nan.isChecked(),
            'boundary_mode': self._boundary_mode.currentText()
        }
        
        if method == "gaussian":
            config['sigma'] = self._sigma.value()
        elif method == "savitzky_golay":
            config['polyorder'] = self._polyorder.value()
            config['deriv'] = self._deriv.value()
            config['delta'] = self._delta.value()
        elif method == "exponential":
            config['alpha'] = self._alpha.value()
            config['adjust'] = self._adjust.isChecked()
        
        return config
    
    def _preview_smoothing(self):
        """Preview da suavização"""
        config = self._get_smoothing_config()
        config['preview'] = True
        self.smoothing_applied.emit(config)
    
    def _apply_smoothing(self):
        """Aplica suavização e fecha diálogo"""
        config = self._get_smoothing_config()
        config['preview'] = False
        self.smoothing_applied.emit(config)
        self.accept()
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """Retorna configuração se diálogo foi aceito"""
        if self.result() == QDialog.DialogCode.Accepted:
            return self._get_smoothing_config()
        return None


def show_smoothing_dialog(parent: Optional[QWidget] = None) -> Optional[Dict[str, Any]]:
    """
    Conveniência para mostrar diálogo de suavização
    
    Returns:
        Configuração de suavização ou None se cancelado
    """
    dialog = SmoothingDialog(parent)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_config()
    
    return None
