# Platform Base v2.0 - API Reference

## Documentação da API para Desenvolvedores

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Módulos Core](#módulos-core)
4. [Módulos de UI](#módulos-de-ui)
5. [Módulos de Processamento](#módulos-de-processamento)
6. [Módulos de I/O](#módulos-de-io)
7. [Módulos de Visualização](#módulos-de-visualização)
8. [Sistema de Plugins](#sistema-de-plugins)
9. [Exemplos de Código](#exemplos-de-código)

---

## Visão Geral

O Platform Base é uma aplicação PyQt6 modular para análise de séries temporais. A arquitetura segue padrões de design como:

- **MVC**: Separação de dados, lógica e apresentação
- **Observer**: Sistema de signals/slots do Qt
- **Singleton**: Managers globais (Logger, Theme, Shortcuts)
- **Factory**: Criação de componentes dinâmicos
- **Strategy**: Algoritmos intercambiáveis (filtros, cálculos)

---

## Arquitetura

```
platform_base/
├── core/               # Núcleo da aplicação
│   ├── models.py       # Modelos de dados
│   ├── session.py      # Gerenciamento de sessão
│   └── logger.py       # Sistema de logging
├── desktop/            # Aplicação desktop
│   ├── main_window.py  # Janela principal
│   ├── widgets/        # Widgets customizados
│   └── workers/        # Workers para threading
├── ui/                 # Componentes de UI
│   ├── themes.py       # Sistema de temas
│   ├── shortcuts.py    # Atalhos de teclado
│   └── panels/         # Painéis da interface
├── processing/         # Processamento de dados
│   ├── calculus.py     # Cálculos matemáticos
│   ├── filters.py      # Filtros de sinal
│   └── downsampling.py # Decimação
├── io/                 # Entrada/Saída
│   ├── readers.py      # Leitores de arquivo
│   └── writers.py      # Escritores de arquivo
├── viz/                # Visualização
│   ├── figures_2d.py   # Gráficos 2D
│   └── figures_3d.py   # Gráficos 3D
└── utils/              # Utilitários
    ├── logging.py      # Logging estruturado
    └── i18n.py         # Internacionalização
```

---

## Módulos Core

### `platform_base.core.models`

Modelos de dados principais.

#### `TimeSeries`

```python
from platform_base.core.models import TimeSeries

class TimeSeries:
    """
    Representa uma série temporal.
    
    Attributes:
        series_id: Identificador único
        name: Nome de exibição
        time_data: Array de timestamps
        value_data: Array de valores
        metadata: Metadados adicionais
    """
    
    def __init__(
        self,
        series_id: str,
        name: str,
        time_data: np.ndarray,
        value_data: np.ndarray,
        metadata: dict | None = None,
    ):
        """Inicializa série temporal."""
        
    @property
    def duration(self) -> float:
        """Duração em segundos."""
        
    @property
    def sample_rate(self) -> float:
        """Taxa de amostragem estimada em Hz."""
        
    def slice(self, start: float, end: float) -> TimeSeries:
        """Retorna fatia temporal."""
        
    def resample(self, new_rate: float) -> TimeSeries:
        """Reamostra para nova taxa."""
```

#### `Dataset`

```python
from platform_base.core.models import Dataset

class Dataset:
    """
    Conjunto de séries temporais relacionadas.
    
    Attributes:
        dataset_id: Identificador único
        name: Nome do dataset
        source_file: Arquivo de origem
        series: Dict de TimeSeries
    """
    
    def add_series(self, series: TimeSeries) -> None:
        """Adiciona série ao dataset."""
        
    def remove_series(self, series_id: str) -> None:
        """Remove série do dataset."""
        
    def get_series(self, series_id: str) -> TimeSeries | None:
        """Obtém série por ID."""
```

#### `TimeWindow`

```python
from platform_base.core.models import TimeWindow

@dataclass
class TimeWindow:
    """Janela temporal para seleção."""
    start: float
    end: float
    
    @property
    def duration(self) -> float:
        """Duração da janela."""
        
    def contains(self, time: float) -> bool:
        """Verifica se tempo está na janela."""
        
    def intersection(self, other: TimeWindow) -> TimeWindow | None:
        """Calcula interseção com outra janela."""
```

---

### `platform_base.core.session`

Gerenciamento de sessão.

```python
from platform_base.core.session import SessionManager

class SessionManager:
    """
    Gerencia estado da sessão da aplicação.
    
    Signals:
        session_changed: Emitido quando sessão muda
        dataset_added: Emitido quando dataset é adicionado
        dataset_removed: Emitido quando dataset é removido
    """
    
    def save_session(self, path: Path) -> None:
        """Salva sessão atual em arquivo."""
        
    def load_session(self, path: Path) -> None:
        """Carrega sessão de arquivo."""
        
    def add_dataset(self, dataset: Dataset) -> None:
        """Adiciona dataset à sessão."""
        
    def get_selected_series(self) -> list[TimeSeries]:
        """Retorna séries selecionadas."""
```

---

### `platform_base.utils.logging`

Sistema de logging estruturado.

```python
from platform_base.utils.logging import get_logger, StructuredLogger

# Obter logger para módulo
logger = get_logger(__name__)

# Uso básico
logger.info("operation_started", operation="load", file="data.csv")
logger.error("operation_failed", error=str(e), traceback=True)

# Com contexto
with logger.context(user_id="123", session="abc"):
    logger.info("user_action", action="upload")

# Métricas de timing
with logger.timed("processing"):
    # operação...
    pass
# Log automático: "processing completed in 1.23s"
```

---

## Módulos de UI

### `platform_base.ui.themes`

Sistema de temas visuais.

```python
from platform_base.ui.themes import ThemeManager, ThemeMode

# Obter manager singleton
theme_manager = ThemeManager()

# Mudar tema
theme_manager.set_theme(ThemeMode.DARK)

# Obter cores atuais
colors = theme_manager.current_theme
print(colors.background)  # "#1E1E1E"
print(colors.text)        # "#E0E0E0"

# Aplicar tema a widget
theme_manager.apply_to_widget(my_widget)

# Detectar tema do sistema
system_theme = ThemeManager.detect_system_theme()
```

---

### `platform_base.ui.shortcuts`

Sistema de atalhos de teclado.

```python
from platform_base.ui.shortcuts import ShortcutManager, ShortcutCategory

# Obter manager singleton
shortcuts = ShortcutManager()

# Registrar callback
shortcuts.register_callback("file.save", my_save_function)

# Vincular a QAction
shortcuts.bind_action("file.open", open_action)

# Customizar atalho
shortcuts.set_shortcut("edit.undo", "Ctrl+Shift+Z")

# Verificar conflito
conflict = shortcuts.check_conflict("Ctrl+S")
if conflict:
    print(f"Conflita com: {conflict}")

# Obter atalhos por categoria
file_shortcuts = shortcuts.get_bindings_by_category(ShortcutCategory.FILE)
```

---

### `platform_base.ui.tooltips`

Sistema de tooltips.

```python
from platform_base.ui.tooltips import TooltipManager, apply_standard_tooltips

# Obter manager
tooltips = TooltipManager()

# Registrar tooltip customizado
tooltips.register_tooltip(
    "my_button",
    "Minha ação customizada",
    shortcut="analysis.custom"
)

# Aplicar a widget
tooltips.apply_tooltip(my_button, "my_button")

# Aplicar tooltips padrão em janela
apply_standard_tooltips(main_window)
```

---

## Módulos de Processamento

### `platform_base.processing.calculus`

Cálculos matemáticos.

```python
from platform_base.processing.calculus import (
    calculate_derivative,
    calculate_integral,
    calculate_area,
)

# Derivada
derivative = calculate_derivative(
    time_data,
    value_data,
    method="central"  # "forward", "backward", "central", "spline"
)

# Integral
integral = calculate_integral(
    time_data,
    value_data,
    method="simpson"  # "trapezoid", "simpson", "romberg"
)

# Área sob curva
area = calculate_area(
    time_data,
    value_data,
    start_time=10.0,
    end_time=20.0
)
```

---

### `platform_base.processing.filters`

Filtros de sinal.

```python
from platform_base.processing.filters import (
    lowpass_filter,
    highpass_filter,
    bandpass_filter,
    moving_average,
)

# Filtro passa-baixa
filtered = lowpass_filter(
    data,
    cutoff_freq=10.0,    # Hz
    sample_rate=100.0,   # Hz
    order=4
)

# Filtro passa-alta
filtered = highpass_filter(
    data,
    cutoff_freq=0.5,
    sample_rate=100.0,
    order=2
)

# Filtro passa-banda
filtered = bandpass_filter(
    data,
    low_freq=1.0,
    high_freq=10.0,
    sample_rate=100.0
)

# Média móvel
smoothed = moving_average(data, window_size=5)
```

---

### `platform_base.processing.downsampling`

Decimação de dados.

```python
from platform_base.processing.downsampling import (
    downsample,
    adaptive_downsample,
    lttb_downsample,
)

# Decimação simples (pegar cada N pontos)
decimated = downsample(data, factor=10)

# Decimação adaptativa (preserva features)
decimated = adaptive_downsample(
    data,
    target_points=1000,
    preserve_peaks=True
)

# LTTB (Largest Triangle Three Buckets)
# Melhor para visualização
decimated = lttb_downsample(
    time_data,
    value_data,
    target_points=1000
)
```

---

### `platform_base.processing.lazy_loading`

Carregamento sob demanda.

```python
from platform_base.processing.lazy_loading import (
    LazyDataArray,
    LazyCSVReader,
    LRUCache,
)

# Array lazy
lazy_array = LazyDataArray(
    total_size=1_000_000,
    chunk_size=10_000,
    load_func=my_load_function
)

# Acesso transparente
value = lazy_array[500_000]  # Carrega chunk sob demanda
slice_data = lazy_array[100:200]  # Slice também funciona

# Pré-carregamento
lazy_array.prefetch_range(start=0, end=10000)

# Leitor CSV lazy
reader = LazyCSVReader(Path("large_file.csv"))
column_data = reader.get_column("temperature")
```

---

## Módulos de I/O

### `platform_base.io.readers`

Leitura de arquivos.

```python
from platform_base.io.readers import (
    read_csv,
    read_excel,
    read_matlab,
    auto_detect_format,
)

# CSV
dataset = read_csv(
    Path("data.csv"),
    time_column="timestamp",
    delimiter=",",
    encoding="utf-8"
)

# Excel
dataset = read_excel(
    Path("data.xlsx"),
    sheet_name="Sheet1",
    time_column="Time"
)

# MATLAB
dataset = read_matlab(
    Path("data.mat"),
    time_variable="t"
)

# Auto-detecção
dataset = auto_detect_format(Path("data.unknown"))
```

---

### `platform_base.io.writers`

Escrita de arquivos.

```python
from platform_base.io.writers import (
    write_csv,
    write_excel,
    write_session,
)

# CSV
write_csv(
    dataset,
    Path("output.csv"),
    delimiter=",",
    include_time=True
)

# Excel
write_excel(
    dataset,
    Path("output.xlsx"),
    one_sheet_per_series=True
)

# Sessão completa
write_session(
    session,
    Path("session.warp"),
    compress=True
)
```

---

## Módulos de Visualização

### `platform_base.viz.multi_y_axis`

Múltiplos eixos Y.

```python
from platform_base.viz.multi_y_axis import (
    MultiYAxisManager,
    AxisPosition,
)

# Criar manager
manager = MultiYAxisManager(plot_item)

# Adicionar eixo Y à direita
y2_axis = manager.add_axis(
    AxisPosition.RIGHT_1,
    label="Pressure (Pa)",
    color="#FF0000"
)

# Adicionar série ao eixo específico
manager.add_series(
    "pressure_data",
    time_data,
    pressure_data,
    axis_position=AxisPosition.RIGHT_1,
    pen=pg.mkPen("red")
)

# Mover série entre eixos
manager.move_series(
    "temperature",
    from_position=AxisPosition.LEFT_1,
    to_position=AxisPosition.RIGHT_1
)
```

---

### `platform_base.viz.datetime_axis`

Eixo temporal formatado.

```python
from platform_base.viz.datetime_axis import (
    DateTimeAxisItem,
    DateTimePlotWidget,
    DateTimeFormat,
)

# Criar widget com eixo temporal
widget = DateTimePlotWidget()

# Configurar formato
widget.datetime_axis.set_format(DateTimeFormat.ISO)

# Plotar dados com timestamps
widget.plot_datetime(
    timestamps,  # datetime ou unix timestamps
    values
)

# O formato se adapta automaticamente ao zoom:
# - Zoom out: "2024-01"
# - Zoom médio: "2024-01-15"
# - Zoom in: "2024-01-15 14:30:45"
```

---

## Sistema de Plugins

### Interface de Plugin

```python
from platform_base.plugins import PluginBase, PluginMeta

class MyPlugin(PluginBase):
    """Plugin de exemplo."""
    
    # Metadados
    meta = PluginMeta(
        name="My Analysis Plugin",
        version="1.0.0",
        author="Developer",
        description="Análise customizada"
    )
    
    def activate(self) -> None:
        """Chamado quando plugin é ativado."""
        # Registrar ações, menus, etc.
        self.register_action(
            "my_action",
            "Minha Análise",
            self.run_analysis
        )
    
    def deactivate(self) -> None:
        """Chamado quando plugin é desativado."""
        pass
    
    def run_analysis(self, series: TimeSeries) -> TimeSeries:
        """Executa análise customizada."""
        result = my_custom_algorithm(series.value_data)
        return TimeSeries(
            series_id=f"{series.series_id}_analyzed",
            name=f"Análise de {series.name}",
            time_data=series.time_data,
            value_data=result
        )
```

### Registrando Plugin

```python
# Em plugin_module/__init__.py
from platform_base.plugins import register_plugin
from .my_plugin import MyPlugin

register_plugin(MyPlugin)
```

---

## Exemplos de Código

### Exemplo 1: Carregar e Plotar

```python
from pathlib import Path
from platform_base.io.readers import read_csv
from platform_base.desktop.widgets.viz_panel import Plot2DWidget

# Carregar dados
dataset = read_csv(Path("sensor_data.csv"), time_column="time")

# Criar widget
plot = Plot2DWidget()

# Adicionar séries
for i, series in enumerate(dataset.series.values()):
    plot.add_series(
        series.series_id,
        series.time_data,
        series.value_data,
        series_index=i,
        name=series.name
    )

# Mostrar
plot.show()
```

### Exemplo 2: Análise com Filtro

```python
from platform_base.processing.filters import lowpass_filter
from platform_base.processing.calculus import calculate_derivative

# Carregar dados
series = dataset.get_series("acceleration")

# Filtrar ruído
filtered = lowpass_filter(
    series.value_data,
    cutoff_freq=5.0,
    sample_rate=series.sample_rate
)

# Calcular velocidade (integral da aceleração)
velocity = calculate_integral(
    series.time_data,
    filtered
)

# Criar nova série
velocity_series = TimeSeries(
    series_id="velocity",
    name="Velocidade Calculada",
    time_data=series.time_data,
    value_data=velocity
)
```

### Exemplo 3: Exportar Relatório

```python
from platform_base.io.writers import write_csv, write_excel
from platform_base.processing.statistics import calculate_statistics

# Calcular estatísticas
stats = calculate_statistics(series)

# Criar DataFrame com resultados
import pandas as pd
df = pd.DataFrame({
    "Métrica": ["Mínimo", "Máximo", "Média", "Desvio"],
    "Valor": [stats.min, stats.max, stats.mean, stats.std]
})

# Exportar
df.to_csv("relatorio.csv", index=False)
```

---

## Constantes e Configurações

### `platform_base.config`

```python
# Limites padrão
MAX_POINTS_DISPLAY = 100_000
MAX_MEMORY_MB = 500
DEFAULT_CACHE_SIZE = 100

# Cores padrão
DEFAULT_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
]

# Intervalos
AUTO_SAVE_INTERVAL_MS = 5 * 60 * 1000  # 5 minutos
TOOLTIP_DELAY_MS = 500
```

---

## Changelog

### v2.0.0 (2026-01)

- Sistema de temas (dark mode)
- Multi-Y axis (até 4 eixos)
- Eixo datetime formatado
- Lazy loading para arquivos grandes
- Sistema de atalhos customizáveis
- Logging estruturado
- Auto-save e crash recovery
- Tooltips completos
- Validação de integridade de arquivos
- Monitoramento de memória

---

*API Reference - Platform Base v2.0*  
*Última atualização: Janeiro 2026*
