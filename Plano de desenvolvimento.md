# SPEC/PRD Técnico Revisado — Platform Base v2.0

**Plataforma de Séries Temporais para Análise Exploratória de Dados de Sensores**

---

## 1. Objetivo do Produto

Desenvolver aplicação Python **Platform Base** para manipular e explorar séries temporais de sensores com timestamps irregulares. A aplicação permite:

- Upload e ingestão robusta multi-formato (CSV/Excel/Parquet/HDF5)
- Detecção automática de schema com validação rigorosa
- Normalização de unidades com rastreabilidade completa
- Interpolação com múltiplos métodos e tracking de proveniência
- Sincronização de múltiplas séries
- Cálculos matemáticos (derivadas 1ª-3ª ordem, integrais, áreas)
- Visualização exploratória 2D/3D com interatividade avançada
- Streaming temporal com sincronização multi-view
- Exportação e persistência de sessão
- Extensibilidade via plugins com isolamento e versionamento

**Não escopo:** análises de domínio específico, detecção de eventos, alarmes, diagnósticos.

---

## 2. Restrições e Requisitos Não-Funcionais

### 2.1 Performance

- Suportar datasets com milhões de pontos por série
- Operações vetorizadas (zero loops Python em hotpaths)
- Downsampling inteligente no render preservando features críticos
- Paralelismo configurável: `ProcessPoolExecutor` com pool size em config
- Numba obrigatório em hotspots identificados (não opcional)
- Cache multi-nível:
  - `lru_cache` para funções pequenas
  - `joblib.Memory` com TTL configurável para resultados grandes
- Profiling estruturado sempre ativo (overhead mínimo via logging)

### 2.2 Reprodutibilidade

- Metadata auditável em cada etapa: método/parâmetros/versão/seed/timestamp
- `is_interpolated_mask` com método usado por ponto
- Lineage tracking: séries derivadas rastreiam origem completa
- Versionamento de datasets (transformações geram versões derivadas)

### 2.3 Extensibilidade

- Plugins com Protocol/ABC validation
- Isolamento: plugin com bug não quebra app
- Discovery controlado (não importação automática arbitrária)
- Versionamento de compatibilidade plugin-core

### 2.4 Observabilidade

- Logging estruturado (JSON) em todos os módulos
- Error handling com contexto rico
- Validação de inputs com schemas explícitos

---

## 3. Stack Tecnológica

- Python 3.10+
- numpy, pandas, scipy
- pint (conversão de unidades)
- plotly (graph_objects)
- Dash (UI principal)
- joblib (cache + paralelismo)
- pydantic (validação de schemas)
- structlog (logging estruturado)
- fastapi (API REST opcional)

---

## 4. Estrutura de Projeto

```
platform_base/
├─ src/
│  ├─ core/
│  │  ├─ dataset_store.py
│  │  ├─ registry.py
│  │  ├─ orchestrator.py
│  │  └─ protocols.py          # ABC/Protocol definitions
│  ├─ io/                       # separado de core
│  │  ├─ loader.py
│  │  ├─ schema_detector.py
│  │  └─ validator.py
│  ├─ processing/
│  │  ├─ units.py
│  │  ├─ timebase.py
│  │  ├─ interpolation.py
│  │  ├─ synchronization.py
│  │  ├─ calculus.py
│  │  └─ smoothing.py          # filtros pré-derivadas
│  ├─ caching/
│  │  ├─ memory.py
│  │  └─ disk.py
│  ├─ viz/
│  │  ├─ base.py               # BaseFigure
│  │  ├─ config.py             # PlotConfig unificado
│  │  ├─ figures_2d.py
│  │  ├─ figures_3d.py
│  │  ├─ multipanel.py
│  │  ├─ heatmaps.py
│  │  ├─ state_cube.py
│  │  └─ streaming.py
│  ├─ ui/
│  │  ├─ app.py
│  │  ├─ layout.py
│  │  ├─ callbacks.py
│  │  ├─ context_menu.py
│  │  ├─ state.py
│  │  ├─ export.py
│  │  └─ selection.py          # data selection
│  ├─ api/                      # REST API
│  │  ├─ server.py
│  │  └─ endpoints.py
│  └─ utils/
│     ├─ ids.py
│     ├─ logging.py
│     ├─ serialization.py
│     ├─ errors.py             # error handling
│     └─ validation.py         # input validation
├─ plugins/
│  ├─ README.md
│  ├─ _base.py                 # base classes
│  └─ advanced_sync/           # DTW/TWED como plugins
├─ configs/
│  └─ platform.yaml            # consolidado hierárquico
├─ tests/
│  ├─ unit/
│  │  ├─ test_loader.py
│  │  ├─ test_interpolation.py
│  │  ├─ test_sync.py
│  │  ├─ test_calculus.py
│  │  ├─ test_registry.py
│  │  └─ test_context_menu.py
│  ├─ integration/
│  │  └─ test_pipeline.py
│  ├─ property/
│  │  └─ test_calculus_props.py
│  ├─ stress/
│  │  └─ test_large_datasets.py
│  └─ fixtures/
│     └─ synthetic_data.py     # gerador
├─ docs/
│  ├─ quickstart.md
│  ├─ api_reference.md
│  ├─ architecture.md
│  └─ examples/
├─ pyproject.toml
└─ README.md
```

---

## 5. Modelo de Dados e Contratos

### 5.1 DatasetStore

**Responsabilidades:**
- Armazenar datasets carregados
- Versionar séries derivadas com lineage completo
- Fornecer API consistente

**API:**
```python
add_dataset(dataset: Dataset) -> DatasetID
get_dataset(dataset_id: DatasetID) -> Dataset
list_datasets() -> list[DatasetSummary]

add_series(dataset_id: DatasetID, series: Series, lineage: Lineage) -> SeriesID
get_series(dataset_id: DatasetID, series_id: SeriesID) -> Series
list_series(dataset_id: DatasetID) -> list[SeriesSummary]

create_view(dataset_id: DatasetID, series_ids: list[SeriesID], 
            time_window: TimeWindow) -> ViewData
```

### 5.2 Dataset (Pydantic BaseModel)

```python
class Dataset(BaseModel):
    dataset_id: DatasetID
    version: int
    parent_id: Optional[DatasetID]
    source: SourceInfo  # structured, not dict
    t_seconds: np.ndarray
    t_datetime: np.ndarray
    series: dict[SeriesID, Series]
    metadata: DatasetMetadata  # structured
    created_at: datetime
```

### 5.3 Series (Pydantic BaseModel)

```python
class Series(BaseModel):
    series_id: SeriesID
    name: str
    unit: pint.Unit
    values: np.ndarray
    interpolation_info: InterpolationInfo  # per-point method tracking
    metadata: SeriesMetadata  # structured
    lineage: Lineage  # tracks origin chain
```

### 5.4 Lineage

```python
class Lineage(BaseModel):
    origin_series: list[SeriesID]
    operation: str
    parameters: dict
    timestamp: datetime
    version: str  # platform version
```

### 5.5 ViewData (formal type)

```python
class ViewData(BaseModel):
    dataset_id: DatasetID
    series: dict[SeriesID, np.ndarray]
    t_seconds: np.ndarray
    t_datetime: np.ndarray
    window: TimeWindow
```

### 5.6 DerivedResult (base class)

```python
class DerivedResult(BaseModel):
    """Base for InterpResult, CalcResult, SyncResult"""
    values: np.ndarray
    metadata: ResultMetadata
    quality_metrics: Optional[QualityMetrics]
    
class InterpResult(DerivedResult):
    interpolation_info: InterpolationInfo
    
class CalcResult(DerivedResult):
    operation: str
    order: Optional[int]
    
class SyncResult(DerivedResult):
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
def load(path: str, config: LoadConfig) -> Dataset:
    """
    - Detecta formato
    - Lê dados
    - Detecta schema (robust: pandas dtypes + heuristics)
    - Valida
    - Normaliza unidades (via pint)
    - Constrói Dataset e Series
    """
```

### 6.2 Detecção de Schema

```python
# io/schema_detector.py
class SchemaMap(BaseModel):
    timestamp_column: str
    candidate_series: list[SeriesCandidate]
    confidence: float
    
def detect_schema(df: pd.DataFrame, rules: SchemaRules) -> SchemaMap:
    """Usa tipos pandas + heurísticas robustas (não scores manuais)"""
```

### 6.3 Validação

```python
# io/validator.py
class ValidationReport(BaseModel):
    is_valid: bool
    warnings: list[ValidationWarning]
    errors: list[ValidationError]
    gaps: GapReport
    
def validate_time(df, schema) -> ValidationReport
def validate_values(df, schema) -> ValidationReport
def detect_gaps(t_seconds) -> GapReport
```

**Nunca rejeitar; sempre marcar e registrar.**

---

## 7. Interpolação

### 7.1 Interface Única

```python
# processing/interpolation.py
def interpolate(values, t_seconds, method: InterpMethod, 
                params: InterpParams) -> InterpResult:
    """
    Todos métodos retornam InterpResult com:
    - values_interp
    - interpolation_info (per-point: is_interpolated + method_used)
    - metadata (método, params, seed, timestamp)
    """
```

### 7.2 Métodos

**Core (sempre disponíveis):**
1. `linear`
2. `spline_cubic`
3. `smoothing_spline`
4. `resample_grid`

**Avançados (com graceful degradation):**
5. `mls` (Moving Least Squares)
6. `gpr` (Gaussian Process Regression)
7. `lomb_scargle_spectral`

**Plugins (stub se indisponível):**
8. `nn_interpolation` (plugin)
9. `continuous_time_model` (plugin)
10. `diffusion_conditioned` (plugin)

**Comportamento:**
- Erro claro se método indisponível: log estruturado + exception com mensagem indicando como habilitar
- **SEM fallback automático:** Se método falha, informar erro (não tentar outro)

---

## 8. Sincronização

### 8.1 Interface

```python
# processing/synchronization.py
def synchronize(series_dict, t_dict, method: SyncMethod, 
                params: SyncParams) -> SyncResult:
    """
    SyncResult inclui:
    - t_common
    - synced_series_dict
    - alignment_error (float)
    - confidence (float)
    - metadata
    """
```

### 8.2 Métodos

**Core:**
1. `common_grid_interpolate`
2. `kalman_align`

**Plugins:**
3. `dtw_align` (plugin em plugins/advanced_sync/)
4. `twed_align` (plugin)
5. `statistical_warping` (plugin)
6. `deep_warping` (plugin)

---

## 9. Cálculos Matemáticos

### 9.1 Derivadas

```python
# processing/calculus.py
def derivative(values, t, order: int, method: DerivMethod, 
               params: DerivParams, 
               smoothing: Optional[SmoothingConfig] = None) -> CalcResult:
    """
    - Valida order: 1 <= order <= 3, senão raise ValueError
    - Smoothing é OPCIONAL (usuário decide se aplicar pré-filtro)
    - Métodos: finite_diff, savitzky_golay, spline_derivative
    - Retorna série completa (mesmo comprimento)
    """
```

### 9.2 Integrais

```python
def integral(values, t, method="trapezoid") -> CalcResult
```

### 9.3 Área entre curvas

```python
def area_between(series_upper: np.ndarray, 
                 series_lower: np.ndarray, 
                 t: np.ndarray) -> CalcResult:
    """
    Pares como parâmetro direto (não via config externa).
    """
```

### 9.4 Suavização

```python
# processing/smoothing.py
def smooth(values, method: SmoothMethod, params: SmoothParams) -> np.ndarray:
    """
    Métodos: savitzky_golay, gaussian, median, lowpass
    Usuário decide quando aplicar (não automático).
    """
```

---

## 10. Visualização (Plotly)

### 10.1 Abstração Base

```python
# viz/base.py
class BaseFigure(ABC):
    def __init__(self, config: PlotConfig):
        self.config = config
    
    @abstractmethod
    def render(self, data) -> go.Figure:
        pass
```

### 10.2 Config Unificado

```python
# viz/config.py
class PlotConfig(BaseModel):
    title: str
    axes: AxisConfig
    colors: ColorScheme
    downsample: DownsampleStrategy
    interactive: InteractivityConfig
```

### 10.3 Implementações

```python
# viz/figures_2d.py
class TimeseriesPlot(BaseFigure):
    def render(self, view_data: ViewData) -> go.Figure
    
class MultipanelPlot(BaseFigure):
    def render(self, panel_spec: PanelSpec) -> go.Figure

# viz/figures_3d.py
class Trajectory3D(BaseFigure):
    def render(self, points_3d) -> go.Figure

# viz/heatmaps.py
class StateHeatmap(BaseFigure):
    def render(self, matrix, axes) -> go.Figure

# viz/state_cube.py
class StateCube3D(BaseFigure):
    def render(self, states) -> go.Figure
```

### 10.4 Downsampling Strategy

```python
class DownsampleStrategy(BaseModel):
    method: Literal["lttb", "minmax", "adaptive"]
    max_points: int
    preserve_features: list[FeatureType]  # peaks, valleys, edges
```

### 10.5 Menu Contextual (IMPLEMENTADO)

```python
# ui/context_menu.py
class ContextMenu:
    actions: list[MenuAction]
    
    def show(self, event: ClickEvent) -> None
    def execute_action(self, action: MenuAction, context: SelectionContext) -> None

# Ações implementadas:
- zoom/pan/reset
- selecionar região/pontos
- extrair subsérie
- filtros visuais
- exportar seleção
- anotar
- comparar séries
- estatísticas em seleção
- operações via registry
```

---

## 11. Streaming Temporal

### 11.1 Estado de Streaming (NÃO global)

```python
# viz/streaming.py
class StreamingState(BaseModel):
    """Instância por sessão, não singleton global"""
    play_state: PlayState
    current_time_index: int
    speed: float
    window_size: timedelta
    loop: bool
    filters: StreamFilters

class StreamingEngine:
    def __init__(self, state: StreamingState):
        self.state = state
    
    def tick(self) -> TickUpdate
    def sync_views(self, views: list[ViewID]) -> None
```

### 11.2 Filters no Streaming (DETALHADO)

```python
class StreamFilters(BaseModel):
    # 1) Filtros temporais
    time_include: Optional[list[TimeInterval]]
    time_exclude: Optional[list[TimeInterval]]
    
    # 2) Filtros de amostragem
    max_points_per_window: int
    downsample_method: Literal["lttb", "minmax", "adaptive"]
    
    # 3) Filtros de qualidade
    hide_interpolated: bool
    hide_nan: bool
    quality_threshold: Optional[float]
    
    # 4) Filtros de valor
    value_predicates: dict[SeriesID, ValuePredicate]
    
    # 5) Filtros visuais (render-only)
    visual_smoothing: Optional[SmoothConfig]
    hidden_series: list[SeriesID]
    scale_override: Optional[ScaleConfig]
```

**Filters operam em duas fases:**
1. **Elegibilidade:** determina quais timestamps entram no playback
2. **Render:** downsampling/ocultação na janela atual

#### Descrição Detalhada dos Filtros

**1) Filtros Temporais (time filters)**

Definem quais intervalos de tempo serão reproduzidos.

- Incluir apenas um intervalo: 2026-01-10 08:00 → 2026-01-10 12:00
- Excluir intervalos: pular paradas, manutenção, períodos sem operação
- Lista de janelas: reproduzir somente "trechos de interesse"

Efeito: o streaming "pula" automaticamente os períodos filtrados.

**2) Filtros de Amostragem (sampling / decimation)**

Controlam quantos pontos entram no render para manter fluidez.

- Downsample por limite de pontos por janela (ex.: máximo 50k pontos)
- Downsample adaptativo por densidade de pixels (ex.: 1 ponto por pixel no eixo X)
- Agregação por bin (min/max/mean por intervalo)

Efeito: visualização continua suave mesmo com milhões de pontos.

**3) Filtros de Qualidade de Dado (data quality)**

Usam flags do próprio pipeline:

- Remover/ocultar pontos interpolados (`is_interpolated_mask`)
- Remover NaNs/outliers marcados
- Aplicar "somente dados válidos" conforme relatório de validação

Efeito: o streaming pode mostrar apenas pontos "confiáveis" ou destacar o que é imputado.

**4) Filtros de Valor/Condição (value-based)**

Seleção baseada em condições:

- Reproduzir somente quando P > limite
- Reproduzir somente quando Q estiver dentro de faixa
- Reproduzir apenas transições (ex.: mudanças acima de um delta mínimo)

Efeito: útil para exploração, mas deve ser tratado com cuidado para não "distorcer" a percepção temporal.

**5) Filtros Visuais (render-only)**

Não mudam o dataset do streaming, apenas o que é desenhado:

- Suavização apenas para exibição
- Ocultar séries
- Mudar escala/normalização apenas no plot

Efeito: mantém a reprodução fiel, mas melhora legibilidade.

#### Como Filters se Encaixam no Motor de Streaming

```
1. Dataset completo (tudo que foi carregado e processado)
2. Aplicar filters → cria um índice elegível (subconjunto ordenado dos timestamps)
3. O streaming percorre esse índice e, a cada tick, recorta a janela deslizante
4. (Opcional) aplica downsampling na janela para renderizar
5. Atualiza as views 2D/3D sincronizadas
```

#### Recomendações de Implementação

- Separar "filters" em duas categorias:
  - Filters de elegibilidade do playback (mudam quais timestamps são percorridos)
  - Filters de render (downsampling/ocultação/estilo)
- Sempre manter rastreabilidade: registrar quais filters estavam ativos durante o streaming e export

### 11.3 Sincronização Multi-View

```python
# ui/state.py
class AppState:
    streaming_engines: dict[SessionID, StreamingEngine]
    view_subscriptions: dict[ViewID, SessionID]
    
def sync_callback(session_id: SessionID):
    """
    Chamado a cada tick:
    1. Atualiza current_time_index no StreamingEngine
    2. Notifica todas views subscritas via Dash callback
    3. Views recalculam janela e re-renderizam
    """
```

### 11.4 Exportar Vídeo

```python
# viz/streaming.py
class VideoExporter:
    def __init__(self, library: Literal["opencv", "moviepy"]):
        self.library = library
    
    def export(self, streaming_session, output_path: Path, 
               fps: int, resolution: tuple[int, int]) -> None:
        """Usa opencv-python ou moviepy (configurável)"""
```

---

## 12. UI (Dash)

### 12.1 Layout Responsivo e Configurável

```python
# ui/layout.py
class LayoutConfig(BaseModel):
    areas: list[PanelConfig]  # não fixo em 4
    responsive: bool
    breakpoints: dict[str, int]  # mobile, tablet, desktop

def build_layout(config: LayoutConfig) -> html.Div:
    """
    Áreas configuráveis:
    - DataPanel (upload + datasets + series)
    - VizPanel (2D/3D/heatmap/cube)
    - ConfigPanel (métodos + streaming + perf)
    - ResultsPanel (tabelas + logs + export)
    
    Suporta mobile/diferentes resoluções via dash-bootstrap-components.
    """
```

### 12.2 Callbacks com Debouncing

```python
# ui/callbacks.py
from dash import callback, Input, Output, State
from dash.long_callback import DiskcacheLongCallbackManager

# Debouncing para inputs rápidos
@callback(
    Output(...),
    Input(...),
    prevent_initial_call=True,
    debounce=300  # ms
)

# Async para operações pesadas
@callback(
    Output(...),
    Input(...),
    background=True,
    manager=DiskcacheLongCallbackManager(...)
)
```

### 12.3 State Management Consolidado

```python
# ui/state.py
class AppState:
    """Estado centralizado da aplicação"""
    datasets: DatasetStore
    streaming_sessions: dict[SessionID, StreamingEngine]
    ui_selections: dict[ViewID, Selection]
    cache: CacheManager
    
# Sincronização:
# Dash Store (client) <-> AppState (server) <-> DatasetStore (persistence)
```

### 12.4 Export Assíncrono

```python
# ui/export.py
@callback(
    Output("export-status"),
    Input("export-button"),
    background=True
)
def export_large_dataset(selection, format):
    """
    Grandes exports rodam em background.
    UI mostra progress bar.
    """
```

---

## 13. Data Selection

```python
# ui/selection.py
class Selection(BaseModel):
    """3 métodos de seleção de dados"""
    
    # Método 1: Temporal (range)
    time_range: Optional[TimeInterval]
    
    # Método 2: Interativo (clique/arrasto no gráfico)
    interactive_points: Optional[list[int]]  # índices
    
    # Método 3: Condicional (query-like)
    predicates: Optional[list[Predicate]]
    # Ex: [Predicate(series="temp", op=">", value=100)]
    
    # Combinação (AND/OR)
    combination: Literal["and", "or"]

def apply_selection(data: ViewData, selection: Selection) -> ViewData:
    """Filtra ViewData conforme seleção"""
```

**Alternativas propostas:**
1. **Range temporal:** slider duplo ou datetime pickers
2. **Interativo:** brush selection no gráfico Plotly
3. **Condicional:** builder de queries na UI (tipo filter builder)

---

## 14. Registry + Orchestrator + Plugins

### 14.1 Protocol/ABC para Plugins

```python
# core/protocols.py
from abc import ABC, abstractmethod
from typing import Protocol

class PluginProtocol(Protocol):
    """Validação de interface via Protocol"""
    PLUGIN_ID: str
    VERSION: str
    
    def get_manifest(self) -> PluginManifest
    def validate_inputs(self, context: PluginContext) -> ValidationResult
    def execute(self, context: PluginContext, params: dict) -> PluginResult

class BasePlugin(ABC):
    """Classe base opcional para herança"""
    @abstractmethod
    def execute(self, context, params):
        pass
```

### 14.2 Registry com Validação

```python
# core/registry.py
class PluginRegistry:
    plugins: dict[str, PluginProtocol]
    
    def register(self, plugin: PluginProtocol) -> None:
        """Valida que plugin implementa Protocol"""
        if not isinstance(plugin, PluginProtocol):
            raise PluginInterfaceError(...)
        
        # Valida compatibilidade de versão
        if not self._check_compatibility(plugin.VERSION):
            raise PluginVersionError(...)
        
        self.plugins[plugin.PLUGIN_ID] = plugin
    
    def discover_plugins(self, path: Path) -> None:
        """
        Discovery controlado (não importação arbitrária):
        1. Lê manifest.json de cada subdiretório
        2. Valida schema do manifest
        3. Só então importa módulo
        4. Sandbox: executa em subprocess se flag ativada
        """
```

### 14.3 Plugin Manifest Schema

```python
# Pydantic schema, não dict livre
class PluginManifest(BaseModel):
    plugin_id: str
    version: str
    core_min_version: str
    core_max_version: Optional[str]
    requires: list[str]  # dependências de outros plugins
    produces: list[str]  # outputs
    entry_point: str
```

### 14.4 Orchestrator com DAG

```python
# core/orchestrator.py
class Orchestrator:
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.dag = DependencyGraph()
    
    def execute_pipeline(self, operations: list[OpSpec]) -> PipelineResult:
        """
        1. Resolve dependências (topological sort)
        2. Valida inputs de cada op
        3. Executa em ordem
        4. Propaga outputs para próxima op
        5. Armazena resultados no DatasetStore
        6. Log estruturado de execução
        """
```

### 14.5 Isolamento de Plugins

```python
class IsolatedPluginRunner:
    """Executa plugin em subprocess para isolamento"""
    def run(self, plugin_id, context, params, timeout=60):
        proc = subprocess.Popen(...)
        result, error = proc.communicate(timeout=timeout)
        if proc.returncode != 0:
            raise PluginExecutionError(error)
        return result
```

---

## 15. Configuração Consolidada

```yaml
# configs/platform.yaml (estrutura hierárquica)
platform:
  version: "2.0.0"
  
data:
  schema_detection:
    timestamp_patterns: 
      - "timestamp"
      - "time"
      - "datetime"
      - "date"
    heuristics:
      - monotonic_increasing
      - datetime_type
      - unix_epoch_range
  units:
    # Usa pint, não conversões hard-coded
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
    max_workers: 4  # configurável
  cache:
    disk:
      enabled: true
      ttl_hours: 24  # TTL configurável
      max_size_gb: 10
      path: ".cache"
    memory:
      enabled: true
      max_items: 1000
  profiling:
    enabled: true
    log_level: "INFO"
    output_path: "profiling/"
  numba:
    enabled: true
    cache: true
    
visualization:
  downsampling:
    method: "lttb"
    max_points: 10000
    preserve_features: 
      - peaks
      - valleys
      - edges
  defaults:
    theme: "plotly_white"
    height: 600
    width: 1000
  interactive:
    context_menu: true
    annotations: true
    
streaming:
  default_speed: 1.0
  window_size_seconds: 60
  filters:
    max_points_per_window: 5000
    hide_interpolated_default: false
  video_export:
    library: "opencv"  # ou "moviepy"
    default_fps: 30
    default_resolution: [1920, 1080]
    
ui:
  layout:
    responsive: true
    breakpoints:
      mobile: 768
      tablet: 1024
      desktop: 1440
    default_areas:
      - name: "data"
        position: "left"
        width: 0.25
      - name: "viz"
        position: "center"
        width: 0.50
      - name: "config"
        position: "right"
        width: 0.25
  export:
    async_threshold_mb: 10
    chunk_size_mb: 50
    
plugins:
  discovery:
    enabled: true
    path: "plugins/"
    isolation: false  # true = subprocess
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
  enabled: false  # REST API opcional
  host: "127.0.0.1"
  port: 8000
  cors:
    enabled: true
    origins: ["*"]
```

---

## 16. Exportação

### 16.1 Seleção + Export

```python
# ui/export.py
def export_selection(selection: Selection, format: ExportFormat, 
                     output_path: Path) -> ExportResult:
    """
    Formatos: CSV, XLSX, Parquet, HDF5
    
    Se tamanho > threshold (config):
    - Roda em background
    - Export incremental (chunks)
    - Progress bar na UI
    """
```

### 16.2 Sessão (não salvar datasets completos)

```python
def export_session(output_path: Path) -> None:
    """
    Salva:
    - Config usada
    - Seleções
    - Anotações
    - Referências a datasets (paths, não dados)
    - Estado de visualizações
    
    NÃO salva: dados brutos (apenas referência)
    """
```

### 16.3 Export Incremental

```python
def export_large_dataset(dataset_id: DatasetID, 
                        output_path: Path,
                        chunk_size_mb: int = 50) -> Iterator[ExportProgress]:
    """
    Generator que exporta em chunks.
    Yield progress para update de UI.
    """
```

---

## 17. Testes

### 17.1 Unit Tests

```python
# tests/unit/
test_loader.py              # multi-formato
test_interpolation.py       # todos métodos
test_sync.py                # métodos core + plugins
test_calculus.py            # derivadas/integrais
test_registry.py            # plugin registration/validation
test_context_menu.py        # ações do menu
test_smoothing.py           # filtros pré-derivadas
test_units.py               # conversões pint
test_schema_detector.py     # detecção robusta
```

### 17.2 Integration Tests

```python
# tests/integration/
test_pipeline.py
"""
Testa pipeline completo:
1. Load CSV
2. Detect schema
3. Validate data
4. Interpolate gaps
5. Synchronize series
6. Compute derivative
7. Visualize
8. Export
"""
```

### 17.3 Property-Based Tests

```python
# tests/property/
test_calculus_props.py
"""
Propriedades matemáticas:
- derivative(integral(f)) ≈ f
- derivative é linear: d(af + bg) = a*df + b*dg
- spline interpolation passa por pontos originais
- integral de constante = constante * intervalo
"""
```

### 17.4 Stress Tests

```python
# tests/stress/
test_large_datasets.py
"""
- 10M pontos por série
- 100 séries simultâneas
- Interpolação + derivadas + plot
- Validar: tempo < threshold, memória < limit
"""
```

### 17.5 UI Tests (automatizados)

```python
# tests/ui/
test_ui_smoke.py (via dash.testing)
"""
- Subir app
- Upload dataset
- Selecionar série
- Plotar 2D/3D
- Aplicar streaming
- Exportar
- Validar: figura renderizada sem crash
"""
```

---

## 18. Logging e Error Handling

### 18.1 Logging Estruturado

```python
# utils/logging.py
import structlog

logger = structlog.get_logger()

# Uso:
logger.info("dataset_loaded", 
            dataset_id=dataset_id,
            n_series=len(series),
            n_points=len(t_seconds),
            duration_sec=elapsed)

logger.error("interpolation_failed",
             method=method,
             series_id=series_id,
             error=str(e),
             traceback=traceback.format_exc())
```

### 18.2 Error Handling

```python
# utils/errors.py
class PlatformError(Exception):
    """Base para todas exceptions"""
    def __init__(self, message: str, context: dict):
        self.message = message
        self.context = context
        super().__init__(message)

class DataLoadError(PlatformError): pass
class SchemaDetectionError(PlatformError): pass
class ValidationError(PlatformError): pass
class InterpolationError(PlatformError): pass
class CalculusError(PlatformError): pass
class PluginError(PlatformError): pass
class ExportError(PlatformError): pass

# Error handler global registra em log estruturado
def handle_error(error: PlatformError) -> None:
    logger.error(
        "platform_error",
        error_type=type(error).__name__,
        message=error.message,
        context=error.context
    )
```

### 18.3 Input Validation

```python
# utils/validation.py (usa Pydantic)
def validate_config(config_dict: dict, schema: Type[BaseModel]) -> BaseModel:
    """
    Valida config contra schema Pydantic.
    Retorna objeto validado ou raise ValidationError com detalhes.
    """
    try:
        return schema(**config_dict)
    except pydantic.ValidationError as e:
        logger.error("config_validation_failed", errors=e.errors())
        raise
```

---

## 19. API REST (Opcional)

```python
# api/server.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Platform Base API", version="2.0.0")

# CORS se habilitado
if config.api.cors.enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors.origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload e processa dataset"""
    ...

@app.get("/datasets")
def list_datasets():
    """Lista datasets carregados"""
    ...

@app.get("/datasets/{dataset_id}/series")
def list_series(dataset_id: str):
    """Lista séries de um dataset"""
    ...

@app.post("/datasets/{dataset_id}/series/{series_id}/interpolate")
def interpolate_series(
    dataset_id: str, 
    series_id: str, 
    request: InterpolationRequest
):
    """Aplica interpolação"""
    ...

@app.post("/datasets/{dataset_id}/view")
def create_view(dataset_id: str, request: ViewRequest):
    """Cria view para visualização"""
    ...

# Habilitado via config.api.enabled
```

---

## 20. Documentação

### 20.1 README.md (Estruturado)

```markdown
# Platform Base v2.0

**Plataforma de análise exploratória para séries temporais irregulares**

## Quickstart

### Instalação
```bash
pip install platform-base
```

### Exemplo Básico
```python
from platform_base import load_dataset, interpolate, plot

# Carregar dados
dataset = load_dataset("sensor_data.csv")

# Interpolar gaps
series_interp = interpolate(dataset, method="spline_cubic")

# Visualizar
plot(series_interp, type="2d")
```

## Features

- ✅ Upload multi-formato (CSV/Excel/Parquet/HDF5)
- ✅ 10 métodos de interpolação (linear a deep learning)
- ✅ Sincronização de múltiplas séries temporais
- ✅ Cálculos matemáticos (derivadas 1ª-3ª, integrais, áreas)
- ✅ Visualização 2D/3D interativa
- ✅ Streaming temporal com filtros avançados
- ✅ Extensibilidade via plugins
- ✅ Export para múltiplos formatos

## Documentation

- [Quickstart Guide](docs/quickstart.md)
- [API Reference](docs/api_reference.md)
- [Architecture](docs/architecture.md)
- [Plugin Development](docs/plugin_development.md)
- [Examples](docs/examples/)

## Development

### Setup
```bash
git clone https://github.com/org/platform-base
cd platform-base
pip install -e ".[dev]"
```

### Testes
```bash
pytest tests/
```

### Coverage
```bash
pytest --cov=src/
```

## Contributing

Ver [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT
```

### 20.2 Gerador de Dados Sintéticos

```python
# tests/fixtures/synthetic_data.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class SyntheticDataGenerator:
    def generate_timeseries(
        self,
        n_points: int,
        n_series: int,
        irregularity: float,  # 0-1
        noise: float,
        gaps: list[tuple[int, int]],  # [(start, end), ...]
        seed: int = 42
    ) -> pd.DataFrame:
        """
        Gera dados sintéticos para testes.
        
        Args:
            n_points: número de pontos temporais
            n_series: número de séries
            irregularity: 0=regular, 1=muito irregular
            noise: desvio padrão do ruído
            gaps: lista de (início, fim) de gaps
            seed: seed para reprodutibilidade
            
        Returns:
            DataFrame com timestamp + n_series colunas
        """
        np.random.seed(seed)
        
        # Timestamps irregulares
        if irregularity > 0:
            deltas = np.random.exponential(1.0/irregularity, n_points)
            t = np.cumsum(deltas)
        else:
            t = np.linspace(0, n_points, n_points)
        
        timestamps = [datetime(2024, 1, 1) + timedelta(seconds=s) for s in t]
        
        # Séries com ruído
        data = {}
        for i in range(n_series):
            signal = np.sin(2 * np.pi * t / (n_points/10))  # sinal base
            signal += np.random.normal(0, noise, n_points)
            data[f"series_{i}"] = signal
        
        df = pd.DataFrame(data, index=timestamps)
        df.index.name = "timestamp"
        
        # Inserir gaps
        for start, end in gaps:
            df.iloc[start:end] = np.nan
        
        return df.reset_index()
```

---

## 21. Plano de Implementação Iterativo

### Fase 1: Core + Config (2 semanas)
1. Setup projeto + estrutura de diretórios
2. Config consolidado YAML + validação Pydantic
3. Logging estruturado (structlog)
4. Error handling (PlatformError hierarchy)
5. DatasetStore + Lineage + Versionamento
6. Protocols/ABC para plugins

**Entregável:** Skeleton funcional com logging e config

### Fase 2: I/O + Data (2 semanas)
7. Loader multi-formato (CSV/Excel/Parquet/HDF5)
8. Schema detection robusto (pandas dtypes + heuristics)
9. Validação completa (time/values/gaps)
10. Units (pint integration)
11. Dados sintéticos (SyntheticDataGenerator)

**Entregável:** Carga de dados funcionando end-to-end

### Fase 3: Processing Core (2 semanas)
12. Timebase operations
13. Interpolação (4 métodos core: linear, spline, smoothing, resample)
14. Smoothing (separado, opcional)
15. Sincronização (2 métodos core: common_grid, kalman)

**Entregável:** Processamento básico operacional

### Fase 4: Calculus (1 semana)
16. Derivadas 1-3 ordem (finite_diff, savitzky_golay, spline)
17. Integrais (trapezoid)
18. Area between (parâmetros diretos)
19. Property-based tests

**Entregável:** Cálculos matemáticos validados

### Fase 5: Registry + Orchestrator (1 semana)
20. PluginRegistry com validação Protocol
21. Orchestrator com DAG
22. Plugin discovery controlado
23. Isolamento (subprocess optional)
24. PluginManifest schema

**Entregável:** Sistema de plugins funcional

### Fase 6: Visualização Base (2 semanas)
25. BaseFigure abstraction + PlotConfig
26. Figures 2D (timeseries, multipanel)
27. Figures 3D (trajectory, cube)
28. Heatmaps
29. Downsampling inteligente (LTTB, preserve features)
30. Context menu implementado

**Entregável:** Visualizações básicas funcionais

### Fase 7: Streaming (1 semana)
31. StreamingEngine (não global, por sessão)
32. StreamFilters detalhados (5 tipos)
33. Sincronização multi-view
34. Video export (opencv/moviepy)

**Entregável:** Streaming temporal completo

### Fase 8: UI (2 semanas)
35. Layout responsivo configurável (dash-bootstrap)
36. Callbacks com debouncing
37. State management consolidado
38. Data selection (3 métodos: temporal/interativo/condicional)
39. Export assíncrono
40. UI smoke tests

**Entregável:** Interface completa e responsiva

### Fase 9: Plugins Avançados (1 semana)
41. DTW/TWED/warping como plugins
42. Interpolação avançada (GPR/MLS/neural) como plugins
43. Template de plugin + documentação

**Entregável:** Exemplos de plugins avançados

### Fase 10: Cache + Performance (1 semana)
44. Cache multi-nível (memory + disk com TTL)
45. Paralelismo (ProcessPoolExecutor configurável)
46. Numba optimization obrigatória
47. Profiling integrado
48. Stress tests

**Entregável:** Sistema otimizado

### Fase 11: Testes + Docs (1 semana)
49. Completar unit tests (>80% coverage)
50. Integration tests
51. Property-based tests
52. README estruturado
53. API documentation
54. Examples/tutorials

**Entregável:** Documentação completa

### Fase 12: Opcional (1 semana)
55. API REST (FastAPI)
56. Optimizações finais baseadas em profiling
57. Docker image

**Entregável:** Recursos opcionais

**Total: ~15 semanas**

---

## 22. Critérios de Aceitação (Mensuráveis)

### Funcional
- [ ] Upload de CSV/Excel/Parquet/HDF5 completa sem erro para dataset de 1M pontos
- [ ] Schema detectado automaticamente com >95% acurácia em 100 datasets sintéticos variados
- [ ] 4 métodos de interpolação core executam sem erro e retornam InterpResult válido
- [ ] Derivadas ordem 1-3 retornam série completa (length = input length) para todos métodos
- [ ] Integral(derivative(f)) ≈ f com erro < 1% (property test)
- [ ] Visualização 2D renderiza com <500ms para 100k pontos (com downsampling)
- [ ] Visualização 3D renderiza com <1s para 50k pontos
- [ ] Streaming sincroniza 3+ views simultaneamente sem dessincronização > 100ms
- [ ] Context menu executa todas ações sem erro
- [ ] Export assíncrono de 10MB completa sem travar UI (<2s response time)

### Performance
- [ ] 1M pontos: load + schema detection < 3s
- [ ] 1M pontos: interpolação linear < 2s
- [ ] 1M pontos: interpolação spline < 5s
- [ ] 1M pontos: derivada 1ª ordem < 1s
- [ ] 10M pontos: load + plot (com downsampling) < 10s
- [ ] Cache hit rate > 80% em workflow típico (load → interp → deriv → plot × 3)
- [ ] Memória: processar 10M pontos com <2GB RAM

### Qualidade
- [ ] Cobertura de testes > 80% (unit + integration)
- [ ] Property tests passam com 1000 exemplos gerados
- [ ] Stress test com 10M pontos completa sem crash ou memory leak
- [ ] Stress test com 100 séries simultâneas completa sem degradação > 2x
- [ ] Logs estruturados (JSON) em 100% das operações principais
- [ ] Zero warnings em pytest com -W error
- [ ] Mypy passa com strict mode

### Extensibilidade
- [ ] Plugin pode ser adicionado criando arquivo em plugins/ sem modificar core
- [ ] Registry valida interface Protocol em tempo de registro
- [ ] Plugin com erro não quebra app (isolamento funciona)
- [ ] Plugin com manifest inválido é rejeitado com mensagem clara
- [ ] Plugin avançado (DTW) executa via registry sem código especial

### Usabilidade
- [ ] README permite usuário executar exemplo em <5min
- [ ] Erro de schema detection mostra sugestões de correção
- [ ] Erro de interpolação indisponível mostra como instalar dependência
- [ ] Export session e reload restaura estado completo
- [ ] UI responsiva funciona em mobile (>768px) sem quebrar

### Reprodutibilidade
- [ ] Mesma config + mesmos dados → resultados bit-identical
- [ ] Lineage completo de série derivada rastreável até origem
- [ ] Export session contém metadata suficiente para reproduzir
- [ ] Logs contém timestamp/versão/config para auditoria

---

## 23. Entrega Final

### Código
- [ ] Estrutura completa conforme seção 4
- [ ] Todos módulos com docstrings
- [ ] Type hints em 100% das funções públicas
- [ ] Code style: black + isort + flake8

### Configuração
- [ ] `configs/platform.yaml` consolidado e documentado
- [ ] Validação Pydantic para toda config
- [ ] Exemplos de configs em `configs/examples/`

### Testes
- [ ] Suite completa: unit/integration/property/stress
- [ ] Fixtures e dados sintéticos
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Coverage report

### Documentação
- [ ] README.md estruturado (quickstart/features/docs/dev)
- [ ] `docs/quickstart.md`
- [ ] `docs/api_reference.md` (auto-gerado via sphinx)
- [ ] `docs/architecture.md`
- [ ] `docs/plugin_development.md`
- [ ] `docs/examples/` com 5+ notebooks Jupyter

### Deployment
- [ ] PyPI package
- [ ] Docker image (opcional)
- [ ] Requirements pinned (requirements.txt + pyproject.toml)

### Extras
- [ ] Changelog (CHANGELOG.md)
- [ ] Contributing guide (CONTRIBUTING.md)
- [ ] License (LICENSE)
- [ ] Code of conduct (CODE_OF_CONDUCT.md)

---

## Apêndice A: Dependências Python

```toml
# pyproject.toml
[project]
name = "platform-base"
version = "2.0.0"
dependencies = [
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "scipy>=1.10.0",
    "plotly>=5.14.0",
    "dash>=2.9.0",
    "dash-bootstrap-components>=1.4.0",
    "pydantic>=2.0.0",
    "pint>=0.21.0",
    "structlog>=23.1.0",
    "joblib>=1.2.0",
    "numba>=0.57.0",
    "pyarrow>=12.0.0",  # Parquet
    "openpyxl>=3.1.0",  # Excel
    "h5py>=3.8.0",      # HDF5
    "fastapi>=0.100.0",  # API REST
    "uvicorn>=0.22.0",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.3.0",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.3.0",
    "hypothesis>=6.75.0",
    "black>=23.3.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.3.0",
    "sphinx>=6.2.0",
    "sphinx-rtd-theme>=1.2.0",
]
viz = [
    "opencv-python>=4.7.0",
    "moviepy>=1.0.3",
]
ml = [
    "scikit-learn>=1.2.0",
    "torch>=2.0.0",
]
```

---

## Apêndice B: Glossário Técnico

**Dataset**: Conjunto de séries temporais compartilhando mesma base temporal

**Series**: Sequência de valores com timestamps associados

**Lineage**: Rastreamento de origem de séries derivadas

**Interpolation**: Estimação de valores em timestamps não observados

**Synchronization**: Alinhamento de múltiplas séries em base temporal comum

**Downsampling**: Redução de pontos para visualização mantendo features

**Streaming**: Reprodução temporal de dados históricos como animação

**Plugin**: Módulo extensível registrado via Registry

**ViewData**: Subset de dados preparado para visualização

**TimeWindow**: Intervalo temporal para análise/visualização

**DerivedResult**: Resultado de operação matemática sobre série

---

## Apêndice C: Convenções de Código

### Naming
- Classes: `PascalCase`
- Funções/métodos: `snake_case`
- Constantes: `UPPER_SNAKE_CASE`
- Private: prefixo `_`

### Docstrings
```python
def interpolate(values: np.ndarray, t: np.ndarray, 
                method: str, params: dict) -> InterpResult:
    """
    Interpola valores em timestamps irregulares.
    
    Args:
        values: Array de valores observados
        t: Array de timestamps (segundos)
        method: Método de interpolação ('linear', 'spline_cubic', ...)
        params: Parâmetros específicos do método
        
    Returns:
        InterpResult com valores interpolados e metadata
        
    Raises:
        InterpolationError: Se método não disponível ou params inválidos
        
    Example:
        >>> result = interpolate(values, t, 'linear', {})
        >>> result.values.shape == values.shape
        True
    """
```

### Type Hints
```python
from typing import Optional, Union, Literal
from numpy.typing import NDArray

def process(data: NDArray[np.float64], 
            mode: Literal["fast", "accurate"] = "fast",
            threshold: Optional[float] = None) -> tuple[NDArray, dict]:
    ...
```

---

**Versão:** 2.0.0  
**Data:** 2025-01-19  
**Autores:** Platform Base Team  
**Status:** Final Specification
