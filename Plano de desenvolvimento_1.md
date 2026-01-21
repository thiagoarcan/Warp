# SPEC/PRD Técnico Completo — Platform Base v2.0 (PyQt6 Desktop)

**Aplicação Desktop para Análise Exploratória de Séries Temporais**  
**Documento de Migração Dash → PyQt6**

---

## 1. Objetivo do Produto

Desenvolver aplicação desktop Python **Platform Base** (PyQt6) para manipular e explorar séries temporais de sensores com timestamps irregulares. A aplicação permite:

- Upload e ingestão robusta multi-formato (CSV/Excel/Parquet/HDF5)
- Detecção automática de schema com validação rigorosa
- Normalização de unidades com rastreabilidade completa
- Interpolação com múltiplos métodos e tracking de proveniência
- Sincronização de múltiplas séries
- Cálculos matemáticos (derivadas 1ª-3ª ordem, integrais, áreas)
- Visualização exploratória 2D/3D nativa com interatividade avançada
- Streaming temporal com sincronização multi-view
- Exportação e persistência de sessão
- Extensibilidade via plugins com isolamento e versionamento

**Interface:** Aplicação desktop nativa multiplataforma (Windows/Linux/macOS)

**Não escopo:** análises de domínio específico, detecção de eventos, alarmes, diagnósticos.

---

## 2. Mapeamento de Migração Dash → PyQt6

### 2.1 Tabela de Equivalências

| Conceito Dash | Equivalente PyQt6 | Notas |
|---------------|-------------------|-------|
| `dcc.Interval` | `QTimer` | Mesmo padrão: timeout → callback |
| `dash.callback` | `pyqtSignal/pyqtSlot` | Signals conectam a slots |
| `dash.Store` (client-side) | `SessionState` (Python object) | Sem serialização client/server |
| `dash.long_callback` | `QThread` + Worker | Background processing |
| `html.Div` | `QWidget` | Container base |
| `dcc.Graph` (Plotly) | `pg.PlotWidget` / `QtInteractor` | pyqtgraph (2D) / PyVista (3D) |
| `dash.dcc.Loading` | `QProgressBar` / `QBusyIndicator` | Indicadores de loading |
| `callback_context` | `sender()` + signal metadata | Identificar origem |
| `prevent_initial_call` | Lógica no slot | Verificar estado inicial |
| `debounce` | `QTimer.singleShot` | Debouncing manual |

### 2.2 Padrão de Conversão de Callbacks

**Dash (antes):**

```python
@callback(
    Output("graph", "figure"),
    Input("series-dropdown", "value"),
    State("dataset-store", "data"),
    prevent_initial_call=True
)
def update_graph(series_id, dataset_data):
    # lógica
    return figure
```

**PyQt6 (depois):**

```python
class VizPanel(QWidget):
    # Signal emitido quando seleção muda
    series_selected = pyqtSignal(str)  # series_id
    
    def __init__(self, session_state: SessionState):
        super().__init__()
        self.session_state = session_state
        self._initial_call = True
        
        # Conectar signal ao slot
        self.series_dropdown.currentTextChanged.connect(self._on_series_changed)
    
    @pyqtSlot(str)
    def _on_series_changed(self, series_id: str):
        # Equivalente a prevent_initial_call
        if self._initial_call:
            self._initial_call = False
            return
        
        # Equivalente a State (acessa session_state)
        dataset_data = self.session_state.current_dataset
        
        # Lógica de atualização
        self._update_graph(series_id, dataset_data)
```

---

## 3. Stack Tecnológica

- Python 3.10+
- **PyQt6** (UI desktop)
- **pyqtgraph** (plotting rápido 2D)
- **PyVista** + **pyvistaqt** (visualização 3D via VTK)
- numpy, pandas, scipy
- pint (conversão de unidades)
- joblib (cache + paralelismo)
- pydantic (validação)
- structlog (logging)
- numba (otimização)
- fastapi (API REST opcional)

---

## 4. Estrutura de Projeto

```
platform_base/
├─ src/
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ dataset_store.py      # Armazenamento de datasets
│  │  ├─ registry.py           # Plugin registry
│  │  ├─ orchestrator.py       # Pipeline execution
│  │  └─ protocols.py          # ABC/Protocol definitions
│  ├─ io/
│  │  ├─ __init__.py
│  │  ├─ loader.py             # Multi-format loader
│  │  ├─ schema_detector.py    # Schema detection
│  │  └─ validator.py          # Data validation
│  ├─ processing/
│  │  ├─ __init__.py
│  │  ├─ units.py              # Unit conversion (pint)
│  │  ├─ timebase.py           # Time normalization
│  │  ├─ interpolation.py      # 10 interpolation methods
│  │  ├─ synchronization.py    # Series sync
│  │  ├─ calculus.py           # Derivatives/integrals
│  │  └─ smoothing.py          # Pre-derivative filters
│  ├─ caching/
│  │  ├─ __init__.py
│  │  ├─ memory.py             # LRU cache
│  │  └─ disk.py               # joblib.Memory
│  ├─ viz/
│  │  ├─ __init__.py
│  │  ├─ base.py               # BasePlot abstraction
│  │  ├─ config.py             # PlotConfig
│  │  ├─ plot_2d.py            # pyqtgraph plots
│  │  ├─ plot_3d.py            # PyVista plots
│  │  ├─ multipanel.py         # Multi-panel layouts
│  │  ├─ heatmaps.py           # Heatmap visualization
│  │  ├─ downsampling.py       # LTTB/MinMax/Adaptive
│  │  └─ streaming.py          # StreamingEngine
│  ├─ desktop/                  # ← PyQt6 UI (NOVA CAMADA)
│  │  ├─ __init__.py
│  │  ├─ app.py                # QApplication setup
│  │  ├─ main_window.py        # MainWindow
│  │  ├─ session_state.py      # Estado centralizado
│  │  ├─ signal_hub.py         # Central signal dispatcher
│  │  ├─ widgets/
│  │  │  ├─ __init__.py
│  │  │  ├─ data_panel.py      # Dataset/series tree
│  │  │  ├─ viz_panel.py       # Visualization container
│  │  │  ├─ config_panel.py    # Configuration UI
│  │  │  ├─ results_panel.py   # Results/logs
│  │  │  ├─ streaming_panel.py # Streaming controls
│  │  │  ├─ selection_widget.py # Data selection
│  │  │  └─ context_menu.py    # Plot context menu
│  │  ├─ dialogs/
│  │  │  ├─ __init__.py
│  │  │  ├─ upload_dialog.py
│  │  │  ├─ export_dialog.py
│  │  │  ├─ settings_dialog.py
│  │  │  ├─ interpolation_dialog.py
│  │  │  ├─ derivative_dialog.py
│  │  │  └─ about_dialog.py
│  │  ├─ workers/
│  │  │  ├─ __init__.py
│  │  │  ├─ base_worker.py     # Worker base class
│  │  │  ├─ loader_worker.py
│  │  │  ├─ processing_worker.py
│  │  │  ├─ export_worker.py
│  │  │  ├─ streaming_worker.py
│  │  │  └─ video_export_worker.py
│  │  ├─ models/
│  │  │  ├─ __init__.py
│  │  │  ├─ dataset_model.py   # QAbstractItemModel
│  │  │  └─ series_model.py
│  │  └─ resources/
│  │     ├─ icons/
│  │     ├─ styles/
│  │     │  ├─ light.qss
│  │     │  └─ dark.qss
│  │     └─ resources.qrc
│  ├─ api/                      # REST API opcional
│  │  ├─ __init__.py
│  │  ├─ server.py
│  │  └─ endpoints.py
│  └─ utils/
│     ├─ __init__.py
│     ├─ ids.py                # ID generation
│     ├─ logging.py            # Structured logging
│     ├─ serialization.py
│     ├─ errors.py             # Exception hierarchy
│     └─ validation.py         # Input validation
├─ plugins/
│  ├─ README.md
│  ├─ _base.py
│  └─ advanced_sync/
│     ├─ manifest.json
│     ├─ __init__.py
│     └─ dtw_plugin.py
├─ configs/
│  ├─ platform.yaml
│  └─ examples/
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ property/
│  ├─ stress/
│  ├─ ui/                      # pytest-qt tests
│  └─ fixtures/
├─ docs/
├─ resources/                   # Compiled .qrc
├─ installers/                  # PyInstaller scripts
├─ pyproject.toml
└─ README.md
```

---

## 5. Modelo de Dados (Contratos)

### 5.1 Type Aliases

```python
# core/protocols.py
from typing import NewType
from uuid import UUID

DatasetID = NewType('DatasetID', str)
SeriesID = NewType('SeriesID', str)
SessionID = NewType('SessionID', str)
ViewID = NewType('ViewID', str)
PluginID = NewType('PluginID', str)
```

### 5.2 DatasetStore

```python
# core/dataset_store.py
from pydantic import BaseModel
from typing import Optional
import numpy as np

class DatasetStore:
    """
    Armazenamento central de datasets.
    Thread-safe para acesso de workers.
    """
    
    def __init__(self):
        self._datasets: dict[DatasetID, Dataset] = {}
        self._lock = threading.RLock()
    
    def add_dataset(self, dataset: Dataset) -> DatasetID:
        """Adiciona dataset e retorna ID"""
        with self._lock:
            self._datasets[dataset.dataset_id] = dataset
            return dataset.dataset_id
    
    def get_dataset(self, dataset_id: DatasetID) -> Dataset:
        """Retorna dataset por ID"""
        with self._lock:
            if dataset_id not in self._datasets:
                raise KeyError(f"Dataset {dataset_id} not found")
            return self._datasets[dataset_id]
    
    def list_datasets(self) -> list[DatasetSummary]:
        """Lista resumo de todos datasets"""
        with self._lock:
            return [
                DatasetSummary(
                    dataset_id=d.dataset_id,
                    name=d.source.filename,
                    n_series=len(d.series),
                    n_points=len(d.t_seconds),
                    created_at=d.created_at
                )
                for d in self._datasets.values()
            ]
    
    def add_series(self, dataset_id: DatasetID, series: Series, 
                   lineage: Lineage) -> SeriesID:
        """Adiciona série derivada a um dataset"""
        with self._lock:
            dataset = self._datasets[dataset_id]
            series.lineage = lineage
            dataset.series[series.series_id] = series
            return series.series_id
    
    def get_series(self, dataset_id: DatasetID, series_id: SeriesID) -> Series:
        """Retorna série específica"""
        with self._lock:
            return self._datasets[dataset_id].series[series_id]
    
    def list_series(self, dataset_id: DatasetID) -> list[SeriesSummary]:
        """Lista séries de um dataset"""
        with self._lock:
            dataset = self._datasets[dataset_id]
            return [
                SeriesSummary(
                    series_id=s.series_id,
                    name=s.name,
                    unit=str(s.unit),
                    n_points=len(s.values),
                    is_derived=s.lineage is not None
                )
                for s in dataset.series.values()
            ]
    
    def create_view(self, dataset_id: DatasetID, series_ids: list[SeriesID],
                    time_window: TimeWindow) -> ViewData:
        """Cria view para visualização"""
        with self._lock:
            dataset = self._datasets[dataset_id]
            
            # Aplicar janela temporal
            mask = (dataset.t_seconds >= time_window.start) & \
                   (dataset.t_seconds <= time_window.end)
            
            return ViewData(
                dataset_id=dataset_id,
                series={
                    sid: dataset.series[sid].values[mask]
                    for sid in series_ids
                },
                t_seconds=dataset.t_seconds[mask],
                t_datetime=dataset.t_datetime[mask],
                window=time_window
            )
```

### 5.3 Dataset

```python
class SourceInfo(BaseModel):
    """Informação de origem do arquivo"""
    filepath: str
    filename: str
    format: str  # csv, xlsx, parquet, hdf5
    size_bytes: int
    checksum: str  # SHA256
    
class DatasetMetadata(BaseModel):
    """Metadata do dataset"""
    description: Optional[str] = None
    tags: list[str] = []
    custom: dict = {}

class Dataset(BaseModel):
    """Dataset completo"""
    dataset_id: DatasetID
    version: int = 1
    parent_id: Optional[DatasetID] = None
    source: SourceInfo
    t_seconds: np.ndarray  # Tempo em segundos (float64)
    t_datetime: np.ndarray  # Timestamps datetime64
    series: dict[SeriesID, Series] = {}
    metadata: DatasetMetadata = DatasetMetadata()
    created_at: datetime
    
    class Config:
        arbitrary_types_allowed = True
```

### 5.4 Series

```python
class InterpolationInfo(BaseModel):
    """Informação de interpolação por ponto"""
    is_interpolated: np.ndarray  # bool mask
    method_used: np.ndarray  # string array com método por ponto
    confidence: Optional[np.ndarray] = None
    
    class Config:
        arbitrary_types_allowed = True

class SeriesMetadata(BaseModel):
    """Metadata da série"""
    original_name: str
    description: Optional[str] = None
    tags: list[str] = []
    custom: dict = {}

class Lineage(BaseModel):
    """Rastreamento de origem de séries derivadas"""
    origin_series: list[SeriesID]
    operation: str  # ex: "derivative", "interpolate", "sync"
    parameters: dict
    timestamp: datetime
    version: str  # versão da plataforma

class Series(BaseModel):
    """Série temporal"""
    series_id: SeriesID
    name: str
    unit: pint.Unit
    values: np.ndarray
    interpolation_info: Optional[InterpolationInfo] = None
    metadata: SeriesMetadata
    lineage: Optional[Lineage] = None
    
    class Config:
        arbitrary_types_allowed = True
```

### 5.5 ViewData

```python
class TimeWindow(BaseModel):
    """Janela temporal"""
    start: float  # segundos
    end: float  # segundos
    
    @property
    def duration(self) -> float:
        return self.end - self.start

class ViewData(BaseModel):
    """Dados preparados para visualização"""
    dataset_id: DatasetID
    series: dict[SeriesID, np.ndarray]
    t_seconds: np.ndarray
    t_datetime: np.ndarray
    window: TimeWindow
    
    class Config:
        arbitrary_types_allowed = True
```

### 5.6 DerivedResult

```python
class ResultMetadata(BaseModel):
    """Metadata de resultado de operação"""
    operation: str
    parameters: dict
    timestamp: datetime
    duration_ms: float
    platform_version: str

class QualityMetrics(BaseModel):
    """Métricas de qualidade do resultado"""
    n_valid: int
    n_interpolated: int
    n_nan: int
    error_estimate: Optional[float] = None

class DerivedResult(BaseModel):
    """Base para resultados de operações"""
    values: np.ndarray
    metadata: ResultMetadata
    quality_metrics: Optional[QualityMetrics] = None
    
    class Config:
        arbitrary_types_allowed = True

class InterpResult(DerivedResult):
    """Resultado de interpolação"""
    interpolation_info: InterpolationInfo

class CalcResult(DerivedResult):
    """Resultado de cálculo matemático"""
    operation: str  # derivative, integral, area
    order: Optional[int] = None  # para derivadas

class SyncResult(DerivedResult):
    """Resultado de sincronização"""
    t_common: np.ndarray
    synced_series: dict[SeriesID, np.ndarray]
    alignment_error: float
    confidence: float
```

---

## 6. Carga de Arquivos

### 6.1 API do Loader

```python
# io/loader.py
from enum import Enum
from pathlib import Path

class FileFormat(Enum):
    CSV = "csv"
    EXCEL = "xlsx"
    PARQUET = "parquet"
    HDF5 = "hdf5"

class LoadConfig(BaseModel):
    """Configuração de carregamento"""
    timestamp_column: Optional[str] = None  # auto-detect se None
    delimiter: str = ","
    encoding: str = "utf-8"
    sheet_name: Optional[str] = None  # para Excel
    hdf5_key: Optional[str] = None  # para HDF5
    chunk_size: Optional[int] = None  # para streaming

def detect_format(path: Path) -> FileFormat:
    """Detecta formato pelo extension e magic bytes"""
    suffix = path.suffix.lower()
    format_map = {
        '.csv': FileFormat.CSV,
        '.xlsx': FileFormat.EXCEL,
        '.xls': FileFormat.EXCEL,
        '.parquet': FileFormat.PARQUET,
        '.h5': FileFormat.HDF5,
        '.hdf5': FileFormat.HDF5,
    }
    if suffix not in format_map:
        raise DataLoadError(f"Unsupported format: {suffix}", 
                           context={"path": str(path)})
    return format_map[suffix]

def load(path: str | Path, config: LoadConfig) -> Dataset:
    """
    Carrega arquivo e retorna Dataset.
    
    Pipeline:
    1. Detecta formato
    2. Lê dados (pandas)
    3. Detecta schema
    4. Valida dados
    5. Normaliza unidades
    6. Constrói Dataset
    
    Args:
        path: Caminho do arquivo
        config: Configuração de carregamento
        
    Returns:
        Dataset completo
        
    Raises:
        DataLoadError: Se arquivo não pode ser lido
        SchemaDetectionError: Se schema não pode ser detectado
        ValidationError: Se dados inválidos
    """
    path = Path(path)
    
    # 1. Detectar formato
    fmt = detect_format(path)
    
    # 2. Ler dados
    df = _read_file(path, fmt, config)
    
    # 3. Detectar schema
    schema = detect_schema(df, config)
    
    # 4. Validar
    report = validate_data(df, schema)
    if report.errors:
        # Log warnings mas continua
        for warning in report.warnings:
            logger.warning("validation_warning", **warning.dict())
    
    # 5. Normalizar unidades
    df, unit_map = normalize_units(df, schema)
    
    # 6. Construir Dataset
    return _build_dataset(path, df, schema, unit_map, report)

def _read_file(path: Path, fmt: FileFormat, config: LoadConfig) -> pd.DataFrame:
    """Lê arquivo conforme formato"""
    readers = {
        FileFormat.CSV: lambda: pd.read_csv(
            path, delimiter=config.delimiter, encoding=config.encoding
        ),
        FileFormat.EXCEL: lambda: pd.read_excel(
            path, sheet_name=config.sheet_name or 0
        ),
        FileFormat.PARQUET: lambda: pd.read_parquet(path),
        FileFormat.HDF5: lambda: pd.read_hdf(path, key=config.hdf5_key),
    }
    return readers[fmt]()
```

### 6.2 Detecção de Schema

```python
# io/schema_detector.py
class SeriesCandidate(BaseModel):
    """Candidato a série temporal"""
    column: str
    dtype: str
    unit_hint: Optional[str] = None
    confidence: float

class SchemaMap(BaseModel):
    """Schema detectado"""
    timestamp_column: str
    timestamp_format: str
    candidate_series: list[SeriesCandidate]
    confidence: float

class SchemaRules(BaseModel):
    """Regras para detecção"""
    timestamp_patterns: list[str] = ["timestamp", "time", "datetime", "date"]
    numeric_threshold: float = 0.9  # % de valores numéricos para ser série

def detect_schema(df: pd.DataFrame, config: LoadConfig) -> SchemaMap:
    """
    Detecta schema do DataFrame.
    
    Heurísticas:
    1. Timestamp: coluna com nome padrão OU datetime type OU monotônica crescente
    2. Séries: colunas numéricas (float/int)
    3. Unidades: extrai de nome da coluna (ex: "pressure_bar")
    
    Returns:
        SchemaMap com mapeamento detectado
        
    Raises:
        SchemaDetectionError: Se não consegue identificar timestamp
    """
    # Se timestamp especificado, usar
    if config.timestamp_column:
        ts_col = config.timestamp_column
    else:
        ts_col = _detect_timestamp_column(df)
    
    if ts_col is None:
        raise SchemaDetectionError(
            "Could not detect timestamp column",
            context={"columns": list(df.columns)}
        )
    
    # Detectar formato do timestamp
    ts_format = _detect_timestamp_format(df[ts_col])
    
    # Detectar séries candidatas
    candidates = []
    for col in df.columns:
        if col == ts_col:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            unit_hint = _extract_unit_from_name(col)
            candidates.append(SeriesCandidate(
                column=col,
                dtype=str(df[col].dtype),
                unit_hint=unit_hint,
                confidence=1.0 - df[col].isna().mean()
            ))
    
    return SchemaMap(
        timestamp_column=ts_col,
        timestamp_format=ts_format,
        candidate_series=candidates,
        confidence=_calculate_schema_confidence(df, ts_col, candidates)
    )

def _detect_timestamp_column(df: pd.DataFrame) -> Optional[str]:
    """Detecta coluna de timestamp por heurísticas"""
    rules = SchemaRules()
    
    # 1. Por nome
    for pattern in rules.timestamp_patterns:
        for col in df.columns:
            if pattern.lower() in col.lower():
                return col
    
    # 2. Por tipo datetime
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    
    # 3. Por monotonia crescente
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].is_monotonic_increasing:
                return col
    
    return None
```

### 6.3 Validação

```python
# io/validator.py
class ValidationWarning(BaseModel):
    """Aviso de validação"""
    code: str
    message: str
    column: Optional[str] = None
    rows: Optional[list[int]] = None

class ValidationError(BaseModel):
    """Erro de validação"""
    code: str
    message: str
    column: Optional[str] = None
    rows: Optional[list[int]] = None

class GapReport(BaseModel):
    """Relatório de gaps temporais"""
    n_gaps: int
    max_gap_seconds: float
    gap_intervals: list[tuple[int, int]]  # índices

class ValidationReport(BaseModel):
    """Relatório completo de validação"""
    is_valid: bool
    warnings: list[ValidationWarning] = []
    errors: list[ValidationError] = []
    gaps: Optional[GapReport] = None
    stats: dict = {}

def validate_data(df: pd.DataFrame, schema: SchemaMap) -> ValidationReport:
    """
    Valida dados conforme schema.
    
    NUNCA rejeita dados - sempre marca e registra.
    """
    warnings = []
    errors = []
    
    # Validar timestamp
    ts_report = validate_time(df, schema)
    warnings.extend(ts_report.warnings)
    
    # Validar valores
    val_report = validate_values(df, schema)
    warnings.extend(val_report.warnings)
    
    # Detectar gaps
    gaps = detect_gaps(df[schema.timestamp_column])
    if gaps.n_gaps > 0:
        warnings.append(ValidationWarning(
            code="GAPS_DETECTED",
            message=f"Found {gaps.n_gaps} temporal gaps, max {gaps.max_gap_seconds}s"
        ))
    
    return ValidationReport(
        is_valid=len(errors) == 0,
        warnings=warnings,
        errors=errors,
        gaps=gaps,
        stats=_calculate_stats(df, schema)
    )

def validate_time(df: pd.DataFrame, schema: SchemaMap) -> ValidationReport:
    """Valida coluna temporal"""
    warnings = []
    ts_col = schema.timestamp_column
    
    # Verificar valores nulos
    n_null = df[ts_col].isna().sum()
    if n_null > 0:
        warnings.append(ValidationWarning(
            code="NULL_TIMESTAMPS",
            message=f"Found {n_null} null timestamps",
            column=ts_col
        ))
    
    # Verificar monotonia
    if not df[ts_col].dropna().is_monotonic_increasing:
        warnings.append(ValidationWarning(
            code="NON_MONOTONIC",
            message="Timestamps are not strictly monotonic increasing",
            column=ts_col
        ))
    
    return ValidationReport(is_valid=True, warnings=warnings)

def validate_values(df: pd.DataFrame, schema: SchemaMap) -> ValidationReport:
    """Valida colunas de valores"""
    warnings = []
    
    for candidate in schema.candidate_series:
        col = candidate.column
        
        # NaN ratio
        nan_ratio = df[col].isna().mean()
        if nan_ratio > 0.1:
            warnings.append(ValidationWarning(
                code="HIGH_NAN_RATIO",
                message=f"Column has {nan_ratio:.1%} NaN values",
                column=col
            ))
        
        # Outliers (3-sigma)
        mean = df[col].mean()
        std = df[col].std()
        if std > 0:
            outliers = ((df[col] - mean).abs() > 3 * std).sum()
            if outliers > 0:
                warnings.append(ValidationWarning(
                    code="OUTLIERS_DETECTED",
                    message=f"Found {outliers} potential outliers (>3σ)",
                    column=col
                ))
    
    return ValidationReport(is_valid=True, warnings=warnings)

def detect_gaps(timestamps: pd.Series) -> GapReport:
    """Detecta gaps temporais"""
    ts_clean = timestamps.dropna()
    if len(ts_clean) < 2:
        return GapReport(n_gaps=0, max_gap_seconds=0, gap_intervals=[])
    
    # Calcular diferenças
    diffs = ts_clean.diff().dropna()
    
    # Threshold: gaps > 5x mediana
    median_diff = diffs.median()
    threshold = 5 * median_diff
    
    gaps_mask = diffs > threshold
    gap_indices = gaps_mask[gaps_mask].index.tolist()
    
    return GapReport(
        n_gaps=len(gap_indices),
        max_gap_seconds=float(diffs.max()) if len(diffs) > 0 else 0,
        gap_intervals=[(i-1, i) for i in gap_indices]
    )
```

---

## 7. Interpolação

### 7.1 Interface Única

```python
# processing/interpolation.py
from enum import Enum
from typing import Literal

class InterpMethod(Enum):
    """Métodos de interpolação disponíveis"""
    # Core (sempre disponíveis)
    LINEAR = "linear"
    SPLINE_CUBIC = "spline_cubic"
    SMOOTHING_SPLINE = "smoothing_spline"
    RESAMPLE_GRID = "resample_grid"
    
    # Avançados (com graceful degradation)
    MLS = "mls"  # Moving Least Squares
    GPR = "gpr"  # Gaussian Process Regression
    LOMB_SCARGLE = "lomb_scargle_spectral"
    
    # Plugins
    NN_INTERPOLATION = "nn_interpolation"
    CONTINUOUS_TIME = "continuous_time_model"
    DIFFUSION = "diffusion_conditioned"

class InterpParams(BaseModel):
    """Parâmetros de interpolação"""
    # Comuns
    fill_value: Optional[float] = None
    
    # Spline
    smoothing_factor: float = 0.0
    spline_order: int = 3
    
    # GPR
    kernel: str = "rbf"
    length_scale: float = 1.0
    
    # MLS
    polynomial_order: int = 2
    weight_function: str = "gaussian"
    
    # Resample
    target_freq: Optional[float] = None  # Hz

def interpolate(values: np.ndarray, t_seconds: np.ndarray,
                method: InterpMethod, params: InterpParams) -> InterpResult:
    """
    Interpola valores em timestamps irregulares.
    
    Args:
        values: Array de valores observados
        t_seconds: Array de timestamps (segundos)
        method: Método de interpolação
        params: Parâmetros específicos do método
        
    Returns:
        InterpResult com valores interpolados e metadata
        
    Raises:
        InterpolationError: Se método não disponível ou params inválidos
        
    Notes:
        - SEM fallback automático: se método falha, reporta erro
        - Cada ponto tem tracking de método usado
    """
    # Verificar disponibilidade do método
    if not _is_method_available(method):
        raise InterpolationError(
            f"Method {method.value} not available",
            context={
                "method": method.value,
                "hint": _get_availability_hint(method)
            }
        )
    
    # Identificar gaps
    gap_mask = _identify_gaps(values)
    
    # Aplicar interpolação
    start_time = time.perf_counter()
    
    interpolator = _get_interpolator(method)
    values_interp, method_used = interpolator(values, t_seconds, params, gap_mask)
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    # Construir resultado
    return InterpResult(
        values=values_interp,
        interpolation_info=InterpolationInfo(
            is_interpolated=gap_mask,
            method_used=method_used,
            confidence=_calculate_confidence(values, values_interp, gap_mask)
        ),
        metadata=ResultMetadata(
            operation="interpolation",
            parameters=params.dict(),
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            platform_version=__version__
        ),
        quality_metrics=QualityMetrics(
            n_valid=int((~gap_mask).sum()),
            n_interpolated=int(gap_mask.sum()),
            n_nan=int(np.isnan(values_interp).sum())
        )
    )

# Implementações dos métodos
def _interpolate_linear(values, t, params, gap_mask):
    """Interpolação linear (scipy.interpolate.interp1d)"""
    from scipy.interpolate import interp1d
    
    valid_mask = ~np.isnan(values)
    f = interp1d(t[valid_mask], values[valid_mask], 
                 kind='linear', fill_value='extrapolate')
    
    result = values.copy()
    result[gap_mask] = f(t[gap_mask])
    
    method_used = np.where(gap_mask, 'linear', 'original')
    return result, method_used

def _interpolate_spline_cubic(values, t, params, gap_mask):
    """Interpolação spline cúbica (scipy.interpolate.CubicSpline)"""
    from scipy.interpolate import CubicSpline
    
    valid_mask = ~np.isnan(values)
    cs = CubicSpline(t[valid_mask], values[valid_mask])
    
    result = values.copy()
    result[gap_mask] = cs(t[gap_mask])
    
    method_used = np.where(gap_mask, 'spline_cubic', 'original')
    return result, method_used

def _interpolate_gpr(values, t, params, gap_mask):
    """Gaussian Process Regression"""
    try:
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import RBF, ConstantKernel
    except ImportError:
        raise InterpolationError(
            "GPR requires scikit-learn",
            context={"hint": "pip install scikit-learn"}
        )
    
    valid_mask = ~np.isnan(values)
    
    kernel = ConstantKernel() * RBF(length_scale=params.length_scale)
    gpr = GaussianProcessRegressor(kernel=kernel)
    
    gpr.fit(t[valid_mask].reshape(-1, 1), values[valid_mask])
    
    result = values.copy()
    result[gap_mask] = gpr.predict(t[gap_mask].reshape(-1, 1))
    
    method_used = np.where(gap_mask, 'gpr', 'original')
    return result, method_used
```

---

## 8. Sincronização

### 8.1 Interface

```python
# processing/synchronization.py
class SyncMethod(Enum):
    """Métodos de sincronização"""
    COMMON_GRID = "common_grid_interpolate"
    KALMAN = "kalman_align"
    DTW = "dtw_align"  # plugin
    TWED = "twed_align"  # plugin
    STATISTICAL = "statistical_warping"  # plugin
    DEEP = "deep_warping"  # plugin

class SyncParams(BaseModel):
    """Parâmetros de sincronização"""
    target_freq: Optional[float] = None  # Hz, None = usar mínima comum
    interp_method: InterpMethod = InterpMethod.LINEAR
    reference_series: Optional[SeriesID] = None

def synchronize(series_dict: dict[SeriesID, np.ndarray],
                t_dict: dict[SeriesID, np.ndarray],
                method: SyncMethod,
                params: SyncParams) -> SyncResult:
    """
    Sincroniza múltiplas séries em base temporal comum.
    
    Args:
        series_dict: Dict de série_id → valores
        t_dict: Dict de série_id → timestamps
        method: Método de sincronização
        params: Parâmetros
        
    Returns:
        SyncResult com séries sincronizadas
    """
    start_time = time.perf_counter()
    
    if method == SyncMethod.COMMON_GRID:
        t_common, synced = _sync_common_grid(series_dict, t_dict, params)
        alignment_error = 0.0
        confidence = 1.0
    elif method == SyncMethod.KALMAN:
        t_common, synced, alignment_error, confidence = \
            _sync_kalman(series_dict, t_dict, params)
    else:
        # Plugin methods
        plugin = registry.get_plugin(method.value)
        t_common, synced, alignment_error, confidence = \
            plugin.execute(series_dict, t_dict, params)
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    return SyncResult(
        values=np.column_stack(list(synced.values())),
        t_common=t_common,
        synced_series=synced,
        alignment_error=alignment_error,
        confidence=confidence,
        metadata=ResultMetadata(
            operation="synchronization",
            parameters=params.dict(),
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            platform_version=__version__
        )
    )

def _sync_common_grid(series_dict, t_dict, params):
    """Sincronização por grid comum com interpolação"""
    # Determinar base temporal comum
    all_t = np.concatenate(list(t_dict.values()))
    t_min, t_max = all_t.min(), all_t.max()
    
    if params.target_freq:
        n_points = int((t_max - t_min) * params.target_freq)
    else:
        # Usar densidade mínima das séries
        densities = [len(t) / (t.max() - t.min()) for t in t_dict.values()]
        freq = min(densities)
        n_points = int((t_max - t_min) * freq)
    
    t_common = np.linspace(t_min, t_max, n_points)
    
    # Interpolar cada série para grid comum
    synced = {}
    for series_id, values in series_dict.items():
        t = t_dict[series_id]
        result = interpolate(
            values, t,
            method=params.interp_method,
            params=InterpParams()
        )
        # Re-interpolar para t_common
        from scipy.interpolate import interp1d
        f = interp1d(t, result.values, fill_value='extrapolate')
        synced[series_id] = f(t_common)
    
    return t_common, synced
```

---

## 9. Cálculos Matemáticos

### 9.1 Derivadas

```python
# processing/calculus.py
class DerivMethod(Enum):
    """Métodos de derivação"""
    FINITE_DIFF = "finite_diff"
    SAVITZKY_GOLAY = "savitzky_golay"
    SPLINE_DERIVATIVE = "spline_derivative"

class DerivParams(BaseModel):
    """Parâmetros de derivação"""
    # Finite diff
    accuracy: int = 2  # 2, 4, 6 (ordem do esquema)
    
    # Savitzky-Golay
    window_length: int = 5
    polyorder: int = 2
    
    # Spline
    smoothing: float = 0.0

class SmoothingConfig(BaseModel):
    """Configuração de suavização pré-derivada"""
    method: Literal["savitzky_golay", "gaussian", "median", "lowpass"]
    params: dict

def derivative(values: np.ndarray, t: np.ndarray,
               order: int, method: DerivMethod,
               params: DerivParams,
               smoothing: Optional[SmoothingConfig] = None) -> CalcResult:
    """
    Calcula derivada de ordem especificada.
    
    Args:
        values: Array de valores
        t: Array de timestamps (segundos)
        order: Ordem da derivada (1, 2, ou 3)
        method: Método de derivação
        params: Parâmetros do método
        smoothing: Config de suavização pré-derivada (opcional)
        
    Returns:
        CalcResult com derivada calculada
        
    Raises:
        ValueError: Se order não está em [1, 2, 3]
        CalculusError: Se cálculo falha
        
    Notes:
        - Retorna série completa (mesmo comprimento que input)
        - Smoothing é OPCIONAL (usuário decide)
    """
    if order < 1 or order > 3:
        raise ValueError(f"Order must be 1, 2, or 3, got {order}")
    
    start_time = time.perf_counter()
    
    # Aplicar suavização se especificada
    if smoothing:
        values = smooth(values, smoothing.method, smoothing.params)
    
    # Calcular derivada
    if method == DerivMethod.FINITE_DIFF:
        result = _derivative_finite_diff(values, t, order, params)
    elif method == DerivMethod.SAVITZKY_GOLAY:
        result = _derivative_savgol(values, t, order, params)
    elif method == DerivMethod.SPLINE_DERIVATIVE:
        result = _derivative_spline(values, t, order, params)
    else:
        raise CalculusError(f"Unknown method: {method}")
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    return CalcResult(
        values=result,
        operation="derivative",
        order=order,
        metadata=ResultMetadata(
            operation=f"derivative_order_{order}",
            parameters={
                "method": method.value,
                **params.dict(),
                "smoothing": smoothing.dict() if smoothing else None
            },
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            platform_version=__version__
        )
    )

def _derivative_finite_diff(values, t, order, params):
    """Derivada por diferenças finitas"""
    from scipy.signal import savgol_filter
    
    dt = np.diff(t)
    
    if order == 1:
        # Central differences
        deriv = np.gradient(values, t)
    elif order == 2:
        deriv = np.gradient(np.gradient(values, t), t)
    else:  # order == 3
        deriv = np.gradient(np.gradient(np.gradient(values, t), t), t)
    
    return deriv

def _derivative_savgol(values, t, order, params):
    """Derivada via Savitzky-Golay"""
    from scipy.signal import savgol_filter
    
    # Estimar dt médio
    dt_mean = np.mean(np.diff(t))
    
    deriv = savgol_filter(
        values,
        window_length=params.window_length,
        polyorder=params.polyorder,
        deriv=order,
        delta=dt_mean
    )
    
    return deriv

def _derivative_spline(values, t, order, params):
    """Derivada via spline"""
    from scipy.interpolate import UnivariateSpline
    
    spline = UnivariateSpline(t, values, s=params.smoothing)
    deriv_spline = spline.derivative(n=order)
    
    return deriv_spline(t)
```

### 9.2 Integrais

```python
def integral(values: np.ndarray, t: np.ndarray,
             method: Literal["trapezoid", "simpson"] = "trapezoid") -> CalcResult:
    """
    Calcula integral cumulativa.
    
    Args:
        values: Array de valores
        t: Array de timestamps
        method: Método de integração
        
    Returns:
        CalcResult com integral cumulativa
    """
    start_time = time.perf_counter()
    
    if method == "trapezoid":
        from scipy.integrate import cumulative_trapezoid
        result = cumulative_trapezoid(values, t, initial=0)
    elif method == "simpson":
        from scipy.integrate import simpson
        # Simpson requer número ímpar de pontos
        result = np.zeros_like(values)
        for i in range(1, len(values)):
            result[i] = simpson(values[:i+1], t[:i+1])
    else:
        raise CalculusError(f"Unknown method: {method}")
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    return CalcResult(
        values=result,
        operation="integral",
        metadata=ResultMetadata(
            operation="integral",
            parameters={"method": method},
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            platform_version=__version__
        )
    )
```

### 9.3 Área entre Curvas

```python
def area_between(series_upper: np.ndarray, series_lower: np.ndarray,
                 t: np.ndarray) -> CalcResult:
    """
    Calcula área entre duas curvas.
    
    Args:
        series_upper: Série superior
        series_lower: Série inferior
        t: Timestamps comuns
        
    Returns:
        CalcResult com área cumulativa
    """
    diff = series_upper - series_lower
    return integral(diff, t, method="trapezoid")
```

### 9.4 Suavização

```python
# processing/smoothing.py
class SmoothMethod(Enum):
    """Métodos de suavização"""
    SAVITZKY_GOLAY = "savitzky_golay"
    GAUSSIAN = "gaussian"
    MEDIAN = "median"
    LOWPASS = "lowpass"

def smooth(values: np.ndarray, method: str, params: dict) -> np.ndarray:
    """
    Aplica suavização aos valores.
    
    Args:
        values: Array de valores
        method: Método de suavização
        params: Parâmetros do método
        
    Returns:
        Array suavizado
        
    Notes:
        - Usuário decide quando aplicar (não automático)
    """
    if method == "savitzky_golay":
        from scipy.signal import savgol_filter
        return savgol_filter(values, 
                            window_length=params.get("window", 5),
                            polyorder=params.get("polyorder", 2))
    
    elif method == "gaussian":
        from scipy.ndimage import gaussian_filter1d
        return gaussian_filter1d(values, sigma=params.get("sigma", 1.0))
    
    elif method == "median":
        from scipy.signal import medfilt
        return medfilt(values, kernel_size=params.get("kernel_size", 5))
    
    elif method == "lowpass":
        from scipy.signal import butter, filtfilt
        b, a = butter(
            params.get("order", 4),
            params.get("cutoff", 0.1),
            btype='low'
        )
        return filtfilt(b, a, values)
    
    else:
        raise ValueError(f"Unknown smoothing method: {method}")
```

---

## 10. Visualização (PyQt6 + pyqtgraph + PyVista)

### 10.1 Abstração Base

```python
# viz/base.py
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget

class BasePlot(ABC):
    """
    Abstração base para todos os plots.
    
    Diferença Dash → PyQt6:
    - Dash: render() retorna go.Figure (JSON)
    - PyQt6: render() retorna QWidget (widget nativo)
    """
    
    def __init__(self, config: PlotConfig):
        self.config = config
        self._widget: Optional[QWidget] = None
    
    @abstractmethod
    def render(self, data: ViewData) -> QWidget:
        """
        Renderiza dados e retorna widget Qt.
        
        Args:
            data: Dados a visualizar
            
        Returns:
            QWidget com plot renderizado
        """
        pass
    
    @abstractmethod
    def update(self, data: ViewData) -> None:
        """
        Atualiza plot existente (sem recriar widget).
        
        Args:
            data: Novos dados
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Limpa o plot"""
        pass
    
    def get_widget(self) -> Optional[QWidget]:
        """Retorna widget atual"""
        return self._widget
    
    def apply_downsampling(self, data: ViewData) -> ViewData:
        """Aplica downsampling se necessário"""
        if self.config.downsample.enabled:
            return _downsample(data, self.config.downsample)
        return data
```

### 10.2 Config Unificado

```python
# viz/config.py
class AxisConfig(BaseModel):
    """Configuração de eixo"""
    label: str = ""
    unit: Optional[str] = None
    range: Optional[tuple[float, float]] = None
    log_scale: bool = False

class ColorScheme(BaseModel):
    """Esquema de cores"""
    background: str = "#FFFFFF"
    foreground: str = "#000000"
    series_colors: list[str] = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
        "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"
    ]

class DownsampleStrategy(BaseModel):
    """Estratégia de downsampling"""
    enabled: bool = True
    method: Literal["lttb", "minmax", "adaptive"] = "lttb"
    max_points: int = 10000
    preserve_features: list[str] = ["peaks", "valleys", "edges"]

class InteractivityConfig(BaseModel):
    """Configuração de interatividade"""
    zoom_enabled: bool = True
    pan_enabled: bool = True
    hover_enabled: bool = True
    crosshair_enabled: bool = False
    context_menu_enabled: bool = True

class PlotConfig(BaseModel):
    """Configuração completa de plot"""
    title: str = ""
    axes: dict[str, AxisConfig] = {}
    colors: ColorScheme = ColorScheme()
    downsample: DownsampleStrategy = DownsampleStrategy()
    interactive: InteractivityConfig = InteractivityConfig()
    height: int = 600
    width: int = 800
```

### 10.3 Plot 2D (pyqtgraph)

```python
# viz/plot_2d.py
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

class TimeseriesPlot2D(BasePlot):
    """
    Plot 2D de séries temporais usando pyqtgraph.
    
    Equivalente ao dcc.Graph do Dash, mas nativo.
    """
    
    # Signals para comunicação com UI
    region_selected = pyqtSignal(float, float)  # start, end
    point_clicked = pyqtSignal(int, float, float)  # index, x, y
    
    def __init__(self, config: PlotConfig):
        super().__init__(config)
        self._curves: dict[SeriesID, pg.PlotDataItem] = {}
        self._plot_widget: Optional[pg.PlotWidget] = None
    
    def render(self, data: Optional[ViewData]) -> QWidget:
        """
        Renderiza plot 2D.
        
        Args:
            data: ViewData ou None para placeholder
            
        Returns:
            QWidget contendo plot pyqtgraph
        """
        # Criar widget container
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Criar PlotWidget
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground(self.config.colors.background)
        self._plot_widget.setTitle(self.config.title)
        
        # Configurar eixos
        self._plot_widget.setLabel('bottom', 'Time', units='s')
        self._plot_widget.setLabel('left', 'Value')
        
        # Configurar interatividade
        if self.config.interactive.zoom_enabled:
            self._plot_widget.enableAutoRange()
        
        if self.config.interactive.crosshair_enabled:
            self._setup_crosshair()
        
        # Adicionar região de seleção
        self._region = pg.LinearRegionItem()
        self._region.sigRegionChanged.connect(self._on_region_changed)
        self._region.setVisible(False)
        self._plot_widget.addItem(self._region)
        
        # Plotar dados se fornecidos
        if data:
            self._plot_data(data)
        
        # Context menu
        if self.config.interactive.context_menu_enabled:
            self._plot_widget.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu
            )
            self._plot_widget.customContextMenuRequested.connect(
                self._show_context_menu
            )
        
        layout.addWidget(self._plot_widget)
        self._widget = container
        return container
    
    def update(self, data: ViewData) -> None:
        """Atualiza dados sem recriar widget"""
        if self._plot_widget is None:
            return
        
        # Aplicar downsampling
        data = self.apply_downsampling(data)
        
        # Atualizar cada curva
        for series_id, values in data.series.items():
            if series_id in self._curves:
                self._curves[series_id].setData(data.t_seconds, values)
            else:
                # Nova série
                color_idx = len(self._curves) % len(self.config.colors.series_colors)
                color = self.config.colors.series_colors[color_idx]
                curve = self._plot_widget.plot(
                    data.t_seconds, values,
                    pen=pg.mkPen(color=color, width=2),
                    name=series_id
                )
                self._curves[series_id] = curve
    
    def clear(self) -> None:
        """Limpa todas as curvas"""
        if self._plot_widget:
            self._plot_widget.clear()
            self._curves.clear()
    
    def _plot_data(self, data: ViewData) -> None:
        """Plota dados iniciais"""
        data = self.apply_downsampling(data)
        
        for i, (series_id, values) in enumerate(data.series.items()):
            color = self.config.colors.series_colors[i % len(self.config.colors.series_colors)]
            curve = self._plot_widget.plot(
                data.t_seconds, values,
                pen=pg.mkPen(color=color, width=2),
                name=series_id
            )
            self._curves[series_id] = curve
    
    def _setup_crosshair(self) -> None:
        """Configura crosshair para hover"""
        self._vLine = pg.InfiniteLine(angle=90, movable=False)
        self._hLine = pg.InfiniteLine(angle=0, movable=False)
        self._plot_widget.addItem(self._vLine, ignoreBounds=True)
        self._plot_widget.addItem(self._hLine, ignoreBounds=True)
        
        self._plot_widget.scene().sigMouseMoved.connect(self._on_mouse_moved)
    
    def _on_mouse_moved(self, pos):
        """Handler de movimento do mouse"""
        if self._plot_widget.sceneBoundingRect().contains(pos):
            mousePoint = self._plot_widget.plotItem.vb.mapSceneToView(pos)
            self._vLine.setPos(mousePoint.x())
            self._hLine.setPos(mousePoint.y())
    
    def _on_region_changed(self):
        """Handler de mudança de região selecionada"""
        region = self._region.getRegion()
        self.region_selected.emit(region[0], region[1])
    
    def _show_context_menu(self, pos):
        """Mostra menu contextual"""
        from .context_menu import PlotContextMenu
        menu = PlotContextMenu(self._plot_widget)
        menu.exec(self._plot_widget.mapToGlobal(pos))
    
    # Métodos de seleção
    def enable_selection(self):
        """Habilita modo de seleção"""
        self._region.setVisible(True)
    
    def disable_selection(self):
        """Desabilita modo de seleção"""
        self._region.setVisible(False)
    
    def get_selection(self) -> tuple[float, float]:
        """Retorna região selecionada"""
        return self._region.getRegion()


class MultipanelPlot2D(BasePlot):
    """
    Múltiplos plots 2D sincronizados.
    
    Equivalente ao subplot do Plotly, mas com pyqtgraph.
    """
    
    def __init__(self, config: PlotConfig, n_panels: int = 2):
        super().__init__(config)
        self.n_panels = n_panels
        self._plots: list[pg.PlotItem] = []
    
    def render(self, data: Optional[ViewData]) -> QWidget:
        """Renderiza múltiplos painéis"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Usar GraphicsLayoutWidget para múltiplos plots
        self._graphics_widget = pg.GraphicsLayoutWidget()
        
        # Criar painéis
        for i in range(self.n_panels):
            plot = self._graphics_widget.addPlot(row=i, col=0)
            plot.setLabel('bottom', 'Time', units='s')
            self._plots.append(plot)
            
            # Sincronizar eixo X
            if i > 0:
                plot.setXLink(self._plots[0])
        
        layout.addWidget(self._graphics_widget)
        self._widget = container
        return container
    
    def update(self, data: ViewData) -> None:
        """Atualiza dados em todos os painéis"""
        # Distribuir séries entre painéis
        series_list = list(data.series.items())
        for i, plot in enumerate(self._plots):
            if i < len(series_list):
                series_id, values = series_list[i]
                plot.clear()
                plot.plot(data.t_seconds, values)
    
    def clear(self) -> None:
        """Limpa todos os painéis"""
        for plot in self._plots:
            plot.clear()
```

### 10.4 Plot 3D (PyVista)

```python
# viz/plot_3d.py
import pyvista as pv
from pyvistaqt import QtInteractor
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

class Trajectory3D(BasePlot):
    """
    Plot 3D de trajetórias usando PyVista.
    
    Equivalente ao go.Scatter3d do Plotly, mas VTK nativo.
    """
    
    point_picked = pyqtSignal(int, float, float, float)  # index, x, y, z
    
    def __init__(self, config: PlotConfig):
        super().__init__(config)
        self._plotter: Optional[QtInteractor] = None
        self._meshes: dict[str, pv.PolyData] = {}
    
    def render(self, data: Optional[ViewData]) -> QWidget:
        """
        Renderiza plot 3D.
        
        Requer 3 séries em data para x, y, z.
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Criar QtInteractor (widget VTK para Qt)
        self._plotter = QtInteractor(container)
        
        # Configurar visualização
        self._plotter.set_background(self.config.colors.background)
        
        # Adicionar axes
        self._plotter.add_axes()
        
        # Plotar dados se fornecidos
        if data and len(data.series) >= 3:
            self._plot_trajectory(data)
        
        # Habilitar picking
        self._plotter.enable_point_picking(
            callback=self._on_point_picked,
            show_message=False
        )
        
        layout.addWidget(self._plotter)
        self._widget = container
        return container
    
    def update(self, data: ViewData) -> None:
        """Atualiza trajetória 3D"""
        if self._plotter is None or len(data.series) < 3:
            return
        
        # Limpar meshes anteriores
        self._plotter.clear()
        
        # Replottar
        self._plot_trajectory(data)
    
    def _plot_trajectory(self, data: ViewData) -> None:
        """Plota trajetória 3D"""
        # Extrair coordenadas (primeiras 3 séries)
        series_ids = list(data.series.keys())[:3]
        x = data.series[series_ids[0]]
        y = data.series[series_ids[1]]
        z = data.series[series_ids[2]]
        
        # Criar pontos
        points = np.column_stack([x, y, z])
        
        # Aplicar downsampling se necessário
        if self.config.downsample.enabled and len(points) > self.config.downsample.max_points:
            indices = np.linspace(0, len(points)-1, 
                                 self.config.downsample.max_points, 
                                 dtype=int)
            points = points[indices]
        
        # Criar polydata
        cloud = pv.PolyData(points)
        
        # Colorir por tempo (índice)
        cloud['time'] = np.arange(len(points))
        
        # Adicionar como pontos
        self._plotter.add_mesh(
            cloud, 
            scalars='time',
            cmap='viridis',
            point_size=5,
            render_points_as_spheres=True
        )
        
        # Adicionar linha conectando pontos
        lines = pv.lines_from_points(points)
        self._plotter.add_mesh(lines, color='gray', line_width=1)
        
        # Reset camera
        self._plotter.reset_camera()
    
    def _on_point_picked(self, point):
        """Handler de ponto selecionado"""
        if point is not None:
            # Encontrar índice mais próximo
            # ... (implementação)
            self.point_picked.emit(0, point[0], point[1], point[2])
    
    def clear(self) -> None:
        """Limpa visualização"""
        if self._plotter:
            self._plotter.clear()


class StateCube3D(BasePlot):
    """
    Visualização de cubo de estados 3D.
    
    Para visualizar espaço de estados discreto.
    """
    
    def __init__(self, config: PlotConfig):
        super().__init__(config)
        self._plotter: Optional[QtInteractor] = None
    
    def render(self, states: np.ndarray) -> QWidget:
        """
        Renderiza cubo de estados.
        
        Args:
            states: Array 3D de estados (NxMxK)
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._plotter = QtInteractor(container)
        self._plotter.set_background(self.config.colors.background)
        
        # Criar grid 3D
        grid = pv.ImageData()
        grid.dimensions = np.array(states.shape) + 1
        grid.cell_data['values'] = states.flatten(order='F')
        
        # Threshold para mostrar apenas células com valor > 0
        threshed = grid.threshold(0.5)
        
        self._plotter.add_mesh(threshed, scalars='values', cmap='coolwarm')
        self._plotter.add_axes()
        
        layout.addWidget(self._plotter)
        self._widget = container
        return container
    
    def update(self, states: np.ndarray) -> None:
        """Atualiza cubo de estados"""
        if self._plotter:
            self._plotter.clear()
            # Recriar...
    
    def clear(self) -> None:
        if self._plotter:
            self._plotter.clear()
```

### 10.5 Heatmap

```python
# viz/heatmaps.py
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class StateHeatmap(BasePlot):
    """
    Heatmap usando pyqtgraph ImageView.
    
    Equivalente ao go.Heatmap do Plotly.
    """
    
    def __init__(self, config: PlotConfig):
        super().__init__(config)
        self._image_view: Optional[pg.ImageView] = None
    
    def render(self, matrix: Optional[np.ndarray]) -> QWidget:
        """
        Renderiza heatmap.
        
        Args:
            matrix: Matriz 2D de valores
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._image_view = pg.ImageView()
        self._image_view.ui.roiBtn.hide()
        self._image_view.ui.menuBtn.hide()
        
        if matrix is not None:
            self._image_view.setImage(matrix.T)
        
        layout.addWidget(self._image_view)
        self._widget = container
        return container
    
    def update(self, matrix: np.ndarray) -> None:
        """Atualiza heatmap"""
        if self._image_view:
            self._image_view.setImage(matrix.T)
    
    def clear(self) -> None:
        if self._image_view:
            self._image_view.clear()
```

### 10.6 Downsampling

```python
# viz/downsampling.py
def _downsample(data: ViewData, strategy: DownsampleStrategy) -> ViewData:
    """
    Aplica downsampling a ViewData.
    
    Métodos:
    - lttb: Largest Triangle Three Buckets
    - minmax: Preserva min/max por bucket
    - adaptive: Ajusta baseado em variância local
    """
    n_points = len(data.t_seconds)
    if n_points <= strategy.max_points:
        return data
    
    if strategy.method == "lttb":
        indices = _lttb_downsample(data.t_seconds, 
                                   list(data.series.values())[0],
                                   strategy.max_points)
    elif strategy.method == "minmax":
        indices = _minmax_downsample(data.t_seconds,
                                     list(data.series.values())[0],
                                     strategy.max_points)
    elif strategy.method == "adaptive":
        indices = _adaptive_downsample(data.t_seconds,
                                       list(data.series.values())[0],
                                       strategy.max_points,
                                       strategy.preserve_features)
    else:
        # Fallback: uniform sampling
        indices = np.linspace(0, n_points-1, strategy.max_points, dtype=int)
    
    return ViewData(
        dataset_id=data.dataset_id,
        series={k: v[indices] for k, v in data.series.items()},
        t_seconds=data.t_seconds[indices],
        t_datetime=data.t_datetime[indices],
        window=data.window
    )

def _lttb_downsample(t: np.ndarray, values: np.ndarray, 
                     n_out: int) -> np.ndarray:
    """
    Largest Triangle Three Buckets algorithm.
    
    Preserva forma visual da série.
    """
    n = len(t)
    bucket_size = (n - 2) / (n_out - 2)
    
    indices = [0]  # Sempre incluir primeiro ponto
    
    a = 0
    for i in range(n_out - 2):
        # Calcular bucket
        bucket_start = int((i + 1) * bucket_size) + 1
        bucket_end = int((i + 2) * bucket_size) + 1
        bucket_end = min(bucket_end, n)
        
        # Próximo bucket para média
        next_bucket_start = bucket_end
        next_bucket_end = int((i + 3) * bucket_size) + 1
        next_bucket_end = min(next_bucket_end, n)
        
        if next_bucket_start < n:
            avg_x = np.mean(t[next_bucket_start:next_bucket_end])
            avg_y = np.mean(values[next_bucket_start:next_bucket_end])
        else:
            avg_x = t[-1]
            avg_y = values[-1]
        
        # Encontrar ponto que maximiza área do triângulo
        max_area = -1
        max_idx = bucket_start
        
        for j in range(bucket_start, bucket_end):
            area = abs(
                (t[a] - avg_x) * (values[j] - values[a]) -
                (t[a] - t[j]) * (avg_y - values[a])
            ) * 0.5
            
            if area > max_area:
                max_area = area
                max_idx = j
        
        indices.append(max_idx)
        a = max_idx
    
    indices.append(n - 1)  # Sempre incluir último ponto
    
    return np.array(indices)
```

---

## 11. Streaming Temporal (QTimer + Signals)

### 11.1 StreamingState

```python
# viz/streaming.py
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from enum import Enum

class PlayState(Enum):
    """Estados de reprodução"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"

class StreamingState(BaseModel):
    """
    Estado de streaming por sessão.
    
    NOTA: Não é singleton global - cada sessão tem seu próprio estado.
    """
    play_state: PlayState = PlayState.STOPPED
    current_time_index: int = 0
    max_index: int = 0
    speed: float = 1.0  # multiplicador
    window_size_seconds: float = 60.0
    loop: bool = False
    filters: StreamFilters
    
    class Config:
        arbitrary_types_allowed = True
```

### 11.2 StreamFilters (Detalhado)

```python
class ValuePredicate(BaseModel):
    """Predicado para filtro de valor"""
    operator: Literal["gt", "gte", "lt", "lte", "eq", "neq", "between"]
    value: float
    value_upper: Optional[float] = None  # para 'between'

class TimeInterval(BaseModel):
    """Intervalo temporal"""
    start: float  # segundos
    end: float  # segundos

class ScaleConfig(BaseModel):
    """Configuração de escala"""
    mode: Literal["auto", "fixed", "percentile"]
    min: Optional[float] = None
    max: Optional[float] = None
    percentile_low: float = 1.0
    percentile_high: float = 99.0

class StreamFilters(BaseModel):
    """
    Filtros aplicáveis ao streaming.
    
    Operam em duas fases:
    1. Elegibilidade: quais timestamps entram no playback
    2. Render: downsampling/ocultação na janela atual
    """
    
    # ========== FILTROS DE ELEGIBILIDADE (FASE 1) ==========
    
    # 1) Filtros temporais
    time_include: Optional[list[TimeInterval]] = None
    time_exclude: Optional[list[TimeInterval]] = None
    
    # 2) Filtros de amostragem
    max_points_per_window: int = 5000
    downsample_method: Literal["lttb", "minmax", "adaptive"] = "lttb"
    
    # 3) Filtros de qualidade
    hide_interpolated: bool = False
    hide_nan: bool = True
    quality_threshold: Optional[float] = None  # 0-1
    
    # 4) Filtros de valor/condição
    value_predicates: dict[SeriesID, ValuePredicate] = {}
    
    # ========== FILTROS DE RENDER (FASE 2) ==========
    
    # 5) Filtros visuais (não mudam dados, só exibição)
    visual_smoothing: Optional[SmoothConfig] = None
    hidden_series: list[SeriesID] = []
    scale_override: Optional[ScaleConfig] = None
    
    def apply_eligibility(self, t_seconds: np.ndarray, 
                          data: ViewData) -> np.ndarray:
        """
        Aplica filtros de elegibilidade.
        
        Returns:
            Máscara booleana de timestamps elegíveis
        """
        mask = np.ones(len(t_seconds), dtype=bool)
        
        # Time include
        if self.time_include:
            include_mask = np.zeros(len(t_seconds), dtype=bool)
            for interval in self.time_include:
                include_mask |= (t_seconds >= interval.start) & \
                               (t_seconds <= interval.end)
            mask &= include_mask
        
        # Time exclude
        if self.time_exclude:
            for interval in self.time_exclude:
                mask &= ~((t_seconds >= interval.start) & \
                         (t_seconds <= interval.end))
        
        # Value predicates
        for series_id, predicate in self.value_predicates.items():
            if series_id in data.series:
                values = data.series[series_id]
                if predicate.operator == "gt":
                    mask &= values > predicate.value
                elif predicate.operator == "gte":
                    mask &= values >= predicate.value
                elif predicate.operator == "lt":
                    mask &= values < predicate.value
                elif predicate.operator == "lte":
                    mask &= values <= predicate.value
                elif predicate.operator == "eq":
                    mask &= values == predicate.value
                elif predicate.operator == "between":
                    mask &= (values >= predicate.value) & \
                           (values <= predicate.value_upper)
        
        return mask
```

### 11.3 StreamingEngine

```python
class StreamingEngine(QObject):
    """
    Motor de streaming temporal.
    
    Equivalente ao dcc.Interval do Dash, mas:
    - Usa QTimer para ticks
    - Usa pyqtSignal para notificação
    - Suporta filtros avançados
    - Sincroniza múltiplas views
    """
    
    # ========== SIGNALS ==========
    tick_update = pyqtSignal(int, float)  # index, time_seconds
    window_update = pyqtSignal(ViewData)  # dados da janela atual
    playback_started = pyqtSignal()
    playback_paused = pyqtSignal()
    playback_stopped = pyqtSignal()
    playback_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, state: StreamingState, 
                 dataset_store: DatasetStore,
                 parent: Optional[QObject] = None):
        super().__init__(parent)
        self.state = state
        self.dataset_store = dataset_store
        
        # Timer para ticks
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        
        # Índices elegíveis (após filtros)
        self._eligible_indices: Optional[np.ndarray] = None
        self._current_position: int = 0  # Posição no array de elegíveis
    
    # ========== CONTROLE DE PLAYBACK ==========
    
    def play(self) -> None:
        """Inicia ou retoma reprodução"""
        if self.state.play_state == PlayState.PLAYING:
            return
        
        # Calcular intervalo do timer
        base_interval_ms = 100  # 10 FPS base
        interval_ms = int(base_interval_ms / self.state.speed)
        
        self.state.play_state = PlayState.PLAYING
        self._timer.start(interval_ms)
        self.playback_started.emit()
    
    def pause(self) -> None:
        """Pausa reprodução"""
        if self.state.play_state != PlayState.PLAYING:
            return
        
        self._timer.stop()
        self.state.play_state = PlayState.PAUSED
        self.playback_paused.emit()
    
    def stop(self) -> None:
        """Para reprodução e reseta posição"""
        self._timer.stop()
        self.state.play_state = PlayState.STOPPED
        self.state.current_time_index = 0
        self._current_position = 0
        self.playback_stopped.emit()
    
    def seek(self, time_seconds: float) -> None:
        """
        Salta para tempo específico.
        
        Args:
            time_seconds: Tempo alvo em segundos
        """
        if self._eligible_indices is None:
            return
        
        # Encontrar índice mais próximo
        # ... (implementação)
        self._emit_current_window()
    
    def set_speed(self, speed: float) -> None:
        """
        Define velocidade de reprodução.
        
        Args:
            speed: Multiplicador (1.0 = tempo real)
        """
        self.state.speed = speed
        
        # Reiniciar timer com novo intervalo se estiver tocando
        if self.state.play_state == PlayState.PLAYING:
            base_interval_ms = 100
            interval_ms = int(base_interval_ms / speed)
            self._timer.setInterval(interval_ms)
    
    # ========== PREPARAÇÃO ==========
    
    def prepare(self, dataset_id: DatasetID, 
                series_ids: list[SeriesID]) -> None:
        """
        Prepara streaming para dataset.
        
        1. Carrega dados
        2. Aplica filtros de elegibilidade
        3. Cria índice de timestamps elegíveis
        """
        dataset = self.dataset_store.get_dataset(dataset_id)
        
        # Criar ViewData completo
        view_data = self.dataset_store.create_view(
            dataset_id, series_ids,
            TimeWindow(
                start=float(dataset.t_seconds[0]),
                end=float(dataset.t_seconds[-1])
            )
        )
        
        # Aplicar filtros de elegibilidade
        mask = self.state.filters.apply_eligibility(
            dataset.t_seconds, view_data
        )
        
        self._eligible_indices = np.where(mask)[0]
        self.state.max_index = len(self._eligible_indices) - 1
        self._current_position = 0
        
        # Guardar referências
        self._dataset_id = dataset_id
        self._series_ids = series_ids
        self._t_seconds = dataset.t_seconds
    
    # ========== TICK HANDLER ==========
    
    def _on_tick(self) -> None:
        """Handler de tick do timer"""
        if self._eligible_indices is None:
            return
        
        # Avançar posição
        self._current_position += 1
        
        # Verificar fim
        if self._current_position >= len(self._eligible_indices):
            if self.state.loop:
                self._current_position = 0
            else:
                self.stop()
                self.playback_finished.emit()
                return
        
        # Atualizar índice no estado
        self.state.current_time_index = self._eligible_indices[self._current_position]
        
        # Emitir sinais
        current_time = self._t_seconds[self.state.current_time_index]
        self.tick_update.emit(self.state.current_time_index, current_time)
        
        # Emitir janela de dados
        self._emit_current_window()
    
    def _emit_current_window(self) -> None:
        """Emite ViewData da janela atual"""
        current_time = self._t_seconds[self.state.current_time_index]
        
        window = TimeWindow(
            start=current_time - self.state.window_size_seconds / 2,
            end=current_time + self.state.window_size_seconds / 2
        )
        
        view_data = self.dataset_store.create_view(
            self._dataset_id, self._series_ids, window
        )
        
        # Aplicar filtros de render
        view_data = self._apply_render_filters(view_data)
        
        self.window_update.emit(view_data)
    
    def _apply_render_filters(self, data: ViewData) -> ViewData:
        """Aplica filtros de render (fase 2)"""
        filters = self.state.filters
        
        # Ocultar séries
        if filters.hidden_series:
            data.series = {
                k: v for k, v in data.series.items()
                if k not in filters.hidden_series
            }
        
        # Downsampling
        if len(data.t_seconds) > filters.max_points_per_window:
            from .downsampling import _downsample
            data = _downsample(data, DownsampleStrategy(
                method=filters.downsample_method,
                max_points=filters.max_points_per_window
            ))
        
        return data
```

### 11.4 Sincronização Multi-View

```python
# desktop/signal_hub.py
class SignalHub(QObject):
    """
    Hub central de signals para sincronização.
    
    Substitui o padrão de callbacks do Dash.
    Todas as views se conectam aqui para sincronização.
    """
    
    # Streaming signals
    streaming_tick = pyqtSignal(int, float)  # index, time
    streaming_window = pyqtSignal(ViewData)
    
    # Selection signals
    selection_changed = pyqtSignal(Selection)
    
    # Data signals
    dataset_loaded = pyqtSignal(DatasetID)
    series_added = pyqtSignal(DatasetID, SeriesID)
    
    # UI signals
    status_message = pyqtSignal(str)
    progress_update = pyqtSignal(int, str)  # percent, message
    
    _instance: Optional['SignalHub'] = None
    
    @classmethod
    def instance(cls) -> 'SignalHub':
        """Singleton para acesso global"""
        if cls._instance is None:
            cls._instance = SignalHub()
        return cls._instance
    
    def connect_streaming_engine(self, engine: StreamingEngine) -> None:
        """Conecta StreamingEngine ao hub"""
        engine.tick_update.connect(self.streaming_tick)
        engine.window_update.connect(self.streaming_window)
    
    def connect_view(self, view: BasePlot) -> None:
        """Conecta view para receber atualizações de streaming"""
        self.streaming_window.connect(view.update)
```

### 11.5 Video Export

```python
# desktop/workers/video_export_worker.py
from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np

class VideoExportWorker(QThread):
    """
    Worker para exportar streaming como vídeo.
    
    Usa OpenCV ou MoviePy conforme configuração.
    """
    
    progress = pyqtSignal(int)  # 0-100
    finished = pyqtSignal(str)  # output path
    error = pyqtSignal(str)
    
    def __init__(self, streaming_engine: StreamingEngine,
                 output_path: str, fps: int = 30,
                 resolution: tuple[int, int] = (1920, 1080),
                 library: str = "opencv"):
        super().__init__()
        self.engine = streaming_engine
        self.output_path = output_path
        self.fps = fps
        self.resolution = resolution
        self.library = library
    
    def run(self):
        try:
            if self.library == "opencv":
                self._export_opencv()
            else:
                self._export_moviepy()
            
            self.finished.emit(self.output_path)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _export_opencv(self):
        """Exporta usando OpenCV"""
        import cv2
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            self.output_path, fourcc, self.fps, self.resolution
        )
        
        total_frames = len(self.engine._eligible_indices)
        
        for i, idx in enumerate(self.engine._eligible_indices):
            # Capturar frame da view
            # (requer acesso ao widget - implementação simplificada)
            frame = self._capture_frame(idx)
            out.write(frame)
            
            progress = int((i + 1) / total_frames * 100)
            self.progress.emit(progress)
        
        out.release()
    
    def _capture_frame(self, index: int) -> np.ndarray:
        """Captura frame do plot atual"""
        # Implementação depende do tipo de plot
        # Para pyqtgraph: exportar como imagem
        # Para PyVista: screenshot
        pass
```

---

## 12. Desktop UI (PyQt6)

### 12.1 Application Entry Point

```python
# desktop/app.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

def run_app():
    """Entry point da aplicação"""
    # HiDPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Platform Base")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("PlatformBase")
    
    # Carregar configuração
    config = load_config()
    
    # Aplicar tema
    apply_theme(app, config.desktop.theme)
    
    # Criar janela principal
    from .main_window import MainWindow
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec())

def apply_theme(app: QApplication, theme: str):
    """Aplica tema à aplicação"""
    if theme == "auto":
        # Detectar tema do sistema
        palette = app.palette()
        is_dark = palette.color(palette.ColorRole.Window).lightness() < 128
        theme = "dark" if is_dark else "light"
    
    # Carregar stylesheet
    style_path = f"resources/styles/{theme}.qss"
    with open(style_path) as f:
        app.setStyleSheet(f.read())
```

### 12.2 SessionState (State Management)

```python
# desktop/session_state.py
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional

class SessionState(QObject):
    """
    Estado centralizado da sessão.
    
    Substitui:
    - dash.Store (client-side state)
    - AppState do Dash (server-side state)
    
    Usa signals para notificar mudanças (padrão Observer).
    """
    
    # Signals para mudanças de estado
    current_dataset_changed = pyqtSignal(DatasetID)
    selected_series_changed = pyqtSignal(list)  # list[SeriesID]
    selection_changed = pyqtSignal(Selection)
    view_config_changed = pyqtSignal(PlotConfig)
    streaming_state_changed = pyqtSignal(StreamingState)
    
    def __init__(self, dataset_store: DatasetStore):
        super().__init__()
        self.dataset_store = dataset_store
        
        # Estado atual
        self._current_dataset_id: Optional[DatasetID] = None
        self._selected_series: list[SeriesID] = []
        self._selection: Optional[Selection] = None
        self._view_configs: dict[ViewID, PlotConfig] = {}
        self._streaming_state: Optional[StreamingState] = None
        
        # Cache de views
        self._view_cache: dict[str, ViewData] = {}
    
    # ========== DATASET ==========
    
    @property
    def current_dataset(self) -> Optional[Dataset]:
        """Retorna dataset atual"""
        if self._current_dataset_id:
            return self.dataset_store.get_dataset(self._current_dataset_id)
        return None
    
    @property
    def current_dataset_id(self) -> Optional[DatasetID]:
        return self._current_dataset_id
    
    @current_dataset_id.setter
    def current_dataset_id(self, value: DatasetID):
        if value != self._current_dataset_id:
            self._current_dataset_id = value
            self._view_cache.clear()
            self.current_dataset_changed.emit(value)
    
    # ========== SERIES SELECTION ==========
    
    @property
    def selected_series(self) -> list[SeriesID]:
        return self._selected_series.copy()
    
    @selected_series.setter
    def selected_series(self, value: list[SeriesID]):
        if value != self._selected_series:
            self._selected_series = value.copy()
            self.selected_series_changed.emit(value)
    
    # ========== DATA SELECTION ==========
    
    @property
    def selection(self) -> Optional[Selection]:
        return self._selection
    
    @selection.setter
    def selection(self, value: Selection):
        self._selection = value
        self.selection_changed.emit(value)
    
    # ========== VIEW DATA ==========
    
    def get_current_view(self, time_window: Optional[TimeWindow] = None) -> Optional[ViewData]:
        """
        Obtém ViewData para visualização atual.
        
        Usa cache para evitar recálculos.
        """
        if not self._current_dataset_id or not self._selected_series:
            return None
        
        dataset = self.current_dataset
        
        if time_window is None:
            time_window = TimeWindow(
                start=float(dataset.t_seconds[0]),
                end=float(dataset.t_seconds[-1])
            )
        
        cache_key = f"{self._current_dataset_id}:{':'.join(self._selected_series)}:{time_window.start}:{time_window.end}"
        
        if cache_key not in self._view_cache:
            self._view_cache[cache_key] = self.dataset_store.create_view(
                self._current_dataset_id,
                self._selected_series,
                time_window
            )
        
        return self._view_cache[cache_key]
    
    # ========== STREAMING ==========
    
    @property
    def streaming_state(self) -> Optional[StreamingState]:
        return self._streaming_state
    
    @streaming_state.setter
    def streaming_state(self, value: StreamingState):
        self._streaming_state = value
        self.streaming_state_changed.emit(value)
    
    # ========== SERIALIZATION ==========
    
    def save_session(self, path: str) -> None:
        """Salva sessão para arquivo"""
        session_data = {
            "current_dataset_id": self._current_dataset_id,
            "selected_series": self._selected_series,
            "selection": self._selection.dict() if self._selection else None,
            "view_configs": {k: v.dict() for k, v in self._view_configs.items()},
            # Não salva dados brutos, apenas referências
        }
        
        import json
        with open(path, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def load_session(self, path: str) -> None:
        """Carrega sessão de arquivo"""
        import json
        with open(path) as f:
            session_data = json.load(f)
        
        # Restaurar estado
        if session_data.get("current_dataset_id"):
            self.current_dataset_id = session_data["current_dataset_id"]
        
        if session_data.get("selected_series"):
            self.selected_series = session_data["selected_series"]
        
        if session_data.get("selection"):
            self.selection = Selection(**session_data["selection"])
```

### 12.3 MainWindow

```python
# desktop/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QDockWidget, QToolBar,
    QStatusBar, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QIcon

class MainWindow(QMainWindow):
    """
    Janela principal da aplicação.
    
    Layout:
    - Menu bar (File, Edit, View, Tools, Help)
    - Toolbar (ações rápidas)
    - Central: Splitter com painéis
    - Status bar
    """
    
    def __init__(self, config: PlatformConfig):
        super().__init__()
        self.config = config
        
        # Criar stores e estado
        self.dataset_store = DatasetStore()
        self.session_state = SessionState(self.dataset_store)
        self.signal_hub = SignalHub.instance()
        
        # Setup UI
        self.setWindowTitle("Platform Base v2.0")
        self._setup_geometry()
        self._create_central_widget()
        self._create_menus()
        self._create_toolbar()
        self._create_status_bar()
        self._create_dock_widgets()
        
        # Conectar signals
        self._connect_signals()
        
        # Aplicar tema
        self._apply_theme()
    
    def _setup_geometry(self):
        """Configura geometria da janela"""
        settings = QSettings()
        
        if self.config.desktop.window.remember_geometry:
            geometry = settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
                return
        
        # Default
        self.resize(
            self.config.desktop.window.width,
            self.config.desktop.window.height
        )
        self.center_on_screen()
    
    def _create_central_widget(self):
        """Cria widget central com splitter"""
        self.central_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.central_splitter)
        
        # Painel de dados (esquerda)
        self.data_panel = DataPanel(self.dataset_store, self.session_state)
        self.central_splitter.addWidget(self.data_panel)
        
        # Painel de visualização (centro)
        self.viz_panel = VizPanel(self.session_state, self.signal_hub)
        self.central_splitter.addWidget(self.viz_panel)
        
        # Painel de configuração (direita)
        self.config_panel = ConfigPanel(self.session_state)
        self.central_splitter.addWidget(self.config_panel)
        
        # Proporções
        self.central_splitter.setSizes([250, 700, 250])
    
    def _create_menus(self):
        """Cria menus da aplicação"""
        menubar = self.menuBar()
        
        # ========== FILE MENU ==========
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction(QIcon(":/icons/open.png"), "&Open Dataset...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_dataset)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        export_action = QAction(QIcon(":/icons/export.png"), "&Export...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        export_video_action = QAction("Export &Video...", self)
        export_video_action.triggered.connect(self.export_video)
        file_menu.addAction(export_video_action)
        
        file_menu.addSeparator()
        
        save_session_action = QAction("&Save Session...", self)
        save_session_action.setShortcut("Ctrl+S")
        save_session_action.triggered.connect(self.save_session)
        file_menu.addAction(save_session_action)
        
        load_session_action = QAction("&Load Session...", self)
        load_session_action.triggered.connect(self.load_session)
        file_menu.addAction(load_session_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ========== EDIT MENU ==========
        edit_menu = menubar.addMenu("&Edit")
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # ========== VIEW MENU ==========
        view_menu = menubar.addMenu("&View")
        
        self.toggle_data_action = QAction("&Data Panel", self, checkable=True)
        self.toggle_data_action.setChecked(True)
        self.toggle_data_action.triggered.connect(self.toggle_data_panel)
        view_menu.addAction(self.toggle_data_action)
        
        self.toggle_config_action = QAction("&Config Panel", self, checkable=True)
        self.toggle_config_action.setChecked(True)
        self.toggle_config_action.triggered.connect(self.toggle_config_panel)
        view_menu.addAction(self.toggle_config_action)
        
        view_menu.addSeparator()
        
        theme_menu = view_menu.addMenu("&Theme")
        light_action = QAction("&Light", self)
        light_action.triggered.connect(lambda: self._set_theme("light"))
        theme_menu.addAction(light_action)
        
        dark_action = QAction("&Dark", self)
        dark_action.triggered.connect(lambda: self._set_theme("dark"))
        theme_menu.addAction(dark_action)
        
        # ========== TOOLS MENU ==========
        tools_menu = menubar.addMenu("&Tools")
        
        interp_action = QAction("&Interpolate...", self)
        interp_action.triggered.connect(self.run_interpolation)
        tools_menu.addAction(interp_action)
        
        deriv_action = QAction("Calculate &Derivative...", self)
        deriv_action.triggered.connect(self.calculate_derivative)
        tools_menu.addAction(deriv_action)
        
        sync_action = QAction("&Synchronize Series...", self)
        sync_action.triggered.connect(self.synchronize_series)
        tools_menu.addAction(sync_action)
        
        tools_menu.addSeparator()
        
        smooth_action = QAction("Apply S&moothing...", self)
        smooth_action.triggered.connect(self.apply_smoothing)
        tools_menu.addAction(smooth_action)
        
        # ========== HELP MENU ==========
        help_menu = menubar.addMenu("&Help")
        
        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut("F1")
        docs_action.triggered.connect(self.show_docs)
        help_menu.addAction(docs_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About...", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """Cria toolbar principal"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Ações rápidas
        toolbar.addAction(QIcon(":/icons/open.png"), "Open", self.open_dataset)
        toolbar.addAction(QIcon(":/icons/export.png"), "Export", self.export_data)
        toolbar.addSeparator()
        
        # Controles de streaming
        self.play_action = toolbar.addAction(
            QIcon(":/icons/play.png"), "Play", self.toggle_streaming
        )
        toolbar.addAction(QIcon(":/icons/stop.png"), "Stop", self.stop_streaming)
        
        # Speed control
        from PyQt6.QtWidgets import QDoubleSpinBox
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setRange(0.1, 10.0)
        self.speed_spinbox.setValue(1.0)
        self.speed_spinbox.setSuffix("x")
        self.speed_spinbox.valueChanged.connect(self._on_speed_changed)
        toolbar.addWidget(self.speed_spinbox)
    
    def _create_status_bar(self):
        """Cria barra de status"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Progress bar (inicialmente oculta)
        from PyQt6.QtWidgets import QProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def _create_dock_widgets(self):
        """Cria dock widgets opcionais"""
        # Painel de resultados (dock na parte inferior)
        self.results_dock = QDockWidget("Results", self)
        self.results_panel = ResultsPanel()
        self.results_dock.setWidget(self.results_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.results_dock)
        self.results_dock.setVisible(False)
        
        # Painel de streaming (dock lateral)
        self.streaming_dock = QDockWidget("Streaming", self)
        self.streaming_panel = StreamingPanel(self.session_state, self.signal_hub)
        self.streaming_dock.setWidget(self.streaming_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.streaming_dock)
    
    def _connect_signals(self):
        """Conecta signals entre componentes"""
        # Data panel → Session state
        self.data_panel.dataset_selected.connect(
            lambda did: setattr(self.session_state, 'current_dataset_id', did)
        )
        self.data_panel.series_selected.connect(
            lambda sids: setattr(self.session_state, 'selected_series', sids)
        )
        
        # Session state → Viz panel
        self.session_state.current_dataset_changed.connect(
            self.viz_panel.on_dataset_changed
        )
        self.session_state.selected_series_changed.connect(
            self.viz_panel.on_series_changed
        )
        
        # Signal hub → Status bar
        self.signal_hub.status_message.connect(self.status_bar.showMessage)
        self.signal_hub.progress_update.connect(self._on_progress_update)
    
    # ========== ACTION HANDLERS ==========
    
    def open_dataset(self):
        """Abre diálogo para carregar dataset"""
        from .dialogs.upload_dialog import UploadDialog
        dialog = UploadDialog(self)
        
        if dialog.exec():
            path = dialog.get_path()
            config = dialog.get_config()
            
            # Executar em worker thread
            self.loader_worker = LoaderWorker(path, config)
            self.loader_worker.progress.connect(self._on_loader_progress)
            self.loader_worker.finished.connect(self._on_dataset_loaded)
            self.loader_worker.error.connect(self._on_loader_error)
            self.loader_worker.start()
            
            self.progress_bar.setVisible(True)
    
    def _on_dataset_loaded(self, dataset: Dataset):
        """Handler de dataset carregado"""
        self.progress_bar.setVisible(False)
        
        # Adicionar ao store
        dataset_id = self.dataset_store.add_dataset(dataset)
        
        # Atualizar UI
        self.data_panel.refresh()
        self.session_state.current_dataset_id = dataset_id
        
        self.status_bar.showMessage(
            f"Loaded dataset: {dataset.source.filename} "
            f"({len(dataset.series)} series, {len(dataset.t_seconds)} points)"
        )
    
    def export_data(self):
        """Abre diálogo de exportação"""
        from .dialogs.export_dialog import ExportDialog
        dialog = ExportDialog(self.session_state.selection, self)
        
        if dialog.exec():
            # Executar export em worker
            self.export_worker = ExportWorker(
                self.session_state,
                dialog.get_output_path(),
                dialog.get_format()
            )
            self.export_worker.progress.connect(
                lambda p: self.progress_bar.setValue(p)
            )
            self.export_worker.finished.connect(
                lambda: self.status_bar.showMessage("Export completed")
            )
            self.export_worker.error.connect(
                lambda e: QMessageBox.critical(self, "Export Error", e)
            )
            self.export_worker.start()
            
            self.progress_bar.setVisible(True)
    
    def run_interpolation(self):
        """Abre diálogo de interpolação"""
        from .dialogs.interpolation_dialog import InterpolationDialog
        dialog = InterpolationDialog(self.session_state, self)
        
        if dialog.exec():
            method = dialog.get_method()
            params = dialog.get_params()
            
            # Executar em worker
            self.processing_worker = ProcessingWorker(
                interpolate,
                self.session_state.current_dataset.series[
                    self.session_state.selected_series[0]
                ].values,
                self.session_state.current_dataset.t_seconds,
                method, params
            )
            self.processing_worker.finished.connect(self._on_interpolation_done)
            self.processing_worker.error.connect(
                lambda e: QMessageBox.critical(self, "Interpolation Error", e)
            )
            self.processing_worker.start()
    
    def _on_interpolation_done(self, result: InterpResult):
        """Handler de interpolação concluída"""
        # Criar nova série com resultado
        original_series = self.session_state.current_dataset.series[
            self.session_state.selected_series[0]
        ]
        
        new_series = Series(
            series_id=SeriesID(f"{original_series.series_id}_interp"),
            name=f"{original_series.name} (interpolated)",
            unit=original_series.unit,
            values=result.values,
            interpolation_info=result.interpolation_info,
            metadata=original_series.metadata
        )
        
        lineage = Lineage(
            origin_series=[original_series.series_id],
            operation="interpolate",
            parameters=result.metadata.parameters,
            timestamp=datetime.now(),
            version=__version__
        )
        
        # Adicionar ao store
        self.dataset_store.add_series(
            self.session_state.current_dataset_id,
            new_series,
            lineage
        )
        
        # Atualizar UI
        self.data_panel.refresh()
        self.status_bar.showMessage("Interpolation completed")
    
    def toggle_streaming(self):
        """Toggle play/pause do streaming"""
        if not hasattr(self, 'streaming_engine'):
            # Criar engine
            state = StreamingState(
                filters=StreamFilters(),
                window_size_seconds=self.config.streaming.window_size_seconds
            )
            self.streaming_engine = StreamingEngine(
                state, self.dataset_store
            )
            self.signal_hub.connect_streaming_engine(self.streaming_engine)
            
            # Preparar
            self.streaming_engine.prepare(
                self.session_state.current_dataset_id,
                self.session_state.selected_series
            )
        
        if self.streaming_engine.state.play_state == PlayState.PLAYING:
            self.streaming_engine.pause()
            self.play_action.setIcon(QIcon(":/icons/play.png"))
        else:
            self.streaming_engine.play()
            self.play_action.setIcon(QIcon(":/icons/pause.png"))
    
    def stop_streaming(self):
        """Para streaming"""
        if hasattr(self, 'streaming_engine'):
            self.streaming_engine.stop()
            self.play_action.setIcon(QIcon(":/icons/play.png"))
    
    # ========== CLEANUP ==========
    
    def closeEvent(self, event):
        """Handler de fechamento"""
        # Salvar geometria
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        
        # Parar streaming
        self.stop_streaming()
        
        event.accept()
```

### 12.4 Data Panel

```python
# desktop/widgets/data_panel.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeView,
    QGroupBox, QLabel, QHeaderView
)
from PyQt6.QtCore import pyqtSignal, QModelIndex

class DataPanel(QWidget):
    """
    Painel de datasets e séries.
    
    Equivalente ao layout de upload/seleção do Dash.
    """
    
    # Signals
    dataset_selected = pyqtSignal(DatasetID)
    series_selected = pyqtSignal(list)  # list[SeriesID]
    
    def __init__(self, dataset_store: DatasetStore, 
                 session_state: SessionState):
        super().__init__()
        self.dataset_store = dataset_store
        self.session_state = session_state
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura UI"""
        layout = QVBoxLayout(self)
        
        # ========== UPLOAD SECTION ==========
        upload_group = QGroupBox("Data Upload")
        upload_layout = QVBoxLayout()
        
        self.upload_btn = QPushButton("Upload Dataset...")
        self.upload_btn.clicked.connect(self._on_upload_clicked)
        upload_layout.addWidget(self.upload_btn)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        # ========== DATASETS TREE ==========
        tree_group = QGroupBox("Datasets & Series")
        tree_layout = QVBoxLayout()
        
        self.dataset_tree = QTreeView()
        self.dataset_model = DatasetTreeModel(self.dataset_store)
        self.dataset_tree.setModel(self.dataset_model)
        self.dataset_tree.setSelectionMode(
            QTreeView.SelectionMode.ExtendedSelection
        )
        self.dataset_tree.header().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        
        tree_layout.addWidget(self.dataset_tree)
        tree_group.setLayout(tree_layout)
        layout.addWidget(tree_group)
        
        # ========== INFO SECTION ==========
        info_group = QGroupBox("Selection Info")
        info_layout = QVBoxLayout()
        
        self.info_label = QLabel("No selection")
        info_layout.addWidget(self.info_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
    
    def _connect_signals(self):
        """Conecta signals internos"""
        self.dataset_tree.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
    
    def _on_upload_clicked(self):
        """Handler de clique no botão upload"""
        # Propaga para MainWindow via signal ou parent
        self.window().open_dataset()
    
    def _on_selection_changed(self, selected, deselected):
        """Handler de mudança de seleção na árvore"""
        indices = self.dataset_tree.selectionModel().selectedIndexes()
        
        if not indices:
            return
        
        # Determinar o que foi selecionado
        datasets = []
        series = []
        
        for index in indices:
            item = self.dataset_model.itemFromIndex(index)
            if item.data(Qt.ItemDataRole.UserRole + 1) == "dataset":
                datasets.append(item.data(Qt.ItemDataRole.UserRole))
            elif item.data(Qt.ItemDataRole.UserRole + 1) == "series":
                series.append(item.data(Qt.ItemDataRole.UserRole))
        
        # Emitir signals
        if datasets:
            self.dataset_selected.emit(datasets[0])
        
        if series:
            self.series_selected.emit(series)
        
        # Atualizar info
        self._update_info(datasets, series)
    
    def _update_info(self, datasets: list, series: list):
        """Atualiza label de informação"""
        if datasets:
            dataset = self.dataset_store.get_dataset(datasets[0])
            self.info_label.setText(
                f"Dataset: {dataset.source.filename}\n"
                f"Points: {len(dataset.t_seconds)}\n"
                f"Series: {len(dataset.series)}"
            )
        elif series:
            self.info_label.setText(f"Selected {len(series)} series")
        else:
            self.info_label.setText("No selection")
    
    def refresh(self):
        """Atualiza modelo da árvore"""
        self.dataset_model.refresh()
```

### 12.5 Workers (QThread)

```python
# desktop/workers/base_worker.py
from PyQt6.QtCore import QThread, pyqtSignal
from typing import Callable, Any

class BaseWorker(QThread):
    """
    Worker base para operações em background.
    
    Substitui:
    - dash.long_callback
    - DiskcacheLongCallbackManager
    """
    
    progress = pyqtSignal(int, str)  # percent, message
    finished = pyqtSignal(object)  # resultado
    error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_cancelled = False
    
    def cancel(self):
        """Solicita cancelamento"""
        self._is_cancelled = True
    
    def is_cancelled(self) -> bool:
        """Verifica se foi cancelado"""
        return self._is_cancelled
    
    def emit_progress(self, percent: int, message: str = ""):
        """Emite progresso de forma thread-safe"""
        self.progress.emit(percent, message)


# desktop/workers/loader_worker.py
class LoaderWorker(BaseWorker):
    """Worker para carregamento de datasets"""
    
    def __init__(self, path: str, config: LoadConfig):
        super().__init__()
        self.path = path
        self.config = config
    
    def run(self):
        try:
            self.emit_progress(0, "Reading file...")
            
            # Carregar arquivo
            from io.loader import load
            dataset = load(self.path, self.config)
            
            self.emit_progress(100, "Done")
            self.finished.emit(dataset)
            
        except Exception as e:
            logger.exception("loader_error")
            self.error.emit(str(e))


# desktop/workers/processing_worker.py
class ProcessingWorker(BaseWorker):
    """Worker genérico para operações de processamento"""
    
    def __init__(self, operation: Callable, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.operation(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            logger.exception("processing_error")
            self.error.emit(str(e))


# desktop/workers/export_worker.py
class ExportWorker(BaseWorker):
    """Worker para exportação de dados"""
    
    def __init__(self, session_state: SessionState, 
                 output_path: str, format: str):
        super().__init__()
        self.session_state = session_state
        self.output_path = output_path
        self.format = format
    
    def run(self):
        try:
            view_data = self.session_state.get_current_view()
            
            if view_data is None:
                self.error.emit("No data to export")
                return
            
            self.emit_progress(10, "Preparing data...")
            
            # Converter para DataFrame
            df = pd.DataFrame(view_data.series)
            df.insert(0, 'timestamp', view_data.t_datetime)
            
            self.emit_progress(50, "Writing file...")
            
            # Exportar conforme formato
            if self.format == "csv":
                df.to_csv(self.output_path, index=False)
            elif self.format == "xlsx":
                df.to_excel(self.output_path, index=False)
            elif self.format == "parquet":
                df.to_parquet(self.output_path)
            elif self.format == "hdf5":
                df.to_hdf(self.output_path, key='data')
            
            self.emit_progress(100, "Done")
            self.finished.emit(self.output_path)
            
        except Exception as e:
            logger.exception("export_error")
            self.error.emit(str(e))
```

### 12.6 Context Menu

```python
# desktop/widgets/context_menu.py
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

class PlotContextMenu(QMenu):
    """
    Menu contextual para plots.
    
    Equivalente ao context_menu do Dash.
    
    Ações implementadas:
    - zoom/pan/reset
    - selecionar região/pontos
    - extrair subsérie
    - filtros visuais
    - exportar seleção
    - anotar
    - comparar séries
    - estatísticas em seleção
    """
    
    def __init__(self, plot_widget, session_state: SessionState = None, 
                 parent=None):
        super().__init__(parent)
        self.plot_widget = plot_widget
        self.session_state = session_state
        
        self._create_actions()
    
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
        # Implementação depende do tipo de plot
        pass
    
    def _extract_selection(self):
        """Extrai dados da seleção"""
        # Criar nova série com seleção
        pass
    
    def _show_stats(self):
        """Mostra estatísticas da seleção"""
        from PyQt6.QtWidgets import QMessageBox
        
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
    
    def _export_plot(self):
        """Exporta plot como imagem"""
        from PyQt6.QtWidgets import QFileDialog
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Plot", "",
            "PNG (*.png);;SVG (*.svg);;PDF (*.pdf)"
        )
        
        if path:
            if hasattr(self.plot_widget, 'export'):
                # pyqtgraph
                import pyqtgraph.exporters as exp
                exporter = exp.ImageExporter(self.plot_widget.plotItem)
                exporter.export(path)
```

---

## 13. Selection (PyQt6)

```python
# desktop/widgets/selection_widget.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QDateTimeEdit,
    QPushButton, QTextEdit, QFormLayout, QComboBox,
    QDoubleSpinBox, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal

class Predicate(BaseModel):
    """Predicado para seleção condicional"""
    series: SeriesID
    operator: Literal["gt", "gte", "lt", "lte", "eq", "neq", "between"]
    value: float
    value_upper: Optional[float] = None

class Selection(BaseModel):
    """
    Modelo de seleção de dados.
    
    Suporta 3 métodos combinados:
    1. Temporal (range)
    2. Interativo (clique/arrasto no gráfico)
    3. Condicional (query-like)
    """
    
    # Método 1: Temporal
    time_range: Optional[TimeWindow] = None
    
    # Método 2: Interativo
    interactive_indices: Optional[list[int]] = None
    
    # Método 3: Condicional
    predicates: Optional[list[Predicate]] = None
    
    # Combinação
    combination: Literal["and", "or"] = "and"
    
    def to_mask(self, data: ViewData) -> np.ndarray:
        """Converte seleção em máscara booleana"""
        masks = []
        
        # Temporal
        if self.time_range:
            mask = (data.t_seconds >= self.time_range.start) & \
                   (data.t_seconds <= self.time_range.end)
            masks.append(mask)
        
        # Interativo
        if self.interactive_indices:
            mask = np.zeros(len(data.t_seconds), dtype=bool)
            mask[self.interactive_indices] = True
            masks.append(mask)
        
        # Condicional
        if self.predicates:
            for pred in self.predicates:
                if pred.series in data.series:
                    values = data.series[pred.series]
                    if pred.operator == "gt":
                        mask = values > pred.value
                    elif pred.operator == "gte":
                        mask = values >= pred.value
                    elif pred.operator == "lt":
                        mask = values < pred.value
                    elif pred.operator == "lte":
                        mask = values <= pred.value
                    elif pred.operator == "eq":
                        mask = values == pred.value
                    elif pred.operator == "between":
                        mask = (values >= pred.value) & \
                               (values <= pred.value_upper)
                    masks.append(mask)
        
        if not masks:
            return np.ones(len(data.t_seconds), dtype=bool)
        
        # Combinar
        if self.combination == "and":
            return np.all(masks, axis=0)
        else:
            return np.any(masks, axis=0)


class SelectionWidget(QWidget):
    """
    Widget de seleção de dados.
    
    Equivalente à interface de seleção do Dash.
    """
    
    selection_changed = pyqtSignal(Selection)
    
    def __init__(self, session_state: SessionState):
        super().__init__()
        self.session_state = session_state
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura UI"""
        layout = QVBoxLayout(self)
        
        # ========== TEMPORAL SELECTION ==========
        time_group = QGroupBox("Time Range")
        time_layout = QFormLayout()
        
        self.start_time = QDateTimeEdit()
        self.end_time = QDateTimeEdit()
        
        time_layout.addRow("Start:", self.start_time)
        time_layout.addRow("End:", self.end_time)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # ========== INTERACTIVE SELECTION ==========
        interactive_group = QGroupBox("Interactive Selection")
        interactive_layout = QVBoxLayout()
        
        self.selection_info = QTextEdit()
        self.selection_info.setReadOnly(True)
        self.selection_info.setMaximumHeight(60)
        
        clear_btn = QPushButton("Clear Selection")
        clear_btn.clicked.connect(self._clear_interactive)
        
        interactive_layout.addWidget(self.selection_info)
        interactive_layout.addWidget(clear_btn)
        
        interactive_group.setLayout(interactive_layout)
        layout.addWidget(interactive_group)
        
        # ========== CONDITIONAL SELECTION ==========
        cond_group = QGroupBox("Conditional")
        cond_layout = QVBoxLayout()
        
        # Builder de predicados
        pred_row = QHBoxLayout()
        
        self.series_combo = QComboBox()
        pred_row.addWidget(self.series_combo)
        
        self.operator_combo = QComboBox()
        self.operator_combo.addItems([">", ">=", "<", "<=", "=", "between"])
        pred_row.addWidget(self.operator_combo)
        
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(-1e9, 1e9)
        pred_row.addWidget(self.value_spin)
        
        add_pred_btn = QPushButton("+")
        add_pred_btn.clicked.connect(self._add_predicate)
        pred_row.addWidget(add_pred_btn)
        
        cond_layout.addLayout(pred_row)
        
        # Lista de predicados
        self.predicates_list = QTextEdit()
        self.predicates_list.setReadOnly(True)
        self.predicates_list.setMaximumHeight(60)
        cond_layout.addWidget(self.predicates_list)
        
        cond_group.setLayout(cond_layout)
        layout.addWidget(cond_group)
        
        # ========== COMBINAÇÃO ==========
        comb_layout = QHBoxLayout()
        
        self.combination_combo = QComboBox()
        self.combination_combo.addItems(["AND", "OR"])
        comb_layout.addWidget(QLabel("Combine:"))
        comb_layout.addWidget(self.combination_combo)
        
        layout.addLayout(comb_layout)
        
        # ========== APPLY BUTTON ==========
        apply_btn = QPushButton("Apply Selection")
        apply_btn.clicked.connect(self._apply_selection)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
    
    def _add_predicate(self):
        """Adiciona predicado à lista"""
        # Implementação
        pass
    
    def _clear_interactive(self):
        """Limpa seleção interativa"""
        self.selection_info.clear()
    
    def _apply_selection(self):
        """Aplica seleção e emite signal"""
        selection = Selection(
            time_range=TimeWindow(
                start=self.start_time.dateTime().toSecsSinceEpoch(),
                end=self.end_time.dateTime().toSecsSinceEpoch()
            ) if self.start_time.dateTime() != self.end_time.dateTime() else None,
            combination="and" if self.combination_combo.currentText() == "AND" else "or"
        )
        
        self.selection_changed.emit(selection)
        self.session_state.selection = selection
    
    def update_from_plot(self, indices: list[int]):
        """Atualiza seleção a partir de interação no plot"""
        self.selection_info.setText(f"Selected {len(indices)} points")
        # Armazenar para uso posterior
        self._interactive_indices = indices
```

---

## 14. Registry + Orchestrator + Plugins

*(Mantém especificação do documento original - backend não muda)*

Ver seções 14.1 a 14.5 do documento original `Plano_de_desenvolvimento.md`.

---

## 15. Configuração

```yaml
# configs/platform.yaml
platform:
  version: "2.0.0"
  
desktop:
  theme: "auto"  # light, dark, auto
  window:
    width: 1440
    height: 900
    remember_geometry: true
  high_dpi: true
  
data:
  schema_detection:
    timestamp_patterns: [timestamp, time, datetime, date]
    heuristics: [monotonic_increasing, datetime_type, unix_epoch_range]
  units:
    default_system: "SI"
    custom_definitions: {}
  validation:
    max_gap_seconds: 300
    outlier_threshold: 3.0
    min_data_points: 10

processing:
  interpolation:
    default_method: "linear"
    available_methods: 
      - linear
      - spline_cubic
      - smoothing_spline
      - resample_grid
      - mls
      - gpr
      - lomb_scargle_spectral
  calculus:
    derivative_default: "finite_diff"
    max_order: 3
    smoothing_presets:
      light: 
        method: savitzky_golay
        window: 5
        polyorder: 2
      heavy: 
        method: gaussian
        sigma: 2.0
  synchronization:
    default_method: "common_grid_interpolate"
      
performance:
  parallelism:
    executor: "process"
    max_workers: 4
  cache:
    disk:
      enabled: true
      ttl_hours: 24
      max_size_gb: 10
      path: ".cache"
    memory:
      enabled: true
      max_items: 1000
  profiling:
    enabled: true
    log_level: "INFO"
  numba:
    enabled: true
    cache: true
    
visualization:
  backend_2d: "pyqtgraph"
  backend_3d: "pyvista"
  downsampling:
    method: "lttb"
    max_points: 10000
    preserve_features: [peaks, valleys, edges]
  defaults:
    height: 600
    width: 800
  
streaming:
  default_speed: 1.0
  window_size_seconds: 60
  filters:
    max_points_per_window: 5000
    hide_interpolated_default: false
  video_export:
    library: "opencv"
    default_fps: 30
    default_resolution: [1920, 1080]
    
plugins:
  discovery:
    enabled: true
    path: "plugins/"
    isolation: false
    timeout_seconds: 60
  validation:
    strict: true
    
logging:
  format: "json"
  level: "INFO"
  output: "logs/platform.log"
  rotation: "1 day"
  retention: "30 days"
  
api:
  enabled: false
  host: "127.0.0.1"
  port: 8000
```

---

## 16-19. Export, Testes, Logging, API REST

*(Mantém especificação do documento original - backend não muda)*

Ver seções correspondentes do documento original `Plano_de_desenvolvimento.md`.

**Nota para UI Tests PyQt6:**

```python
# tests/ui/test_main_window.py
import pytest
from pytestqt.qtbot import QtBot
from platform_base.desktop.main_window import MainWindow
from platform_base.desktop.session_state import SessionState
from platform_base.core.dataset_store import DatasetStore

@pytest.fixture
def main_window(qtbot):
    """Fixture para MainWindow"""
    config = load_test_config()
    window = MainWindow(config)
    qtbot.addWidget(window)
    return window

def test_main_window_opens(main_window, qtbot):
    """Testa que janela abre corretamente"""
    main_window.show()
    assert main_window.isVisible()

def test_upload_dialog(main_window, qtbot):
    """Testa abertura do diálogo de upload"""
    qtbot.mouseClick(main_window.data_panel.upload_btn, Qt.MouseButton.LeftButton)
    
    # Verificar que dialog abriu
    dialog = main_window.findChild(UploadDialog)
    assert dialog is not None
    dialog.close()

def test_streaming_controls(main_window, qtbot):
    """Testa controles de streaming"""
    # Carregar dataset de teste
    main_window._on_dataset_loaded(create_test_dataset())
    
    # Play
    qtbot.mouseClick(main_window.play_action, Qt.MouseButton.LeftButton)
    assert main_window.streaming_engine.state.play_state == PlayState.PLAYING
    
    # Pause
    qtbot.mouseClick(main_window.play_action, Qt.MouseButton.LeftButton)
    assert main_window.streaming_engine.state.play_state == PlayState.PAUSED
```

---

## 20. Plano de Implementação

### Fase 1: Core + Config (2 semanas)

1. Setup projeto PyQt6
2. Config YAML + Pydantic
3. Logging estruturado (structlog)
4. DatasetStore thread-safe
5. Protocols + tipos base

**Entregável:** Infraestrutura básica funcional

### Fase 2: I/O + Data (2 semanas)

1. Loader multi-formato
2. Schema detection
3. Validação
4. Units (pint)

**Entregável:** Pipeline de carregamento completo

### Fase 3: Processing (2 semanas)

1. Interpolação (7 métodos core)
2. Sincronização (2 métodos core)
3. Cálculos (derivadas, integrais)
4. Smoothing

**Entregável:** Processamento matemático completo

### Fase 4: Desktop UI Base (2 semanas)

1. QApplication + MainWindow
2. SessionState + SignalHub
3. DataPanel
4. VizPanel (placeholder)
5. ConfigPanel

**Entregável:** Esqueleto UI funcional

### Fase 5: Visualização 2D (1 semana)

1. BasePlot abstraction
2. TimeseriesPlot2D (pyqtgraph)
3. MultipanelPlot2D
4. Downsampling (LTTB)

**Entregável:** Visualização 2D completa

### Fase 6: Visualização 3D (1 semana)

1. Trajectory3D (PyVista)
2. StateCube3D
3. Heatmap

**Entregável:** Visualização 3D completa

### Fase 7: Workers & Threading (1 semana)

1. BaseWorker
2. LoaderWorker
3. ProcessingWorker
4. ExportWorker

**Entregável:** Operações assíncronas funcionais

### Fase 8: Streaming (1 semana)

1. StreamingState + StreamFilters
2. StreamingEngine (QTimer)
3. Multi-view sync (signals)
4. StreamingPanel

**Entregável:** Streaming temporal completo

### Fase 9: Dialogs & Context Menu (1 semana)

1. UploadDialog
2. ExportDialog
3. SettingsDialog
4. InterpolationDialog
5. PlotContextMenu

**Entregável:** Diálogos e menus completos

### Fase 10: Selection (1 semana)

1. Selection model
2. SelectionWidget
3. 3 métodos integrados

**Entregável:** Sistema de seleção completo

### Fase 11: Plugins + Registry (1 semana)

1. Plugin system
2. Discovery controlado
3. Example plugins (DTW)

**Entregável:** Sistema de plugins funcional

### Fase 12: Video Export (0.5 semana)

1. VideoExportWorker
2. OpenCV integration

**Entregável:** Exportação de vídeo

### Fase 13: Testes (1 semana)

1. Unit tests (backend)
2. UI tests (pytest-qt)
3. Integration tests
4. Stress tests

**Entregável:** Suite de testes >80% coverage

### Fase 14: Packaging (1 semana)

1. PyInstaller setup
2. Windows installer (.exe)
3. macOS bundle (.app)
4. Linux AppImage

**Entregável:** Instaladores multiplataforma

**Total: ~14 semanas**

---

## 21. Critérios de Aceitação

### Desktop

- [ ] Aplicação abre em <2s
- [ ] Interface responsiva (sem freezes)
- [ ] Operações pesadas não bloqueiam UI (QThread)
- [ ] Temas claro/escuro funcionam
- [ ] HiDPI funciona corretamente
- [ ] Multiplataforma (Windows/Linux/macOS)

### Performance

- [ ] 1M pontos: plot 2D < 500ms
- [ ] 10M pontos: downsampling automático
- [ ] UI response time < 100ms
- [ ] Streaming 60 FPS estável

### Funcional

- [ ] Upload multi-formato funciona
- [ ] Schema detection >95% accuracy
- [ ] Interpolação 7 métodos funcionais
- [ ] Visualização 2D/3D renderiza
- [ ] Streaming sincroniza views
- [ ] Export funciona assíncrono
- [ ] Plugins carregam sem erro

### Qualidade

- [ ] Test coverage > 80%
- [ ] Zero warnings em pytest -W error
- [ ] Mypy passa com strict mode
- [ ] Logs estruturados em 100% das operações

---

## 22. Entrega Final

### Executáveis

- [ ] Windows: `.exe` installer
- [ ] macOS: `.app` bundle
- [ ] Linux: AppImage ou .deb

### Código

- [ ] Estrutura completa PyQt6
- [ ] Type hints 100%
- [ ] Docstrings Google style

### Recursos

- [ ] Icons compiled (.qrc)
- [ ] Styles (QSS light/dark)
- [ ] Splash screen

### Docs

- [ ] README.md
- [ ] User manual
- [ ] Developer guide
- [ ] API reference

---

## Apêndice A: Dependências

```toml
[project]
name = "platform-base"
version = "2.0.0"
dependencies = [
    "PyQt6>=6.5.0",
    "pyqtgraph>=0.13.0",
    "pyvista>=0.43.0",
    "pyvistaqt>=0.11.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "scipy>=1.10.0",
    "pydantic>=2.0.0",
    "pint>=0.21.0",
    "structlog>=23.1.0",
    "joblib>=1.2.0",
    "numba>=0.57.0",
    "pyarrow>=12.0.0",
    "openpyxl>=3.1.0",
    "h5py>=3.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.3.0",
    "pytest-qt>=4.2.0",
    "pytest-cov>=4.1.0",
    "hypothesis>=6.75.0",
    "black>=23.3.0",
    "isort>=5.12.0",
    "mypy>=1.3.0",
]
packaging = [
    "pyinstaller>=5.10.0",
]
video = [
    "opencv-python>=4.7.0",
    "moviepy>=1.0.3",
]
ml = [
    "scikit-learn>=1.2.0",
]
api = [
    "fastapi>=0.100.0",
    "uvicorn>=0.22.0",
]
```

---

## Apêndice B: Mapeamento Completo Dash → PyQt6

| Componente Dash | Equivalente PyQt6 | Arquivo |
|-----------------|-------------------|---------|
| `dash.Dash()` | `QApplication` | `desktop/app.py` |
| `html.Div` | `QWidget` | — |
| `dcc.Graph` | `pg.PlotWidget` / `QtInteractor` | `viz/plot_2d.py`, `viz/plot_3d.py` |
| `dcc.Interval` | `QTimer` | `viz/streaming.py` |
| `dcc.Store` | `SessionState` | `desktop/session_state.py` |
| `dash.callback` | `pyqtSignal` + `@pyqtSlot` | — |
| `callback Output` | Signal emit | — |
| `callback Input` | Signal connection | — |
| `callback State` | Property access | — |
| `prevent_initial_call` | Flag check in slot | — |
| `debounce` | `QTimer.singleShot` | — |
| `long_callback` | `QThread` + Worker | `desktop/workers/` |
| `dash.dcc.Loading` | `QProgressBar` | — |
| `callback_context` | `sender()` | — |
| `dcc.Dropdown` | `QComboBox` | — |
| `dcc.Slider` | `QSlider` | — |
| `dcc.DatePickerRange` | `QDateTimeEdit` × 2 | — |
| `dash_bootstrap_components` | `QSS` styling | `resources/styles/` |

---

**Versão:** 2.0.0 (PyQt6 Desktop)  
**Data:** 2025-01-19  
**Interface:** Desktop Nativa Multiplataforma  
**Status:** Especificação Completa para Migração
