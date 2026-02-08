"""
Operation Preview - Preview em tempo real de operações matemáticas

Fornece visualização prévia dos resultados de operações como:
- Interpolação
- Derivadas/Integrais
- Filtros e suavização
- Área sob curva

Interface carregada de: desktop/ui_files/operationPreviewDialog.ui
"""

from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from platform_base.ui.ui_loader_mixin import UiLoaderMixin
from platform_base.utils.logging import get_logger


logger = get_logger(__name__)


class PreviewCanvas(QWidget):
    """Canvas de matplotlib para preview"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Figura matplotlib
        self.figure = Figure(figsize=(8, 5), dpi=100, tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def clear(self):
        """Limpa o gráfico"""
        self.ax.clear()
        self.canvas.draw()

    def plot_comparison(self, x_original: np.ndarray, y_original: np.ndarray,
                        x_result: np.ndarray, y_result: np.ndarray,
                        title: str = "Preview",
                        original_label: str = "Original",
                        result_label: str = "Resultado"):
        """Plota comparação entre original e resultado"""
        self.ax.clear()

        # Plot original
        self.ax.plot(x_original, y_original, "b-", linewidth=1.5,
                    alpha=0.7, label=original_label)

        # Plot resultado
        self.ax.plot(x_result, y_result, "r-", linewidth=2,
                    alpha=0.9, label=result_label)

        # Configuração
        self.ax.set_title(title, fontsize=12, fontweight="bold")
        self.ax.legend(loc="best", framealpha=0.9)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel("Índice")
        self.ax.set_ylabel("Valor")

        # Estilo
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        self.canvas.draw()

    def plot_single(self, x: np.ndarray, y: np.ndarray,
                   title: str = "Resultado", label: str = "Dados"):
        """Plota série única"""
        self.ax.clear()

        self.ax.plot(x, y, "b-", linewidth=2, label=label)
        self.ax.set_title(title, fontsize=12, fontweight="bold")
        self.ax.legend(loc="best")
        self.ax.grid(True, alpha=0.3)

        self.canvas.draw()

    def plot_area(self, x: np.ndarray, y: np.ndarray,
                  area_value: float, title: str = "Área"):
        """Plota área sob a curva"""
        self.ax.clear()

        self.ax.plot(x, y, "b-", linewidth=2, label="Dados")
        self.ax.fill_between(x, y, alpha=0.3, color="blue")

        self.ax.set_title(f"{title} = {area_value:.4f}", fontsize=12, fontweight="bold")
        self.ax.legend(loc="best")
        self.ax.grid(True, alpha=0.3)

        self.canvas.draw()


class OperationPreviewDialog(QDialog, UiLoaderMixin):
    """
    Diálogo de preview para operações matemáticas

    Características:
    - Visualização em tempo real
    - Comparação antes/depois
    - Estatísticas do resultado
    - Opção de aplicar ou cancelar

    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "operationPreviewDialog.ui"

    # Signal quando o usuário aceita
    apply_requested = pyqtSignal(dict)  # params da operação

    def __init__(self, operation_name: str, params: dict[str, Any],
                 series_data: np.ndarray, parent=None):
        super().__init__(parent)

        self.operation_name = operation_name
        self.params = params
        self.series_data = series_data
        self.result_data: np.ndarray | None = None

        # Carrega interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()

        self._compute_preview()

        logger.debug("operation_preview_dialog_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        # Encontra widgets do arquivo .ui
        self.content_widget = self.findChild(QWidget, "contentWidget")
        self.button_box = self.findChild(QDialogButtonBox, "buttonBox")

        # Se o contentWidget existe mas está vazio, preenche programaticamente
        if self.content_widget:
            content_layout = self.content_widget.layout()
            if content_layout and content_layout.count() == 0:
                # UI está vazio, criar conteúdo programaticamente
                self._create_content_widgets(content_layout)

    def _create_content_widgets(self, layout: QVBoxLayout):
        """Cria widgets de conteúdo quando o .ui está vazio"""
        # Título
        title = QLabel(f"🔍 Preview: {self.operation_name.replace('_', ' ').title()}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0d6efd;")
        layout.addWidget(title)

        # Splitter para canvas e info
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Canvas de preview
        self._canvas = PreviewCanvas()
        splitter.addWidget(self._canvas)

        # Painel de informações
        info_panel = self._create_info_panel()
        splitter.addWidget(info_panel)

        splitter.setSizes([600, 200])
        layout.addWidget(splitter)

    def _create_info_panel(self) -> QWidget:
        """Cria painel de informações"""
        info_panel = QWidget()
        info_layout = QVBoxLayout(info_panel)
        info_layout.setSpacing(8)

        # Parâmetros
        params_label = QLabel("📝 <b>Parâmetros:</b>")
        info_layout.addWidget(params_label)

        for key, value in self.params.items():
            param_text = QLabel(f"  • {key}: {value}")
            param_text.setStyleSheet("font-size: 12px; color: #495057;")
            info_layout.addWidget(param_text)

        info_layout.addSpacing(16)

        # Estatísticas
        self._stats_label = QLabel("📊 <b>Estatísticas:</b>")
        info_layout.addWidget(self._stats_label)

        self._stats_content = QLabel("Calculando...")
        self._stats_content.setStyleSheet("font-size: 11px; color: #6c757d; padding-left: 8px;")
        self._stats_content.setWordWrap(True)
        info_layout.addWidget(self._stats_content)

        info_layout.addStretch()

        # Checkbox para mostrar original
        self._show_original = QCheckBox("Mostrar dados originais")
        self._show_original.setChecked(True)
        self._show_original.stateChanged.connect(self._update_plot)
        info_layout.addWidget(self._show_original)

        info_panel.setMaximumWidth(250)
        return info_panel

    def _compute_preview(self):
        """Calcula preview da operação"""
        try:
            np.arange(len(self.series_data))
            y_orig = self.series_data

            # Computar resultado baseado na operação
            if self.operation_name == "interpolation":
                self.result_data = self._preview_interpolation()
            elif self.operation_name == "derivative":
                self.result_data = self._preview_derivative()
            elif self.operation_name == "integral":
                self.result_data = self._preview_integral()
            elif self.operation_name == "smoothing":
                self.result_data = self._preview_smoothing()
            elif self.operation_name == "remove_outliers":
                self.result_data = self._preview_remove_outliers()
            else:
                self.result_data = y_orig.copy()

            # Atualizar plot
            self._update_plot()

            # Atualizar estatísticas
            self._update_stats()

        except Exception as e:
            logger.exception(f"Preview computation error: {e}")
            self._stats_content.setText(f"Erro: {e!s}")

    def _preview_interpolation(self) -> np.ndarray:
        """Preview de interpolação"""
        from scipy import interpolate

        method = self.params.get("method", "linear")
        num_points = self.params.get("num_points", len(self.series_data))

        x_orig = np.arange(len(self.series_data))
        x_new = np.linspace(0, len(self.series_data) - 1, num_points)

        if method == "linear":
            f = interpolate.interp1d(x_orig, self.series_data, kind="linear")
        elif method in ("cubic_spline", "cubic"):
            f = interpolate.interp1d(x_orig, self.series_data, kind="cubic")
        else:
            f = interpolate.interp1d(x_orig, self.series_data, kind="linear")

        return f(x_new)

    def _preview_derivative(self) -> np.ndarray:
        """Preview de derivada"""
        order = self.params.get("order", 1)
        result = self.series_data.copy()

        for _ in range(order):
            result = np.gradient(result)

        return result

    def _preview_integral(self) -> np.ndarray:
        """Preview de integral cumulativa"""
        from scipy import integrate
        return integrate.cumulative_trapezoid(self.series_data, initial=0)

    def _preview_smoothing(self) -> np.ndarray:
        """Preview de suavização"""
        from scipy import ndimage

        method = self.params.get("method", "gaussian")
        window = self.params.get("window", 5)
        sigma = self.params.get("sigma", 1.0)

        if method == "gaussian":
            return ndimage.gaussian_filter1d(self.series_data, sigma=sigma)
        if method == "moving_average":
            kernel = np.ones(window) / window
            return np.convolve(self.series_data, kernel, mode="same")
        return ndimage.uniform_filter1d(self.series_data, size=window)

    def _preview_remove_outliers(self) -> np.ndarray:
        """Preview de remoção de outliers"""
        threshold = self.params.get("threshold", 3.0)

        mean = np.mean(self.series_data)
        std = np.std(self.series_data)

        result = self.series_data.copy()
        outliers = np.abs(result - mean) > threshold * std
        result[outliers] = np.nan

        # Interpolar valores nan
        mask = ~np.isnan(result)
        return np.interp(np.arange(len(result)),
                          np.arange(len(result))[mask],
                          result[mask])


    def _update_plot(self):
        """Atualiza visualização"""
        if self.result_data is None:
            return

        x_orig = np.arange(len(self.series_data))
        x_result = np.arange(len(self.result_data))

        if self._show_original.isChecked():
            self._canvas.plot_comparison(
                x_orig, self.series_data,
                x_result, self.result_data,
                title=f"Preview: {self.operation_name.replace('_', ' ').title()}",
                original_label="Original",
                result_label="Resultado",
            )
        else:
            self._canvas.plot_single(
                x_result, self.result_data,
                title=f"Resultado: {self.operation_name.replace('_', ' ').title()}",
                label="Resultado",
            )

    def _update_stats(self):
        """Atualiza estatísticas"""
        if self.result_data is None:
            return

        orig = self.series_data
        res = self.result_data

        stats_text = (
            f"Original:\n"
            f"  • Pontos: {len(orig):,}\n"
            f"  • Min: {orig.min():.4f}\n"
            f"  • Max: {orig.max():.4f}\n"
            f"  • Média: {orig.mean():.4f}\n"
            f"  • Desvio: {orig.std():.4f}\n\n"
            f"Resultado:\n"
            f"  • Pontos: {len(res):,}\n"
            f"  • Min: {res.min():.4f}\n"
            f"  • Max: {res.max():.4f}\n"
            f"  • Média: {res.mean():.4f}\n"
            f"  • Desvio: {res.std():.4f}"
        )

        self._stats_content.setText(stats_text)

    def _on_apply(self):
        """Aplicar operação"""
        self.apply_requested.emit(self.params)
        self.accept()

    def get_result(self) -> np.ndarray | None:
        """Retorna resultado calculado"""
        return self.result_data


def show_preview_dialog(operation_name: str, params: dict[str, Any],
                        series_data: np.ndarray, parent=None) -> np.ndarray | None:
    """
    Função de conveniência para mostrar preview

    Args:
        operation_name: Nome da operação
        params: Parâmetros da operação
        series_data: Dados da série
        parent: Widget pai

    Returns:
        Resultado se aceito, None se cancelado
    """
    dialog = OperationPreviewDialog(operation_name, params, series_data, parent)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_result()

    return None
