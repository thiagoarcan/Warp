"""
ResultsPanel - Painel para exibição de estatísticas e resultados

Características:
- Estatísticas descritivas completas
- Visualização de métricas em cards
- Exportação de resultados
- Atualização em tempo real

Autor: Platform Base Team
Versão: 2.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class StatisticsResult:
    """Resultado de cálculo estatístico"""
    name: str
    value: float
    unit: str = ""
    description: str = ""
    category: str = "Geral"


@dataclass
class ComparisonResult:
    """Resultado de comparação entre séries"""
    series_a: str
    series_b: str
    correlation: float = 0.0
    rmse: float = 0.0
    mae: float = 0.0
    dtw_distance: float | None = None
    lag: int = 0
    description: str = ""


class StatCard(QFrame):
    """Card para exibição de estatística individual"""

    def __init__(
        self,
        title: str,
        value: str,
        description: str = "",
        icon: str = "📊",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("statCard")
        self._setup_ui(title, value, description, icon)
        self._apply_style()

    def _setup_ui(self, title: str, value: str, description: str, icon: str):
        """Configura a interface do card"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # Header com ícone e título
        header = QHBoxLayout()

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        header.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: #6c757d;
        """)
        header.addWidget(title_label)
        header.addStretch()

        layout.addLayout(header)

        # Valor principal
        self._value_label = QLabel(value)
        self._value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #212529;
        """)
        layout.addWidget(self._value_label)

        # Descrição opcional
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                font-size: 11px;
                color: #adb5bd;
            """)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

    def _apply_style(self):
        """Aplica estilo ao card"""
        self.setStyleSheet("""
            QFrame#statCard {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
            QFrame#statCard:hover {
                border-color: #0d6efd;
                box-shadow: 0 2px 8px rgba(13, 110, 253, 0.1);
            }
        """)
        self.setFixedHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_value(self, value: str):
        """Atualiza o valor exibido"""
        self._value_label.setText(value)


class StatisticsTable(QWidget):
    """Tabela de estatísticas detalhadas"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tabela
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels([
            "Estatística", "Valor", "Unidade", "Categoria",
        ])
        header = self._table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(True)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                gridline-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #e7f1ff;
                color: #212529;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: 600;
            }
        """)

        layout.addWidget(self._table)

    def set_statistics(self, stats: list[StatisticsResult]):
        """Popula a tabela com estatísticas"""
        self._table.setRowCount(len(stats))

        for i, stat in enumerate(stats):
            self._table.setItem(i, 0, QTableWidgetItem(stat.name))
            self._table.setItem(i, 1, QTableWidgetItem(f"{stat.value:.6g}"))
            self._table.setItem(i, 2, QTableWidgetItem(stat.unit))
            self._table.setItem(i, 3, QTableWidgetItem(stat.category))

        self._table.resizeColumnsToContents()

    def get_statistics_text(self) -> str:
        """Retorna estatísticas em formato texto"""
        lines = []
        for row in range(self._table.rowCount()):
            name_item = self._table.item(row, 0)
            value_item = self._table.item(row, 1)
            unit_item = self._table.item(row, 2)
            name = name_item.text() if name_item else ""
            value = value_item.text() if value_item else ""
            unit = unit_item.text() if unit_item else ""
            lines.append(f"{name}: {value} {unit}")
        return "\n".join(lines)


class ResultsPanel(QWidget):
    """
    Painel principal de resultados e estatísticas

    Signals:
        statistics_updated: Emitido quando estatísticas são atualizadas
        export_requested: Emitido quando exportação é solicitada
    """

    statistics_updated = pyqtSignal()
    export_requested = pyqtSignal(str)  # format: csv, json, txt

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._series: Any | None = None
        self._stats: list[StatisticsResult] = []
        self._cards: dict[str, StatCard] = {}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Configura a interface principal"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Header
        header = self._create_header()
        layout.addWidget(header)

        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Área de cards (resumo)
        cards_area = self._create_cards_area()
        splitter.addWidget(cards_area)

        # Tabs de detalhes
        tabs = self._create_detail_tabs()
        splitter.addWidget(tabs)

        splitter.setSizes([200, 400])
        layout.addWidget(splitter)

    def _create_header(self) -> QWidget:
        """Cria header com título e ações"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        # Título
        title = QLabel("📊 Resultados e Estatísticas")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #212529;
        """)
        layout.addWidget(title)

        layout.addStretch()

        # Info da série
        self._series_info = QLabel("Nenhuma série selecionada")
        self._series_info.setStyleSheet("color: #6c757d;")
        layout.addWidget(self._series_info)

        # Botões de ação
        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.setToolTip("Recalcular estatísticas")
        refresh_btn.clicked.connect(self._refresh_statistics)
        layout.addWidget(refresh_btn)

        export_btn = QPushButton("📤 Exportar")
        export_btn.setToolTip("Exportar resultados")
        export_btn.clicked.connect(self._show_export_menu)
        layout.addWidget(export_btn)

        return header

    def _create_cards_area(self) -> QWidget:
        """Cria área de cards de resumo"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Título da seção
        section_title = QLabel("Resumo Rápido")
        section_title.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 8px;
        """)
        layout.addWidget(section_title)

        # Grid de cards
        self._cards_grid = QWidget()
        self._cards_layout = QGridLayout(self._cards_grid)
        self._cards_layout.setSpacing(12)

        # Cards padrão
        self._create_default_cards()

        scroll = QScrollArea()
        scroll.setWidget(self._cards_grid)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout.addWidget(scroll)

        return container

    def _create_default_cards(self):
        """Cria cards padrão de estatísticas"""
        cards_config = [
            ("count", "Amostras", "0", "Total de pontos", "📏"),
            ("mean", "Média", "0.000", "Valor médio", "📊"),
            ("std", "Desvio", "0.000", "Desvio padrão", "📈"),
            ("min", "Mínimo", "0.000", "Valor mínimo", "⬇️"),
            ("max", "Máximo", "0.000", "Valor máximo", "⬆️"),
            ("range", "Range", "0.000", "Amplitude", "↔️"),
        ]

        for i, (key, title, value, desc, icon) in enumerate(cards_config):
            card = StatCard(title, value, desc, icon)
            self._cards[key] = card
            row, col = divmod(i, 3)
            self._cards_layout.addWidget(card, row, col)

    def _create_detail_tabs(self) -> QTabWidget:
        """Cria tabs de detalhes"""
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e9ecef;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 4px;
                border: 1px solid transparent;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-color: #e9ecef;
            }
            QTabBar::tab:hover:!selected {
                background-color: #f8f9fa;
            }
        """)

        # Tab de estatísticas detalhadas
        self._stats_table = StatisticsTable()
        tabs.addTab(self._stats_table, "📋 Estatísticas Detalhadas")

        # Tab de distribuição
        dist_widget = self._create_distribution_tab()
        tabs.addTab(dist_widget, "📊 Distribuição")

        # Tab de resumo texto
        self._text_summary = QTextEdit()
        self._text_summary.setReadOnly(True)
        self._text_summary.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 12px;
                background-color: #f8f9fa;
                border: none;
            }
        """)
        tabs.addTab(self._text_summary, "📝 Resumo Texto")

        return tabs

    def _create_distribution_tab(self) -> QWidget:
        """Cria tab de distribuição com histograma e box plot."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Import pyqtgraph for plotting
        try:
            import pyqtgraph as pg
            pg.setConfigOptions(antialias=True)
            
            # Create splitter for histogram and stats
            splitter = QSplitter(Qt.Orientation.Vertical)
            
            # === Histogram Section ===
            hist_widget = QWidget()
            hist_layout = QVBoxLayout(hist_widget)
            hist_layout.setContentsMargins(0, 0, 0, 0)
            
            hist_label = QLabel("📊 Histograma de Distribuição")
            hist_label.setStyleSheet("font-weight: bold; font-size: 12px; padding: 4px;")
            hist_layout.addWidget(hist_label)
            
            # Create plot widget for histogram
            self._hist_plot = pg.PlotWidget()
            self._hist_plot.setBackground('w')
            self._hist_plot.setLabel('left', 'Frequência')
            self._hist_plot.setLabel('bottom', 'Valor')
            self._hist_plot.showGrid(x=True, y=True, alpha=0.3)
            hist_layout.addWidget(self._hist_plot)
            
            splitter.addWidget(hist_widget)
            
            # === Box Plot Statistics Section ===
            box_widget = QWidget()
            box_layout = QVBoxLayout(box_widget)
            box_layout.setContentsMargins(0, 0, 0, 0)
            
            box_label = QLabel("📦 Estatísticas de Distribuição")
            box_label.setStyleSheet("font-weight: bold; font-size: 12px; padding: 4px;")
            box_layout.addWidget(box_label)
            
            # Distribution stats grid
            self._dist_stats_widget = QWidget()
            dist_grid = QGridLayout(self._dist_stats_widget)
            dist_grid.setSpacing(8)
            
            # Create stat labels
            self._dist_labels = {}
            stats_items = [
                ('min', 'Mínimo', 0, 0),
                ('q1', 'Q1 (25%)', 0, 1),
                ('median', 'Mediana (Q2)', 0, 2),
                ('q3', 'Q3 (75%)', 0, 3),
                ('max', 'Máximo', 1, 0),
                ('iqr', 'IQR (Q3-Q1)', 1, 1),
                ('skewness', 'Assimetria', 1, 2),
                ('kurtosis', 'Curtose', 1, 3),
            ]
            
            for key, label_text, row, col in stats_items:
                frame = QFrame()
                frame.setFrameStyle(QFrame.Shape.StyledPanel)
                frame.setStyleSheet("""
                    QFrame {
                        background-color: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        padding: 8px;
                    }
                """)
                frame_layout = QVBoxLayout(frame)
                frame_layout.setContentsMargins(8, 4, 8, 4)
                frame_layout.setSpacing(2)
                
                name_label = QLabel(label_text)
                name_label.setStyleSheet("color: #6c757d; font-size: 10px;")
                frame_layout.addWidget(name_label)
                
                value_label = QLabel("--")
                value_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #212529;")
                frame_layout.addWidget(value_label)
                
                self._dist_labels[key] = value_label
                dist_grid.addWidget(frame, row, col)
            
            box_layout.addWidget(self._dist_stats_widget)
            
            # Info label for empty state
            self._dist_info = QLabel(
                "Selecione uma série para visualizar a distribuição dos valores"
            )
            self._dist_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._dist_info.setStyleSheet("color: #6c757d; padding: 20px;")
            box_layout.addWidget(self._dist_info)
            self._dist_info.setVisible(False)
            
            splitter.addWidget(box_widget)
            
            # Set splitter sizes
            splitter.setSizes([300, 150])
            
            layout.addWidget(splitter)
            
        except ImportError:
            # Fallback if pyqtgraph not available
            info = QLabel(
                "📊 Visualização de distribuição\n\n"
                "pyqtgraph não disponível para gráficos.\n"
                "Instale com: pip install pyqtgraph"
            )
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info.setStyleSheet("color: #6c757d; padding: 40px;")
            layout.addWidget(info)
            self._hist_plot = None
            self._dist_labels = {}
        
        return widget
    
    def update_distribution(self, values: np.ndarray):
        """Atualiza o histograma e estatísticas de distribuição.
        
        Args:
            values: Array de valores para análise de distribuição.
        """
        if not hasattr(self, '_hist_plot') or self._hist_plot is None:
            return
            
        try:
            import pyqtgraph as pg
            from scipy import stats as scipy_stats

            # Filter out NaN values
            clean_values = values[~np.isnan(values)]
            
            if len(clean_values) == 0:
                return
            
            # Clear previous plot
            self._hist_plot.clear()
            
            # Calculate histogram
            n_bins = min(50, max(10, int(np.sqrt(len(clean_values)))))
            hist, bins = np.histogram(clean_values, bins=n_bins)
            
            # Create bar graph for histogram
            bin_centers = (bins[:-1] + bins[1:]) / 2
            bar_width = bins[1] - bins[0]
            
            bar_item = pg.BarGraphItem(
                x=bin_centers,
                height=hist,
                width=bar_width * 0.9,
                brush=pg.mkBrush(100, 150, 255, 180),
                pen=pg.mkPen(color=(50, 100, 200), width=1)
            )
            self._hist_plot.addItem(bar_item)
            
            # Add mean line
            mean_val = np.mean(clean_values)
            mean_line = pg.InfiniteLine(
                pos=mean_val,
                angle=90,
                pen=pg.mkPen(color='r', width=2, style=2),  # Dashed red
                label=f'Média: {mean_val:.2f}'
            )
            self._hist_plot.addItem(mean_line)
            
            # Add median line
            median_val = np.median(clean_values)
            median_line = pg.InfiniteLine(
                pos=median_val,
                angle=90,
                pen=pg.mkPen(color='g', width=2, style=3),  # Dot-dash green
                label=f'Mediana: {median_val:.2f}'
            )
            self._hist_plot.addItem(median_line)
            
            # Update distribution statistics
            q1 = np.percentile(clean_values, 25)
            q3 = np.percentile(clean_values, 75)
            iqr = q3 - q1
            
            # Calculate skewness and kurtosis
            try:
                skewness = scipy_stats.skew(clean_values)
                kurtosis = scipy_stats.kurtosis(clean_values)
            except Exception:
                skewness = 0.0
                kurtosis = 0.0
            
            # Update labels
            if hasattr(self, '_dist_labels') and self._dist_labels:
                self._dist_labels['min'].setText(f"{np.min(clean_values):.4g}")
                self._dist_labels['max'].setText(f"{np.max(clean_values):.4g}")
                self._dist_labels['q1'].setText(f"{q1:.4g}")
                self._dist_labels['median'].setText(f"{median_val:.4g}")
                self._dist_labels['q3'].setText(f"{q3:.4g}")
                self._dist_labels['iqr'].setText(f"{iqr:.4g}")
                self._dist_labels['skewness'].setText(f"{skewness:.4f}")
                self._dist_labels['kurtosis'].setText(f"{kurtosis:.4f}")
            
            # Hide info label
            if hasattr(self, '_dist_info'):
                self._dist_info.setVisible(False)
            if hasattr(self, '_dist_stats_widget'):
                self._dist_stats_widget.setVisible(True)
                
            logger.debug("distribution_updated", n_values=len(clean_values), n_bins=n_bins)
            
        except Exception as e:
            logger.warning(f"distribution_update_failed: {e}")

    def _connect_signals(self):
        """Conecta signals internos"""

    def set_series(self, series: Any):
        """
        Define a série para análise

        Args:
            series: Série de dados a analisar
        """
        self._series = series
        self._update_series_info()
        self._calculate_statistics()

    def _update_series_info(self):
        """Atualiza info da série no header"""
        if self._series:
            self._series_info.setText(
                f"Série: {self._series.name} | "
                f"Unidade: {self._series.unit} | "
                f"Pontos: {len(self._series.values):,}",
            )
        else:
            self._series_info.setText("Nenhuma série selecionada")

    def _calculate_statistics(self):
        """Calcula estatísticas da série"""
        if not self._series:
            return

        values = self._series.values
        n = len(values)

        if n == 0:
            return

        # Estatísticas básicas
        self._stats = [
            StatisticsResult("Contagem", n, "pontos", "Total de amostras", "Básico"),
            StatisticsResult("Média", float(np.mean(values)), self._series.unit, "Média aritmética", "Tendência Central"),
            StatisticsResult("Mediana", float(np.median(values)), self._series.unit, "Valor central", "Tendência Central"),
            StatisticsResult("Desvio Padrão", float(np.std(values)), self._series.unit, "Dispersão", "Dispersão"),
            StatisticsResult("Variância", float(np.var(values)), f"({self._series.unit})²", "Variância", "Dispersão"),
            StatisticsResult("Mínimo", float(np.min(values)), self._series.unit, "Valor mínimo", "Extremos"),
            StatisticsResult("Máximo", float(np.max(values)), self._series.unit, "Valor máximo", "Extremos"),
            StatisticsResult("Range", float(np.ptp(values)), self._series.unit, "Amplitude total", "Extremos"),
            StatisticsResult("Soma", float(np.sum(values)), self._series.unit, "Soma total", "Básico"),
        ]

        # Quartis
        q1, q2, q3 = np.percentile(values, [25, 50, 75])
        self._stats.extend([
            StatisticsResult("Q1 (25%)", float(q1), self._series.unit, "Primeiro quartil", "Quartis"),
            StatisticsResult("Q2 (50%)", float(q2), self._series.unit, "Mediana", "Quartis"),
            StatisticsResult("Q3 (75%)", float(q3), self._series.unit, "Terceiro quartil", "Quartis"),
            StatisticsResult("IQR", float(q3 - q1), self._series.unit, "Intervalo interquartil", "Quartis"),
        ])

        # Atualiza cards
        self._update_cards()

        # Atualiza tabela
        self._stats_table.set_statistics(self._stats)

        # Atualiza resumo texto
        self._update_text_summary()

        self.statistics_updated.emit()
        logger.info(f"statistics_calculated: series={self._series.name}, n_stats={len(self._stats)}")

    def _update_cards(self):
        """Atualiza valores dos cards"""
        if not self._series:
            return

        values = self._series.values

        self._cards["count"].set_value(f"{len(values):,}")
        self._cards["mean"].set_value(f"{np.mean(values):.4f}")
        self._cards["std"].set_value(f"{np.std(values):.4f}")
        self._cards["min"].set_value(f"{np.min(values):.4f}")
        self._cards["max"].set_value(f"{np.max(values):.4f}")
        self._cards["range"].set_value(f"{np.ptp(values):.4f}")

    def _update_text_summary(self):
        """Atualiza resumo em texto"""
        if not self._series:
            self._text_summary.clear()
            return

        lines = [
            f"{'='*50}",
            "ANÁLISE ESTATÍSTICA",
            f"{'='*50}",
            "",
            f"Série: {self._series.name}",
            f"Unidade: {self._series.unit}",
            f"Data da análise: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"{'-'*50}",
            "ESTATÍSTICAS",
            f"{'-'*50}",
            "",
        ]

        for stat in self._stats:
            lines.append(f"{stat.name:.<25} {stat.value:>15.6g} {stat.unit}")

        lines.extend([
            "",
            f"{'='*50}",
        ])

        self._text_summary.setText("\n".join(lines))

    def _refresh_statistics(self):
        """Recalcula estatísticas"""
        self._calculate_statistics()

    def _show_export_menu(self):
        """Mostra menu de exportação"""
        from PyQt6.QtWidgets import QMenu

        menu = QMenu(self)

        csv_action = menu.addAction("📄 Exportar CSV")
        if csv_action is not None:
            csv_action.triggered.connect(lambda: self._export("csv"))

        json_action = menu.addAction("📋 Exportar JSON")
        if json_action is not None:
            json_action.triggered.connect(lambda: self._export("json"))

        txt_action = menu.addAction("📝 Exportar Texto")
        if txt_action is not None:
            txt_action.triggered.connect(lambda: self._export("txt"))

        menu.exec(self.mapToGlobal(self.rect().bottomRight()))

    def _export(self, format: str):
        """Exporta estatísticas no formato especificado"""
        self.export_requested.emit(format)
        logger.info(f"export_requested: format={format}")

    def get_statistics(self) -> list[StatisticsResult]:
        """Retorna lista de estatísticas calculadas"""
        return self._stats.copy()

    def get_statistics_dict(self) -> dict[str, float]:
        """Retorna estatísticas como dicionário"""
        return {stat.name: stat.value for stat in self._stats}


# Export para uso em outros módulos
__all__ = [
    "ResultsPanel",
    "StatCard",
    "StatisticsResult",
    "StatisticsTable",
    "ComparisonResult",
]
