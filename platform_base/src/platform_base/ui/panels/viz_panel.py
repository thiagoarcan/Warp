"""
VizPanel - Painel moderno de visualização com drag-and-drop

Características:
- Sistema drag-and-drop para criar gráficos
- Área de plotagem com zonas definidas
- Interface intuitiva e moderna
- Suporte para múltiplas visualizações
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Matplotlib imports para visualização real
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from platform_base.desktop.widgets.base import UiLoaderMixin
from platform_base.ui.panels.performance import (
    DecimationMethod,
    PerformanceConfig,
    decimate_for_plot,
)
from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from platform_base.ui.state import SessionState


logger = get_logger(__name__)

# Nota: emojis removidos dos labels do matplotlib para evitar warnings de fonte

# Configuração de performance para grandes volumes
_perf_config = PerformanceConfig(
    direct_render_limit=10_000,
    decimation_limit=100_000,
    streaming_limit=1_000_000,
    target_display_points=5_000,
    decimation_method=DecimationMethod.MINMAX,
)


class MatplotlibWidget(QWidget):
    """Widget real de matplotlib para visualização de dados com suporte a múltiplas séries"""

    # Signal para coordenadas do crosshair
    coordinates_changed = pyqtSignal(float, float)  # x, y
    # Signal para região selecionada
    region_selected = pyqtSignal(float, float, float, float)  # x1, x2, y1, y2
    # Signal para dados extraídos
    data_extracted = pyqtSignal(object)  # numpy array
    # Signal para solicitar adição de série
    series_drop_requested = pyqtSignal(str, str)  # dataset_id, series_id
    # Signal para cálculos
    calculation_requested = pyqtSignal(str, str, str, dict)  # dataset_id, series_id, calc_type, params

    def __init__(self, series, plot_type: str = "2d", parent=None, dataset_name: str = "", 
                 t_datetime=None, t_seconds=None):
        super().__init__(parent)

        # Suporte a múltiplas séries
        self.series_list = []  # Lista de (series, dataset_name, line_obj)
        self.series = series  # Série principal (compatibilidade)
        self.plot_type = plot_type
        self._dataset_name = dataset_name or "Dataset"
        
        # Dados de tempo para eixo X
        self._t_datetime = t_datetime  # numpy.datetime64 array
        self._t_seconds = t_seconds    # numpy.float64 array

        # Configurar matplotlib com estilo moderno
        plt.style.use("default")

        # Criar figura matplotlib com design moderno
        self.figure = Figure(figsize=(12, 8), dpi=100, tight_layout=True,
                            facecolor="white", edgecolor="none")
        self.canvas = FigureCanvas(self.figure)

        # Configurar cores modernas
        self.colors = ["#0d6efd", "#198754", "#dc3545", "#fd7e14", "#6f42c1", "#20c997"]
        self.current_color_idx = 0

        # Crosshair state
        self._crosshair_enabled = False
        self._crosshair_hline = None
        self._crosshair_vline = None
        self._crosshair_text = None
        self._motion_cid = None

        # Region selection (brush) state
        self._selection_enabled = False
        self._selection_rect = None
        self._selection_start = None
        self._press_cid = None
        self._release_cid = None
        self._drag_cid = None

        # Pan state
        self._pan_enabled = False
        self._pan_start = None

        # Legend pick event connection ID
        self._pick_cid = None

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Toolbar compacta por plot
        self._toolbar = self._create_toolbar()
        layout.addWidget(self._toolbar)

        # Canvas
        layout.addWidget(self.canvas)

        # Enable context menu
        self.canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self._show_context_menu)

        # Enable drop de séries no canvas
        self.setAcceptDrops(True)
        self.canvas.setAcceptDrops(True)

        # Conectar evento de movimento do mouse para tooltip de coordenadas
        self._coord_cid = self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)
        
        # Tooltip para coordenadas (QLabel na toolbar)
        self._coord_label = None  # Será criada na toolbar

        # Criar o gráfico
        self._create_plot()

    def _on_mouse_move(self, event):
        """Handler para movimento do mouse - mostra coordenadas"""
        if event.inaxes is None:
            if self._coord_label:
                self._coord_label.setText("")
            return
            
        try:
            x, y = event.xdata, event.ydata
            
            # Formatar X como datetime se disponível
            if self._t_datetime is not None and len(self._t_datetime) > 0:
                # Converter índice x para datetime
                idx = int(x) if x >= 0 else 0
                idx = min(idx, len(self._t_datetime) - 1)
                dt_val = self._t_datetime[idx]
                x_str = str(np.datetime_as_string(dt_val, unit='s'))
            else:
                x_str = f"{x:.2f}"
            
            coord_text = f"X: {x_str}  |  Y: {y:.4f}"
            
            if self._coord_label:
                self._coord_label.setText(coord_text)
                
            # Emitir sinal de coordenadas
            self.coordinates_changed.emit(x, y)
            
        except Exception:
            pass

    def _create_toolbar(self) -> QWidget:
        """Cria toolbar compacta para o plot"""
        toolbar = QWidget()
        toolbar.setMaximumHeight(32)
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 4px 8px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:checked {
                background-color: #0d6efd;
                color: white;
            }
        """)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        # Zoom In
        zoom_in_btn = QPushButton("🔍+")
        zoom_in_btn.setToolTip("Zoom In")
        zoom_in_btn.clicked.connect(self._zoom_in)
        layout.addWidget(zoom_in_btn)

        # Zoom Out
        zoom_out_btn = QPushButton("🔍−")
        zoom_out_btn.setToolTip("Zoom Out")
        zoom_out_btn.clicked.connect(self._zoom_out)
        layout.addWidget(zoom_out_btn)

        # Fit/Reset
        reset_btn = QPushButton("🔄")
        reset_btn.setToolTip("Reset View (Fit)")
        reset_btn.clicked.connect(self._reset_view)
        layout.addWidget(reset_btn)

        # Separador
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("color: #dee2e6;")
        layout.addWidget(sep1)

        # Pan
        self._pan_btn = QPushButton("✋")
        self._pan_btn.setToolTip("Pan (arrastar)")
        self._pan_btn.setCheckable(True)
        self._pan_btn.clicked.connect(self._toggle_pan)
        layout.addWidget(self._pan_btn)

        # Crosshair
        self._crosshair_btn = QPushButton("✛")
        self._crosshair_btn.setToolTip("Crosshair (coordenadas)")
        self._crosshair_btn.setCheckable(True)
        self._crosshair_btn.clicked.connect(self.toggle_crosshair)
        layout.addWidget(self._crosshair_btn)

        # Selection
        self._selection_btn = QPushButton("⬚")
        self._selection_btn.setToolTip("Seleção de região")
        self._selection_btn.setCheckable(True)
        self._selection_btn.clicked.connect(self.toggle_selection)
        layout.addWidget(self._selection_btn)

        # Separador
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet("color: #dee2e6;")
        layout.addWidget(sep2)

        # Configure
        config_btn = QPushButton("⚙")
        config_btn.setToolTip("Configurar eixos")
        config_btn.clicked.connect(self.configure_axes)
        layout.addWidget(config_btn)

        # Copy
        copy_btn = QPushButton("📋")
        copy_btn.setToolTip("Copiar para clipboard")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(copy_btn)

        # Save
        save_btn = QPushButton("💾")
        save_btn.setToolTip("Salvar imagem")
        save_btn.clicked.connect(self._save_image)
        layout.addWidget(save_btn)

        layout.addStretch()
        
        # Coordenadas do mouse (tooltip em tempo real)
        self._coord_label = QLabel("")
        self._coord_label.setStyleSheet("font-size: 10px; color: #0d6efd; font-weight: bold; padding: 0 8px;")
        self._coord_label.setMinimumWidth(200)
        layout.addWidget(self._coord_label)

        # Info label
        self._info_label = QLabel("")
        self._info_label.setStyleSheet("font-size: 10px; color: #6c757d; padding-right: 8px;")
        layout.addWidget(self._info_label)

        return toolbar

    def _create_plot(self):
        """Cria o gráfico com base no tipo"""
        self.figure.clear()
        self.series_list = []  # Reset lista de séries

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
            logger.exception(f"plot_creation_error: {e}, plot_type={self.plot_type}")
            self._create_error_plot(str(e))

    def _create_2d_plot(self):
        """Cria gráfico 2D de linha com design moderno, suporte a múltiplas séries, legenda interativa"""
        ax = self.figure.add_subplot(111)
        self._ax = ax  # Guardar referência para adicionar séries depois

        # Plotar série principal
        line_obj = self._plot_single_series(ax, self.series, self._dataset_name, self.current_color_idx)
        self.series_list.append({
            "series": self.series,
            "dataset_name": self._dataset_name,
            "line": line_obj,
            "visible": True,
            "color_idx": self.current_color_idx,
        })
        self.current_color_idx += 1

        # Configuração do eixo
        self._setup_ax_style(ax)

        # Legenda interativa (clicável e arrastável)
        self._setup_interactive_legend(ax)

        # Estatísticas da série principal
        self._add_stats_box(ax, self.series)

    def _plot_single_series(self, ax, series, dataset_name: str, color_idx: int):
        """Plota uma única série no eixo e retorna o objeto de linha"""
        import matplotlib.dates as mdates
        
        values = series.values
        n_points = len(values)
        
        # Usar datetime se disponível, senão usar índice
        if self._t_datetime is not None and len(self._t_datetime) == n_points:
            # Converter datetime64 para matplotlib dates
            x_data = mdates.date2num(self._t_datetime.astype('datetime64[ms]').astype('datetime64[us]'))
            use_datetime = True
        else:
            x_data = np.arange(n_points)
            use_datetime = False

        # Otimização de performance
        if n_points > _perf_config.direct_render_limit:
            x_render, y_render = decimate_for_plot(
                x_data, values,
                target_points=_perf_config.target_display_points,
                method=DecimationMethod.MINMAX,
            )
            n_render = len(y_render)
        else:
            x_render, y_render = x_data, values
            n_render = n_points

        # Cor
        color = self.colors[color_idx % len(self.colors)]

        # Label com nome do dataset (não "valor")
        series_name = series.name if series.name != "valor" else dataset_name
        label = f"{dataset_name} - {series_name}" if series.name != "valor" else dataset_name

        # Plot
        if n_render > 1000:
            (line,) = ax.plot(x_render, y_render, linewidth=1.5, color=color, alpha=0.9,
                              label=label, picker=5)  # picker para clicável
        else:
            (line,) = ax.plot(x_render, y_render, linewidth=2.0, color=color, alpha=0.9,
                              label=label, picker=5,
                              markevery=max(1, n_render//50), marker="o", markersize=3,
                              markerfacecolor=color, markeredgecolor="white", markeredgewidth=0.5)

        return line

    def _setup_ax_style(self, ax):
        """Configura estilo moderno do eixo"""
        import matplotlib.dates as mdates

        # Título dinâmico
        n_series = len(self.series_list) if self.series_list else 1
        if n_series == 1:
            title = "Análise Temporal"
        else:
            title = f"Comparativo ({n_series} séries)"
        ax.set_title(title, fontsize=16, fontweight="bold", color="#212529", pad=20)

        # Configurar eixo X para datetime se disponível
        if self._t_datetime is not None and len(self._t_datetime) > 0:
            ax.set_xlabel("Data/Hora", fontsize=13, color="#495057", fontweight="500")
            # Formatar ticks de data automaticamente
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            # Rotacionar labels para melhor legibilidade
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            self.figure.tight_layout()
        else:
            ax.set_xlabel("Índice da Amostra", fontsize=13, color="#495057", fontweight="500")
            
        ax.set_ylabel("Valor", fontsize=13, color="#495057", fontweight="500")

        # Grid moderno
        ax.grid(True, alpha=0.2, linestyle="-", linewidth=0.8, color="#dee2e6")
        ax.set_axisbelow(True)
        ax.set_facecolor("#fafbfc")

        # Bordas
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#dee2e6")
        ax.spines["bottom"].set_color("#dee2e6")
        ax.spines["left"].set_linewidth(1.2)
        ax.spines["bottom"].set_linewidth(1.2)

    def _setup_interactive_legend(self, ax):
        """Configura legenda interativa (clicável para ocultar/mostrar, arrastável)"""
        if not ax.get_legend_handles_labels()[1]:
            return

        legend = ax.legend(loc="upper right", frameon=True, fancybox=True, shadow=False,
                          facecolor="white", edgecolor="#e9ecef", framealpha=0.98,
                          fontsize=11)
        legend.get_frame().set_linewidth(1.5)
        legend.get_frame().set_boxstyle("round,pad=0.3")
        
        # Tornar legenda arrastável (método compatível com várias versões)
        try:
            legend.set_draggable(True)
        except AttributeError:
            try:
                legend.draggable(True)
            except Exception:
                pass  # Ignorar se não suportado

        self._legend = legend
        self._legend_line_map = {}

        # Mapear linhas da legenda para linhas do plot
        legend_lines = legend.get_lines()
        for i, legend_line in enumerate(legend_lines):
            if i < len(self.series_list):
                legend_line.set_picker(5)  # Tornar clicável
                self._legend_line_map[legend_line] = self.series_list[i]

        # Conectar evento de clique na legenda (apenas uma vez)
        if not hasattr(self, "_pick_cid") or self._pick_cid is None:
            self._pick_cid = self.canvas.mpl_connect("pick_event", self._on_legend_pick)

    def _on_legend_pick(self, event):
        """Handler para clique na legenda - oculta/mostra série"""
        legend_line = event.artist

        # Verificar se é uma linha da legenda
        if legend_line not in self._legend_line_map:
            return

        series_info = self._legend_line_map[legend_line]
        plot_line = series_info["line"]
        visible = series_info["visible"]

        # Toggle visibilidade
        new_visible = not visible
        plot_line.set_visible(new_visible)
        series_info["visible"] = new_visible

        # Atualizar alpha da linha da legenda
        legend_line.set_alpha(1.0 if new_visible else 0.2)

        self.canvas.draw_idle()
        logger.debug(f"series_visibility_toggled: visible={new_visible}")

    def _add_stats_box(self, ax, series):
        """Adiciona caixa de estatísticas"""
        values = series.values
        n_points = len(values)
        std_val = np.std(values)

        stats_text = f"ESTATÍSTICAS\n" \
                    f"Pontos: {n_points:,}\n" \
                    f"Min: {np.min(values):.3f}\n" \
                    f"Max: {np.max(values):.3f}\n" \
                    f"Média: {np.mean(values):.3f}\n" \
                    f"Desvio: {std_val:.3f}"

        self._stats_text = ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
               verticalalignment="top", fontsize=9, fontweight="500",
               bbox={"boxstyle": "round,pad=0.6", "facecolor": "white",
                        "edgecolor": "#e9ecef", "alpha": 0.95, "linewidth": 1.2})

    def add_series(self, series, dataset_name: str = ""):
        """Adiciona uma nova série ao gráfico existente (para múltiplas séries no mesmo plot)"""
        if self.plot_type != "2d" or not hasattr(self, "_ax"):
            logger.warning("add_series: only supported for 2d plots")
            return False

        try:
            ax = self._ax

            # Plotar nova série
            line_obj = self._plot_single_series(ax, series, dataset_name, self.current_color_idx)
            self.series_list.append({
                "series": series,
                "dataset_name": dataset_name,
                "line": line_obj,
                "visible": True,
                "color_idx": self.current_color_idx,
            })
            self.current_color_idx += 1

            # Atualizar título
            n_series = len(self.series_list)
            ax.set_title(f"Comparativo ({n_series} séries)", fontsize=16, fontweight="bold", color="#212529", pad=20)

            # Recriar legenda interativa
            self._setup_interactive_legend(ax)

            # Ajustar limites do eixo
            ax.relim()
            ax.autoscale_view()

            self.canvas.draw()
            logger.info(f"series_added_to_plot: {dataset_name}/{series.name}, total={n_series}")
            return True

        except Exception as e:
            logger.exception(f"add_series_error: {e}")
            return False

    # === DRAG & DROP para adicionar séries ===
    def dragEnterEvent(self, event):
        """Aceita drag de séries"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            # Visual feedback
            self.canvas.setStyleSheet("border: 3px solid #198754;")

    def dragLeaveEvent(self, event):
        """Remove visual feedback"""
        self.canvas.setStyleSheet("")

    def dropEvent(self, event):
        """Adiciona série dropada ao gráfico"""
        if event.mimeData().hasText():
            data = event.mimeData().text().split("|")
            if len(data) == 2:
                dataset_id, series_id = data
                self.series_drop_requested.emit(dataset_id, series_id)
                event.acceptProposedAction()
                logger.info(f"series_drop_on_plot: {dataset_id}/{series_id}")
        self.canvas.setStyleSheet("")


    def _create_3d_plot(self):
        """Cria visualização 3D (superfície)"""
        ax = self.figure.add_subplot(111, projection="3d")

        values = self.series.values
        n_points = len(values)

        # Criar dados 3D simulados baseados na série
        # Grid para superfície
        grid_size = min(50, int(np.sqrt(n_points)))
        grid_size = max(grid_size, 5)

        x = np.linspace(0, 1, grid_size)
        y = np.linspace(0, 1, grid_size)
        X, Y = np.meshgrid(x, y)

        # Interpolar dados para grid 2D
        indices = np.linspace(0, n_points-1, grid_size*grid_size).astype(int)
        z_data = values[indices].reshape(grid_size, grid_size)

        # Surface plot
        surf = ax.plot_surface(X, Y, z_data, cmap="viridis", alpha=0.8,
                              linewidth=0, antialiased=True,
                              label=f"{self.series.name}")

        # Personalização
        ax.set_title(f"{self.series.name} - Visualização 3D",
                    fontsize=14, fontweight="bold")
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
        grid_size = max(grid_size, 10)

        # Preencher com zeros se necessário
        matrix_size = grid_size * grid_size
        if matrix_size > n_points:
            padded_values = np.pad(values, (0, matrix_size - n_points), "constant")
        else:
            padded_values = values[:matrix_size]

        heat_data = padded_values.reshape(grid_size, grid_size)

        # Heatmap
        im = ax.imshow(heat_data, cmap="plasma", aspect="auto", interpolation="bilinear")

        # Personalização
        ax.set_title(f"{self.series.name} - Heatmap", fontsize=14, fontweight="bold")
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
        scatter = ax.scatter(x_data, values, c=values, cmap="viridis",
                           alpha=0.7, s=20, edgecolors="black", linewidth=0.5,
                           label=f"{self.series.name}")

        # Personalização
        ax.set_title(f"{self.series.name} - Scatter Plot",
                    fontsize=14, fontweight="bold")
        ax.set_xlabel("Índice da Amostra")
        ax.set_ylabel(f"Valor ({self.series.unit})")

        # Grid, legenda e colorbar
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)

        # Legenda
        legend = ax.legend(loc="upper right", frameon=True, fancybox=True, shadow=True,
                          facecolor="white", edgecolor="#dee2e6", framealpha=0.95)
        legend.get_frame().set_linewidth(1)

        # Colorbar com label
        cbar = self.figure.colorbar(scatter, ax=ax)
        cbar.set_label(f"Intensidade - {self.series.name} ({self.series.unit})",
                      rotation=270, labelpad=15)

    def _create_error_plot(self, error_msg: str):
        """Cria plot de erro quando algo falha"""
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, f"Erro na visualização:\n{error_msg}",
               transform=ax.transAxes, ha="center", va="center",
               fontsize=12, color="red",
               bbox={"boxstyle": "round", "facecolor": "#ffe6e6", "alpha": 0.8})
        ax.set_title("Erro na Visualização", fontsize=14, color="red")
        ax.axis("off")

    # === TOOLBAR ACTIONS ===

    def _zoom_in(self):
        """Zoom in 20%"""
        try:
            ax = self.figure.gca()
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) * 0.4  # 80% of original
            y_range = (ylim[1] - ylim[0]) * 0.4

            ax.set_xlim(x_center - x_range, x_center + x_range)
            ax.set_ylim(y_center - y_range, y_center + y_range)
            self.canvas.draw()

            self._info_label.setText("Zoom: +20%")
            logger.debug("zoom_in_applied")
        except Exception as e:
            logger.exception(f"zoom_in_error: {e}")

    def _zoom_out(self):
        """Zoom out 20%"""
        try:
            ax = self.figure.gca()
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) * 0.6  # 120% of original
            y_range = (ylim[1] - ylim[0]) * 0.6

            ax.set_xlim(x_center - x_range, x_center + x_range)
            ax.set_ylim(y_center - y_range, y_center + y_range)
            self.canvas.draw()

            self._info_label.setText("Zoom: -20%")
            logger.debug("zoom_out_applied")
        except Exception as e:
            logger.exception(f"zoom_out_error: {e}")

    def _reset_view(self):
        """Reset view to fit all data"""
        try:
            ax = self.figure.gca()
            ax.autoscale(enable=True, axis="both", tight=True)
            ax.relim()
            ax.autoscale_view()
            self.canvas.draw()

            self._info_label.setText("View resetado")
            logger.debug("view_reset")
        except Exception as e:
            logger.exception(f"reset_view_error: {e}")

    def _toggle_pan(self):
        """Toggle pan mode"""
        try:
            # Toggle pan state
            if hasattr(self, "_pan_enabled"):
                self._pan_enabled = not self._pan_enabled
            else:
                self._pan_enabled = True

            if self._pan_enabled:
                # Disable other modes
                if self._crosshair_enabled:
                    self.toggle_crosshair()
                if self._selection_enabled:
                    self.toggle_selection()

                # Enable pan
                self.canvas.mpl_connect("button_press_event", self._pan_press)
                self.canvas.mpl_connect("button_release_event", self._pan_release)
                self.canvas.mpl_connect("motion_notify_event", self._pan_motion)
                self._info_label.setText("Pan ativado")
                logger.debug("pan_enabled")
            else:
                self._info_label.setText("Pan desativado")
                logger.debug("pan_disabled")

            self._pan_btn.setChecked(self._pan_enabled)
        except Exception as e:
            logger.exception(f"toggle_pan_error: {e}")

    def _pan_press(self, event):
        """Handle pan press"""
        if event.button == 1 and self._pan_enabled:
            self._pan_start = (event.xdata, event.ydata)

    def _pan_release(self, event):
        """Handle pan release"""
        self._pan_start = None

    def _pan_motion(self, event):
        """Handle pan motion"""
        if not self._pan_enabled or self._pan_start is None:
            return
        if event.xdata is None or event.ydata is None:
            return

        try:
            ax = self.figure.gca()
            dx = self._pan_start[0] - event.xdata
            dy = self._pan_start[1] - event.ydata

            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

            ax.set_xlim(xlim[0] + dx, xlim[1] + dx)
            ax.set_ylim(ylim[0] + dy, ylim[1] + dy)
            self.canvas.draw()
        except Exception:
            pass

    def _save_image(self):
        """Save plot as image"""
        try:
            from PyQt6.QtWidgets import QFileDialog

            formats = "PNG (*.png);;SVG (*.svg);;PDF (*.pdf);;JPEG (*.jpg)"
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self, "Salvar Imagem",
                f"{self.series.name}_plot.png",
                formats,
            )

            if file_path:
                # Determinar formato pelo filtro selecionado
                if "SVG" in selected_filter:
                    fmt = "svg"
                elif "PDF" in selected_filter:
                    fmt = "pdf"
                elif "JPEG" in selected_filter:
                    fmt = "jpg"
                else:
                    fmt = "png"

                self.figure.savefig(file_path, format=fmt, dpi=150,
                                   bbox_inches="tight", facecolor="white")

                self._info_label.setText(f"Salvo: {file_path.split('/')[-1]}")
                logger.info(f"plot_saved: {file_path}")

                QMessageBox.information(self, "Sucesso",
                    f"Imagem salva em:\n{file_path}")
        except Exception as e:
            logger.exception(f"save_image_error: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao salvar imagem:\n{e!s}")

    def _show_context_menu(self, position):
        """Mostra menu de contexto moderno para o gráfico"""
        try:
            from PyQt6.QtGui import QAction
            from PyQt6.QtWidgets import QMenu

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

            # Título (usando widget label para estilização em vez de QAction.setStyleSheet)
            title_action = QAction(f"📊 Gráfico {self.plot_type.upper()}", self)
            title_action.setEnabled(False)
            # Nota: QAction não suporta setStyleSheet em PyQt6 - o estilo é definido no QMenu
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

            # Crosshair toggle
            crosshair_text = "❌ Desativar Crosshair" if self._crosshair_enabled else "➕ Ativar Crosshair"
            crosshair_action = QAction(crosshair_text, self)
            crosshair_action.triggered.connect(self.toggle_crosshair)
            menu.addAction(crosshair_action)

            # Selection (brush) toggle
            selection_text = "❌ Desativar Seleção" if self._selection_enabled else "🎯 Ativar Seleção"
            selection_action = QAction(selection_text, self)
            selection_action.triggered.connect(self.toggle_selection)
            menu.addAction(selection_action)

            # Clear selection
            if self._selection_rect:
                clear_sel_action = QAction("🗑️ Limpar Seleção", self)
                clear_sel_action.triggered.connect(self.clear_selection)
                menu.addAction(clear_sel_action)

            menu.addSeparator()
            
            # === CÁLCULOS MATEMÁTICOS ===
            calc_menu = menu.addMenu("🧮 Cálculos")
            
            # Derivadas
            deriv_menu = calc_menu.addMenu("📈 Derivadas")
            deriv1_action = QAction("1ª Derivada", self)
            deriv1_action.triggered.connect(lambda: self._request_calculation("derivative", {"order": 1}))
            deriv_menu.addAction(deriv1_action)
            deriv2_action = QAction("2ª Derivada", self)
            deriv2_action.triggered.connect(lambda: self._request_calculation("derivative", {"order": 2}))
            deriv_menu.addAction(deriv2_action)
            deriv3_action = QAction("3ª Derivada", self)
            deriv3_action.triggered.connect(lambda: self._request_calculation("derivative", {"order": 3}))
            deriv_menu.addAction(deriv3_action)
            
            # Integral
            integral_action = QAction("∫ Integral", self)
            integral_action.triggered.connect(lambda: self._request_calculation("integral", {}))
            calc_menu.addAction(integral_action)
            
            # Área sob curva
            area_action = QAction("📏 Área sob Curva", self)
            area_action.triggered.connect(lambda: self._request_calculation("area", {}))
            calc_menu.addAction(area_action)
            
            calc_menu.addSeparator()
            
            # Interpolação
            interp_menu = calc_menu.addMenu("📐 Interpolação")
            interp_linear_action = QAction("Linear", self)
            interp_linear_action.triggered.connect(lambda: self._request_calculation("interpolation", {"method": "linear"}))
            interp_menu.addAction(interp_linear_action)
            interp_cubic_action = QAction("Cúbica", self)
            interp_cubic_action.triggered.connect(lambda: self._request_calculation("interpolation", {"method": "cubic_spline"}))
            interp_menu.addAction(interp_cubic_action)
            interp_akima_action = QAction("Akima", self)
            interp_akima_action.triggered.connect(lambda: self._request_calculation("interpolation", {"method": "akima"}))
            interp_menu.addAction(interp_akima_action)
            
            # Filtros
            filter_menu = calc_menu.addMenu("🎚️ Filtros")
            smooth_action = QAction("Suavização (Moving Average)", self)
            smooth_action.triggered.connect(lambda: self._request_calculation("filter", {"type": "moving_average"}))
            filter_menu.addAction(smooth_action)
            savgol_action = QAction("Savitzky-Golay", self)
            savgol_action.triggered.connect(lambda: self._request_calculation("filter", {"type": "savgol"}))
            filter_menu.addAction(savgol_action)
            
            menu.addSeparator()
            
            # === EIXO Y SECUNDÁRIO ===
            axis_menu = menu.addMenu("📊 Eixos")
            add_y_axis_action = QAction("➕ Adicionar Eixo Y Secundário", self)
            add_y_axis_action.triggered.connect(self._add_secondary_y_axis)
            axis_menu.addAction(add_y_axis_action)
            
            menu.addSeparator()

            # === OPÇÕES DE VISUALIZAÇÃO AVANÇADAS ===
            # Sombrear área sob curva
            shade_action = QAction("🎨 Sombrear Área sob Curva", self)
            shade_action.triggered.connect(self._toggle_area_shade)
            menu.addAction(shade_action)

            # Eixo Y secundário (se tiver mais de uma série)
            if len(self.series_list) > 1:
                secondary_menu = menu.addMenu("📊 Eixo Y Secundário")
                for i, series_info in enumerate(self.series_list[1:], 1):
                    series_name = series_info["dataset_name"]
                    is_secondary = series_info.get("secondary_axis", False)
                    prefix = "✓ " if is_secondary else ""
                    action = QAction(f"{prefix}{series_name}", self)
                    action.triggered.connect(lambda checked, idx=i: self._toggle_secondary_axis(idx))
                    secondary_menu.addAction(action)

            menu.addSeparator()

            # Copiar para clipboard
            copy_action = QAction("📋 Copiar para Clipboard", self)
            copy_action.triggered.connect(self.copy_to_clipboard)
            menu.addAction(copy_action)

            menu.addSeparator()

            # Configure axes
            axes_action = QAction("📐 Configurar Eixos", self)
            axes_action.triggered.connect(self.configure_axes)
            menu.addAction(axes_action)

            # Propriedades
            props_action = QAction("⚙️ Propriedades do Gráfico", self)
            props_action.triggered.connect(self._show_properties)
            menu.addAction(props_action)

            # Mostrar menu
            menu.exec(self.mapToGlobal(position))

        except Exception as e:
            logger.exception(f"context_menu_error: {e}")

    def _export_png(self):
        """Exporta gráfico como PNG"""
        try:
            from PyQt6.QtWidgets import QFileDialog

            filename, _ = QFileDialog.getSaveFileName(
                self, "Salvar Gráfico", f"{self.series.name}_{self.plot_type}.png",
                "PNG files (*.png);;All files (*.*)",
            )

            if filename:
                self.figure.savefig(filename, dpi=300, bbox_inches="tight", facecolor="white")
                logger.info(f"plot_exported_png: {filename}")

        except Exception as e:
            logger.exception(f"export_png_error: {e}")

    def _export_pdf(self):
        """Exporta gráfico como PDF"""
        try:
            from PyQt6.QtWidgets import QFileDialog

            filename, _ = QFileDialog.getSaveFileName(
                self, "Salvar Gráfico", f"{self.series.name}_{self.plot_type}.pdf",
                "PDF files (*.pdf);;All files (*.*)",
            )

            if filename:
                self.figure.savefig(filename, format="pdf", bbox_inches="tight", facecolor="white")
                logger.info(f"plot_exported_pdf: {filename}")

        except Exception as e:
            logger.exception(f"export_pdf_error: {e}")

    def _zoom_to_fit(self):
        """Ajusta zoom para mostrar todos os dados"""
        try:
            for ax in self.figure.get_axes():
                ax.relim()
                ax.autoscale()
            self.canvas.draw()

        except Exception as e:
            logger.exception(f"zoom_fit_error: {e}")

    def _toggle_grid(self):
        """Alterna exibição do grid"""
        try:
            for ax in self.figure.get_axes():
                ax.grid(not ax.get_gridlines()[0].get_visible() if ax.get_gridlines() else True)
            self.canvas.draw()

        except Exception as e:
            logger.exception(f"toggle_grid_error: {e}")

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
            logger.exception(f"toggle_legend_error: {e}")

    def _request_calculation(self, calc_type: str, params: dict):
        """Solicita cálculo para a série atual"""
        try:
            if not self.series_list:
                QMessageBox.warning(self, "Aviso", "Nenhuma série disponível para cálculo.")
                return
                
            # Usar primeira série visível
            series_info = self.series_list[0]
            dataset_name = series_info["dataset_name"]
            series_id = series_info["series"].series_id if hasattr(series_info["series"], "series_id") else "unknown"
            
            # Emitir sinal de cálculo solicitado
            self.calculation_requested.emit(dataset_name, series_id, calc_type, params)
            
            # Feedback visual
            self._info_label.setText(f"Cálculo: {calc_type}")
            logger.info(f"calculation_requested: type={calc_type}, params={params}")
            
            # Mostrar mensagem temporária
            QMessageBox.information(self, "Cálculo Solicitado",
                f"Tipo: {calc_type}\n"
                f"Série: {dataset_name}\n"
                f"Parâmetros: {params}\n\n"
                "Use o painel de Operações para configurar e executar o cálculo.")
                
        except Exception as e:
            logger.exception(f"request_calculation_error: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao solicitar cálculo: {e}")

    def _add_secondary_y_axis(self):
        """Adiciona eixo Y secundário ao gráfico"""
        try:
            if not hasattr(self, "_ax") or self._ax is None:
                QMessageBox.warning(self, "Aviso", "Nenhum gráfico disponível.")
                return
                
            # Verificar se já existe eixo secundário
            if hasattr(self, "_ax2") and self._ax2 is not None:
                QMessageBox.information(self, "Info", "Eixo Y secundário já existe.")
                return
                
            # Criar eixo Y secundário
            self._ax2 = self._ax.twinx()
            self._ax2.set_ylabel("Eixo Y Secundário", fontsize=13, color="#dc3545", fontweight="500")
            self._ax2.spines["right"].set_color("#dc3545")
            self._ax2.tick_params(axis='y', labelcolor='#dc3545')
            
            self.canvas.draw()
            self._info_label.setText("Eixo Y secundário adicionado")
            logger.info("secondary_y_axis_added")
            
            QMessageBox.information(self, "Sucesso",
                "Eixo Y secundário criado.\n\n"
                "Arraste uma nova série para o gráfico para plotá-la no eixo secundário.")
                
        except Exception as e:
            logger.exception(f"add_secondary_y_axis_error: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao criar eixo secundário: {e}")

    def _toggle_area_shade(self):
        """Alterna sombreamento da área sob a curva"""
        try:
            if not hasattr(self, "_area_fills"):
                self._area_fills = []

            ax = self.figure.get_axes()[0] if self.figure.get_axes() else None
            if not ax:
                return

            # Se já tem preenchimento, remove
            if self._area_fills:
                for fill in self._area_fills:
                    try:
                        fill.remove()
                    except Exception:
                        pass
                self._area_fills = []
                self.canvas.draw()
                self._info_label.setText("Área removida")
                logger.info("area_shade_removed")
                return

            # Adicionar preenchimento para cada série
            for series_info in self.series_list:
                line = series_info["line"]
                if not line.get_visible():
                    continue

                x_data = line.get_xdata()
                y_data = line.get_ydata()
                color = line.get_color()

                fill = ax.fill_between(x_data, y_data, alpha=0.3, color=color)
                self._area_fills.append(fill)

            self.canvas.draw()
            self._info_label.setText("Área sombreada")
            logger.info("area_shade_added")

        except Exception as e:
            logger.exception(f"toggle_area_shade_error: {e}")

    def _toggle_secondary_axis(self, series_idx: int):
        """Move uma série para o eixo Y secundário"""
        try:
            if series_idx >= len(self.series_list):
                return

            series_info = self.series_list[series_idx]
            is_secondary = series_info.get("secondary_axis", False)

            ax = self.figure.get_axes()[0]
            line = series_info["line"]

            if is_secondary:
                # Mover de volta para eixo principal
                # Remover linha do eixo secundário
                if hasattr(self, "_secondary_ax") and self._secondary_ax:
                    line.remove()
                    # Replotar no eixo principal
                    series = series_info["series"]
                    new_line = self._plot_single_series(ax, series, series_info["dataset_name"], series_info["color_idx"])
                    series_info["line"] = new_line
                    series_info["secondary_axis"] = False

                    # Remover eixo secundário se não houver mais séries nele
                    has_secondary = any(s.get("secondary_axis", False) for s in self.series_list)
                    if not has_secondary and hasattr(self, "_secondary_ax"):
                        self._secondary_ax.remove()
                        self._secondary_ax = None
            else:
                # Mover para eixo secundário
                # Criar eixo secundário se necessário
                if not hasattr(self, "_secondary_ax") or not self._secondary_ax:
                    self._secondary_ax = ax.twinx()
                    self._secondary_ax.set_ylabel("Eixo Secundário", fontsize=13, color="#495057")

                # Remover linha do eixo principal
                line.remove()

                # Replotar no eixo secundário
                series = series_info["series"]
                color = self.colors[series_info["color_idx"] % len(self.colors)]
                values = series.values
                x_data = np.arange(len(values))

                (new_line,) = self._secondary_ax.plot(x_data, values, linewidth=1.5, color=color,
                                                       linestyle="--", alpha=0.9,
                                                       label=f"{series_info['dataset_name']} (sec)",
                                                       picker=5)
                series_info["line"] = new_line
                series_info["secondary_axis"] = True

            # Recriar legenda
            self._setup_interactive_legend(ax)
            self.canvas.draw()

            logger.info(f"secondary_axis_toggled: series={series_idx}, is_secondary={not is_secondary}")

        except Exception as e:
            logger.exception(f"toggle_secondary_axis_error: {e}")

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
            logger.exception(f"show_properties_error: {e}")

    # ========== CROSSHAIR METHODS ==========

    def toggle_crosshair(self):
        """Alterna exibição do crosshair"""
        self._crosshair_enabled = not self._crosshair_enabled

        if self._crosshair_enabled:
            self._enable_crosshair()
        else:
            self._disable_crosshair()

    def _enable_crosshair(self):
        """Habilita o crosshair com label de coordenadas"""
        try:
            if self.figure.get_axes():
                ax = self.figure.get_axes()[0]

                # Criar linhas do crosshair (inicialmente invisíveis)
                self._crosshair_hline = ax.axhline(
                    y=0, color="#dc3545", linestyle="--",
                    linewidth=1, alpha=0.7, visible=False,
                )
                self._crosshair_vline = ax.axvline(
                    x=0, color="#dc3545", linestyle="--",
                    linewidth=1, alpha=0.7, visible=False,
                )

                # Criar texto das coordenadas
                self._crosshair_text = ax.text(
                    0, 0, "", transform=ax.transData,
                    fontsize=9, fontweight="bold",
                    bbox={"boxstyle": "round,pad=0.4", "facecolor": "#fff3cd",
                             "edgecolor": "#ffc107", "alpha": 0.95, "linewidth": 1.5},
                    ha="left", va="bottom", visible=False,
                )

                # Conectar evento de movimento do mouse
                self._motion_cid = self.canvas.mpl_connect(
                    "motion_notify_event", self._on_mouse_move,
                )

                self.canvas.draw()
                logger.info("Crosshair enabled")

        except Exception as e:
            logger.exception(f"enable_crosshair_error: {e}")

    def _disable_crosshair(self):
        """Desabilita o crosshair"""
        try:
            # Desconectar evento
            if self._motion_cid is not None:
                self.canvas.mpl_disconnect(self._motion_cid)
                self._motion_cid = None

            # Remover linhas e texto
            if self._crosshair_hline is not None:
                self._crosshair_hline.remove()
                self._crosshair_hline = None

            if self._crosshair_vline is not None:
                self._crosshair_vline.remove()
                self._crosshair_vline = None

            if self._crosshair_text is not None:
                self._crosshair_text.remove()
                self._crosshair_text = None

            self.canvas.draw()
            logger.info("Crosshair disabled")

        except Exception as e:
            logger.exception(f"disable_crosshair_error: {e}")

    def _on_mouse_move(self, event):
        """Handler para movimento do mouse - atualiza crosshair"""
        try:
            if not self._crosshair_enabled:
                return

            # Verificar se está dentro de um eixo
            if event.inaxes is None:
                # Fora do eixo - esconder crosshair
                if self._crosshair_hline:
                    self._crosshair_hline.set_visible(False)
                if self._crosshair_vline:
                    self._crosshair_vline.set_visible(False)
                if self._crosshair_text:
                    self._crosshair_text.set_visible(False)
                self.canvas.draw_idle()
                return

            ax = event.inaxes
            x, y = event.xdata, event.ydata

            if x is None or y is None:
                return

            # Atualizar posição das linhas
            if self._crosshair_hline:
                self._crosshair_hline.set_ydata([y, y])
                self._crosshair_hline.set_visible(True)

            if self._crosshair_vline:
                self._crosshair_vline.set_xdata([x, x])
                self._crosshair_vline.set_visible(True)

            # Atualizar texto das coordenadas
            if self._crosshair_text:
                # Formatar coordenadas
                x_display = f"{x:.2f}" if abs(x) < 10000 else f"{x:.2e}"
                y_display = f"{y:.4f}" if abs(y) < 10000 else f"{y:.2e}"
                coord_text = f"X: {x_display}\nY: {y_display}"

                self._crosshair_text.set_text(coord_text)

                # Posição do texto - um pouco deslocado do cursor
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                x_offset = (xlim[1] - xlim[0]) * 0.02
                y_offset = (ylim[1] - ylim[0]) * 0.02

                # Ajustar lado do texto para não sair do gráfico
                if x > (xlim[0] + xlim[1]) / 2:
                    ha = "right"
                    text_x = x - x_offset
                else:
                    ha = "left"
                    text_x = x + x_offset

                if y > (ylim[0] + ylim[1]) / 2:
                    va = "top"
                    text_y = y - y_offset
                else:
                    va = "bottom"
                    text_y = y + y_offset

                self._crosshair_text.set_position((text_x, text_y))
                self._crosshair_text.set_ha(ha)
                self._crosshair_text.set_va(va)
                self._crosshair_text.set_visible(True)

            # Emitir sinal de coordenadas
            self.coordinates_changed.emit(x, y)

            # Redesenhar (usando draw_idle para melhor performance)
            self.canvas.draw_idle()

        except Exception as e:
            logger.exception(f"crosshair_mouse_move_error: {e}")

    def is_crosshair_enabled(self) -> bool:
        """Retorna se o crosshair está habilitado"""
        return self._crosshair_enabled

    # ========== COPY TO CLIPBOARD ==========

    def copy_to_clipboard(self):
        """Copia o gráfico para a área de transferência"""
        try:
            import io

            from PyQt6.QtGui import QImage
            from PyQt6.QtWidgets import QApplication

            # Renderizar figura para buffer
            buf = io.BytesIO()
            self.figure.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
            buf.seek(0)

            # Criar QImage a partir do buffer
            image_data = buf.read()
            qimage = QImage()
            qimage.loadFromData(image_data)

            # Copiar para clipboard
            clipboard = QApplication.clipboard()
            clipboard.setImage(qimage)

            logger.info("Plot copied to clipboard")

            # Mostrar feedback visual
            from PyQt6.QtWidgets import QToolTip
            QToolTip.showText(self.canvas.mapToGlobal(self.canvas.rect().center()),
                             "✓ Copiado para área de transferência!",
                             self, self.canvas.rect(), 1500)

        except Exception as e:
            logger.exception(f"copy_to_clipboard_error: {e}")

    # ========== REGION SELECTION (BRUSH) ==========

    def toggle_selection(self):
        """Alterna modo de seleção de região"""
        self._selection_enabled = not self._selection_enabled

        if self._selection_enabled:
            self._enable_selection()
        else:
            self._disable_selection()

    def _enable_selection(self):
        """Habilita seleção de região por brush"""
        try:
            # Desabilitar crosshair se estiver ativo
            if self._crosshair_enabled:
                self.toggle_crosshair()

            # Conectar eventos de mouse
            self._press_cid = self.canvas.mpl_connect("button_press_event", self._on_selection_press)
            self._release_cid = self.canvas.mpl_connect("button_release_event", self._on_selection_release)
            self._drag_cid = self.canvas.mpl_connect("motion_notify_event", self._on_selection_drag)

            logger.info("Region selection enabled")

            # Feedback visual
            from PyQt6.QtWidgets import QToolTip
            QToolTip.showText(self.canvas.mapToGlobal(self.canvas.rect().center()),
                             "🎯 Modo seleção ativo - arraste para selecionar região",
                             self, self.canvas.rect(), 2000)

        except Exception as e:
            logger.exception(f"enable_selection_error: {e}")

    def _disable_selection(self):
        """Desabilita seleção de região"""
        try:
            # Desconectar eventos
            if self._press_cid:
                self.canvas.mpl_disconnect(self._press_cid)
                self._press_cid = None
            if self._release_cid:
                self.canvas.mpl_disconnect(self._release_cid)
                self._release_cid = None
            if self._drag_cid:
                self.canvas.mpl_disconnect(self._drag_cid)
                self._drag_cid = None

            # Remover retângulo de seleção se existir
            if self._selection_rect:
                self._selection_rect.remove()
                self._selection_rect = None
                self.canvas.draw()

            logger.info("Region selection disabled")

        except Exception as e:
            logger.exception(f"disable_selection_error: {e}")

    def _on_selection_press(self, event):
        """Handler para início da seleção"""
        if event.inaxes is None or event.button != 1:  # Só botão esquerdo
            return

        self._selection_start = (event.xdata, event.ydata)

        # Remover retângulo anterior se existir
        if self._selection_rect:
            self._selection_rect.remove()
            self._selection_rect = None

    def _on_selection_drag(self, event):
        """Handler para arrastar seleção"""
        if self._selection_start is None or event.inaxes is None:
            return

        if event.xdata is None or event.ydata is None:
            return

        ax = event.inaxes
        x0, y0 = self._selection_start
        x1, y1 = event.xdata, event.ydata

        # Calcular dimensões
        width = x1 - x0
        height = y1 - y0

        # Remover retângulo anterior
        if self._selection_rect:
            self._selection_rect.remove()

        # Criar novo retângulo
        from matplotlib.patches import Rectangle
        self._selection_rect = ax.add_patch(
            Rectangle((x0, y0), width, height,
                      fill=True, facecolor="#0d6efd", alpha=0.2,
                      edgecolor="#0d6efd", linewidth=2, linestyle="--"),
        )

        self.canvas.draw_idle()

    def _on_selection_release(self, event):
        """Handler para fim da seleção"""
        if self._selection_start is None or event.inaxes is None:
            return

        if event.xdata is None or event.ydata is None:
            self._selection_start = None
            return

        x0, y0 = self._selection_start
        x1, y1 = event.xdata, event.ydata

        # Normalizar coordenadas
        x_min, x_max = min(x0, x1), max(x0, x1)
        y_min, y_max = min(y0, y1), max(y0, y1)

        # Emitir sinal de região selecionada
        self.region_selected.emit(x_min, x_max, y_min, y_max)

        # Extrair dados na região
        self._extract_region_data(x_min, x_max)

        self._selection_start = None
        logger.info(f"Region selected: X=[{x_min:.2f}, {x_max:.2f}], Y=[{y_min:.2f}, {y_max:.2f}]")

    def _extract_region_data(self, x_min: float, x_max: float):
        """Extrai dados da região selecionada"""
        try:
            values = self.series.values
            n_points = len(values)

            # Converter coordenadas X para índices
            idx_min = max(0, int(x_min))
            idx_max = min(n_points, int(x_max) + 1)

            if idx_min < idx_max:
                extracted = values[idx_min:idx_max]

                # Emitir dados extraídos
                self.data_extracted.emit(extracted)

                # Mostrar info
                from PyQt6.QtWidgets import QMessageBox
                msg = QMessageBox(self)
                msg.setWindowTitle("📊 Dados Extraídos")
                msg.setText("Região selecionada com sucesso!")
                msg.setInformativeText(
                    f"Pontos: {len(extracted):,}\n"
                    f"Índices: [{idx_min}, {idx_max})\n"
                    f"Min: {extracted.min():.4f}\n"
                    f"Max: {extracted.max():.4f}\n"
                    f"Média: {extracted.mean():.4f}",
                )
                msg.setIcon(QMessageBox.Icon.Information)
                msg.exec()

        except Exception as e:
            logger.exception(f"extract_region_data_error: {e}")

    def is_selection_enabled(self) -> bool:
        """Retorna se o modo de seleção está habilitado"""
        return self._selection_enabled

    def clear_selection(self):
        """Limpa seleção atual"""
        if self._selection_rect:
            self._selection_rect.remove()
            self._selection_rect = None
            self.canvas.draw()

    # ========== CONFIGURE AXES ==========

    def configure_axes(self):
        """Abre diálogo de configuração dos eixos"""
        try:
            if not self.figure.get_axes():
                return

            ax = self.figure.get_axes()[0]

            dialog = AxesConfigDialog(ax, self)
            if dialog.exec():
                config = dialog.get_config()
                self._apply_axes_config(ax, config)
                self.canvas.draw()

        except Exception as e:
            logger.exception(f"configure_axes_error: {e}")

    def _apply_axes_config(self, ax, config: dict):
        """Aplica configuração aos eixos"""
        try:
            # Título
            if config.get("title"):
                ax.set_title(config["title"], fontsize=config.get("title_size", 14),
                            fontweight="bold")

            # Labels
            if config.get("xlabel"):
                ax.set_xlabel(config["xlabel"], fontsize=config.get("label_size", 12))
            if config.get("ylabel"):
                ax.set_ylabel(config["ylabel"], fontsize=config.get("label_size", 12))

            # Limites
            if config.get("xlim_auto", True):
                ax.autoscale(axis="x")
            else:
                ax.set_xlim(config.get("xmin", 0), config.get("xmax", 1))

            if config.get("ylim_auto", True):
                ax.autoscale(axis="y")
            else:
                ax.set_ylim(config.get("ymin", 0), config.get("ymax", 1))

            # Grid
            ax.grid(config.get("show_grid", True), alpha=config.get("grid_alpha", 0.3))

            # Escala
            if config.get("xscale"):
                ax.set_xscale(config["xscale"])
            if config.get("yscale"):
                ax.set_yscale(config["yscale"])

            logger.info("Axes configuration applied")

        except Exception as e:
            logger.exception(f"apply_axes_config_error: {e}")

    # ========== SYNCHRONIZATION SUPPORT ==========

    def set_crosshair_position(self, x: float, y: float):
        """
        Define posição do crosshair (para sincronização)

        Args:
            x: Coordenada X
            y: Coordenada Y
        """
        if not self._crosshair_enabled:
            return

        try:
            if self._crosshair_hline:
                self._crosshair_hline.set_ydata([y, y])
                self._crosshair_hline.set_visible(True)

            if self._crosshair_vline:
                self._crosshair_vline.set_xdata([x, x])
                self._crosshair_vline.set_visible(True)

            if self._crosshair_text:
                x_display = f"{x:.2f}" if abs(x) < 10000 else f"{x:.2e}"
                y_display = f"{y:.4f}" if abs(y) < 10000 else f"{y:.2e}"
                self._crosshair_text.set_text(f"X: {x_display}\nY: {y_display}")
                self._crosshair_text.set_position((x, y))
                self._crosshair_text.set_visible(True)

            self.canvas.draw_idle()

        except Exception as e:
            logger.exception(f"set_crosshair_position_error: {e}")

    def set_selection_region(self, x1: float, x2: float, y1: float, y2: float):
        """
        Define região de seleção (para sincronização)

        Args:
            x1, x2: Coordenadas X da região
            y1, y2: Coordenadas Y da região
        """
        try:
            from matplotlib import patches

            if self.figure.get_axes():
                ax = self.figure.get_axes()[0]

                # Remover seleção anterior
                if self._selection_rect:
                    self._selection_rect.remove()

                # Criar nova seleção
                width = abs(x2 - x1)
                height = abs(y2 - y1)
                x_min = min(x1, x2)
                y_min = min(y1, y2)

                self._selection_rect = patches.Rectangle(
                    (x_min, y_min), width, height,
                    linewidth=2, edgecolor="#0d6efd", facecolor="#0d6efd",
                    alpha=0.2, linestyle="--",
                )
                ax.add_patch(self._selection_rect)
                self.canvas.draw_idle()

        except Exception as e:
            logger.exception(f"set_selection_region_error: {e}")

    def set_xlim(self, xmin: float, xmax: float):
        """Define limites do eixo X (para sincronização)"""
        try:
            if self.figure.get_axes():
                ax = self.figure.get_axes()[0]
                ax.set_xlim(xmin, xmax)
                self.canvas.draw_idle()
        except Exception as e:
            logger.exception(f"set_xlim_error: {e}")

    def set_ylim(self, ymin: float, ymax: float):
        """Define limites do eixo Y (para sincronização)"""
        try:
            if self.figure.get_axes():
                ax = self.figure.get_axes()[0]
                ax.set_ylim(ymin, ymax)
                self.canvas.draw_idle()
        except Exception as e:
            logger.exception(f"set_ylim_error: {e}")

    def get_xlim(self):
        """Retorna limites do eixo X"""
        try:
            if self.figure.get_axes():
                return self.figure.get_axes()[0].get_xlim()
        except Exception:
            pass
        return (0, 1)

    def get_ylim(self):
        """Retorna limites do eixo Y"""
        try:
            if self.figure.get_axes():
                return self.figure.get_axes()[0].get_ylim()
        except Exception:
            pass
        return (0, 1)


class AxesConfigDialog(QDialog, UiLoaderMixin):
    """Diálogo de configuração dos eixos"""

    UI_FILE = "desktop/ui_files/axesConfigDialog.ui"

    def __init__(self, ax, parent=None):
        super().__init__(parent)
        self.ax = ax

        self.setWindowTitle("⚙️ Configurar Eixos")
        self.setMinimumSize(400, 450)
        self.setModal(True)

        if not self._load_ui():
            self._setup_ui_fallback()
        else:
            self._setup_ui_from_file()
        self._load_current_values()

    def _setup_ui_from_file(self):
        """Configura widgets após carregar .ui"""
        # Busca widgets do arquivo .ui
        self._title_edit = self.findChild(QLineEdit, "title_edit")
        self._title_size_spin = self.findChild(QSpinBox, "title_size_spin")
        self._xlabel_edit = self.findChild(QLineEdit, "xlabel_edit")
        self._ylabel_edit = self.findChild(QLineEdit, "ylabel_edit")
        self._label_size_spin = self.findChild(QSpinBox, "label_size_spin")
        self._xlim_auto_check = self.findChild(QCheckBox, "xlim_auto_check")
        self._xmin_spin = self.findChild(QDoubleSpinBox, "xmin_spin")
        self._xmax_spin = self.findChild(QDoubleSpinBox, "xmax_spin")
        self._ylim_auto_check = self.findChild(QCheckBox, "ylim_auto_check")
        self._ymin_spin = self.findChild(QDoubleSpinBox, "ymin_spin")
        self._ymax_spin = self.findChild(QDoubleSpinBox, "ymax_spin")
        self._xscale_combo = self.findChild(QComboBox, "xscale_combo")
        self._yscale_combo = self.findChild(QComboBox, "yscale_combo")
        self._grid_check = self.findChild(QCheckBox, "grid_check")
        self._grid_alpha_spin = self.findChild(QDoubleSpinBox, "grid_alpha_spin")
        
        # Conecta sinais
        if self._xlim_auto_check:
            self._xlim_auto_check.stateChanged.connect(self._on_xlim_auto_changed)
        if self._ylim_auto_check:
            self._ylim_auto_check.stateChanged.connect(self._on_ylim_auto_changed)
        
        # Botões OK/Cancel
        ok_btn = self.findChild(QPushButton, "ok_btn")
        cancel_btn = self.findChild(QPushButton, "cancel_btn")
        if ok_btn:
            ok_btn.clicked.connect(self.accept)
        if cancel_btn:
            cancel_btn.clicked.connect(self.reject)

    def _setup_ui_fallback(self):
        """Configura interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Grupo: Título
        title_group = QGroupBox("📝 Título")
        title_layout = QFormLayout(title_group)

        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText("Título do gráfico")
        title_layout.addRow("Título:", self._title_edit)

        self._title_size_spin = QSpinBox()
        self._title_size_spin.setRange(8, 24)
        self._title_size_spin.setValue(14)
        title_layout.addRow("Tamanho:", self._title_size_spin)

        layout.addWidget(title_group)

        # Grupo: Labels
        labels_group = QGroupBox("🏷️ Labels")
        labels_layout = QFormLayout(labels_group)

        self._xlabel_edit = QLineEdit()
        self._xlabel_edit.setPlaceholderText("Label do eixo X")
        labels_layout.addRow("Eixo X:", self._xlabel_edit)

        self._ylabel_edit = QLineEdit()
        self._ylabel_edit.setPlaceholderText("Label do eixo Y")
        labels_layout.addRow("Eixo Y:", self._ylabel_edit)

        self._label_size_spin = QSpinBox()
        self._label_size_spin.setRange(8, 18)
        self._label_size_spin.setValue(12)
        labels_layout.addRow("Tamanho:", self._label_size_spin)

        layout.addWidget(labels_group)

        # Grupo: Limites X
        xlim_group = QGroupBox("↔️ Limites X")
        xlim_layout = QVBoxLayout(xlim_group)

        self._xlim_auto_check = QCheckBox("Auto-ajustar")
        self._xlim_auto_check.setChecked(True)
        self._xlim_auto_check.stateChanged.connect(self._on_xlim_auto_changed)
        xlim_layout.addWidget(self._xlim_auto_check)

        xlim_vals = QHBoxLayout()
        xlim_vals.addWidget(QLabel("Min:"))
        self._xmin_spin = QDoubleSpinBox()
        self._xmin_spin.setRange(-1e10, 1e10)
        self._xmin_spin.setDecimals(4)
        self._xmin_spin.setEnabled(False)
        xlim_vals.addWidget(self._xmin_spin)
        xlim_vals.addWidget(QLabel("Max:"))
        self._xmax_spin = QDoubleSpinBox()
        self._xmax_spin.setRange(-1e10, 1e10)
        self._xmax_spin.setDecimals(4)
        self._xmax_spin.setEnabled(False)
        xlim_vals.addWidget(self._xmax_spin)
        xlim_layout.addLayout(xlim_vals)

        layout.addWidget(xlim_group)

        # Grupo: Limites Y
        ylim_group = QGroupBox("↕️ Limites Y")
        ylim_layout = QVBoxLayout(ylim_group)

        self._ylim_auto_check = QCheckBox("Auto-ajustar")
        self._ylim_auto_check.setChecked(True)
        self._ylim_auto_check.stateChanged.connect(self._on_ylim_auto_changed)
        ylim_layout.addWidget(self._ylim_auto_check)

        ylim_vals = QHBoxLayout()
        ylim_vals.addWidget(QLabel("Min:"))
        self._ymin_spin = QDoubleSpinBox()
        self._ymin_spin.setRange(-1e10, 1e10)
        self._ymin_spin.setDecimals(4)
        self._ymin_spin.setEnabled(False)
        ylim_vals.addWidget(self._ymin_spin)
        ylim_vals.addWidget(QLabel("Max:"))
        self._ymax_spin = QDoubleSpinBox()
        self._ymax_spin.setRange(-1e10, 1e10)
        self._ymax_spin.setDecimals(4)
        self._ymax_spin.setEnabled(False)
        ylim_vals.addWidget(self._ymax_spin)
        ylim_layout.addLayout(ylim_vals)

        layout.addWidget(ylim_group)

        # Grupo: Escala
        scale_group = QGroupBox("📏 Escala")
        scale_layout = QFormLayout(scale_group)

        self._xscale_combo = QComboBox()
        self._xscale_combo.addItems(["linear", "log", "symlog"])
        scale_layout.addRow("Escala X:", self._xscale_combo)

        self._yscale_combo = QComboBox()
        self._yscale_combo.addItems(["linear", "log", "symlog"])
        scale_layout.addRow("Escala Y:", self._yscale_combo)

        layout.addWidget(scale_group)

        # Grupo: Grid
        grid_group = QGroupBox("⚏ Grid")
        grid_layout = QFormLayout(grid_group)

        self._grid_check = QCheckBox("Mostrar grid")
        self._grid_check.setChecked(True)
        grid_layout.addRow(self._grid_check)

        self._grid_alpha_spin = QDoubleSpinBox()
        self._grid_alpha_spin.setRange(0.0, 1.0)
        self._grid_alpha_spin.setSingleStep(0.1)
        self._grid_alpha_spin.setValue(0.3)
        grid_layout.addRow("Transparência:", self._grid_alpha_spin)

        layout.addWidget(grid_group)

        # Botões
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("✓ Aplicar")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        # Estilo
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                color: #0d6efd;
            }
        """)

    def _load_current_values(self):
        """Carrega valores atuais do eixo"""
        try:
            self._title_edit.setText(self.ax.get_title())
            self._xlabel_edit.setText(self.ax.get_xlabel())
            self._ylabel_edit.setText(self.ax.get_ylabel())

            xlim = self.ax.get_xlim()
            self._xmin_spin.setValue(xlim[0])
            self._xmax_spin.setValue(xlim[1])

            ylim = self.ax.get_ylim()
            self._ymin_spin.setValue(ylim[0])
            self._ymax_spin.setValue(ylim[1])

            # Grid - tentar detectar estado atual
            self._grid_check.setChecked(True)  # Assume grid ativo por padrão

        except Exception as e:
            logger.exception(f"load_axes_values_error: {e}")

    def _on_xlim_auto_changed(self, state):
        """Handler para mudança de auto X"""
        enabled = state != Qt.CheckState.Checked.value
        self._xmin_spin.setEnabled(enabled)
        self._xmax_spin.setEnabled(enabled)

    def _on_ylim_auto_changed(self, state):
        """Handler para mudança de auto Y"""
        enabled = state != Qt.CheckState.Checked.value
        self._ymin_spin.setEnabled(enabled)
        self._ymax_spin.setEnabled(enabled)

    def get_config(self) -> dict:
        """Retorna configuração definida"""
        return {
            "title": self._title_edit.text(),
            "title_size": self._title_size_spin.value(),
            "xlabel": self._xlabel_edit.text(),
            "ylabel": self._ylabel_edit.text(),
            "label_size": self._label_size_spin.value(),
            "xlim_auto": self._xlim_auto_check.isChecked(),
            "xmin": self._xmin_spin.value(),
            "xmax": self._xmax_spin.value(),
            "ylim_auto": self._ylim_auto_check.isChecked(),
            "ymin": self._ymin_spin.value(),
            "ymax": self._ymax_spin.value(),
            "xscale": self._xscale_combo.currentText(),
            "yscale": self._yscale_combo.currentText(),
            "show_grid": self._grid_check.isChecked(),
            "grid_alpha": self._grid_alpha_spin.value(),
        }


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
        self.setStyleSheet("""
            DropZone {
                border: 3px dashed #dee2e6;
                border-radius: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                font-weight: 600;
            }
            DropZone:hover {
                border: 3px dashed #0d6efd;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #e3f2fd, stop: 1 #f3e5f5);
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


class ModernVizPanel(QWidget, UiLoaderMixin):
    """
    Painel de visualização moderno com drag-and-drop

    Funcionalidades:
    - Zonas de drop para gráficos 2D/3D
    - Sistema intuitivo de drag-and-drop
    - Múltiplas visualizações em abas
    - Interface moderna e responsiva
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "desktop/ui_files/modernVizPanel.ui"

    # Signals
    plot_requested = pyqtSignal(str, str, str)  # dataset_id, series_id, plot_type
    calculation_requested = pyqtSignal(str, str, str, dict)  # dataset_id, series_id, calc_type, params

    def __init__(self, session_state: SessionState):
        super().__init__()

        self.session_state = session_state
        self._plots = []  # Lista de gráficos ativos

        # Tenta carregar do arquivo .ui, senão usa fallback
        if not self._load_ui():
            self._setup_modern_ui_fallback()
        else:
            self._setup_ui_from_file()
        
        self._setup_connections()
        logger.debug("modern_viz_panel_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        self._viz_tabs = self.findChild(QTabWidget, "vizTabs")
        
        new_2d_btn = self.findChild(QPushButton, "new2dBtn")
        new_3d_btn = self.findChild(QPushButton, "new3dBtn")
        
        if new_2d_btn:
            new_2d_btn.clicked.connect(self.create_2d_plot)
        if new_3d_btn:
            new_3d_btn.clicked.connect(self.create_3d_plot)
        if self._viz_tabs:
            self._viz_tabs.setTabsClosable(True)
            self._viz_tabs.tabCloseRequested.connect(self._close_tab)

    def _setup_modern_ui_fallback(self):
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
            "📊 Suporte para gráficos 2D, 3D, Heatmap e Scatter",
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
            "2d",
        )
        zone_2d.series_dropped.connect(self._on_series_dropped_2d)
        zones_layout.addWidget(zone_2d, 0, 0)

        # Zona 3D
        zone_3d = DropZone(
            "📈 Gráfico 3D",
            "Arraste série aqui para\ncriar visualização 3D",
            "3d",
        )
        zone_3d.series_dropped.connect(self._on_series_dropped_3d)
        zones_layout.addWidget(zone_3d, 0, 1)

        # Zona Heatmap
        zone_heatmap = DropZone(
            "🔥 Heatmap",
            "Arraste série aqui para\ncriar mapa de calor",
            "heatmap",
        )
        zone_heatmap.series_dropped.connect(self._on_series_dropped_heatmap)
        zones_layout.addWidget(zone_heatmap, 1, 0)

        # Zona Scatter
        zone_scatter = DropZone(
            "🔵 Scatter Plot",
            "Arraste série aqui para\ncriar gráfico de dispersão",
            "scatter",
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
        pass  # Implementar refresh se necessário

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
        """Cria novo gráfico ou adiciona série a gráfico existente (se tab 2D estiver ativa)"""
        try:
            # Get series data
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                return

            series = dataset.series[series_id]
            dataset_name = dataset.source.filename if dataset.source else dataset_id
            
            # Obter dados de tempo do dataset
            t_datetime = getattr(dataset, 't_datetime', None)
            t_seconds = getattr(dataset, 't_seconds', None)

            # Verificar se tab atual é um gráfico 2D que pode receber mais séries
            current_idx = self._viz_tabs.currentIndex()
            if current_idx > 0 and plot_type == "2d":
                current_widget = self._viz_tabs.widget(current_idx)
                if isinstance(current_widget, MatplotlibWidget) and current_widget.plot_type == "2d":
                    # Adicionar série ao gráfico existente
                    if current_widget.add_series(series, dataset_name):
                        # Atualizar título da tab
                        n_series = len(current_widget.series_list)
                        tab_title = f"Comparativo ({n_series} séries)"
                        self._viz_tabs.setTabText(current_idx, tab_title)
                        logger.info(f"series_added_to_existing_plot: {dataset_id}/{series_id}")
                        return

            # Criar novo gráfico em nova tab (passando dados de tempo)
            plot_widget = self._create_plot_widget(series, plot_type, dataset_name, t_datetime, t_seconds)

            # Conectar signal de drop para adicionar mais séries
            if isinstance(plot_widget, MatplotlibWidget):
                plot_widget.series_drop_requested.connect(
                    lambda ds_id, sr_id, pw=plot_widget: self._on_series_drop_on_plot(pw, ds_id, sr_id)
                )

            # Add as new tab
            tab_title = f"{dataset_name} ({plot_type.upper()})"
            tab_index = self._viz_tabs.addTab(plot_widget, tab_title)
            self._viz_tabs.setCurrentIndex(tab_index)

            # Store plot info
            self._plots.append({
                "widget": plot_widget,
                "series": series,
                "dataset_id": dataset_id,
                "type": plot_type,
                "tab_index": tab_index,
            })

            logger.info(f"plot_created: series={series_id}, type={plot_type}, tab={tab_index}")

        except Exception as e:
            logger.exception(f"plot_creation_failed: series={series_id}, type={plot_type}, error={e}")

    def _on_series_drop_on_plot(self, plot_widget: MatplotlibWidget, dataset_id: str, series_id: str):
        """Handler para série dropada em um gráfico existente"""
        try:
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or series_id not in dataset.series:
                return

            series = dataset.series[series_id]
            dataset_name = dataset.source.filename if dataset.source else dataset_id

            if plot_widget.add_series(series, dataset_name):
                # Atualizar título da tab
                tab_idx = self._viz_tabs.indexOf(plot_widget)
                if tab_idx >= 0:
                    n_series = len(plot_widget.series_list)
                    self._viz_tabs.setTabText(tab_idx, f"Comparativo ({n_series} séries)")

        except Exception as e:
            logger.exception(f"series_drop_on_plot_error: {e}")

    def create_plot_for_series(self, dataset_id: str, series_id: str, plot_type: str):
        """Cria gráfico para série específica (API pública)"""
        self._create_plot(dataset_id, series_id, plot_type)

    def _create_plot_widget(self, series, plot_type: str, dataset_name: str = "", 
                           t_datetime=None, t_seconds=None) -> QWidget:
        """Cria widget de gráfico REAL usando matplotlib"""
        try:
            # Criar widget matplotlib real com nome do dataset e dados de tempo
            widget = MatplotlibWidget(series, plot_type, dataset_name=dataset_name,
                                   t_datetime=t_datetime, t_seconds=t_seconds)
            
            # Conectar signal de cálculo do widget ao panel
            widget.calculation_requested.connect(self.calculation_requested.emit)
            
            return widget

        except Exception as e:
            logger.exception(f"matplotlib_widget_creation_failed: {e}, plot_type={plot_type}")

            # Fallback para widget de erro
            widget = QFrame()
            layout = QVBoxLayout(widget)

            content = QLabel(
                f"❌ Erro na Visualização\n\n"
                f"Série: {series.name}\n"
                f"Tipo: {plot_type.upper()}\n"
                f"Erro: {e!s}\n\n"
                "Verifique se matplotlib está instalado corretamente.",
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
            if plot["tab_index"] == index:
                plot_to_remove = plot
                break

        if plot_to_remove:
            self._plots.remove(plot_to_remove)

        # Remove tab
        self._viz_tabs.removeTab(index)

        # Update tab indices
        for plot in self._plots:
            if plot["tab_index"] > index:
                plot["tab_index"] -= 1

        logger.debug(f"plot_tab_closed: index={index}")

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
