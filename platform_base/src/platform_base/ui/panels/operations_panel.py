"""
OperationsPanel - Painel completo de operações matemáticas

Funcionalidades:
- Tabs: Interpolação, Cálculos (Derivadas/Integrais), Filtros, Export
- Histórico de operações
- Configuração de parâmetros
- Preview em tempo real
- Integração com SessionState
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import TYPE_CHECKING, Any

import numpy as np
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from platform_base.desktop.widgets.base import UiLoaderMixin
from platform_base.ui.preview_dialog import OperationPreviewDialog
from platform_base.utils.logging import get_logger
from platform_base.utils.widgets import StableComboBox

if TYPE_CHECKING:
    from platform_base.ui.state import SessionState


logger = get_logger(__name__)


class OperationHistoryItem:
    """Item do histórico de operações"""
    def __init__(self, operation: str, params: dict[str, Any], timestamp: datetime | None = None):
        self.operation = operation
        self.params = params
        self.timestamp = timestamp or datetime.now()
        self.success = True
        self.result_info = ""


class OperationsPanel(QWidget, UiLoaderMixin):
    """
    Painel de operações completo com tabs e histórico

    Características:
    - Tab Interpolação: 10 métodos disponíveis
    - Tab Cálculos: Derivadas (1ª/2ª/3ª), Integrais, Área
    - Tab Filtros: Suavização, Butterworth, Outliers
    - Tab Export: CSV, Excel, Parquet, HDF5, JSON
    - Histórico: Últimas 50 operações
    
    Interface carregada do arquivo .ui via UiLoaderMixin.
    """

    # Arquivo .ui que define a interface (Fase 0: Migração UI - sem fallback)
    UI_FILE = "operationsPanel.ui"

    # Signals
    operation_requested = pyqtSignal(str, dict)  # operation_name, params
    export_requested = pyqtSignal(str, dict)     # format, options
    streaming_data_updated = pyqtSignal(str, object, object)  # series_id, x_data, y_data

    def __init__(self, session_state: SessionState):
        super().__init__()

        self.session_state = session_state
        self._history: list[OperationHistoryItem] = []
        self._max_history = 50

        # Streaming state
        self._streaming_timer: QTimer | None = None
        self._streaming_position: int = 0
        self._streaming_data: dict[str, Any] = {}  # {series_id: {x, y}}
        self._streaming_paused: bool = False
        self._streaming_start_time: float = 0.0
        self._frame_count: int = 0
        self._last_fps_update: float = 0.0
        self._total_points_sent: int = 0

        # Carregar interface do arquivo .ui (obrigatório, sem fallback)
        if not self._load_ui():
            raise RuntimeError(
                f"Falha ao carregar arquivo UI: {self.UI_FILE}. "
                "Verifique se o arquivo existe em desktop/ui_files/"
            )
        
        self._setup_ui_from_file()
        self._setup_connections()
        logger.debug("operations_panel_initialized", ui_loaded=self._ui_loaded)

    def _setup_ui_from_file(self):
        """
        Configura widgets carregados do arquivo .ui
        
        Mapeia os widgets do arquivo operationsPanel.ui para os atributos
        da classe, mantendo compatibilidade com os métodos existentes.
        
        IMPORTANTE: Todos os widgets são carregados do arquivo .ui.
        Não há fallback - se o widget não existir, será None.
        """
        # Configurações básicas
        self.setMinimumWidth(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # === WIDGETS PRINCIPAIS ===
        self._tabs = self.findChild(QTabWidget, "tabWidget")
        self._series_combo = self.findChild(QComboBox, "seriesCombo")
        self._history_list = self.findChild(QListWidget, "historyList")
        
        # === TAB INTERPOLAÇÃO ===
        self._interp_method = self.findChild(QComboBox, "interpMethodCombo")
        self._interp_points = self.findChild(QSpinBox, "interpPointsSpin")
        self._interp_smooth = self.findChild(QDoubleSpinBox, "interpSmoothSpin")
        self._interp_degree = self.findChild(QSpinBox, "interpDegreeSpin")
        self._interp_extrapolate = self.findChild(QCheckBox, "interpExtrapolateCheck")
        
        # Botões de interpolação
        interp_preview_btn = self.findChild(QPushButton, "interpPreviewBtn")
        interp_apply_btn = self.findChild(QPushButton, "interpApplyBtn")
        if interp_preview_btn:
            interp_preview_btn.clicked.connect(self._preview_interpolation)
        if interp_apply_btn:
            interp_apply_btn.clicked.connect(self._apply_interpolation)
        
        # === TAB CÁLCULOS (DERIVADAS/INTEGRAIS) ===
        self._deriv_order = self.findChild(QComboBox, "derivOrderCombo")
        self._deriv_method = self.findChild(QComboBox, "derivMethodCombo")
        self._deriv_window = self.findChild(QSpinBox, "derivWindowSpin")
        self._deriv_smooth = self.findChild(QCheckBox, "derivSmoothCheck")
        self._area_type = self.findChild(QComboBox, "areaTypeCombo")
        
        # Botões de derivada
        deriv_preview_btn = self.findChild(QPushButton, "derivPreviewBtn")
        deriv_apply_btn = self.findChild(QPushButton, "derivApplyBtn")
        if deriv_preview_btn:
            deriv_preview_btn.clicked.connect(self._preview_derivative)
        if deriv_apply_btn:
            deriv_apply_btn.clicked.connect(self._calculate_derivative)
        
        # Integral
        self._integ_method = self.findChild(QComboBox, "integMethodCombo")
        integ_preview_btn = self.findChild(QPushButton, "integPreviewBtn")
        integ_apply_btn = self.findChild(QPushButton, "integApplyBtn")
        if integ_preview_btn:
            integ_preview_btn.clicked.connect(self._preview_integral)
        if integ_apply_btn:
            integ_apply_btn.clicked.connect(self._calculate_integral)
        
        # Área
        area_apply_btn = self.findChild(QPushButton, "areaApplyBtn")
        if area_apply_btn:
            area_apply_btn.clicked.connect(self._calculate_area)
        
        # === TAB FILTROS ===
        self._smooth_method = self.findChild(QComboBox, "smoothMethodCombo")
        self._smooth_window = self.findChild(QSpinBox, "smoothWindowSpin")
        self._smooth_sigma = self.findChild(QDoubleSpinBox, "smoothSigmaSpin")
        self._outlier_method = self.findChild(QComboBox, "outlierMethodCombo")
        self._outlier_threshold = self.findChild(QDoubleSpinBox, "outlierThresholdSpin")
        self._fft_window = self.findChild(QComboBox, "fftWindowCombo")
        self._fft_detrend = self.findChild(QCheckBox, "fftDetrendCheck")
        self._corr_mode = self.findChild(QComboBox, "corrModeCombo")
        self._corr_normalize = self.findChild(QCheckBox, "corrNormalizeCheck")
        self._filter_type = self.findChild(QComboBox, "filterTypeCombo")
        self._filter_cutoff = self.findChild(QDoubleSpinBox, "filterCutoffSpin")
        self._filter_cutoff_high = self.findChild(QDoubleSpinBox, "filterCutoffHighSpin")
        self._filter_cutoff_label = self.findChild(QLabel, "filterCutoffLabel")
        self._filter_cutoff_high_label = self.findChild(QLabel, "filterCutoffHighLabel")
        self._filter_order = self.findChild(QSpinBox, "filterOrderSpin")
        self._filter_method = self.findChild(QComboBox, "filterMethodCombo")
        
        # Botões de filtros
        smooth_preview_btn = self.findChild(QPushButton, "smoothPreviewBtn")
        smooth_apply_btn = self.findChild(QPushButton, "smoothApplyBtn")
        if smooth_preview_btn:
            smooth_preview_btn.clicked.connect(self._preview_smoothing)
        if smooth_apply_btn:
            smooth_apply_btn.clicked.connect(self._apply_smoothing)
            
        outlier_preview_btn = self.findChild(QPushButton, "outlierPreviewBtn")
        outlier_apply_btn = self.findChild(QPushButton, "outlierApplyBtn")
        if outlier_preview_btn:
            outlier_preview_btn.clicked.connect(self._preview_remove_outliers)
        if outlier_apply_btn:
            outlier_apply_btn.clicked.connect(self._remove_outliers)
            
        fft_apply_btn = self.findChild(QPushButton, "fftApplyBtn")
        if fft_apply_btn:
            fft_apply_btn.clicked.connect(self._compute_fft)
            
        corr_apply_btn = self.findChild(QPushButton, "corrApplyBtn")
        if corr_apply_btn:
            corr_apply_btn.clicked.connect(self._compute_correlation)
            
        filter_preview_btn = self.findChild(QPushButton, "filterPreviewBtn")
        filter_apply_btn = self.findChild(QPushButton, "filterApplyBtn")
        if filter_preview_btn:
            filter_preview_btn.clicked.connect(self._preview_filter)
        if filter_apply_btn:
            filter_apply_btn.clicked.connect(self._apply_filter)
        if self._filter_type:
            self._filter_type.currentTextChanged.connect(self._on_filter_type_changed)
        
        # === TAB SINCRONIZAÇÃO ===
        self._sync_datasets_list = self.findChild(QListWidget, "syncDatasetsList")
        self._sync_method = self.findChild(QComboBox, "syncMethodCombo")
        self._sync_grid_method = self.findChild(QComboBox, "syncGridMethodCombo")
        self._sync_dt_fixed = self.findChild(QCheckBox, "syncDtFixedCheck")
        self._sync_dt_value = self.findChild(QDoubleSpinBox, "syncDtValueSpin")
        self._sync_interp_method = self.findChild(QComboBox, "syncInterpMethodCombo")
        self._kalman_group = self.findChild(QGroupBox, "kalmanGroup")
        self._sync_process_noise = self.findChild(QDoubleSpinBox, "syncProcessNoiseSpin")
        self._sync_measurement_noise = self.findChild(QDoubleSpinBox, "syncMeasurementNoiseSpin")
        self._sync_create_new = self.findChild(QCheckBox, "syncCreateNewCheck")
        self._sync_keep_original = self.findChild(QCheckBox, "syncKeepOriginalCheck")
        
        # Botões de sincronização
        sync_refresh_btn = self.findChild(QPushButton, "syncRefreshBtn")
        sync_preview_btn = self.findChild(QPushButton, "syncPreviewBtn")
        sync_apply_btn = self.findChild(QPushButton, "syncApplyBtn")
        if sync_refresh_btn:
            sync_refresh_btn.clicked.connect(self._refresh_sync_datasets)
        if sync_preview_btn:
            sync_preview_btn.clicked.connect(self._preview_sync)
        if sync_apply_btn:
            sync_apply_btn.clicked.connect(self._apply_sync)
        if self._sync_method:
            self._sync_method.currentTextChanged.connect(self._on_sync_method_changed)
        if self._sync_dt_fixed:
            self._sync_dt_fixed.toggled.connect(self._on_sync_dt_fixed_changed)
        
        # === TAB STREAMING ===
        self._streaming_rate = self.findChild(QSpinBox, "streamRateSpin")
        self._streaming_window = self.findChild(QSpinBox, "streamWindowSpin")
        self._streaming_scroll_mode = self.findChild(QComboBox, "streamScrollModeCombo")
        self._streaming_buffer_size = self.findChild(QSpinBox, "bufferSizeSpin")
        self._streaming_auto_decimate = self.findChild(QCheckBox, "autoDecimateCheck")
        self._streaming_fps_label = self.findChild(QLabel, "streamFpsLabel")
        self._streaming_latency_label = self.findChild(QLabel, "streamLatencyLabel")
        self._streaming_points_label = self.findChild(QLabel, "streamPointsSecLabel")
        self._streaming_status_label = self.findChild(QLabel, "streamStatus")
        
        # Botões de streaming
        stream_start_btn = self.findChild(QPushButton, "streamStartBtn")
        stream_pause_btn = self.findChild(QPushButton, "streamPauseBtn")
        stream_stop_btn = self.findChild(QPushButton, "streamStopBtn")
        if stream_start_btn:
            stream_start_btn.clicked.connect(self._start_streaming)
        if stream_pause_btn:
            stream_pause_btn.clicked.connect(self._pause_streaming)
        if stream_stop_btn:
            stream_stop_btn.clicked.connect(self._stop_streaming)
        
        # === TAB EXPORTAÇÃO ===
        self._export_format = self.findChild(QComboBox, "exportFormatCombo")
        self._export_metadata = self.findChild(QCheckBox, "exportMetadataCheck")
        self._export_timestamps = self.findChild(QCheckBox, "exportTimestampsCheck")
        self._export_interp_flags = self.findChild(QCheckBox, "exportInterpFlagsCheck")
        self._export_selected_only = self.findChild(QCheckBox, "exportSelectedOnlyCheck")
        
        # Botões de exportação
        export_data_btn = self.findChild(QPushButton, "exportDataBtn")
        export_session_btn = self.findChild(QPushButton, "exportSessionBtn")
        export_plot_btn = self.findChild(QPushButton, "exportPlotBtn")
        if export_data_btn:
            export_data_btn.clicked.connect(self._export_data)
        if export_session_btn:
            export_session_btn.clicked.connect(self._export_session)
        if export_plot_btn:
            export_plot_btn.clicked.connect(self._export_plot)
        
        # === TAB CONFIGURAÇÕES ===
        self._theme_combo = self.findChild(QComboBox, "themeCombo")
        self._plot_style_combo = self.findChild(QComboBox, "plotStyleCombo")
        self._antialiasing_check = self.findChild(QCheckBox, "antialiasingCheck")
        self._plot_dpi_spin = self.findChild(QSpinBox, "plotDpiSpin")
        self._direct_render_limit = self.findChild(QSpinBox, "directRenderLimitSpin")
        self._target_display_points = self.findChild(QSpinBox, "targetDisplayPointsSpin")
        self._decimation_method = self.findChild(QComboBox, "decimationMethodCombo")
        self._use_threading = self.findChild(QCheckBox, "useThreadingCheck")
        self._date_format = self.findChild(QComboBox, "dateFormatCombo")
        self._numeric_precision = self.findChild(QSpinBox, "numericPrecisionSpin")
        self._auto_detect_types = self.findChild(QCheckBox, "autoDetectTypesCheck")
        
        # Botões de configurações
        settings_apply_btn = self.findChild(QPushButton, "settingsApplyBtn")
        settings_reset_btn = self.findChild(QPushButton, "settingsResetBtn")
        if settings_apply_btn:
            settings_apply_btn.clicked.connect(self._apply_settings)
        if settings_reset_btn:
            settings_reset_btn.clicked.connect(self._reset_settings)
        
        # === TAB HISTÓRICO ===
        clear_history_btn = self.findChild(QPushButton, "clearHistoryBtn")
        if clear_history_btn:
            clear_history_btn.clicked.connect(self._clear_history)
        if self._history_list:
            self._history_list.itemDoubleClicked.connect(self._replay_operation)
        
        # Inicializar lista de datasets se existir
        if self._sync_datasets_list:
            QTimer.singleShot(100, self._refresh_sync_datasets)
        
        logger.debug("operations_panel_ui_setup_complete")

    def _create_combo_box(self) -> StableComboBox:
        """Cria um ComboBox estável que não fecha automaticamente"""
        return StableComboBox()

    # === MÉTODOS DE OPERAÇÕES (a UI é carregada do arquivo .ui) ===

    def _on_sync_method_changed(self, method: str):
        """Mostra/oculta parâmetros Kalman conforme método selecionado"""
        if hasattr(self, '_kalman_group') and self._kalman_group:
            self._kalman_group.setVisible(method == "kalman_align")

    def _on_sync_dt_fixed_changed(self, checked: bool):
        """Habilita/desabilita campo de dt fixo"""
        if hasattr(self, '_sync_dt_value') and self._sync_dt_value:
            self._sync_dt_value.setEnabled(checked)
        if hasattr(self, '_sync_grid_method') and self._sync_grid_method:
            self._sync_grid_method.setEnabled(not checked)

    def _refresh_sync_datasets(self):
        """Atualiza lista de datasets disponíveis para sincronização"""
        self._sync_datasets_list.clear()

        if not self.session_state:
            return

        # Obter todos os datasets carregados
        dataset_ids = self.session_state.list_datasets()

        for dataset_id in dataset_ids:
            dataset = self.session_state.get_dataset(dataset_id)
            if dataset:
                n_series = len(dataset.series) if dataset.series else 0
                item_text = f"{dataset_id} ({n_series} séries)"
                self._sync_datasets_list.addItem(item_text)

        if len(dataset_ids) < 2:
            info_item = self._sync_datasets_list.item(0)
            if info_item:
                info_item.setToolTip("Carregue pelo menos 2 datasets para sincronizar")

    def _get_sync_params(self) -> dict:
        """Coleta parâmetros de sincronização"""
        params = {
            "method": self._sync_method.currentText(),
            "grid_method": self._sync_grid_method.currentText(),
            "interp_method": self._sync_interp_method.currentText(),
        }

        if self._sync_dt_fixed.isChecked():
            params["dt"] = self._sync_dt_value.value()

        if self._sync_method.currentText() == "kalman_align":
            params["process_noise"] = self._sync_process_noise.value()
            params["measurement_noise"] = self._sync_measurement_noise.value()

        return params

    def _get_selected_sync_datasets(self) -> list[str]:
        """Retorna IDs dos datasets selecionados para sincronização"""
        selected = []
        for item in self._sync_datasets_list.selectedItems():
            # Extrair ID do texto (formato: "dataset_id (N séries)")
            text = item.text()
            dataset_id = text.split(" (")[0]
            selected.append(dataset_id)
        return selected

    def _preview_sync(self):
        """Preview da sincronização com visualização gráfica"""
        import numpy as np
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        
        selected_datasets = self._get_selected_sync_datasets()

        if len(selected_datasets) < 2:
            QMessageBox.warning(
                self, "Aviso",
                "Selecione pelo menos 2 datasets para sincronizar.\n"
                "Use Ctrl+Click para selecionar múltiplos."
            )
            return

        params = self._get_sync_params()
        
        # Coletar dados para preview
        all_series_data = {}
        all_t_data = {}
        
        for dataset_id in selected_datasets:
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or not dataset.series:
                continue
                
            for series_id, series in dataset.series.items():
                key = f"{dataset_id}/{series_id}"
                if series.values is not None and len(series.values) > 0:
                    all_series_data[key] = np.array(series.values[:1000])  # Limitar para preview
                    if hasattr(dataset, 't_seconds') and dataset.t_seconds is not None:
                        all_t_data[key] = np.array(dataset.t_seconds[:1000])
                    else:
                        all_t_data[key] = np.arange(len(series.values[:1000]))
        
        if len(all_series_data) < 2:
            QMessageBox.warning(self, "Aviso", "Dados insuficientes para preview.")
            return
            
        # Criar diálogo de preview
        dialog = QDialog(self)
        dialog.setWindowTitle("Preview de Sincronização")
        dialog.resize(900, 700)
        dialog_layout = QVBoxLayout(dialog)
        
        # Criar figura com 2 subplots
        fig = Figure(figsize=(10, 8), dpi=100)
        canvas = FigureCanvas(fig)
        
        # Subplot 1: Dados originais
        ax1 = fig.add_subplot(211)
        ax1.set_title("Dados Originais (antes da sincronização)", fontsize=12, fontweight='bold')
        
        colors = ['#0d6efd', '#198754', '#dc3545', '#fd7e14', '#6f42c1', '#20c997']
        for i, (key, values) in enumerate(all_series_data.items()):
            t = all_t_data[key]
            color = colors[i % len(colors)]
            ax1.plot(t, values, label=key[:30], color=color, alpha=0.8, linewidth=1)
        
        ax1.set_xlabel("Tempo (s)")
        ax1.set_ylabel("Valor")
        ax1.legend(loc='upper right', fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Histograma de intervalos de tempo
        ax2 = fig.add_subplot(212)
        ax2.set_title("Distribuição de Intervalos de Tempo (dt)", fontsize=12, fontweight='bold')
        
        all_dts = []
        for key, t in all_t_data.items():
            if len(t) > 1:
                dt = np.diff(t)
                all_dts.extend(dt)
        
        if all_dts:
            ax2.hist(all_dts, bins=50, color='#0d6efd', alpha=0.7, edgecolor='white')
            ax2.axvline(np.median(all_dts), color='#dc3545', linestyle='--', 
                       label=f'Mediana: {np.median(all_dts):.4f}s')
            ax2.axvline(np.mean(all_dts), color='#198754', linestyle='--', 
                       label=f'Média: {np.mean(all_dts):.4f}s')
            ax2.legend()
        
        ax2.set_xlabel("dt (segundos)")
        ax2.set_ylabel("Frequência")
        ax2.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        dialog_layout.addWidget(canvas)
        
        # Info label
        info_label = QLabel(
            f"📊 Datasets: {', '.join(selected_datasets)}\n"
            f"📈 Total de séries: {len(all_series_data)}\n"
            f"⚙️ Método: {params['method']} | Interpolação: {params['interp_method']}"
        )
        info_label.setStyleSheet("padding: 10px; background: #f8f9fa; border-radius: 4px;")
        dialog_layout.addWidget(info_label)
        
        # Botões
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        dialog_layout.addLayout(btn_layout)
        
        dialog.exec()
        logger.info(f"sync_preview_shown: {len(all_series_data)} series")

    def _apply_sync(self):
        """Aplica sincronização aos datasets selecionados"""
        from datetime import datetime as dt

        import numpy as np
        from pint import UnitRegistry

        from platform_base.core.models import (
            Dataset,
            DatasetMetadata,
            Series,
            SeriesMetadata,
            SourceInfo,
        )
        from platform_base.processing.synchronization import synchronize

        ureg = UnitRegistry()
        selected_datasets = self._get_selected_sync_datasets()

        if len(selected_datasets) < 2:
            QMessageBox.warning(
                self, "Aviso",
                "Selecione pelo menos 2 datasets para sincronizar.\n"
                "Use Ctrl+Click para selecionar múltiplos."
            )
            return

        params = self._get_sync_params()

        logger.info(f"sync_requested: datasets={selected_datasets}, params={params}")

        try:
            # Coletar todas as séries de todos os datasets
            series_dict = {}  # nome -> valores
            t_dict = {}       # nome -> timestamps

            for dataset_id in selected_datasets:
                dataset = self.session_state.get_dataset(dataset_id)
                if not dataset or not dataset.series:
                    continue

                for series_id, series in dataset.series.items():
                    key = f"{dataset_id}/{series_id}"

                    if series.values is not None and len(series.values) > 0:
                        series_dict[key] = np.array(series.values, dtype=float)

                        # Usar timestamps se disponível, senão criar índice
                        if hasattr(dataset, 't_seconds') and dataset.t_seconds is not None:
                            t_dict[key] = np.array(dataset.t_seconds, dtype=float)
                        else:
                            t_dict[key] = np.arange(len(series.values), dtype=float)

            if len(series_dict) < 2:
                QMessageBox.warning(
                    self, "Aviso",
                    "Não há séries suficientes para sincronizar."
                )
                return

            # Executar sincronização
            result = synchronize(
                series_dict=series_dict,
                t_dict=t_dict,
                method=params["method"],
                params=params,
            )

            # Criar novo dataset com séries sincronizadas se solicitado
            if self._sync_create_new.isChecked():
                synced_series = {}
                for key, values in result.synced_series.items():
                    series_id = key.replace("/", "_").replace("-", "_")
                    series = Series(
                        series_id=series_id,
                        name=key,
                        unit=ureg.dimensionless,
                        values=np.array(values, dtype=np.float64),
                        metadata=SeriesMetadata(
                            original_name=key,
                            source_column=key,
                            description=f"Série sincronizada de {key}"
                        )
                    )
                    synced_series[series_id] = series

                # Criar timestamps como datetime
                t_common = result.t_common
                base_time = np.datetime64('2024-01-01T00:00:00')
                t_datetime = base_time + (t_common * 1e9).astype('timedelta64[ns]')

                synced_dataset = Dataset(
                    dataset_id="synchronized",
                    version=1,
                    parent_id=None,
                    source=SourceInfo(
                        filepath="memory://synchronized",
                        filename="synchronized.sync",
                        format="sync",
                        size_bytes=0,
                        checksum="sync_generated"
                    ),
                    t_seconds=np.array(t_common, dtype=np.float64),
                    t_datetime=t_datetime,
                    series=synced_series,
                    metadata=DatasetMetadata(
                        description=f"Datasets sincronizados: {', '.join(selected_datasets)}",
                        tags=["synchronized", "generated"],
                        custom={
                            "source_datasets": selected_datasets,
                            "sync_method": params["method"],
                            "alignment_error": result.alignment_error,
                            "confidence": result.confidence,
                        }
                    ),
                    created_at=dt.now(),
                )

                self.session_state.add_dataset(synced_dataset)

            # Adicionar ao histórico
            self._add_to_history("synchronize", {
                **params,
                "datasets": selected_datasets,
                "n_series": len(result.synced_series),
            })

            # Mostrar resultado
            QMessageBox.information(
                self, "Sincronização Concluída",
                f"Séries sincronizadas: {len(result.synced_series)}\n"
                f"Pontos na grade comum: {len(result.t_common):,}\n"
                f"Erro de alinhamento: {result.alignment_error:.4f}\n"
                f"Confiança: {result.confidence:.1%}\n\n"
                "Novo dataset 'synchronized' criado."
            )

            logger.info(f"sync_completed: n_series={len(result.synced_series)}, "
                       f"error={result.alignment_error:.4f}, confidence={result.confidence:.2f}")

        except Exception as e:
            logger.exception(f"sync_failed: {e}")
            QMessageBox.critical(
                self, "Erro na Sincronização",
                f"Falha ao sincronizar datasets:\n{e!s}"
            )

    # === HANDLERS DE STREAMING ===

    def _start_streaming(self):
        """Inicia streaming de dados históricos do dataset carregado"""
        # Verificar se há dataset carregado
        all_datasets = self.session_state.get_all_datasets()
        if not all_datasets:
            QMessageBox.warning(self, "Aviso", 
                "Nenhum dataset carregado.\n\n"
                "Carregue um arquivo Excel/CSV primeiro para fazer streaming dos dados históricos.")
            return
        
        # Obter dados do dataset atual
        dataset_id = list(all_datasets.keys())[0]  # Primeiro dataset
        dataset = all_datasets[dataset_id]

        if not dataset.series:
            QMessageBox.warning(self, "Aviso", 
                "O dataset não contém séries de dados.")
            return
        
        # Configurar dados para streaming
        self._streaming_data = {}
        total_points = 0
        
        for series_id, series in dataset.series.items():
            if series.values is not None and len(series.values) > 0:
                x_data = np.arange(len(series.values))  # Índice como tempo
                # Usar t_seconds se disponível
                if hasattr(dataset, 't_seconds') and dataset.t_seconds is not None:
                    x_data = np.array(dataset.t_seconds)
                    if len(x_data) > len(series.values):
                        x_data = x_data[:len(series.values)]
                    elif len(x_data) < len(series.values):
                        x_data = np.arange(len(series.values))
                
                y_data = np.array(series.values)
                self._streaming_data[series_id] = {
                    'x': x_data,
                    'y': y_data,
                    'name': series.name or series_id
                }
                total_points = max(total_points, len(y_data))
        
        if not self._streaming_data:
            QMessageBox.warning(self, "Aviso", 
                "Não há dados válidos para streaming.")
            return
        
        # Configurar parâmetros de streaming
        self._streaming_position = 0
        self._streaming_paused = False
        self._frame_count = 0
        self._total_points_sent = 0
        self._streaming_start_time = time.time()
        self._last_fps_update = time.time()
        
        # Calcular intervalo do timer baseado no FPS configurado
        fps = self._stream_rate.value()
        interval_ms = int(1000 / fps)  # Converter FPS para milissegundos
        
        # Calcular pontos por frame baseado na janela
        window_size = self._stream_window.value()
        total_frames_needed = total_points // window_size
        if total_frames_needed == 0:
            total_frames_needed = 1
        
        # Criar e iniciar timer
        if self._streaming_timer is None:
            self._streaming_timer = QTimer(self)
            self._streaming_timer.timeout.connect(self._streaming_update)
        
        self._streaming_timer.setInterval(interval_ms)
        self._streaming_timer.start()
        
        # Atualizar UI
        self._stream_status.setText("▶️ Streaming")
        self._stream_status.setStyleSheet("font-weight: bold; color: #28a745;")
        
        # Atualizar info do buffer
        buffer_size = self._buffer_size.value()
        self._buffer_current.setText(f"0 / {buffer_size:,}")
        
        logger.info(f"streaming_started_historical: dataset={dataset_id}, "
                   f"series_count={len(self._streaming_data)}, "
                   f"total_points={total_points}, fps={fps}")

    def _streaming_update(self):
        """Atualiza streaming com próximo chunk de dados"""
        if self._streaming_paused:
            return
        
        window_size = self._stream_window.value()
        scroll_mode = self._stream_scroll.currentText()
        buffer_size = self._buffer_size.value()
        
        # Determinar chunk de dados a enviar
        end_pos = self._streaming_position + window_size
        
        # Para cada série, enviar o chunk atual
        points_this_frame = 0
        all_done = True
        
        for series_id, data in self._streaming_data.items():
            x_data = data['x']
            y_data = data['y']
            series_name = data['name']
            
            if self._streaming_position < len(y_data):
                all_done = False
                
                # Calcular slice de dados
                start_idx = max(0, self._streaming_position - buffer_size) if scroll_mode == "Janela Deslizante" else 0
                end_idx = min(end_pos, len(y_data))
                
                x_chunk = x_data[start_idx:end_idx]
                y_chunk = y_data[start_idx:end_idx]
                
                points_this_frame += len(y_chunk)
                
                # Emitir sinal com dados atualizados
                self.streaming_data_updated.emit(series_id, x_chunk, y_chunk)
        
        # Atualizar posição
        self._streaming_position = end_pos
        self._frame_count += 1
        self._total_points_sent += points_this_frame
        
        # Atualizar estatísticas a cada 0.5 segundos
        current_time = time.time()
        if current_time - self._last_fps_update >= 0.5:
            elapsed = current_time - self._streaming_start_time
            
            # FPS real
            real_fps = self._frame_count / elapsed if elapsed > 0 else 0
            self._stream_fps_label.setText(f"{real_fps:.1f} FPS")
            
            # Latência (estimada como tempo por frame)
            latency_ms = (1000 / real_fps) if real_fps > 0 else 0
            self._stream_latency.setText(f"{latency_ms:.1f} ms")
            
            # Pontos por segundo
            points_per_sec = self._total_points_sent / elapsed if elapsed > 0 else 0
            self._stream_points_sec.setText(f"{points_per_sec:,.0f} pts/s")
            
            # Buffer atual
            buffer_used = min(self._streaming_position, buffer_size)
            self._buffer_current.setText(f"{buffer_used:,} / {buffer_size:,}")
            
            self._last_fps_update = current_time
        
        # Verificar se chegou ao fim
        if all_done:
            self._stop_streaming()
            QMessageBox.information(self, "Streaming Concluído", 
                f"Streaming finalizado!\n\n"
                f"Total de frames: {self._frame_count:,}\n"
                f"Total de pontos: {self._total_points_sent:,}\n"
                f"Tempo total: {current_time - self._streaming_start_time:.1f}s")

    def _pause_streaming(self):
        """Pausa streaming"""
        if self._streaming_timer and self._streaming_timer.isActive():
            self._streaming_paused = True
            self._streaming_timer.stop()
            self._stream_status.setText("⏸️ Pausado")
            self._stream_status.setStyleSheet("font-weight: bold; color: #ffc107;")
            logger.info("streaming_paused")
        else:
            # Retomar se estava pausado
            if self._streaming_paused and self._streaming_timer:
                self._streaming_paused = False
                self._streaming_timer.start()
                self._stream_status.setText("▶️ Streaming")
                self._stream_status.setStyleSheet("font-weight: bold; color: #28a745;")
                logger.info("streaming_resumed")

    def _stop_streaming(self):
        """Para streaming e reseta estado"""
        if self._streaming_timer:
            self._streaming_timer.stop()
        
        self._streaming_position = 0
        self._streaming_paused = False
        self._streaming_data = {}
        
        # Resetar estatísticas
        self._stream_status.setText("⏹️ Parado")
        self._stream_status.setStyleSheet("font-weight: bold; color: #6c757d;")
        self._stream_fps_label.setText("0 FPS")
        self._stream_latency.setText("0 ms")
        self._stream_points_sec.setText("0 pts/s")
        self._buffer_current.setText("0 / 100000")
        
        logger.info("streaming_stopped")

    # === HANDLERS DE CONFIGURAÇÃO ===

    def _apply_settings(self):
        """Aplica configurações"""
        logger.info("settings_applied")
        QMessageBox.information(self, "Configurações",
            "Configurações aplicadas com sucesso!\n\n"
            "Algumas configurações podem requerer reinício da aplicação.")

    def _reset_settings(self):
        """Restaura configurações padrão"""
        # Visualização
        self._theme_combo.setCurrentIndex(0)
        self._plot_style.setCurrentIndex(0)
        self._antialiasing.setChecked(True)
        self._plot_dpi.setValue(100)

        # Performance
        self._direct_render_limit.setValue(10000)
        self._target_display_points.setValue(5000)
        self._decimation_method.setCurrentIndex(0)
        self._use_threading.setChecked(True)

        # Dados
        self._date_format.setCurrentIndex(0)
        self._numeric_precision.setValue(6)
        self._auto_detect_types.setChecked(True)

        logger.info("settings_reset")
        QMessageBox.information(self, "Configurações",
            "Configurações restauradas para os valores padrão.")

    def _setup_connections(self):
        """Configura conexões de sinais"""
        # Apenas uma conexão para dataset_changed
        self.session_state.dataset_changed.connect(self._update_series_selector)
        self.session_state.operation_finished.connect(self._on_operation_finished)

    @pyqtSlot(str)
    def _update_series_selector(self, dataset_id: str):
        """Atualiza o combobox de seleção de série com as séries do dataset atual"""
        try:
            self._series_combo.clear()
            
            if not dataset_id:
                self._series_combo.addItem("(Nenhum dataset carregado)")
                self._series_combo.setEnabled(False)
                return
                
            dataset = self.session_state.get_dataset(dataset_id)
            if not dataset or not dataset.series:
                self._series_combo.addItem("(Nenhuma série disponível)")
                self._series_combo.setEnabled(False)
                return
                
            # Adicionar séries ao combobox
            for series_id, series in dataset.series.items():
                # Usar nome do dataset + nome da série para melhor identificação
                display_name = f"{dataset_id} / {series.name if series.name else series_id}"
                n_points = len(series.values) if series.values is not None else 0
                self._series_combo.addItem(f"{display_name} ({n_points:,} pts)", series_id)
                
            self._series_combo.setEnabled(True)
        except Exception as e:
            logger.exception("_update_series_selector_failed", error=str(e))

    @pyqtSlot(str, bool)
    def _on_operation_finished(self, operation: str, success: bool):
        """Callback quando operação termina"""
        if self._history:
            self._history[-1].success = success
            self._update_history_display()

    def _add_to_history(self, operation: str, params: dict[str, Any]):
        """Adiciona operação ao histórico"""
        item = OperationHistoryItem(operation, params)
        self._history.append(item)

        if len(self._history) > self._max_history:
            self._history.pop(0)

        self._update_history_display()

    def _update_history_display(self):
        """Atualiza visualização do histórico"""
        self._history_list.clear()

        for item in reversed(self._history):
            icon = "✅" if item.success else "❌"
            text = f"{icon} {item.timestamp.strftime('%H:%M:%S')} - {item.operation}"

            list_item = QListWidgetItem(text)
            list_item.setData(Qt.ItemDataRole.UserRole, item)

            if not item.success:
                list_item.setForeground(QColor("#dc3545"))

            self._history_list.addItem(list_item)

    # === HANDLERS DE INTERPOLAÇÃO ===

    def _preview_interpolation(self):
        """Preview de interpolação com visualização gráfica"""

        params = self._get_interpolation_params()
        logger.info(f"interpolation_preview_requested: {params}")

        # Obter dados da série selecionada
        series_data = self._get_selected_series_data()

        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        # Mostrar preview dialog
        dialog = OperationPreviewDialog("interpolation", params, series_data, self)

        if dialog.exec():
            # Se usuário clicou "Aplicar", executar operação
            result = dialog.get_result()
            if result is not None:
                self._add_to_history("interpolation", params)
                self.operation_requested.emit("interpolation", params)
                logger.info(f"interpolation_applied_from_preview: {params}")

    def _apply_interpolation(self):
        """Aplica interpolação"""
        params = self._get_interpolation_params()
        self._add_to_history("interpolation", params)
        self.operation_requested.emit("interpolation", params)
        logger.info(f"interpolation_requested: {params}")

    def _get_interpolation_params(self) -> dict[str, Any]:
        """Coleta parâmetros de interpolação"""
        return {
            "method": self._interp_method.currentText(),
            "num_points": self._interp_points.value(),
            "smoothing": self._interp_smooth.value(),
            "degree": self._interp_degree.value(),
            "extrapolate": self._interp_extrapolate.isChecked(),
        }

    # === HANDLERS DE CÁLCULOS ===

    def _preview_derivative(self):
        """Preview de derivada com visualização gráfica"""

        order = self._deriv_order.currentIndex() + 1
        params = {
            "order": order,
            "method": self._deriv_method.currentText(),
            "window_length": self._deriv_window.value(),
            "pre_smooth": self._deriv_smooth.isChecked(),
        }
        logger.info(f"derivative_preview_requested: {params}")

        series_data = self._get_selected_series_data()
        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        dialog = OperationPreviewDialog("derivative", params, series_data, self)
        if dialog.exec():
            result = dialog.get_result()
            if result is not None:
                self._add_to_history(f"derivative_{order}order", params)
                self.operation_requested.emit("derivative", params)

    def _preview_integral(self):
        """Preview de integral com visualização gráfica"""
        params = {"method": self._integ_method.currentText()}
        logger.info(f"integral_preview_requested: {params}")

        series_data = self._get_selected_series_data()
        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        dialog = OperationPreviewDialog("integral", params, series_data, self)
        if dialog.exec():
            result = dialog.get_result()
            if result is not None:
                self._add_to_history("integral", params)
                self.operation_requested.emit("integral", params)

    def _preview_smoothing(self):
        """Preview de suavização com visualização gráfica"""
        params = {
            "method": self._smooth_method.currentText(),
            "window": self._smooth_window.value(),
            "sigma": self._smooth_sigma.value(),
        }
        logger.info(f"smoothing_preview_requested: {params}")

        series_data = self._get_selected_series_data()
        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        dialog = OperationPreviewDialog("smoothing", params, series_data, self)
        if dialog.exec():
            result = dialog.get_result()
            if result is not None:
                self._add_to_history("smoothing", params)
                self.operation_requested.emit("smoothing", params)

    def _preview_remove_outliers(self):
        """Preview de remoção de outliers com visualização gráfica"""
        params = {
            "method": self._outlier_method.currentText(),
            "threshold": self._outlier_threshold.value(),
        }
        logger.info(f"outlier_removal_preview_requested: {params}")

        series_data = self._get_selected_series_data()
        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        dialog = OperationPreviewDialog("remove_outliers", params, series_data, self)
        if dialog.exec():
            result = dialog.get_result()
            if result is not None:
                self._add_to_history("remove_outliers", params)
                self.operation_requested.emit("remove_outliers", params)

    def _calculate_derivative(self):
        """Calcula derivada"""
        order = self._deriv_order.currentIndex() + 1
        params = {
            "order": order,
            "method": self._deriv_method.currentText(),
            "window_length": self._deriv_window.value(),
            "pre_smooth": self._deriv_smooth.isChecked(),
        }
        self._add_to_history(f"derivative_{order}order", params)
        self.operation_requested.emit("derivative", params)
        logger.info(f"derivative_requested: {params}")

    def _calculate_integral(self):
        """Calcula integral"""
        params = {"method": self._integ_method.currentText()}
        self._add_to_history("integral", params)
        self.operation_requested.emit("integral", params)
        logger.info(f"integral_requested: {params}")

    def _calculate_area(self):
        """Calcula área"""
        area_type = self._area_type.currentText()
        params = {"type": "under_curve" if "sob" in area_type.lower() else "between_curves"}
        self._add_to_history("area", params)
        self.operation_requested.emit("area", params)
        logger.info(f"area_requested: {params}")

    # === HANDLERS DE FILTROS ===

    def _apply_smoothing(self):
        """Aplica suavização"""
        params = {
            "method": self._smooth_method.currentText(),
            "window": self._smooth_window.value(),
            "sigma": self._smooth_sigma.value(),
        }
        self._add_to_history("smoothing", params)
        self.operation_requested.emit("smoothing", params)
        logger.info(f"smoothing_requested: {params}")

    def _remove_outliers(self):
        """Remove outliers"""
        params = {
            "method": self._outlier_method.currentText(),
            "threshold": self._outlier_threshold.value(),
        }
        self._add_to_history("remove_outliers", params)
        self.operation_requested.emit("remove_outliers", params)
        logger.info(f"outlier_removal_requested: {params}")

    # === HANDLERS DE ANÁLISE AVANÇADA ===

    def _compute_fft(self):
        """Compute FFT analysis"""
        window = self._fft_window.currentText()
        if window == "none":
            window = None

        params = {
            "window": window,
            "detrend": self._fft_detrend.isChecked(),
        }

        logger.info("fft_requested", params=params)
        self._add_to_history("fft", params)
        self.operation_requested.emit("fft", params)

    def _compute_correlation(self):
        """Compute correlation analysis"""
        params = {
            "mode": self._corr_mode.currentText(),
            "normalize": self._corr_normalize.isChecked(),
        }

        logger.info("correlation_requested", params=params)
        self._add_to_history("correlation", params)
        self.operation_requested.emit("correlation", params)

    def _on_filter_type_changed(self, filter_type: str):
        """Handle filter type change to show/hide cutoff fields"""
        is_band = filter_type in ("bandpass", "bandstop")

        self._filter_cutoff_high.setVisible(is_band)
        self._filter_cutoff_high_label.setVisible(is_band)

        if is_band:
            self._filter_cutoff_label.setText("Low Cutoff (Hz):")
        else:
            self._filter_cutoff_label.setText("Cutoff (Hz):")

    def _apply_filter(self):
        """Apply digital filter to signal"""
        filter_type = self._filter_type.currentText()

        params = {
            "filter_type": filter_type,
            "filter_order": self._filter_order.value(),
            "method": self._filter_method.currentText(),
        }

        # Add cutoff frequencies based on filter type
        if filter_type in ("bandpass", "bandstop"):
            params["cutoff_frequency"] = (
                self._filter_cutoff.value(),
                self._filter_cutoff_high.value()
            )
        else:
            params["cutoff_frequency"] = self._filter_cutoff.value()

        logger.info("filter_requested", params=params)
        self._add_to_history(f"{filter_type}_filter", params)
        self.operation_requested.emit("filter", params)

    def _preview_filter(self):
        """Preview digital filter effects"""
        filter_type = self._filter_type.currentText()

        params = {
            "filter_type": filter_type,
            "filter_order": self._filter_order.value(),
            "method": self._filter_method.currentText(),
        }

        if filter_type in ("bandpass", "bandstop"):
            params["cutoff_frequency"] = (
                self._filter_cutoff.value(),
                self._filter_cutoff_high.value()
            )
        else:
            params["cutoff_frequency"] = self._filter_cutoff.value()

        logger.info(f"filter_preview_requested: {params}")

        series_data = self._get_selected_series_data()
        if series_data is None or len(series_data) == 0:
            QMessageBox.warning(self, "Aviso",
                "Selecione uma série de dados para preview.")
            return

        dialog = OperationPreviewDialog("filter", params, series_data, self)
        if dialog.exec():
            result = dialog.get_result()
            if result is not None:
                self._add_to_history(f"{filter_type}_filter", params)
                self.operation_requested.emit("filter", params)

    # === HANDLERS DE EXPORT ===

    def _export_data(self):
        """Exporta dados"""
        format_map = {
            "CSV": "csv",
            "Excel (.xlsx)": "xlsx",
            "Parquet": "parquet",
            "HDF5": "hdf5",
            "JSON": "json",
        }

        format_text = self._export_format.currentText()
        params = {
            "format": format_map.get(format_text, "csv"),
            "include_metadata": self._export_metadata.isChecked(),
            "include_timestamps": self._export_timestamps.isChecked(),
            "include_interp_flags": self._export_interp_flags.isChecked(),
            "selected_only": self._export_selected_only.isChecked(),
        }

        self._add_to_history("export_data", params)
        self.export_requested.emit(params["format"], params)
        logger.info(f"export_data_requested: {params}")

    def _export_session(self):
        """Exporta sessão"""
        self.export_requested.emit("session", {"type": "session"})
        logger.info("export_session_requested")

    def _export_plot(self):
        """Exporta gráfico"""
        self.export_requested.emit("image", {"type": "plot"})
        logger.info("export_plot_requested")

    # === HANDLERS DE HISTÓRICO ===

    def _clear_history(self):
        """Limpa histórico"""
        self._history.clear()
        self._history_list.clear()
        logger.info("history_cleared")

    def _replay_selected(self):
        """Repete operação selecionada"""
        current = self._history_list.currentItem()
        if current:
            self._replay_operation(current)

    def _replay_operation(self, item: QListWidgetItem):
        """Repete uma operação do histórico"""
        history_item = item.data(Qt.ItemDataRole.UserRole)
        if history_item:
            logger.info(f"replaying_operation: {history_item.operation}, params={history_item.params}")
            self.operation_requested.emit(history_item.operation, history_item.params)

    # === MÉTODOS PÚBLICOS PARA DIÁLOGOS ===

    def show_interpolation_dialog(self):
        """Mostra diálogo de interpolação expandido"""
        self._tabs.setCurrentIndex(0)
        logger.debug("interpolation_dialog_shown")

    def show_derivative_dialog(self):
        """Mostra diálogo de derivada"""
        self._tabs.setCurrentIndex(1)
        logger.debug("derivative_dialog_shown")

    def show_integral_dialog(self):
        """Mostra diálogo de integral"""
        self._tabs.setCurrentIndex(1)
        logger.debug("integral_dialog_shown")

    def show_export_dialog(self):
        """Mostra diálogo de exportação"""
        self._tabs.setCurrentIndex(3)
        logger.debug("export_dialog_shown")

    # === MÉTODOS DE DADOS ===

    def _get_selected_series_data(self):
        """
        Obtém dados da série selecionada para preview

        Returns:
            numpy.ndarray ou None se não houver seleção
        """
        import numpy as np

        # Obter série selecionada do combobox
        if not hasattr(self, '_series_combo') or self._series_combo.count() == 0:
            logger.debug("No series selector available")
            return None
            
        series_id = self._series_combo.currentData()
        if not series_id:
            logger.debug("No series selected in combo")
            return None
            
        # Obter dados do SessionState
        if self.session_state and self.session_state.current_dataset:
            dataset = self.session_state.get_dataset(self.session_state.current_dataset)
            if dataset and series_id in dataset.series:
                series = dataset.series[series_id]
                if hasattr(series, 'values') and series.values is not None:
                    logger.debug(f"Got series data: {series_id}, {len(series.values)} points")
                    return series.values
                    
        logger.debug("No series data available")
        return None

    def set_data(self, data):
        """
        Define os dados para preview

        Args:
            data: numpy.ndarray ou pandas.DataFrame
        """
        self.session_state._loaded_data = data
        logger.debug("data_set_for_preview")
