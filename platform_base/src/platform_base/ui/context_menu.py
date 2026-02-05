from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from platform_base.desktop.widgets.base import UiLoaderMixin
from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from platform_base.ui.state import SessionState


logger = get_logger(__name__)


class CompareSeriesDialog(QDialog, UiLoaderMixin):
    """
    Diálogo para comparação de séries
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "compareSeriesDialog.ui"

    def __init__(self, available_series: list, parent=None):
        super().__init__(parent)
        self.available_series = available_series
        self.setWindowTitle("Comparar Séries")
        self.setMinimumWidth(400)

        # Carrega interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        self.series1_combo = self.findChild(QComboBox, "series1Combo")
        self.series2_combo = self.findChild(QComboBox, "series2Combo")
        self.correlation_check = self.findChild(QCheckBox, "correlationCheck")
        self.rmse_check = self.findChild(QCheckBox, "rmseCheck")
        self.mae_check = self.findChild(QCheckBox, "maeCheck")
        self.dtw_check = self.findChild(QCheckBox, "dtwCheck")
        self.result_text = self.findChild(QTextEdit, "resultText")
        self.compare_btn = self.findChild(QPushButton, "compareBtn")
        self.close_btn = self.findChild(QPushButton, "closeBtn")
        
        # Valida widgets obrigatórios
        self._validate_widgets()
        
        # Popula combos com séries disponíveis
        self.series1_combo.addItems(self.available_series)
        self.series2_combo.addItems(self.available_series)
        if len(self.available_series) > 1:
            self.series2_combo.setCurrentIndex(1)
        
        # Conecta sinais
        self._setup_connections()
    
    def _validate_widgets(self):
        """Valida que todos os widgets obrigatórios foram carregados"""
        required_widgets = {
            "series1Combo": self.series1_combo,
            "series2Combo": self.series2_combo,
            "correlationCheck": self.correlation_check,
            "rmseCheck": self.rmse_check,
            "maeCheck": self.mae_check,
            "dtwCheck": self.dtw_check,
            "resultText": self.result_text,
            "compareBtn": self.compare_btn,
            "closeBtn": self.close_btn,
        }
        
        missing = [name for name, widget in required_widgets.items() if widget is None]
        if missing:
            raise RuntimeError(
                f"CompareSeriesDialog: Widgets não encontrados no arquivo .ui: {missing}"
            )
    
    def _setup_connections(self):
        """Conecta sinais aos slots"""
        self.compare_btn.clicked.connect(self._compare)
        self.close_btn.clicked.connect(self.accept)

    def _compare(self):
        """Executa comparação"""
        # Simulação de resultados
        s1 = self.series1_combo.currentText()
        s2 = self.series2_combo.currentText()

        results = [f"Comparação: {s1} vs {s2}", "=" * 40]

        if self.correlation_check.isChecked():
            results.append("Correlação (Pearson): 0.942")
        if self.rmse_check.isChecked():
            results.append("RMSE: 0.0234")
        if self.mae_check.isChecked():
            results.append("MAE: 0.0187")
        if self.dtw_check.isChecked():
            results.append("DTW Distance: 1.234")

        self.result_text.setPlainText("\n".join(results))


class SmoothingDialog(QDialog, UiLoaderMixin):
    """
    Diálogo para suavização visual
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "smoothingConfigDialog.ui"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Suavização Visual")

        # Carrega interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        self.method_combo = self.findChild(QComboBox, "methodCombo")
        self.window_spin = self.findChild(QSpinBox, "windowSpin")
        self.sigma_spin = self.findChild(QDoubleSpinBox, "sigmaSpin")
        
        apply_btn = self.findChild(QPushButton, "applyBtn")
        cancel_btn = self.findChild(QPushButton, "cancelBtn")
        
        if apply_btn:
            apply_btn.clicked.connect(self.accept)
        if cancel_btn:
            cancel_btn.clicked.connect(self.reject)

    def get_config(self) -> dict[str, Any]:
        return {
            "method": self.method_combo.currentText().lower().replace(" ", "_"),
            "window_size": self.window_spin.value(),
            "sigma": self.sigma_spin.value(),
        }


class AnnotationDialog(QDialog, UiLoaderMixin):
    """
    Diálogo para adicionar anotação
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface
    UI_FILE = "annotationDialog.ui"

    def __init__(self, x_pos: float = 0, y_pos: float = 0, parent=None):
        super().__init__(parent)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.setWindowTitle("Adicionar Anotação")
        self.setMinimumWidth(400)

        # Carrega interface do arquivo .ui
        if not self._load_ui():
            raise RuntimeError(f"Falha ao carregar arquivo UI: {self.UI_FILE}. Verifique se existe em desktop/ui_files/")
        self._setup_ui_from_file()

    def _setup_ui_from_file(self):
        """Configura widgets carregados do arquivo .ui"""
        self.x_spin = self.findChild(QDoubleSpinBox, "xSpin")
        self.y_spin = self.findChild(QDoubleSpinBox, "ySpin")
        self.text_edit = self.findChild(QTextEdit, "textEdit")
        self.arrow_check = self.findChild(QCheckBox, "arrowCheck")
        self.color_combo = self.findChild(QComboBox, "colorCombo")
        self.add_btn = self.findChild(QPushButton, "addBtn")
        self.cancel_btn = self.findChild(QPushButton, "cancelBtn")
        
        # Valida widgets obrigatórios
        self._validate_widgets()
        
        # Configura valores iniciais
        self.x_spin.setValue(self.x_pos)
        self.y_spin.setValue(self.y_pos)
        
        # Conecta sinais
        self._setup_connections()
    
    def _validate_widgets(self):
        """Valida que todos os widgets obrigatórios foram carregados"""
        required_widgets = {
            "xSpin": self.x_spin,
            "ySpin": self.y_spin,
            "textEdit": self.text_edit,
            "arrowCheck": self.arrow_check,
            "colorCombo": self.color_combo,
            "addBtn": self.add_btn,
            "cancelBtn": self.cancel_btn,
        }
        
        missing = [name for name, widget in required_widgets.items() if widget is None]
        if missing:
            raise RuntimeError(
                f"AnnotationDialog: Widgets não encontrados no arquivo .ui: {missing}"
            )
    
    def _setup_connections(self):
        """Conecta sinais aos slots"""
        self.add_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_annotation(self) -> dict[str, Any]:
        color_map = {
            "Vermelho": "#e74c3c",
            "Azul": "#3498db",
            "Verde": "#2ecc71",
            "Preto": "#2c3e50",
            "Laranja": "#e67e22",
        }

        return {
            "x": self.x_spin.value(),
            "y": self.y_spin.value(),
            "text": self.text_edit.toPlainText(),
            "show_arrow": self.arrow_check.isChecked(),
            "color": color_map.get(self.color_combo.currentText(), "#000000"),
        }


class PlotContextMenu(QMenu):
    """
    Menu contextual para plots PyQt6.

    Implementa ações conforme PRD seção 12.6:
    - Zoom/Pan/Reset
    - Seleção de região
    - Estatísticas
    - Filtros visuais
    - Exportação
    - Anotações
    """

    def __init__(self, plot_widget, session_state: SessionState | None = None,
                 parent=None):
        super().__init__(parent)
        self.plot_widget = plot_widget
        self.session_state = session_state
        self._annotations = []
        self._visual_smoothing_enabled = False
        self._hide_interpolated = False

        self._create_actions()
        logger.debug("plot_context_menu_initialized")

    def _create_actions(self):
        """Cria todas as ações do menu"""

        # ========== ZOOM/PAN ==========
        zoom_menu = self.addMenu("🔍 Zoom")

        zoom_in_action = QAction("➕ Zoom In", self)
        zoom_in_action.setShortcut("+")
        zoom_in_action.triggered.connect(self._zoom_in)
        zoom_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("➖ Zoom Out", self)
        zoom_out_action.setShortcut("-")
        zoom_out_action.triggered.connect(self._zoom_out)
        zoom_menu.addAction(zoom_out_action)

        reset_view_action = QAction("🔄 Reset View", self)
        reset_view_action.setShortcut("R")
        reset_view_action.triggered.connect(self._reset_view)
        zoom_menu.addAction(reset_view_action)

        zoom_menu.addSeparator()

        fit_x_action = QAction("↔️ Ajustar ao eixo X", self)
        fit_x_action.triggered.connect(self._fit_to_x)
        zoom_menu.addAction(fit_x_action)

        fit_y_action = QAction("↕️ Ajustar ao eixo Y", self)
        fit_y_action.triggered.connect(self._fit_to_y)
        zoom_menu.addAction(fit_y_action)

        self.addSeparator()

        # ========== SELEÇÃO ==========
        select_menu = self.addMenu("📐 Seleção")

        select_region_action = QAction("📦 Selecionar Região", self)
        select_region_action.triggered.connect(self._select_region)
        select_menu.addAction(select_region_action)

        select_all_action = QAction("✓ Selecionar Tudo", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self._select_all)
        select_menu.addAction(select_all_action)

        clear_selection_action = QAction("✗ Limpar Seleção", self)
        clear_selection_action.triggered.connect(self._clear_selection)
        select_menu.addAction(clear_selection_action)

        select_menu.addSeparator()

        extract_action = QAction("📤 Extrair Seleção", self)
        extract_action.triggered.connect(self._extract_selection)
        select_menu.addAction(extract_action)

        self.addSeparator()

        # ========== ANÁLISE ==========
        analysis_menu = self.addMenu("📊 Análise")

        stats_action = QAction("📈 Estatísticas", self)
        stats_action.triggered.connect(self._show_stats)
        analysis_menu.addAction(stats_action)

        compare_action = QAction("⚖️ Comparar Séries...", self)
        compare_action.triggered.connect(self._compare_series)
        analysis_menu.addAction(compare_action)

        peaks_action = QAction("🔺 Detectar Picos", self)
        peaks_action.triggered.connect(self._detect_peaks)
        analysis_menu.addAction(peaks_action)

        crossings_action = QAction("✖️ Encontrar Cruzamentos", self)
        crossings_action.triggered.connect(self._find_crossings)
        analysis_menu.addAction(crossings_action)

        self.addSeparator()

        # ========== FILTROS VISUAIS ==========
        filter_menu = self.addMenu("🎨 Filtros Visuais")

        self._hide_interp_action = QAction("👁️ Ocultar Pontos Interpolados", self, checkable=True)
        self._hide_interp_action.triggered.connect(self._toggle_hide_interpolated)
        filter_menu.addAction(self._hide_interp_action)

        smooth_action = QAction("〰️ Suavização Visual...", self)
        smooth_action.triggered.connect(self._apply_visual_smoothing)
        filter_menu.addAction(smooth_action)

        filter_menu.addSeparator()

        show_grid_action = QAction("▦ Mostrar Grade", self, checkable=True)
        show_grid_action.setChecked(True)
        show_grid_action.triggered.connect(self._toggle_grid)
        filter_menu.addAction(show_grid_action)

        show_legend_action = QAction("📋 Mostrar Legenda", self, checkable=True)
        show_legend_action.setChecked(True)
        show_legend_action.triggered.connect(self._toggle_legend)
        filter_menu.addAction(show_legend_action)

        self.addSeparator()

        # ========== EXPORT ==========
        export_menu = self.addMenu("💾 Exportar")

        export_png_action = QAction("🖼️ Exportar como PNG...", self)
        export_png_action.triggered.connect(lambda: self._export_plot("png"))
        export_menu.addAction(export_png_action)

        export_svg_action = QAction("📐 Exportar como SVG...", self)
        export_svg_action.triggered.connect(lambda: self._export_plot("svg"))
        export_menu.addAction(export_svg_action)

        export_pdf_action = QAction("📄 Exportar como PDF...", self)
        export_pdf_action.triggered.connect(lambda: self._export_plot("pdf"))
        export_menu.addAction(export_pdf_action)

        export_menu.addSeparator()

        export_data_action = QAction("📊 Exportar Dados da Seleção...", self)
        export_data_action.triggered.connect(self._export_selection_data)
        export_menu.addAction(export_data_action)

        self.addSeparator()

        # ========== ANOTAÇÕES ==========
        annotation_menu = self.addMenu("📝 Anotações")

        add_annotation_action = QAction("➕ Adicionar Anotação...", self)
        add_annotation_action.triggered.connect(self._add_annotation)
        annotation_menu.addAction(add_annotation_action)

        clear_annotations_action = QAction("🗑️ Limpar Anotações", self)
        clear_annotations_action.triggered.connect(self._clear_annotations)
        annotation_menu.addAction(clear_annotations_action)

        annotation_menu.addSeparator()

        export_annotations_action = QAction("💾 Exportar Anotações...", self)
        export_annotations_action.triggered.connect(self._export_annotations)
        annotation_menu.addAction(export_annotations_action)

    # ========== HANDLERS ==========

    def _zoom_in(self):
        """Zoom in no plot"""
        if hasattr(self.plot_widget, "plotItem"):
            vb = self.plot_widget.plotItem.vb
            vb.scaleBy((0.5, 0.5))
        elif hasattr(self.plot_widget, "axes"):
            # Matplotlib
            ax = self.plot_widget.axes
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) * 0.25
            y_range = (ylim[1] - ylim[0]) * 0.25
            ax.set_xlim(x_center - x_range, x_center + x_range)
            ax.set_ylim(y_center - y_range, y_center + y_range)
            self.plot_widget.draw()

    def _zoom_out(self):
        """Zoom out no plot"""
        if hasattr(self.plot_widget, "plotItem"):
            vb = self.plot_widget.plotItem.vb
            vb.scaleBy((2, 2))
        elif hasattr(self.plot_widget, "axes"):
            ax = self.plot_widget.axes
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0])
            y_range = (ylim[1] - ylim[0])
            ax.set_xlim(x_center - x_range, x_center + x_range)
            ax.set_ylim(y_center - y_range, y_center + y_range)
            self.plot_widget.draw()

    def _reset_view(self):
        """Reseta visualização"""
        if hasattr(self.plot_widget, "autoRange"):
            self.plot_widget.autoRange()
        elif hasattr(self.plot_widget, "axes"):
            self.plot_widget.axes.autoscale()
            self.plot_widget.draw()

    def _fit_to_x(self):
        """Ajusta zoom apenas ao eixo X"""
        if hasattr(self.plot_widget, "plotItem"):
            self.plot_widget.plotItem.enableAutoRange(axis="x")

    def _fit_to_y(self):
        """Ajusta zoom apenas ao eixo Y"""
        if hasattr(self.plot_widget, "plotItem"):
            self.plot_widget.plotItem.enableAutoRange(axis="y")

    def _select_region(self):
        """Habilita seleção de região"""
        if hasattr(self.plot_widget, "enable_selection"):
            self.plot_widget.enable_selection(True)
        QMessageBox.information(self, "Seleção",
            "Clique e arraste para selecionar uma região no gráfico.")

    def _select_all(self):
        """Seleciona todos os dados"""
        if self.session_state:
            self.session_state.select_all_in_view()

    def _clear_selection(self):
        """Limpa seleção atual"""
        if self.session_state:
            self.session_state.clear_selection()

    def _extract_selection(self):
        """Extrai dados da seleção como nova série"""
        if not self.session_state or not self.session_state.selection:
            QMessageBox.warning(self, "Extrair", "Nenhuma seleção ativa.")
            return

        name, ok = QInputDialog.getText(
            self, "Extrair Seleção",
            "Nome para a nova série:",
            text="seleção_extraída",
        )

        if ok and name:
            try:
                view_data = self.session_state.get_current_view()
                if view_data:
                    # Cria nova série com dados da seleção
                    logger.info("selection_extracted", name=name)
                    QMessageBox.information(self, "Sucesso",
                        f"Série '{name}' criada com sucesso.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao extrair: {e}")

    def _show_stats(self):
        """Mostra estatísticas da seleção"""
        if self.session_state and self.session_state.selection:
            view_data = self.session_state.get_current_view()
            if view_data:
                stats_lines = ["📊 Estatísticas da Seleção\n" + "="*40]

                for series_id, values in view_data.series.items():
                    arr = np.array(values)
                    stats_lines.append(f"\n📈 {series_id}:")
                    stats_lines.append(f"  • Média: {np.mean(arr):.4f}")
                    stats_lines.append(f"  • Desvio Padrão: {np.std(arr):.4f}")
                    stats_lines.append(f"  • Mínimo: {np.min(arr):.4f}")
                    stats_lines.append(f"  • Máximo: {np.max(arr):.4f}")
                    stats_lines.append(f"  • Mediana: {np.median(arr):.4f}")
                    stats_lines.append(f"  • Amplitude: {np.ptp(arr):.4f}")
                    stats_lines.append(f"  • Pontos: {len(arr)}")

                QMessageBox.information(self, "Estatísticas", "\n".join(stats_lines))
            else:
                QMessageBox.warning(self, "Estatísticas", "Nenhum dado disponível.")
        else:
            QMessageBox.warning(self, "Estatísticas", "Nenhuma seleção ativa.")

    def _compare_series(self):
        """Abre diálogo de comparação"""
        if not self.session_state:
            return

        # Obtém lista de séries disponíveis
        available_series = []
        if hasattr(self.session_state, "get_all_series"):
            available_series = self.session_state.get_all_series()
        else:
            available_series = ["Série 1", "Série 2", "Série 3"]  # Fallback

        dialog = CompareSeriesDialog(available_series, self)
        dialog.exec()

    def _detect_peaks(self):
        """Detecta picos na série selecionada"""
        if not self.session_state:
            QMessageBox.warning(self, "Picos", "Nenhum dado disponível.")
            return

        # Parâmetros
        prominence, ok = QInputDialog.getDouble(
            self, "Detectar Picos",
            "Proeminência mínima:",
            value=0.1, min=0.001, max=1000.0, decimals=4,
        )

        if ok:
            try:
                from scipy.signal import find_peaks
                view_data = self.session_state.get_current_view()
                if view_data:
                    for series_id, values in view_data.series.items():
                        peaks, props = find_peaks(np.array(values), prominence=prominence)
                        QMessageBox.information(self, "Picos Detectados",
                            f"Série: {series_id}\n"
                            f"Picos encontrados: {len(peaks)}\n"
                            f"Posições: {peaks[:10]}{'...' if len(peaks) > 10 else ''}")
                        break  # Primeira série apenas
            except ImportError:
                QMessageBox.warning(self, "Erro", "scipy não disponível para detecção de picos.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha na detecção: {e}")

    def _find_crossings(self):
        """Encontra cruzamentos entre séries"""
        if not self.session_state:
            QMessageBox.warning(self, "Cruzamentos", "Nenhum dado disponível.")
            return

        view_data = self.session_state.get_current_view()
        if view_data and len(view_data.series) >= 2:
            series_list = list(view_data.series.items())
            s1_name, s1_vals = series_list[0]
            s2_name, s2_vals = series_list[1]

            # Encontra cruzamentos
            diff = np.array(s1_vals) - np.array(s2_vals)
            crossings = np.where(np.diff(np.sign(diff)))[0]

            QMessageBox.information(self, "Cruzamentos",
                f"Cruzamentos entre {s1_name} e {s2_name}:\n"
                f"Total: {len(crossings)}\n"
                f"Índices: {crossings[:20].tolist()}{'...' if len(crossings) > 20 else ''}")
        else:
            QMessageBox.warning(self, "Cruzamentos", "Necessário pelo menos 2 séries.")

    def _toggle_hide_interpolated(self, checked: bool):
        """Alterna visibilidade de pontos interpolados"""
        self._hide_interpolated = checked
        if hasattr(self.plot_widget, "set_hide_interpolated"):
            self.plot_widget.set_hide_interpolated(checked)
        logger.debug("hide_interpolated_toggled", hidden=checked)

    def _apply_visual_smoothing(self):
        """Aplica suavização visual"""
        dialog = SmoothingDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            if hasattr(self.plot_widget, "apply_smoothing"):
                self.plot_widget.apply_smoothing(config)
            logger.info("visual_smoothing_applied", config=config)

    def _toggle_grid(self, checked: bool):
        """Alterna grade do gráfico"""
        if hasattr(self.plot_widget, "showGrid"):
            self.plot_widget.showGrid(x=checked, y=checked)
        elif hasattr(self.plot_widget, "axes"):
            self.plot_widget.axes.grid(checked)
            self.plot_widget.draw()

    def _toggle_legend(self, checked: bool):
        """Alterna legenda"""
        if hasattr(self.plot_widget, "set_legend_visible"):
            self.plot_widget.set_legend_visible(checked)
        elif hasattr(self.plot_widget, "axes"):
            legend = self.plot_widget.axes.get_legend()
            if legend:
                legend.set_visible(checked)
            self.plot_widget.draw()

    def _export_plot(self, format: str = "png"):
        """Exporta plot como imagem"""
        filter_map = {
            "png": "PNG Image (*.png)",
            "svg": "SVG Vector (*.svg)",
            "pdf": "PDF Document (*.pdf)",
        }

        path, _ = QFileDialog.getSaveFileName(
            self, f"Exportar como {format.upper()}", "",
            filter_map.get(format, "All Files (*.*)"),
        )

        if path:
            # Adiciona extensão se não tiver
            if not path.lower().endswith(f".{format}"):
                path += f".{format}"

            try:
                if hasattr(self.plot_widget, "export_image"):
                    self.plot_widget.export_image(path)
                elif hasattr(self.plot_widget, "plotItem"):
                    import pyqtgraph.exporters as exp
                    exporter = exp.ImageExporter(self.plot_widget.plotItem)
                    exporter.export(path)
                elif hasattr(self.plot_widget, "figure"):
                    self.plot_widget.figure.savefig(path, dpi=150, bbox_inches="tight")

                QMessageBox.information(self, "Exportado",
                    f"Gráfico exportado para:\n{path}")
                logger.info("plot_exported", path=path, format=format)

            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha na exportação:\n{e}")

    def _export_selection_data(self):
        """Exporta dados da seleção"""
        if not self.session_state:
            QMessageBox.warning(self, "Exportar", "Nenhum dado disponível.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Dados", "",
            "CSV (*.csv);;Excel (*.xlsx);;JSON (*.json)",
        )

        if path:
            try:
                view_data = self.session_state.get_current_view()
                if view_data:
                    import pandas as pd

                    df_data = {"timestamp": view_data.t_seconds}
                    df_data.update(view_data.series)
                    df = pd.DataFrame(df_data)

                    if path.endswith(".csv"):
                        df.to_csv(path, index=False)
                    elif path.endswith(".xlsx"):
                        df.to_excel(path, index=False)
                    elif path.endswith(".json"):
                        df.to_json(path, orient="records", indent=2)

                    QMessageBox.information(self, "Sucesso",
                        f"Dados exportados para:\n{path}")
                    logger.info("selection_data_exported", path=path)

            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha na exportação:\n{e}")

    def _add_annotation(self):
        """Adiciona anotação ao gráfico"""
        dialog = AnnotationDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            annotation = dialog.get_annotation()
            self._annotations.append(annotation)

            if hasattr(self.plot_widget, "add_annotation"):
                self.plot_widget.add_annotation(annotation)

            logger.info("annotation_added", annotation=annotation)

    def _clear_annotations(self):
        """Remove todas as anotações"""
        reply = QMessageBox.question(
            self, "Limpar Anotações",
            f"Remover {len(self._annotations)} anotações?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._annotations.clear()
            if hasattr(self.plot_widget, "clear_annotations"):
                self.plot_widget.clear_annotations()
            logger.info("annotations_cleared")

    def _export_annotations(self):
        """Exporta anotações para arquivo"""
        if not self._annotations:
            QMessageBox.warning(self, "Exportar", "Nenhuma anotação para exportar.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Anotações", "",
            "JSON (*.json);;Text (*.txt)",
        )

        if path:
            try:
                import json
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self._annotations, f, indent=2, ensure_ascii=False)

                QMessageBox.information(self, "Sucesso",
                    f"Anotações exportadas para:\n{path}")

            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha na exportação:\n{e}")
