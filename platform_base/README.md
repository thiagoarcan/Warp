# Platform Base v2.0

[![CI Pipeline](https://github.com/thiagoarcan/Warp/actions/workflows/ci.yml/badge.svg)](https://github.com/thiagoarcan/Warp/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Plataforma de análise exploratória para séries temporais irregulares**

## Features

- ✅ Upload multi-formato (CSV/Excel/Parquet/HDF5)
- ✅ 10 métodos de interpolação (linear a avançados) 
- ✅ Sincronização de múltiplas séries temporais
- ✅ Cálculos matemáticos (derivadas 1ª-3ª, integrais, áreas)
- ✅ Visualização 2D/3D interativa com Plotly
- ✅ Streaming temporal com filtros avançados
- ✅ Extensibilidade via plugins com isolamento
- ✅ Export assíncrono para múltiplos formatos
- ✅ Cache multi-nível para performance
- ✅ Logging estruturado e observabilidade

## Instalação

```bash
# Instalação básica
pip install -e .

# Com dependências de visualização
pip install -e ".[viz]"

# Para desenvolvimento
pip install -e ".[dev]"
```

## Quickstart

### Exemplo Básico

```python
from platform_base.io.loader import load_dataset
from platform_base.processing.interpolation import interpolate
from platform_base.viz.figures_2d import TimeseriesPlot

# Carregar dados
dataset = load_dataset("sensor_data.csv")

# Interpolar gaps
series_id = next(iter(dataset.series))
series = dataset.series[series_id]

result = interpolate(
    series.values,
    dataset.t_seconds,
    method="spline_cubic",
    params={}
)

# Visualizar
config = PlotConfig(title="Dados de Sensor")
plot = TimeseriesPlot(config)
figure = plot.render(view_data)
```

### Streaming Temporal

```python
from platform_base.viz.streaming import StreamingEngine, StreamingState
from platform_base.viz.streaming import TimeInterval

# Configurar filtros avançados
filters = StreamFilters(
    time_exclude=[TimeInterval(start=1000, end=2000)],  # pular intervalo
    max_points_per_window=5000,
    hide_interpolated=True
)

# Criar sessão de streaming  
state = StreamingState(filters=filters, speed=2.0)
engine = StreamingEngine(state)
engine.setup_data(dataset.t_seconds)

# Controles
engine.play()    # iniciar
engine.pause()   # pausar  
engine.seek(1500.0)  # pular para tempo específico
```

### Exportação

```python
from platform_base.ui.export import export_selection_async
from platform_base.core.dataset_store import DatasetStore

# Export assíncrono para grandes datasets
result = await export_selection_async(
    view_data=view_data,
    format="parquet",
    output_path=Path("resultado.parquet")
)

print(f"Exportado: {result.rows_exported} linhas em {result.export_time_seconds:.2f}s")
```

## Arquitetura

### Modelos de Dados

- **Dataset**: Conjunto de séries temporais com timestamps compartilhados
- **Series**: Sequência de valores com timestamps e metadados  
- **Lineage**: Rastreamento completo de origem de séries derivadas
- **ViewData**: Subset de dados preparado para visualização

### Processamento

- **Interpolação**: 7 métodos core + plugins avançados
- **Sincronização**: Alinhamento de múltiplas séries temporais
- **Cálculos**: Derivadas 1ª-3ª ordem, integrais, áreas entre curvas
- **Suavização**: Filtros opcionais pré-processamento

### Extensibilidade

- **Plugins**: Sistema baseado em Protocols com descoberta controlada
- **Registry**: Validação de interface e versionamento
- **Isolamento**: Execução segura via subprocess (opcional)

## Performance

O platform_base foi otimizado para datasets com milhões de pontos:

- **Operações vetorizadas**: Zero loops Python em hotpaths
- **Cache multi-nível**: LRU + disk cache com TTL configurável  
- **Paralelismo**: ProcessPoolExecutor configurável
- **Downsampling**: LTTB preservando features críticos
- **Numba**: JIT compilation em hotspots identificados

## Configuração

Toda configuração é centralizada em `configs/platform.yaml`:

```yaml
platform:
  version: "2.0.0"

processing:
  interpolation:
    default_method: "linear"
    available_methods: [linear, spline_cubic, smoothing_spline]
  
performance:
  parallelism:
    max_workers: 4
  cache:
    disk:
      enabled: true
      ttl_hours: 24
      max_size_gb: 10

streaming:
  default_speed: 1.0
  window_size_seconds: 60
  filters:
    max_points_per_window: 5000
```

## Development

### Setup

```bash
git clone <repository>
cd platform_base
pip install -e ".[dev]"
```

### Testes

```bash
# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/ 

# Testes de stress
pytest tests/stress/

# Coverage
pytest --cov=src/ --cov-report=html
```

### Qualidade de Código

```bash
# Formatação
black src/ tests/
isort src/ tests/

# Linting  
flake8 src/ tests/
mypy src/
```

## Documentação

- [API Reference](docs/api_reference.md)
- [Architecture](docs/architecture.md) 
- [Plugin Development](docs/plugin_development.md)
- [Examples](docs/examples/)

## Contribuindo

Ver [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT
