# Platform Base v2.0

**Plataforma de Análise Exploratória para Séries Temporais Irregulares**

---

## A) Visão Geral

**Platform Base** é uma plataforma desktop PyQt6 especializada em análise exploratória de séries temporais irregulares provenientes de sensores industriais. O sistema foi projetado para lidar com dados de amostragem não-uniforme, gaps temporais e múltiplas séries dessincronizadas, oferecendo ferramentas robustas de interpolação, sincronização, cálculo matemático e visualização interativa.

**Público-Alvo:** Engenheiros de processos, analistas de dados e pesquisadores que trabalham com dados de sensores industriais (TRANSPETRO e similar), especialmente em cenários onde sensores apresentam taxas de amostragem variáveis, períodos de inatividade ou falhas intermitentes.

**Problema Resolvido:** Análise tradicional de séries temporais assume dados regularmente espaçados. Platform Base preenche a lacuna ao fornecer:
- Detecção automática de esquema temporal em arquivos heterogêneos
- Interpolação avançada preservando características físicas dos sinais
- Sincronização de múltiplas séries em grid temporal comum
- Visualização e processamento em tempo de execução (streaming temporal)
- Extensibilidade via plugins isolados para métodos customizados

**Versão:** 2.0.0 (`pyproject.toml`)  
**Tecnologias Core:** Python ≥3.10, PyQt6 ≥6.5.0, NumPy, Pandas, SciPy, PyQtGraph, PyVista

---

## B) Principais Funcionalidades

### Carregamento de Dados Multi-Formato
- **Suporte a:** CSV, Excel (xlsx/xls), Parquet, HDF5 (`src/platform_base/io/loader.py`)
- **Detecção automática de esquema:** Identifica colunas temporais via heurísticas configuráveis (`src/platform_base/io/schema_detector.py`)
- **Validação de integridade:** Detecta gaps, outliers e problemas de monotonicidade (`src/platform_base/io/validator.py`)
- **Loading assíncrono:** Workers em QThread para interface responsiva (`src/platform_base/ui/workers/file_worker.py`, `src/platform_base/desktop/workers/base_worker.py`)

### Interpolação Avançada (10 Métodos)
- **Métodos disponíveis** (`src/platform_base/processing/interpolation.py`):
  - `linear`: Interpolação linear básica
  - `spline_cubic`: Spline cúbica suave
  - `smoothing_spline`: Spline com controle de suavização
  - `resample_grid`: Reamostragem em grid uniforme
  - `mls`: Moving Least Squares (polinomial local ponderado)
  - `gpr`: Gaussian Process Regression (interpolação probabilística)
  - `lomb_scargle_spectral`: Interpolação espectral para dados irregulares
- **Otimização Numba:** Aceleração JIT para operações críticas quando disponível
- **Metadata de qualidade:** Rastreamento de pontos interpolados com confiança (`src/platform_base/core/models.py:InterpolationInfo`)

### Sincronização de Séries Temporais
- **Alinhamento em grid comum:** Método `common_grid_interpolate` resampleia múltiplas séries para timestamps compartilhados (`src/platform_base/processing/synchronization.py`)
- **Kalman filtering:** Método `kalman_align` para alinhamento robusto com filtro de estado (`src/platform_base/processing/synchronization.py:KalmanFilter1D`)
- **Resultado estruturado:** `SyncResult` com lineage tracking e metadata de qualidade (`src/platform_base/core/models.py:SyncResult`)

### Cálculos Matemáticos
- **Derivadas:** 1ª, 2ª e 3ª ordem com métodos de diferenças finitas e spline (`src/platform_base/processing/calculus.py:derivative`)
- **Integrais:** Trapezoid, Simpson e cumulativa (`src/platform_base/processing/calculus.py:integral`)
- **Operações compostas:** Área entre curvas, suavização pré-cálculo (`src/platform_base/processing/calculus.py:area_between`)
- **Pré-processamento:** Smoothing configurável (Savitzky-Golay, Gaussian) via `src/platform_base/processing/smoothing.py`

### Visualização Interativa 2D/3D
- **2D PyQtGraph:** Gráficos de linha e scatter com brush selection, otimizados para milhões de pontos (`src/platform_base/viz/figures_2d.py`)
- **3D PyVista:** Trajetórias 3D, superfícies, visualizações volumétricas (`src/platform_base/viz/figures_3d.py`)
- **Heatmaps:** Correlação, time-series e estatísticas (`src/platform_base/viz/heatmaps.py`)
- **Downsampling inteligente:** LTTB, MinMax, adaptativo preservando features visuais (`src/platform_base/processing/downsampling.py`)
- **Drag-and-drop:** Interface moderna com zonas de plotagem (`src/platform_base/ui/panels/viz_panel.py`)

### Streaming Temporal
- **Reprodução temporal:** Visualização animada de séries temporais com controles play/pause/seek (`src/platform_base/viz/streaming.py:StreamingEngine`)
- **Filtros avançados:** Intervalos temporais, predicados de valor, ocultação de interpolados (`src/platform_base/viz/streaming.py:StreamFilters`)
- **Sincronização multi-view:** Cursor temporal compartilhado entre visualizações (`src/platform_base/streaming/temporal_sync.py`)
- **Export para vídeo:** Geração de animações via OpenCV/MoviePy (`src/platform_base/ui/video_export.py`)

### Sistema de Plugins
- **Descoberta automática:** Scan de diretório `plugins/` com validação de API (`src/platform_base/core/registry.py:PluginRegistry`)
- **Isolamento:** Sandboxing com limites de recursos (memória, CPU, timeout) (`src/platform_base/core/registry.py:AdvancedPluginSandbox`)
- **Exemplos fornecidos:**
  - DTW (Dynamic Time Warping) para alinhamento temporal (`plugins/dtw_plugin/plugin.py`, `plugins/advanced_sync/dtw_plugin.py`)
- **Protocolo:** Interface `PluginProtocol` com versionamento semântico (`src/platform_base/core/protocols.py`)

### Cache Multi-Nível
- **Disco:** Cache persistente com joblib.Memory, TTL configurável e LRU cleanup (`src/platform_base/caching/disk.py:DiskCache`)
- **Memória:** Cache em RAM com limite de itens (`src/platform_base/caching/memory.py:MemoryCache`)
- **Configuração:** `configs/platform.yaml` define tamanho máximo, TTL e paths

### Observabilidade e Profiling
- **Logging estruturado:** JSON logging via structlog (`src/platform_base/utils/logging.py`)
- **Profiling automático:** Decoradores `@profile` e `@performance_critical` para análise de desempenho (`src/platform_base/profiling/decorators.py`)
- **Relatórios:** Geração de HTML e JSON com estatísticas detalhadas (`src/platform_base/profiling/reports.py`)
- **Targets configuráveis:** Benchmarks automáticos para operações críticas (configs/platform.yaml:profiling.targets)

---

## C) Recursos / Diferenciais Técnicos

### Arquitetura Modular
- **Separação de responsabilidades:** 
  - `core/`: Modelos de dados, orquestração, registro de plugins
  - `io/`: Carregamento e validação
  - `processing/`: Algoritmos de interpolação, sincronização, cálculo
  - `viz/`: Renderização 2D/3D
  - `ui/`: Interface PyQt6 desktop
  - `desktop/`: Aplicação nativa alternativa (MainWindow, dialogs, workers)
- **Injeção de dependências:** `SessionState` e `DatasetStore` compartilhados via construtor (`src/platform_base/ui/state.py`, `src/platform_base/core/dataset_store.py`)

### Threading Assíncrono
- **QThread workers:** Processamento pesado (carregamento, interpolação, exportação) em threads separadas (`src/platform_base/ui/workers/`, `src/platform_base/desktop/workers/`)
- **Sinais PyQt6:** Comunicação thread-safe via pyqtSignal para progresso e resultados
- **Exemplo:** `FileLoadWorker` reporta progresso incremental durante parsing de arquivos grandes

### Validação Pydantic
- **Modelos tipados:** Todas as estruturas de dados usam Pydantic v2 para validação em runtime (`src/platform_base/core/models.py`)
- **Exemplos:** `Dataset`, `Series`, `ResultMetadata`, `LoadConfig`
- **Benefícios:** Type safety, validação automática, serialização JSON

### Configuração YAML Centralizada
- **Arquivo único:** `configs/platform.yaml` define comportamento de toda a plataforma
- **Hierarquia completa:**
  - `data`: Detecção de schema, unidades, validação
  - `processing`: Métodos padrão de interpolação, cálculo, sincronização
  - `performance`: Paralelismo, cache, profiling, Numba
  - `visualization`: Downsampling, temas, interatividade
  - `streaming`: Velocidade, filtros, export de vídeo
  - `ui`: Layout responsivo, áreas de painel
  - `plugins`: Discovery, isolamento, timeout
  - `logging`: Formato, nível, rotação
- **Gerenciamento:** `ConfigManager` com reload dinâmico e validação (`src/platform_base/core/config_manager.py`)

### Internacionalização (i18n)
- **Sistema I18n:** Traduções PT-BR via chave-valor (`src/platform_base/utils/i18n.py`)
- **Função `tr()`:** Wrapper para textos localizados
- **Cobertura:** Interface UI completa em português brasileiro

---

## D) Demonstração Rápida (Quick Start)

### Pré-requisitos
- Python ≥ 3.10
- PyQt6 ≥ 6.5.0 (instalado automaticamente via dependências)

### Instalação

```bash
# Clone o repositório (ou navegue para o diretório)
cd /path/to/platform_base

# Instalação básica
pip install -e .

# Com dependências de visualização avançada
pip install -e ".[viz]"

# Para desenvolvimento (inclui pytest, black, mypy, etc.)
pip install -e ".[dev]"

# Para distribuição (PyInstaller, cx_Freeze)
pip install -e ".[dist]"
```

### Execução da Aplicação Desktop

**Método 1 - Launcher Principal:**
```bash
python launch_app.py
```
- Inicializa `QApplication` com `ModernMainWindow` (`src/platform_base/ui/main_window.py`)
- Configura `SessionState` e `DatasetStore`
- Erro handling integrado com QMessageBox

**Método 2 - Aplicação Desktop Alternativa:**
```bash
python run_app.py
```
- Usa `platform_base.desktop.app.main()` que cria `PlatformApplication` (`src/platform_base/desktop/app.py`)
- Suporta splash screen e graceful shutdown

### Exemplo Programático

```python
from platform_base.io.loader import load, LoadConfig
from platform_base.processing.interpolation import interpolate
from platform_base.processing.calculus import derivative

# 1. Carregar dataset
config = LoadConfig(timestamp_column="timestamp")
dataset = load("sensor_data.csv", config)

# 2. Obter primeira série
series_id = list(dataset.series.keys())[0]
series = dataset.series[series_id]

# 3. Interpolar gaps com cubic spline
interp_result = interpolate(
    series.t, 
    series.values,
    method="spline_cubic",
    params={}
)

# 4. Calcular derivada primeira
deriv_result = derivative(
    interp_result.t,
    interp_result.values,
    order=1,
    method="finite_diff"
)

print(f"Interpolação: {len(interp_result.values)} pontos")
print(f"Derivada: {len(deriv_result.values)} pontos")
```

---

## E) Configuração

### Variáveis de Ambiente
**Nenhuma configuração de variável de ambiente externa detectada no código.**  
A aplicação funciona out-of-the-box sem necessidade de variáveis de ambiente.

### Arquivo de Configuração: `configs/platform.yaml`

O sistema é inteiramente configurável via YAML centralizado:

**Estrutura principal:**
```yaml
platform:
  version: "2.0.0"

data:
  schema_detection:
    timestamp_patterns: ["timestamp", "time", "datetime", "date", "datahora"]
    heuristics: [monotonic_increasing, datetime_type, unix_epoch_range]
  units:
    default_system: "SI"
  validation:
    max_gap_seconds: 300
    outlier_threshold: 3.0

processing:
  interpolation:
    default_method: "linear"
    available_methods: [linear, spline_cubic, smoothing_spline, ...]
  calculus:
    derivative_default: "finite_diff"
    max_order: 3

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
  numba:
    enabled: true
    cache: true

visualization:
  downsampling:
    method: "lttb"
    max_points: 10000

streaming:
  default_speed: 1.0
  window_size_seconds: 60

plugins:
  discovery:
    enabled: true
    path: "plugins/"
    isolation: false
    timeout_seconds: 60

logging:
  format: "json"
  level: "INFO"
  output: "logs/platform.log"
```

**Exemplo de personalização:**
1. Editar `configs/platform.yaml`
2. Modificar `processing.interpolation.default_method` para `"spline_cubic"`
3. Ajustar `performance.cache.max_size_gb` para `20`
4. Reiniciar aplicação (configuração é carregada no startup)

**Sem configuração externa detectada:** Não há suporte nativo para arquivos `.env` ou configuração via linha de comando.

---

## F) Arquitetura e Organização do Código

### Estrutura de Diretórios

```
platform_base/
├── src/platform_base/           # Código fonte principal
│   ├── __init__.py              # Exports públicos (load_dataset)
│   ├── api/                     # API REST (opcional, disabled por padrão)
│   │   ├── endpoints.py         # Definição de rotas
│   │   └── server.py            # Servidor FastAPI
│   ├── caching/                 # Sistema de cache
│   │   ├── disk.py              # DiskCache com joblib.Memory
│   │   └── memory.py            # MemoryCache (LRU em memória)
│   ├── core/                    # Núcleo da plataforma
│   │   ├── config.py            # ConfigManager básico
│   │   ├── config_manager.py    # AdvancedConfigManager com validação
│   │   ├── dataset_store.py     # Armazenamento central de datasets
│   │   ├── models.py            # Modelos Pydantic (Dataset, Series, Results)
│   │   ├── orchestrator.py      # DAG-based task orchestrator
│   │   ├── protocols.py         # Interfaces de plugins
│   │   └── registry.py          # PluginRegistry com sandboxing
│   ├── desktop/                 # Aplicação desktop PyQt6 (versão alternativa)
│   │   ├── app.py               # PlatformApplication (splash, shutdown)
│   │   ├── main_window.py       # MainWindow principal
│   │   ├── session_state.py     # Estado da sessão desktop
│   │   ├── signal_hub.py        # Hub de sinais PyQt6
│   │   ├── dialogs/             # Diálogos modais
│   │   │   ├── about_dialog.py
│   │   │   ├── settings_dialog.py
│   │   │   └── upload_dialog.py
│   │   ├── menus/               # Menus de contexto
│   │   │   └── plot_context_menu.py
│   │   ├── models/              # Modelos de dados UI
│   │   │   └── dataset_model.py  # TreeModel para datasets
│   │   ├── selection/           # Sistema de seleção
│   │   │   ├── selection_manager.py
│   │   │   └── selection_widgets.py
│   │   └── widgets/             # Widgets personalizados
│   │       ├── config_panel.py
│   │       ├── data_panel.py
│   │       ├── results_panel.py
│   │       └── viz_panel.py
│   ├── io/                      # Input/Output
│   │   ├── loader.py            # Carregamento multi-formato
│   │   ├── schema_detector.py   # Detecção automática de esquema
│   │   └── validator.py         # Validação de dados
│   ├── processing/              # Algoritmos de processamento
│   │   ├── calculus.py          # Derivadas, integrais
│   │   ├── downsampling.py      # LTTB, MinMax, adaptativo
│   │   ├── interpolation.py     # 10 métodos de interpolação
│   │   ├── smoothing.py         # Algoritmos de suavização
│   │   ├── synchronization.py   # Sincronização de séries
│   │   ├── timebase.py          # Conversões temporais
│   │   └── units.py             # Sistema de unidades (Pint)
│   ├── profiling/               # Sistema de profiling
│   │   ├── decorators.py        # @profile, @performance_critical
│   │   ├── profiler.py          # Profiler principal
│   │   ├── reports.py           # Geração de relatórios
│   │   └── setup.py             # Configuração de profiling
│   ├── streaming/               # Streaming temporal
│   │   ├── filters.py           # Filtros de stream (qualidade, temporal, valor)
│   │   └── temporal_sync.py     # Sincronização temporal multi-view
│   ├── ui/                      # Interface PyQt6 (versão principal)
│   │   ├── app.py               # PlatformApplication
│   │   ├── callbacks.py         # Callbacks de eventos
│   │   ├── context_menu.py      # Menus de contexto
│   │   ├── export.py            # Exportação assíncrona
│   │   ├── layout.py            # Construtor de layouts
│   │   ├── main_window.py       # ModernMainWindow
│   │   ├── multi_view_sync.py   # Sincronização de visualizações
│   │   ├── operation_dialogs.py # Diálogos de operações
│   │   ├── operation_preview.py # Preview de operações
│   │   ├── panels/              # Painéis da interface
│   │   │   ├── data_panel.py    # CompactDataPanel (gerenciamento datasets)
│   │   │   ├── operations_panel.py  # OperationsPanel
│   │   │   └── viz_panel.py     # ModernVizPanel (drag-and-drop)
│   │   ├── selection.py         # Sistema de seleção de dados
│   │   ├── selection_sync.py    # Sincronização de seleções
│   │   ├── selection_widgets.py # Widgets de seleção
│   │   ├── state.py             # SessionState
│   │   ├── stream_filters.py    # Widgets de filtros de streaming
│   │   ├── streaming_controls.py # Controles de streaming
│   │   ├── video_export.py      # Exportação para vídeo
│   │   └── workers/             # Workers de processamento
│   │       └── file_worker.py   # FileLoadWorker
│   ├── utils/                   # Utilitários
│   │   ├── errors.py            # Exceções customizadas
│   │   ├── i18n.py              # Internacionalização
│   │   ├── ids.py               # Geração de IDs únicos
│   │   ├── logging.py           # Configuração de logging
│   │   ├── serialization.py     # Serialização JSON
│   │   └── validation.py        # Validadores
│   └── viz/                     # Visualização
│       ├── base.py              # BaseFigure
│       ├── config.py            # VizConfig (temas, estilos)
│       ├── figures_2d.py        # Gráficos 2D PyQtGraph
│       ├── figures_3d.py        # Gráficos 3D PyVista
│       ├── heatmaps.py          # Heatmaps
│       ├── multipanel.py        # Visualizações multi-painel
│       ├── state_cube.py        # Visualização 3D de estados
│       └── streaming.py         # StreamingEngine
├── configs/                     # Configurações
│   └── platform.yaml            # Configuração principal
├── plugins/                     # Plugins externos
│   ├── _base.py                 # PluginBase dataclass
│   ├── dtw_plugin/              # Plugin DTW
│   │   └── plugin.py
│   └── advanced_sync/           # Plugin DTW avançado
│       └── dtw_plugin.py
├── tests/                       # Testes automatizados
│   ├── fixtures/                # Dados de teste
│   ├── integration/             # Testes de integração
│   ├── property/                # Property-based tests (Hypothesis)
│   ├── stress/                  # Testes de stress
│   └── unit/                    # Testes unitários
├── docs/                        # Documentação
│   └── examples/                # Exemplos de código
├── launch_app.py                # Launcher principal (ModernMainWindow)
├── run_app.py                   # Launcher alternativo (PlatformApplication)
├── pyproject.toml               # Configuração do projeto
└── README.md                    # Este arquivo
```

### Fluxo de Inicialização da UI

**Caminho Principal (launch_app.py):**
1. `QApplication` é criado com metadata (nome, versão, organização)
2. `DatasetStore` é instanciado para gerenciar datasets em memória (`src/platform_base/core/dataset_store.py:DatasetStore`)
3. `SessionState` é criado com referência ao store (`src/platform_base/ui/state.py:SessionState`)
4. `ModernMainWindow` é inicializado com SessionState (`src/platform_base/ui/main_window.py:ModernMainWindow`)
5. MainWindow configura painéis:
   - **DataPanel** (esquerda): Gerenciamento de datasets, visualização de séries (`src/platform_base/ui/panels/data_panel.py:CompactDataPanel`)
   - **VizPanel** (centro): Área de plotagem com drag-and-drop (`src/platform_base/ui/panels/viz_panel.py:ModernVizPanel`)
   - **OperationsPanel** (direita): Controles de operações (placeholder) (`src/platform_base/ui/panels/operations_panel.py:OperationsPanel`)
6. Toolbar horizontal é configurada com ações (upload, interpolar, calcular, exportar)
7. Status bar e progress bar são anexados
8. Auto-save timer é iniciado (5 minutos)
9. `app.exec()` inicia event loop

**Caminho Alternativo (run_app.py):**
- Usa `desktop.app.PlatformApplication` com `desktop.main_window.MainWindow`
- Adiciona splash screen e signal handling (SIGINT, SIGTERM)
- Estrutura similar com widgets desktop (`src/platform_base/desktop/widgets/`)

### Tratamento de Tarefas Pesadas (Threading)

**Padrão QThread + Worker:**
1. **Criação:** Worker herda de `BaseWorker` ou `QObject` (`src/platform_base/desktop/workers/base_worker.py`)
2. **Sinais:** Define `progress`, `status_updated`, `error`, `finished`
3. **Execução:** 
   - UI instancia worker e QThread
   - Worker é movido para thread: `worker.moveToThread(thread)`
   - Conecta sinais: `worker.progress.connect(self.update_progress_bar)`
   - Inicia thread: `thread.start()`
4. **Processamento:** Worker executa operação pesada (load, interpolate, export) em background
5. **Comunicação:** Emite sinais para atualizar UI de forma thread-safe
6. **Finalização:** Sinal `finished` dispara cleanup e atualização final da UI

**Exemplos de Workers:**
- `FileLoadWorker` (`src/platform_base/ui/workers/file_worker.py`): Carregamento assíncrono de arquivos
- `InterpolationWorker` (`src/platform_base/desktop/workers/processing_worker.py`): Interpolação em background
- `ExportWorker` (`src/platform_base/desktop/workers/export_worker.py`): Exportação assíncrona de dados

---

## G) Mapa de Funcionalidades e Telas

### Janela Principal: `ModernMainWindow`
- **Arquivo:** `src/platform_base/ui/main_window.py`
- **Classe:** `ModernMainWindow(QMainWindow)`
- **Acesso:** Executar `python launch_app.py`
- **Componentes:**
  - Toolbar horizontal com botões: Upload, Interpolar, Sincronizar, Derivada, Integral, Exportar, Configurações
  - 3 painéis em QSplitter: DataPanel (esquerda), VizPanel (centro), OperationsPanel (direita)
  - StatusBar com mensagens e QProgressBar

### Painel de Dados: `CompactDataPanel`
- **Arquivo:** `src/platform_base/ui/panels/data_panel.py`
- **Classe:** `CompactDataPanel(QWidget)`
- **Funcionalidades:**
  - Lista de datasets carregados com nome de arquivo
  - Visualização de séries ativas em TreeWidget
  - Tabela de dados com estatísticas (min, max, mean, std)
  - Botão "Carregar Arquivo" abre FileLoadWorker
- **Sinais:** `dataset_loaded(str)`, `series_selected(str, str)`

### Painel de Visualização: `ModernVizPanel`
- **Arquivo:** `src/platform_base/ui/panels/viz_panel.py`
- **Classes:** `ModernVizPanel(QWidget)`, `MatplotlibWidget(QWidget)`, `DropZone(QWidget)`
- **Funcionalidades:**
  - Sistema drag-and-drop para criar gráficos
  - Integração com Matplotlib via FigureCanvas
  - Suporte a múltiplas tabs para visualizações paralelas
  - Context menu para análise matemática
- **Como acessar:** Arrastar série do DataPanel para DropZone no VizPanel

### Painel de Operações: `OperationsPanel`
- **Arquivo:** `src/platform_base/ui/panels/operations_panel.py`
- **Classe:** `OperationsPanel(QWidget)`
- **Status:** Placeholder (funcionalidades em desenvolvimento conforme código)
- **Planejado:** Controles para interpolação, sincronização, cálculos, streaming

### Diálogos Modais

#### UploadDialog
- **Arquivo:** `src/platform_base/desktop/dialogs/upload_dialog.py`
- **Classe:** `UploadDialog(QDialog)`
- **Acesso:** Botão "Carregar Arquivo" ou menu File > Upload
- **Funcionalidades:**
  - Seleção de arquivo via QFileDialog
  - Configuração de LoadConfig (coluna timestamp, delimiter, encoding, sheet_name, hdf5_key)
  - Preview de dados antes do carregamento completo
  - Barra de progresso durante loading

#### SettingsDialog
- **Arquivo:** `src/platform_base/desktop/dialogs/settings_dialog.py`
- **Classe:** `SettingsDialog(QDialog)` com tabs: `GeneralSettingsTab`, `PerformanceSettingsTab`, `LoggingSettingsTab`
- **Acesso:** Menu Tools > Settings
- **Funcionalidades:**
  - Configuração de preferências gerais (idioma, tema)
  - Ajuste de performance (max_workers, cache size)
  - Níveis de logging

#### AboutDialog
- **Arquivo:** `src/platform_base/desktop/dialogs/about_dialog.py`
- **Classe:** `AboutDialog(QDialog)`
- **Acesso:** Menu Help > About
- **Informações:** Versão, créditos, licença

#### Operation Dialogs (Interpolação, Sincronização, Cálculo)
- **Arquivo:** `src/platform_base/ui/operation_dialogs.py`
- **Classes:** `InterpolationDialog`, `SynchronizationDialog`, `CalculusDialog`
- **Acesso:** Botões na toolbar ou menus de contexto
- **Funcionalidades:**
  - Seleção de método com preview em tempo real
  - Configuração de parâmetros via widgets dinâmicos (`ParameterWidget` subclasses)
  - Preview visual antes de aplicar (`PreviewVisualizationWidget`)

### Widgets de Seleção

#### SelectionPanel
- **Arquivo:** `src/platform_base/desktop/selection/selection_widgets.py`
- **Classe:** `SelectionPanel(QWidget)`
- **Componentes:**
  - `SelectionToolbar`: Modos de seleção (temporal, gráfica, condicional)
  - `ConditionalSelectionDialog`: Query builder para seleção por predicados
  - `SelectionStatsWidget`: Estatísticas da seleção atual
  - `SelectionHistoryWidget`: Histórico de seleções

### Widgets de Streaming

#### StreamingControlWidget
- **Arquivo:** `src/platform_base/ui/streaming_controls.py`
- **Classe:** `StreamingControlWidget(QWidget)`
- **Funcionalidades:**
  - Botões Play/Pause/Stop
  - Slider de velocidade (0.1x a 10x)
  - Seek bar para navegação temporal
  - Indicador de posição atual

#### StreamFiltersWidget
- **Arquivo:** `src/platform_base/ui/stream_filters.py`
- **Classes:** `TimeIntervalWidget`, `ValuePredicateWidget`, `StreamFiltersWidget`
- **Funcionalidades:**
  - Configuração de filtros temporais (incluir/excluir intervalos)
  - Predicados de valor por série
  - Toggle para ocultar interpolados/NaN
  - Configuração de downsampling

### Video Export Dialog
- **Arquivo:** `src/platform_base/ui/video_export.py`
- **Classe:** `VideoExportDialog(QDialog)`
- **Acesso:** Menu Export > Export as Video
- **Funcionalidades:**
  - Seleção de formato (MP4, AVI, GIF)
  - Configuração de qualidade e FPS
  - Range temporal para exportação
  - Worker assíncrono (`VideoExportWorker`) com progresso

---

## H) Catálogo de Funções e Classes

Cobertura completa dos **101 módulos Python** em `src/platform_base/`:

### Módulo: `platform_base/__init__.py`
- **Função:** `load_dataset()` - Atalho público para carregamento de datasets

### Pacote: `platform_base/api/`
Servidor API REST (opcional, desabilitado por padrão em configs)

#### `api/server.py`
- **Classes:** `InterpolationRequest`, `ViewRequest` - Modelos Pydantic para requests
- **Função:** `create_app()` - Cria aplicação FastAPI

#### `api/endpoints.py`
- Define rotas REST para operações remotas (futuro)

### Pacote: `platform_base/caching/`
Sistema de cache de dois níveis (disco + memória)

#### `caching/disk.py`
- **Classe:** `DiskCache` - Cache persistente com joblib.Memory, TTL e LRU
- **Função:** `create_disk_cache_from_config(config)` - Factory a partir de YAML

#### `caching/memory.py`
- **Classe:** `MemoryCache` - LRU cache em RAM com limite de itens
- **Função:** `memory_cache(max_items=1000)` - Decorator para caching

### Pacote: `platform_base/core/`
Núcleo da plataforma (modelos, orquestração, plugins)

#### `core/models.py`
Modelos Pydantic para toda a plataforma:
- **Classes:**
  - `SourceInfo` - Metadata de arquivo fonte (filepath, checksum, formato)
  - `DatasetMetadata` - Metadata de dataset (tags, timezone, warnings)
  - `SeriesMetadata` - Metadata de série temporal (original_name, unit)
  - `InterpolationInfo` - Rastreamento de pontos interpolados com confiança
  - `ResultMetadata` - Metadata de resultados (operation, parameters, duration_ms)
  - `QualityMetrics` - Métricas de qualidade (RMSE, R², confidence)
  - `Lineage` - Rastreamento de linhagem de dados
  - `Series` - Série temporal (t, values, metadata, interpolation_info)
  - `Dataset` - Conjunto de séries temporais (series: dict, t_seconds, source)
  - `TimeWindow` - Janela temporal (start, end)
  - `ViewData` - Dados para visualização
  - `DerivedResult` - Resultado base de operações
  - `InterpResult` - Resultado de interpolação
  - `CalcResult` - Resultado de cálculo (derivada/integral)
  - `SyncResult` - Resultado de sincronização
  - `DownsampleResult` - Resultado de downsampling
  - `SeriesSummary` - Resumo estatístico de série

#### `core/dataset_store.py`
- **Classe:** `DatasetStore` - Repositório central de datasets em memória
- **Métodos:** `add(dataset)`, `get(dataset_id)`, `list_all()`, `remove(dataset_id)`
- **Classe:** `DatasetSummary` - Resumo de dataset para listagem

#### `core/config.py`
- **Classe:** `ConfigManager` - Gerenciador de configuração básico
- **Enums:** `ConfigFormat`, `ConfigScope`, `ConfigSource`
- **Classes:** `ConfigChange`, `ConfigWatcher`, `ConfigValidator`
- **Funções:** `get_config_manager()`, `get_config(key)`, `set_config(key, value)`, `reload_config()`

#### `core/config_manager.py`
- **Classe:** `AdvancedConfigManager` - Gerenciador avançado com validação e métricas
- **Classe:** `ConfigValidationResult` - Resultado de validação
- **Classe:** `ConfigPerformanceMetrics` - Métricas de performance de config
- **Funções:** `get_advanced_config_manager()`, `get_validated_config(schema)`, `update_validated_config(key, value, schema)`

#### `core/orchestrator.py`
- **Classe:** `Orchestrator` - Orquestrador de tarefas baseado em DAG (Directed Acyclic Graph)
- **Classe:** `Task` - Definição de tarefa (name, func, deps)
- **Métodos:** `register(task)`, `run(inputs)` - Execução topológica de dependências

#### `core/protocols.py`
Protocolos de interface para plugins:
- **Classe:** `PluginProtocol` - Interface base de plugin
- **Classe:** `InterpolationPlugin` - Plugin de interpolação customizada
- **Classe:** `SyncPlugin` - Plugin de sincronização customizada

#### `core/registry.py`
Sistema robusto de registro e isolamento de plugins:
- **Classes:**
  - `VersionCompatibility` - Utilitários de versionamento semântico
  - `CompatibilityCheck` - Resultado de verificação de compatibilidade
  - `PluginState` - Enum (DISCOVERED, LOADED, ACTIVE, FAILED, DISABLED)
  - `PluginManifest` - Manifesto de plugin (id, version, capabilities)
  - `PluginInfo` - Informações de plugin registrado
  - `ResourceLimits` - Limites de recursos (memória, CPU, timeout)
  - `SecurityViolation` - Exceção de violação de segurança
  - `AdvancedPluginSandbox` - Sandbox com isolamento de recursos
  - `PluginRegistry` - Registro global de plugins com discovery e validação
- **Métodos principais:**
  - `discover_plugins(path)` - Descobre plugins em diretório
  - `load_plugin(plugin_id)` - Carrega plugin com validação
  - `execute_plugin(plugin_id, context)` - Executa plugin com isolamento

### Pacote: `platform_base/desktop/`
Aplicação desktop PyQt6 (versão alternativa da UI)

#### `desktop/app.py`
- **Classe:** `PlatformApplication(QApplication)` - Aplicação desktop com splash screen
- **Funções:** `create_application(argv)`, `main()` - Entry point da aplicação desktop
- **Features:** HiDPI support, graceful shutdown, global exception handling

#### `desktop/main_window.py`
- **Classe:** `MainWindow(QMainWindow)` - Janela principal desktop
- **Componentes:** Menus, toolbar, status bar, painéis (data, viz, config, results)

#### `desktop/session_state.py`
- **Classe:** `SessionState` - Estado da sessão desktop
- **Subclasses:** `SelectionState`, `ViewState`, `ProcessingState`, `StreamingState`, `UIState`

#### `desktop/signal_hub.py`
- **Classe:** `SignalHub(QObject)` - Hub centralizado de sinais PyQt6 para comunicação entre componentes

#### `desktop/dialogs/about_dialog.py`
- **Classe:** `AboutDialog(QDialog)` - Diálogo "Sobre" com informações da aplicação

#### `desktop/dialogs/settings_dialog.py`
- **Classes:** `SettingsDialog(QDialog)`, `GeneralSettingsTab`, `PerformanceSettingsTab`, `LoggingSettingsTab`
- Configuração de preferências do usuário

#### `desktop/dialogs/upload_dialog.py`
- **Classe:** `UploadDialog(QDialog)` - Diálogo de upload de arquivo com preview
- **Classe:** `FileLoadWorker(BaseWorker)` - Worker assíncrono de carregamento
- **Classe:** `PreviewWorker(BaseWorker)` - Worker de preview de dados

#### `desktop/menus/plot_context_menu.py`
- **Classe:** `PlotContextMenu(QMenu)` - Menu de contexto para gráficos
- **Classe:** `MathAnalysisDialog(QDialog)` - Diálogo de análise matemática
- **Função:** `create_plot_context_menu(plot_widget)` - Factory de menu

#### `desktop/models/dataset_model.py`
- **Classe:** `DatasetTreeModel(QAbstractItemModel)` - Modelo de árvore para datasets
- **Classe:** `TreeItem` - Item de árvore hierárquica

#### `desktop/selection/selection_manager.py`
- **Classes:**
  - `SelectionManager` - Gerenciador de seleções de dados
  - `SelectionState` - Estado de seleção
  - `SelectionCriteria`, `TemporalSelection`, `GraphicalSelection`, `ConditionalSelection`
- **Enums:** `SelectionType`, `SelectionMode`

#### `desktop/selection/selection_widgets.py`
- **Classes:** `SelectionToolbar`, `ConditionalSelectionDialog`, `SelectionStatsWidget`, `SelectionPanel`

#### `desktop/widgets/config_panel.py`
- **Classes:** `ConfigPanel(QWidget)`, `InterpolationConfigWidget`, `CalculusConfigWidget`
- Painéis de configuração de operações

#### `desktop/widgets/data_panel.py`
- **Classe:** `DataPanel(QWidget)` - Painel de gerenciamento de datasets (versão desktop)

#### `desktop/widgets/results_panel.py`
- **Classes:** `ResultsPanel(QWidget)`, `ResultsTable`, `LogWidget`
- Visualização de resultados e logs

#### `desktop/widgets/viz_panel.py`
- **Classes:** `VizPanel(QWidget)`, `Plot2DWidget`, `Plot3DWidget`
- Painéis de visualização 2D/3D

#### `desktop/workers/base_worker.py`
- **Classe:** `BaseWorker(QThread)` - Classe base para workers
- **Sinais:** `progress(int)`, `status_updated(str)`, `error(str)`, `finished()`
- **Métodos:** `run()`, `cancel()`, `emit_progress()`, `emit_error()`

#### `desktop/workers/export_worker.py`
- **Classes:** `DataExportWorker`, `SessionExportWorker`, `PlotExportWorker`, `VideoExportWorker`
- **Classe:** `ExportWorkerManager` - Gerenciador de workers de exportação

#### `desktop/workers/processing_worker.py`
- **Classes:** `InterpolationWorker`, `CalculusWorker`, `SynchronizationWorker`
- **Classe:** `ProcessingWorkerManager` - Gerenciador de workers de processamento

### Pacote: `platform_base/io/`
Input/Output de dados

#### `io/loader.py`
Carregamento multi-formato de séries temporais:
- **Classe:** `LoadConfig` - Configuração de carregamento (timestamp_column, delimiter, encoding, sheet_name, hdf5_key, chunk_size)
- **Enum:** `FileFormat` (CSV, EXCEL, PARQUET, HDF5)
- **Enum:** `LoadStrategy` - Estratégia de carregamento
- **Funções:**
  - `load(filepath, config)` → Dataset - Carregamento síncrono
  - `load_async(filepath, config)` → Awaitable[Dataset] - Carregamento assíncrono
  - `get_file_info(filepath)` - Informações de arquivo

#### `io/schema_detector.py`
Detecção automática de esquema temporal:
- **Classes:** `SeriesCandidate`, `SchemaMap`, `SchemaRules`
- **Função:** `detect_schema(df, rules)` → SchemaMap - Identifica coluna temporal e séries

#### `io/validator.py`
Validação de dados carregados:
- **Classes:** `ValidationWarning`, `ValidationError`, `Gap`, `GapReport`, `ValidationReport`
- **Funções:**
  - `detect_gaps(t, max_gap_seconds)` → GapReport - Detecta gaps temporais
  - `validate_time(t)` → ValidationReport - Valida monotonicidade e ordem
  - `validate_values(values)` → ValidationReport - Valida outliers e NaN

### Pacote: `platform_base/processing/`
Algoritmos de processamento de séries temporais

#### `processing/interpolation.py`
10 métodos de interpolação para dados irregulares:
- **Função:** `interpolate(t, values, method, params)` → InterpResult
- **Métodos suportados:**
  - `linear`: Interpolação linear básica (scipy.interp1d)
  - `spline_cubic`: Spline cúbica (CubicSpline)
  - `smoothing_spline`: Spline suavizada (UnivariateSpline)
  - `resample_grid`: Reamostragem em grid uniforme
  - `mls`: Moving Least Squares (polinomial local)
  - `gpr`: Gaussian Process Regression (probabilístico)
  - `lomb_scargle_spectral`: Interpolação espectral via Lomb-Scargle
- **Otimização:** Numba JIT para operações críticas (quando disponível)

#### `processing/synchronization.py`
Sincronização de múltiplas séries temporais:
- **Função:** `synchronize(t_dict, v_dict, method, params)` → SyncResult
- **Métodos:**
  - `common_grid_interpolate`: Grid comum via interpolação
  - `kalman_align`: Alinhamento com filtro de Kalman
- **Classe:** `KalmanFilter1D` - Filtro de Kalman 1D para alinhamento

#### `processing/calculus.py`
Operações de cálculo diferencial e integral:
- **Funções:**
  - `derivative(t, values, order, method)` → CalcResult - Derivada 1ª, 2ª ou 3ª ordem
  - `integral(t, values, method)` → CalcResult - Integral definida (trapezoid, simpson)
  - `area_between(t, v1, v2)` → CalcResult - Área entre duas curvas
  - `first_derivative(t, v)`, `second_derivative(t, v)` - Atalhos
- **Métodos:** `finite_diff`, `spline`, `savitzky_golay`
- **Pré-processamento:** Suavização opcional via `smoothing.py`

#### `processing/downsampling.py`
Downsampling inteligente para visualização:
- **Função:** `downsample(t, values, n_points, method)` → DownsampleResult
- **Métodos:**
  - `lttb`: Largest Triangle Three Buckets (preserva características visuais)
  - `minmax`: Min-Max por bucket (preserva extremos)
  - `adaptive`: Densidade adaptativa por variância
  - `uniform`: Espaçamento uniforme
  - `peak_aware`: Preservação de picos e vales
- **Funções específicas:** `lttb_downsample()`, `minmax_downsample()`, `adaptive_downsample()`
- **Otimização Numba:** Funções críticas aceleradas via JIT

#### `processing/smoothing.py`
Algoritmos de suavização:
- **Classe:** `SmoothingConfig` - Configuração de suavização
- **Função:** `smooth(values, config)` → np.ndarray - Aplica suavização
- **Métodos:** Savitzky-Golay, Gaussian, median, lowpass

#### `processing/timebase.py`
Conversões de base temporal:
- **Funções:**
  - `to_seconds(timestamps)` → np.ndarray - Converte timestamps para segundos
  - `to_datetime(seconds)` → List[datetime] - Converte segundos para datetime

#### `processing/units.py`
Sistema de unidades (integração Pint):
- **Funções:**
  - `parse_unit(unit_str)` → Unit - Parse de string de unidade
  - `infer_unit_from_name(col_name)` → Optional[str] - Inferência de unidade por nome de coluna
  - `normalize_units(value, from_unit, to_unit)` - Conversão de unidades

### Pacote: `platform_base/profiling/`
Sistema de profiling e análise de desempenho

#### `profiling/decorators.py`
Decoradores para profiling automático:
- **Funções:**
  - `@profile` - Decorator para profiling de função
  - `@memory_profile` - Decorator para profiling de memória
  - `@performance_critical` - Marca função crítica para otimização
  - `set_global_profiler(profiler)` - Configura profiler global

#### `profiling/profiler.py`
Motor de profiling:
- **Classe:** `Profiler` - Profiler principal com cProfile e memory_profiler
- **Classe:** `AutoProfiler` - Profiler automático baseado em threshold
- **Classe:** `ProfilingResult` - Resultado de profiling com stats
- **Função:** `create_auto_profiler_from_config(config)` - Factory a partir de YAML

#### `profiling/reports.py`
Geração de relatórios de profiling:
- **Classe:** `ProfilingReport` - Relatório estruturado
- **Funções:**
  - `generate_html_report(profiling_results)` → str - Gera HTML
  - `generate_json_report(profiling_results)` → dict - Gera JSON

#### `profiling/setup.py`
Configuração de profiling:
- **Funções:**
  - `setup_profiling_from_config(config_path)` - Setup a partir de arquivo YAML
  - `setup_profiling_from_dict(config_dict)` - Setup a partir de dicionário
  - `create_test_profiler()` - Cria profiler para testes

### Pacote: `platform_base/streaming/`
Streaming temporal e filtros

#### `streaming/filters.py`
Sistema de filtros para streaming:
- **Classes:**
  - `StreamFilter` - Filtro base
  - `QualityFilter` - Filtro por qualidade de dados
  - `TemporalFilter` - Filtro por janela temporal
  - `ValueFilter` - Filtro por predicados de valor
  - `ConditionalFilter` - Filtro condicional customizado
  - `FilterChain` - Cadeia de filtros
  - `FilterAction`, `FilterResult` - Resultado de filtragem
- **Funções factory:**
  - `create_quality_filter(threshold)` 
  - `create_range_filter(min_val, max_val)`
  - `create_rate_limit_filter(max_rate)`
  - `create_business_hours_filter(start_hour, end_hour)`
  - `create_standard_filter_chain()` - Cadeia padrão

#### `streaming/temporal_sync.py`
Sincronização temporal para streaming:
- **Classes:**
  - `StreamFrame` - Frame de streaming (timestamp, data, series_id, frame_number)
  - `SyncPoint` - Ponto de sincronização
  - `TemporalSynchronizer` - Sincronizador temporal multi-série
  - `StreamingPlotManager` - Gerenciador de plots em streaming
- **Features:** Sincronização de cursor temporal entre múltiplas visualizações

### Pacote: `platform_base/ui/`
Interface PyQt6 principal (ModernMainWindow)

#### `ui/app.py`
- **Classe:** `PlatformApplication(QApplication)` - Aplicação PyQt6
- **Funções:** `create_application(argv)`, `main()`, `run()` - Entry points

#### `ui/main_window.py`
- **Classe:** `ModernMainWindow(QMainWindow)` - Janela principal moderna
- **Features:**
  - Layout responsivo com 3 painéis (data, viz, operations)
  - Toolbar horizontal com ícones
  - Drag-and-drop para gráficos
  - Auto-save a cada 5 minutos
  - Styling moderno com CSS

#### `ui/state.py`
Gerenciamento de estado da sessão:
- **Classe:** `SessionState` - Estado central da aplicação
- **Subclasses:** `SelectionState`, `OperationState`, `ViewState`
- **Responsabilidades:** Rastreamento de datasets ativos, seleções, operações em andamento

#### `ui/panels/data_panel.py`
- **Classe:** `CompactDataPanel(QWidget)` - Painel de gerenciamento de datasets
- **Features:**
  - Tree view de datasets e séries
  - Tabela de dados com estatísticas
  - Botão de carregamento assíncrono
- **Sinais:** `dataset_loaded(str)`, `series_selected(str, str)`

#### `ui/panels/viz_panel.py`
- **Classe:** `ModernVizPanel(QWidget)` - Painel de visualização com drag-and-drop
- **Classe:** `MatplotlibWidget(QWidget)` - Widget Matplotlib integrado
- **Classe:** `DropZone(QWidget)` - Zona de drop para criar gráficos
- **Features:** Múltiplas tabs, context menu, exportação de figuras

#### `ui/panels/operations_panel.py`
- **Classe:** `OperationsPanel(QWidget)` - Painel de operações (placeholder)
- **Planejado:** Controles para interpolação, sincronização, cálculos

#### `ui/callbacks.py`
- **Função:** `register_callbacks(app, session_state)` - Registra callbacks de eventos

#### `ui/context_menu.py`
- **Classe:** `PlotContextMenu(QMenu)` - Menu de contexto para plots

#### `ui/export.py`
Exportação assíncrona de dados:
- **Classe:** `ExportConfig` - Configuração de exportação
- **Classe:** `SessionData` - Dados de sessão para serialização
- **Classes:** `ExportResult`, `ExportProgress`
- **Funções:**
  - `export_selection(view_data, format, output_path)` - Exportação síncrona
  - `export_session(session_state, output_path)` - Exporta sessão completa
  - `load_session(session_path)` → SessionData - Carrega sessão
  - `restore_session(session_data, session_state)` - Restaura estado
  - `export_session_compressed(session_state, output_path)` - Exportação comprimida

#### `ui/layout.py`
- **Classe:** `LayoutConfig`, `PanelConfig` - Configuração de layout
- **Função:** `build_layout(config)` → QWidget - Constrói layout a partir de config

#### `ui/multi_view_sync.py`
Sincronização de múltiplas visualizações:
- **Classe:** `MultiViewSynchronizer` - Sincronizador global de views
- **Classe:** `ViewSyncMixin` - Mixin para widgets sincronizáveis
- **Classes:** `SyncMode`, `ViewInfo`, `SyncState`
- **Funções:**
  - `get_global_synchronizer()` - Obtém sincronizador global (singleton)
  - `cleanup_global_synchronizer()` - Cleanup

#### `ui/operation_dialogs.py`
Diálogos de operações com preview:
- **Classes:**
  - `BaseOperationDialog(QDialog)` - Diálogo base para operações
  - `InterpolationDialog(BaseOperationDialog)` - Diálogo de interpolação
  - `SynchronizationDialog(BaseOperationDialog)` - Diálogo de sincronização
  - `CalculusDialog(BaseOperationDialog)` - Diálogo de cálculo
  - `ParameterWidget` - Widget base de parâmetro
  - `NumericParameterWidget`, `ChoiceParameterWidget`, `BooleanParameterWidget`
  - `PreviewWidget` - Widget de preview de operação
  - `OperationDialogManager` - Gerenciador de diálogos
- **Funções:** `get_operation_dialog_manager()`, `show_interpolation_dialog()`, `show_synchronization_dialog()`, `show_calculus_dialog()`

#### `ui/operation_preview.py`
Sistema de preview de operações:
- **Classes:**
  - `OperationPreviewManager` - Gerenciador de previews
  - `PreviewProcessor` - Processador de preview em background
  - `PreviewVisualizationWidget` - Widget de visualização de preview
  - `PreviewRequest`, `PreviewResult`, `PreviewMode`
- **Funções:** `get_preview_manager()`, `cleanup_preview_manager()`

#### `ui/selection.py`
Sistema de seleção de dados:
- **Classes:**
  - `DataSelector` - Seletor de dados
  - `Selection` - Seleção ativa
  - `SelectionMode`, `SelectionCriteria`
- **Funções:**
  - `select_time_window(dataset, start, end)` → Selection
  - `select_by_predicate(dataset, predicate)` → Selection

#### `ui/selection_sync.py`
Sincronização de seleções entre views:
- **Classe:** `SelectionSynchronizer` - Sincronizador de seleções
- **Classe:** `GlobalSelectionSynchronizer` - Sincronizador global (singleton)
- **Classes:** `SelectionSyncMode`, `SelectionSyncFilter`, `SelectionSyncEvent`, `SelectionSyncView`
- **Funções:**
  - `get_global_selection_synchronizer()`
  - `cleanup_global_selection_synchronizer()`
  - `sync_temporal_selection_across_views(start, end)`
  - `create_selection_sync_filter(filter_type)`

#### `ui/selection_widgets.py`
Widgets de seleção interativa:
- **Classes:**
  - `RangePickerWidget(QWidget)` - Seletor de range temporal
  - `BrushSelectionWidget(QWidget)` - Seleção por brush em gráfico
  - `QueryBuilderWidget(QWidget)` - Construtor de queries condicionais
  - `SelectionHistoryWidget(QWidget)` - Histórico de seleções
  - `SelectionManagerWidget(QWidget)` - Gerenciador completo de seleções

#### `ui/stream_filters.py`
Widgets de filtros de streaming:
- **Classes:**
  - `StreamFiltersWidget(QWidget)` - Widget principal de filtros
  - `TimeIntervalWidget(QWidget)` - Configuração de intervalos temporais
  - `ValuePredicateWidget(QWidget)` - Configuração de predicados de valor

#### `ui/streaming_controls.py`
- **Classe:** `StreamingControlWidget(QWidget)` - Controles de streaming (play/pause/seek)

#### `ui/video_export.py`
Exportação de animações para vídeo:
- **Classe:** `VideoExportDialog(QDialog)` - Diálogo de exportação
- **Classe:** `VideoExportWorker(BaseWorker)` - Worker assíncrono
- **Classe:** `VideoExportSettings` - Configurações de vídeo
- **Enums:** `VideoFormat` (MP4, AVI, GIF), `VideoQuality` (LOW, MEDIUM, HIGH, ULTRA)
- **Funções:**
  - `show_video_export_dialog(parent, session_state)`
  - `export_video_programmatically(settings, output_path)` - Exportação sem UI

#### `ui/workers/file_worker.py`
- **Classe:** `FileLoadWorker(QObject)` - Worker de carregamento de arquivo
- **Sinais:** `progress(int, str)`, `finished(Dataset)`, `error(str)`
- **Método:** `load_file()` - Carrega arquivo com reporting de progresso

### Pacote: `platform_base/utils/`
Utilitários transversais

#### `utils/errors.py`
Exceções customizadas:
- **Classes:**
  - `PlatformError` - Exceção base
  - `DataLoadError`, `SchemaDetectionError`, `ValidationError`
  - `InterpolationError`, `CalculusError`, `DownsampleError`
  - `PluginError`, `ExportError`, `CacheError`
- **Função:** `handle_error(error, context)` - Handler centralizado

#### `utils/logging.py`
Sistema de logging estruturado:
- **Funções:**
  - `setup_logging(config)` - Setup inicial
  - `configure_logging(level, format, output)` - Configuração dinâmica
  - `get_logger(name)` → Logger - Obtém logger para módulo
- **Integração:** structlog para logging JSON

#### `utils/i18n.py`
Internacionalização:
- **Classe:** `I18n` - Sistema de traduções
- **Funções:**
  - `tr(key, **kwargs)` → str - Traduz chave com interpolação
  - `set_language(lang_code)` - Define idioma (pt-BR, en-US)
  - `get_language()` → str - Idioma atual
  - `get_i18n()` → I18n - Singleton

#### `utils/ids.py`
- **Função:** `new_id(prefix)` → str - Gera UUID prefixado único

#### `utils/serialization.py`
- **Função:** `to_jsonable(obj)` → dict - Converte objetos para JSON-serializável

#### `utils/validation.py`
- **Função:** `validate_config(config, schema)` → ValidationResult - Valida config contra schema

### Pacote: `platform_base/viz/`
Sistema de visualização 2D/3D

#### `viz/base.py`
- **Classe:** `BaseFigure` - Classe base para figuras

#### `viz/config.py`
Configuração de visualização:
- **Classes:**
  - `VizConfig` - Configuração principal de visualização
  - `PlotConfig` - Configuração de plot individual
  - `ColorScheme`, `ColorConfig` - Esquemas de cores
  - `StyleConfig` - Estilos (fontes, linhas, marcadores)
  - `PerformanceConfig` - Otimizações de performance
  - `InteractionConfig`, `InteractivityConfig` - Interatividade
  - `Export2DConfig`, `Export3DConfig` - Configurações de exportação
  - `AxisConfig` - Configuração de eixos
  - `DownsampleStrategy` - Estratégia de downsampling
- **Enums:** `ThemeType`, `RenderMode`, `ColorScale`
- **Funções preset:** `get_default_config()`, `get_dark_config()`, `get_scientific_config()`, `get_high_contrast_config()`

#### `viz/figures_2d.py`
Gráficos 2D com PyQtGraph:
- **Classes:**
  - `Plot2DWidget(QWidget)` - Widget base de plot 2D
  - `TimeseriesPlot(Plot2DWidget)` - Gráfico de séries temporais
  - `ScatterPlot(Plot2DWidget)` - Scatter plot
- **Features:**
  - Brush selection interativa
  - Zoom/pan otimizado
  - Downsampling automático via LTTB
  - Performance para milhões de pontos

#### `viz/figures_3d.py`
Gráficos 3D com PyVista:
- **Classes:**
  - `Plot3DWidget(QWidget)` - Widget base de plot 3D
  - `Trajectory3D(Plot3DWidget)` - Trajetórias 3D
  - `Surface3D(Plot3DWidget)` - Superfícies 3D
  - `VolumetricPlot(Plot3DWidget)` - Visualizações volumétricas

#### `viz/heatmaps.py`
Visualizações de heatmap:
- **Classes:**
  - `HeatmapWidget(QWidget)` - Widget base de heatmap
  - `CorrelationHeatmap(HeatmapWidget)` - Heatmap de correlação
  - `TimeSeriesHeatmap(HeatmapWidget)` - Heatmap temporal
  - `StatisticalHeatmap(HeatmapWidget)` - Heatmap estatístico

#### `viz/multipanel.py`
- Visualizações multi-painel (implementação básica)

#### `viz/state_cube.py`
- **Classe:** `StateCube3D` - Visualização 3D de estados

#### `viz/streaming.py`
Engine de streaming temporal:
- **Classes:**
  - `StreamingEngine` - Motor de streaming temporal
  - `VideoExporter` - Exportador para vídeo
  - `StreamingState` - Estado de streaming
  - `PlayState` - Estado de reprodução
  - `StreamFilters` - Filtros de streaming (temporal, qualidade, valor)
  - `TickUpdate` - Atualização de tick
  - `ViewSubscription` - Inscrição de view para updates
  - `ValuePredicate`, `SmoothConfig`, `ScaleConfig`, `TimeInterval` - Modelos auxiliares
- **Métodos principais:**
  - `setup_data(t_seconds, series_dict)` - Configura dados para streaming
  - `play()`, `pause()`, `stop()` - Controles de reprodução
  - `seek(time)` - Navegação temporal
  - `subscribe_view(view_id, callback)` - Inscrição de callback
  - `set_speed(speed)` - Ajusta velocidade (0.1x a 10x)

---

## I) Testes

### Estrutura de Testes

O projeto possui uma suíte de testes abrangente em **4 níveis** (`tests/`):

#### 1. Testes Unitários: `tests/unit/`
Testes de unidades isoladas (funções, classes):
- `test_interpolation.py` - Testa todos os métodos de interpolação
- `test_advanced_interpolation.py` - Testa MLS, GPR, Lomb-Scargle
- `test_calculus.py` - Derivadas, integrais, área entre curvas
- `test_sync.py` - Sincronização de séries
- `test_lttb_downsampling.py` - Algoritmo LTTB
- `test_smoothing.py` - Algoritmos de suavização
- `test_loader.py` - Carregamento de arquivos
- `test_schema_detector.py` - Detecção de esquema
- `test_registry.py` - Registro de plugins
- `test_disk_cache.py` - Cache em disco
- `test_caching.py` - Cache em memória
- `test_streaming_sync.py` - Sincronização de streaming
- `test_units.py` - Sistema de unidades
- `test_profiling.py` - Sistema de profiling
- `test_numba_optimization.py` - Otimizações Numba

#### 2. Testes de Integração: `tests/integration/`
Testes de fluxos completos:
- `test_pipeline.py` - Pipeline completo (load → interpolate → calculate → visualize)

#### 3. Testes de Stress: `tests/stress/`
Testes de desempenho e limites:
- `test_large_datasets.py` - Datasets com milhões de pontos, múltiplas séries

#### 4. Property-Based Tests: `tests/property/`
Testes baseados em propriedades com Hypothesis:
- `test_calculus_props.py` - Propriedades matemáticas (derivada de integral = identidade, etc.)

### Fixtures de Teste

#### `tests/fixtures/synthetic_data.py`
Geradores de dados sintéticos para testes:
- Séries temporais irregulares
- Dados com gaps controlados
- Múltiplas séries sincronizadas/dessincronizadas

### Execução de Testes

**Framework:** pytest ≥7.3.0 (configurado em `pyproject.toml:dev`)

**Comandos:**

```bash
# Todos os testes
pytest

# Apenas testes unitários
pytest tests/unit/

# Com cobertura
pytest --cov=src/platform_base --cov-report=html

# Paralelo (com pytest-xdist)
pytest -n auto

# Testes de UI (com pytest-qt)
pytest --no-xvfb  # Se em ambiente headless
```

**Configuração no pyproject.toml:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.3.0",
    "pytest-cov>=4.1.0",       # Cobertura
    "pytest-xdist>=3.3.0",     # Paralelização
    "pytest-qt>=4.3.0",        # Testes PyQt6
    "hypothesis>=6.75.0",      # Property-based testing
    ...
]
```

---

## J) Empacotamento/Distribuição

### PyInstaller / cx_Freeze

O projeto está configurado para distribuição standalone via PyInstaller ou cx_Freeze (`pyproject.toml`):

```toml
[project.optional-dependencies]
dist = [
    "pyinstaller>=5.13.0",
    "cx_Freeze>=6.15.0",
]
```

**Instalação de ferramentas de distribuição:**
```bash
pip install -e ".[dist]"
```

### Empacotamento com PyInstaller

**Exemplo básico:**
```bash
pyinstaller --name="PlatformBase" \
            --onefile \
            --windowed \
            --add-data="configs:configs" \
            --add-data="plugins:plugins" \
            --icon="assets/icon.ico" \
            launch_app.py
```

**Considerações:**
- `--windowed`: Oculta console (GUI mode)
- `--add-data`: Inclui diretórios de configuração e plugins
- `--hidden-import`: Pode ser necessário para imports dinâmicos (ex: `--hidden-import=pyvista`)
- PyQt6: Geralmente detectado automaticamente

### Empacotamento com cx_Freeze

**Script setup_cx.py (exemplo):**
```python
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["PyQt6", "numpy", "pandas", "scipy"],
    "include_files": [("configs", "configs"), ("plugins", "plugins")],
    "excludes": []
}

setup(
    name="Platform Base",
    version="2.0.0",
    description="Time Series Analysis Platform",
    options={"build_exe": build_exe_options},
    executables=[Executable("launch_app.py", base="Win32GUI", icon="assets/icon.ico")]
)
```

**Execução:**
```bash
python setup_cx.py build
```

**Nota:** Nenhum script de empacotamento pronto foi detectado no repositório. Os exemplos acima são baseados na presença das dependências no `pyproject.toml`.

---

## K) Troubleshooting

### Problemas Comuns Qt/PyQt6

#### 1. Erro: "Could not find Qt platform plugin"
**Causa:** PyQt6 não encontra plugins de plataforma (Windows/Linux/macOS)

**Solução:**
```bash
# Reinstalar PyQt6
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip
pip install --no-cache-dir PyQt6>=6.5.0

# Verificar variável de ambiente (Linux/macOS)
export QT_QPA_PLATFORM_PLUGIN_PATH=/path/to/pyqt6/plugins
```

#### 2. Erro: "QApplication: no such file or directory"
**Causa:** PyQt6 não instalado ou versão incompatível

**Solução:**
```bash
# Verificar instalação
python -c "from PyQt6.QtWidgets import QApplication; print('OK')"

# Reinstalar se necessário
pip install PyQt6>=6.5.0
```

#### 3. Interface não responde durante carregamento
**Causa:** Operação pesada bloqueando event loop

**Solução:**
- Verificar se `FileLoadWorker` está sendo usado para carregamento (`src/platform_base/ui/workers/file_worker.py`)
- Garantir que operações pesadas rodam em QThread

#### 4. Gráficos não aparecem / PyVista não funciona
**Causa:** Conflito de backends de renderização

**Solução:**
```bash
# Instalar backend correto
pip install pyvistaqt>=0.11.0

# Configurar backend PyVista
import pyvista as pv
pv.set_plot_theme('document')
```

#### 5. HiDPI scaling incorreto (Windows)
**Causa:** Qt não detecta escala corretamente

**Solução:**
```python
# Antes de QApplication (já implementado em launch_app.py)
from PyQt6.QtCore import Qt
# PyQt6 tem HiDPI automático, mas pode forçar:
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
```

### Problemas de Import

#### 1. "ModuleNotFoundError: No module named 'platform_base'"
**Causa:** `src/` não está no PYTHONPATH

**Solução:**
```bash
# Opção 1: Instalação editable
pip install -e .

# Opção 2: Adicionar ao path manualmente (launch_app.py já faz isso)
import sys
sys.path.insert(0, 'src')
```

#### 2. "ImportError: cannot import name 'Dataset'"
**Causa:** Import circular ou módulo não inicializado

**Solução:**
- Verificar imports relativos em `__init__.py`
- Usar `from __future__ import annotations` para type hints
- Imports de tipos podem usar `if TYPE_CHECKING:`

#### 3. Numba não disponível
**Causa:** Numba não instalado ou incompatível

**Solução:**
```bash
# Instalar Numba
pip install numba>=0.57.0

# Código gracefully degrada para NumPy puro se Numba não disponível
# (verificar flags NUMBA_AVAILABLE nos módulos)
```

### Problemas de Paths de Recursos

#### 1. Arquivo YAML de configuração não encontrado
**Causa:** Path relativo incorreto

**Solução:**
```python
# Usar Path absoluto (configs/ deve estar no diretório de execução)
from pathlib import Path
config_path = Path(__file__).parent / "configs" / "platform.yaml"
```

#### 2. Plugins não carregados
**Causa:** Diretório `plugins/` não encontrado

**Solução:**
- Verificar `configs/platform.yaml:plugins.path` aponta para diretório correto
- Garantir `plugins/` está no mesmo diretório de execução
- Verificar `plugins.discovery.enabled: true`

### Problemas de Performance

#### 1. Gráficos lentos com muitos pontos
**Causa:** Downsampling não ativado

**Solução:**
```python
# Ativar downsampling LTTB (já configurado em configs/platform.yaml)
visualization:
  downsampling:
    method: "lttb"
    max_points: 10000  # Ajustar conforme necessidade
```

#### 2. Carregamento de arquivo grande trava UI
**Causa:** Carregamento síncrono

**Solução:**
- Usar `FileLoadWorker` com chunk_size configurado (`src/platform_base/ui/workers/file_worker.py`)
- Configurar `LoadConfig(chunk_size=100000)` para processar em blocos

#### 3. Cache não funciona
**Causa:** Cache desabilitado ou path incorreto

**Solução:**
```yaml
# configs/platform.yaml
performance:
  cache:
    disk:
      enabled: true
      path: ".cache"  # Criar diretório se não existir
```

---

## L) Licença e Contribuição

### Licença
**Nenhum arquivo de licença detectado no repositório.**

**Status:** Projeto sem licença explícita. Por padrão, copyright pertence aos autores originais. Para uso comercial ou distribuição, recomenda-se adicionar licença apropriada (MIT, Apache 2.0, GPL, etc.).

**Referência de Organização:** TRANSPETRO (conforme `launch_app.py:app.setOrganizationName("TRANSPETRO")`)

### Contribuição

**Nenhum arquivo CONTRIBUTING.md detectado no repositório.**

**Diretrizes sugeridas baseadas na estrutura do projeto:**

1. **Código:**
   - Seguir style guides: Black (line-length=100), isort (profile=black)
   - Type hints obrigatórios (mypy strict mode habilitado)
   - Testes obrigatórios para novas funcionalidades
   - Documentação inline (docstrings)

2. **Testes:**
   - Adicionar testes unitários em `tests/unit/`
   - Testes de integração para features complexas
   - Manter cobertura >80%

3. **Commits:**
   - Mensagens descritivas em português ou inglês
   - Um commit por feature/bugfix

4. **Pull Requests:**
   - Descrever mudanças claramente
   - Referenciar issues relacionados
   - Garantir que testes passam

**Ferramentas de desenvolvimento disponíveis:**
```bash
# Instalar dependências de dev
pip install -e ".[dev]"

# Formatação
black src/ tests/
isort src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Testes
pytest --cov=src/platform_base
```

---

## Pontos a Confirmar / TODO

Os seguintes itens foram identificados como ambíguos ou incompletos durante a análise do código:

1. **API REST:** Módulo `api/` existe mas não há evidência de uso ativo. `configs/platform.yaml` define `api.enabled: false`. **Confirmar:** A API REST está planejada para uso futuro ou deve ser removida?

2. **Múltiplas Main Windows:** Existem duas implementações de aplicação desktop:
   - `ui/main_window.py:ModernMainWindow` (usado por `launch_app.py`)
   - `desktop/main_window.py:MainWindow` (usado por `run_app.py`)
   **Confirmar:** Qual é a versão oficial? Há plano de consolidação?

3. **OperationsPanel incompleto:** `ui/panels/operations_panel.py:OperationsPanel` é um placeholder com funcionalidades planejadas. **Confirmar:** Roadmap de implementação?

4. **Plugins DTW duplicados:** Existem dois plugins DTW:
   - `plugins/dtw_plugin/plugin.py`
   - `plugins/advanced_sync/dtw_plugin.py`
   **Confirmar:** São versões diferentes ou redundância? Qual usar?

5. **Backup files:** Arquivos `*_backup.py` em `ui/panels/`. **Confirmar:** Podem ser removidos ou são versionamento manual?

6. **Variáveis de ambiente:** Nenhuma configuração via `.env` ou envvars foi encontrada. **Confirmar:** Há necessidade de suporte futuro para config via ambiente (12-factor app)?

7. **Documentação Sphinx:** `pyproject.toml` inclui `sphinx` nas dependências dev, mas não há diretório `docs/build/` ou `conf.py`. **Confirmar:** Documentação Sphinx está planejada?

8. **Licença e Contribuição:** Sem arquivos LICENSE ou CONTRIBUTING.md. **Confirmar:** Licença a ser adotada e guidelines de contribuição?

9. **Empacotamento:** PyInstaller/cx_Freeze configurados mas sem scripts de build prontos. **Confirmar:** Necessidade de scripts de build automatizados?

10. **Testes de UI:** pytest-qt configurado mas poucos testes de UI em `tests/`. **Confirmar:** Cobertura de testes de interface é prioritária?

11. **I18n Traduções:** Sistema de i18n existe (`utils/i18n.py`) mas dicionários de tradução não foram localizados no repositório. **Confirmar:** Onde devem residir os arquivos de tradução (JSON, YAML)?

12. **Configuração de logging:** `configs/platform.yaml` define `logging.output: "logs/platform.log"` mas diretório `logs/` não existe. **Confirmar:** Criação automática de diretório ou configuração deve ser ajustada?

---

**Fim do README.md**

*Este README foi gerado com base em análise completa do código-fonte (101 módulos) em 25/01/2025. Todas as informações foram extraídas diretamente dos arquivos Python, YAML e TOML do repositório, sem invenção de funcionalidades inexistentes.*

