# TODO LIST - TESTES PARA 95% DE COBERTURA

**Platform Base v2.0**  
**Data: 02 de Fevereiro de 2026**  
**Meta: Cobertura mínima de 95%**

---

## ⚡ ESTRATÉGIAS DE OTIMIZAÇÃO

| Técnica | Comando | Ganho |
|---------|---------|-------|
| **Paralelização** | `pytest -n auto` (pytest-xdist) | 3-4x mais rápido |
| **Cache de testes** | `pytest --cache-show` | Pula testes inalterados |
| **Execução incremental** | `pytest --lf` (last failed) | Foca em falhas |
| **Sampling (mutação)** | `mutmut run --runner="pytest -x"` | Fail-fast |
| **Fuzzing em background** | Execução paralela separada | Não bloqueia |
| **CI paralelo** | GitHub Actions matrix | Múltiplos jobs |

---

## 📋 SUMÁRIO DE EXECUÇÃO (OTIMIZADO)

| # | Categoria | Sequencial | **Otimizado** | Técnica | Status |
|---|-----------|------------|---------------|---------|--------|
| 1 | Análise Estática | 30 min | **5 min** | Paralelo (4 ferramentas simultâneas) | ⬜ |
| 2 | Testes de Documentação | 1 hora | **10 min** | `pytest -n auto --doctest-modules` | ⬜ |
| 3 | Testes Unitários | 2 horas | **15 min** | `pytest -n 8` (8 workers) | ⬜ |
| 4 | Property-based Testing | 1.5 horas | **20 min** | `--hypothesis-seed` + cache | ⬜ |
| 5 | Testes de Contrato/Schema | 1 hora | **8 min** | Paralelo + Pydantic v2 | ⬜ |
| 6 | Testes de Integração | 2 horas | **25 min** | `pytest -n 4` (menos paralelo, mais I/O) | ⬜ |
| 7 | Testes de Snapshot/Golden | 1 hora | **5 min** | Comparação hash rápida | ⬜ |
| 8 | Testes de Concorrência | 1.5 horas | **15 min** | Timeout curto + sampling | ⬜ |
| 9 | Cobertura | 30 min | **0 min** | Executado junto com unitários | ⬜ |
| 10 | Testes de Performance | 45 min | **10 min** | `--benchmark-disable-gc` + warmup | ⬜ |
| 11 | Testes de Mutação | 4 horas | **45 min** | `mutmut -n 8` + sampling 20% | ⬜ |
| 12 | Fuzzing | 8 horas | **30 min** | Sampling + corpus reuse (CI: 4h bg) | ⬜ |
| 13 | Testes de Configuração | 2 horas | **15 min** | GitHub Actions matrix paralelo | ⬜ |

### Comparação de Tempo

| Modo | Tempo Total |
|------|-------------|
| Sequencial (original) | ~25 horas |
| **Otimizado (local)** | **~3 horas** |
| **CI paralelo (GitHub Actions)** | **~45 min** |

**Redução**: 88% local, 97% em CI

---

## 1. ANÁLISE ESTÁTICA

### 1.1 Type Checking (mypy)

**Comando**: `mypy src/platform_base --strict`

| # | Tarefa | Arquivo/Módulo | Status |
|---|--------|----------------|--------|
| 1.1.1 | [ ] Configurar mypy.ini com strict mode | `mypy.ini` | ⬜ |
| 1.1.2 | [ ] Verificar tipos em `core/models.py` | `core/` | ⬜ |
| 1.1.3 | [ ] Verificar tipos em `processing/calculus.py` | `processing/` | ⬜ |
| 1.1.4 | [ ] Verificar tipos em `processing/interpolation.py` | `processing/` | ⬜ |
| 1.1.5 | [ ] Verificar tipos em `processing/downsampling.py` | `processing/` | ⬜ |
| 1.1.6 | [ ] Verificar tipos em `processing/synchronization.py` | `processing/` | ⬜ |
| 1.1.7 | [ ] Verificar tipos em `io/loader.py` | `io/` | ⬜ |
| 1.1.8 | [ ] Verificar tipos em `io/export.py` | `io/` | ⬜ |
| 1.1.9 | [ ] Verificar tipos em `desktop/main_window.py` | `desktop/` | ⬜ |
| 1.1.10 | [ ] Verificar tipos em `desktop/signal_hub.py` | `desktop/` | ⬜ |
| 1.1.11 | [ ] Verificar tipos em `desktop/session_state.py` | `desktop/` | ⬜ |
| 1.1.12 | [ ] Verificar tipos em `desktop/workers/` | `desktop/workers/` | ⬜ |
| 1.1.13 | [ ] Verificar tipos em `ui/panels/` | `ui/panels/` | ⬜ |
| 1.1.14 | [ ] Verificar tipos em `ui/undo_redo.py` | `ui/` | ⬜ |
| 1.1.15 | [ ] Resolver todos os erros de tipo | Global | ⬜ |

**Critério de Aceitação**: 0 erros de mypy com `--strict`

---

### 1.2 Linting (ruff)

**Comando**: `ruff check src/platform_base --fix`

| # | Tarefa | Regra | Status |
|---|--------|-------|--------|
| 1.2.1 | [ ] Configurar ruff.toml com regras completas | `ruff.toml` | ⬜ |
| 1.2.2 | [ ] Habilitar regras E (pycodestyle errors) | E | ⬜ |
| 1.2.3 | [ ] Habilitar regras W (pycodestyle warnings) | W | ⬜ |
| 1.2.4 | [ ] Habilitar regras F (pyflakes) | F | ⬜ |
| 1.2.5 | [ ] Habilitar regras I (isort) | I | ⬜ |
| 1.2.6 | [ ] Habilitar regras N (pep8-naming) | N | ⬜ |
| 1.2.7 | [ ] Habilitar regras D (pydocstyle) | D | ⬜ |
| 1.2.8 | [ ] Habilitar regras UP (pyupgrade) | UP | ⬜ |
| 1.2.9 | [ ] Habilitar regras B (flake8-bugbear) | B | ⬜ |
| 1.2.10 | [ ] Habilitar regras C4 (flake8-comprehensions) | C4 | ⬜ |
| 1.2.11 | [ ] Habilitar regras SIM (flake8-simplify) | SIM | ⬜ |
| 1.2.12 | [ ] Corrigir todos os erros de linting | Global | ⬜ |

**Critério de Aceitação**: 0 erros de ruff

---

### 1.3 Segurança (bandit)

**Comando**: `bandit -r src/platform_base -ll`

| # | Tarefa | Severidade | Status |
|---|--------|------------|--------|
| 1.3.1 | [ ] Configurar .bandit com exclusões válidas | `.bandit` | ⬜ |
| 1.3.2 | [ ] Verificar B101 (assert statements) | LOW | ⬜ |
| 1.3.3 | [ ] Verificar B102 (exec statements) | HIGH | ⬜ |
| 1.3.4 | [ ] Verificar B301 (pickle usage) | MEDIUM | ⬜ |
| 1.3.5 | [ ] Verificar B403 (import pickle) | LOW | ⬜ |
| 1.3.6 | [ ] Verificar B608 (SQL injection) | HIGH | ⬜ |
| 1.3.7 | [ ] Verificar B701 (jinja2 autoescape) | HIGH | ⬜ |
| 1.3.8 | [ ] Corrigir todas as vulnerabilidades HIGH | Global | ⬜ |
| 1.3.9 | [ ] Corrigir todas as vulnerabilidades MEDIUM | Global | ⬜ |
| 1.3.10 | [ ] Documentar exceções justificadas | `SECURITY.md` | ⬜ |

**Critério de Aceitação**: 0 vulnerabilidades HIGH/MEDIUM

---

### 1.4 Código Morto (vulture)

**Comando**: `vulture src/platform_base --min-confidence 80`

| # | Tarefa | Módulo | Status |
|---|--------|--------|--------|
| 1.4.1 | [ ] Instalar vulture | `pip install vulture` | ⬜ |
| 1.4.2 | [ ] Criar whitelist.py para falsos positivos | `vulture_whitelist.py` | ⬜ |
| 1.4.3 | [ ] Identificar funções não utilizadas em `core/` | `core/` | ⬜ |
| 1.4.4 | [ ] Identificar funções não utilizadas em `processing/` | `processing/` | ⬜ |
| 1.4.5 | [ ] Identificar funções não utilizadas em `io/` | `io/` | ⬜ |
| 1.4.6 | [ ] Identificar funções não utilizadas em `desktop/` | `desktop/` | ⬜ |
| 1.4.7 | [ ] Identificar funções não utilizadas em `ui/` | `ui/` | ⬜ |
| 1.4.8 | [ ] Identificar variáveis não utilizadas | Global | ⬜ |
| 1.4.9 | [ ] Identificar imports não utilizados | Global | ⬜ |
| 1.4.10 | [ ] Remover ou documentar código morto | Global | ⬜ |

**Critério de Aceitação**: < 5% de código morto reportado

---

## 2. TESTES DE DOCUMENTAÇÃO (Doctests)

**Comando**: `pytest --doctest-modules src/platform_base`

| # | Tarefa | Arquivo | Exemplos | Status |
|---|--------|---------|----------|--------|
| 2.1 | [ ] Adicionar doctests em `calculus.py` | `processing/calculus.py` | 10 | ⬜ |
| 2.2 | [ ] Adicionar doctests em `interpolation.py` | `processing/interpolation.py` | 8 | ⬜ |
| 2.3 | [ ] Adicionar doctests em `downsampling.py` | `processing/downsampling.py` | 6 | ⬜ |
| 2.4 | [ ] Adicionar doctests em `synchronization.py` | `processing/synchronization.py` | 5 | ⬜ |
| 2.5 | [ ] Adicionar doctests em `smoothing.py` | `processing/smoothing.py` | 5 | ⬜ |
| 2.6 | [ ] Adicionar doctests em `loader.py` | `io/loader.py` | 4 | ⬜ |
| 2.7 | [ ] Adicionar doctests em `validator.py` | `io/validator.py` | 4 | ⬜ |
| 2.8 | [ ] Adicionar doctests em `models.py` | `core/models.py` | 8 | ⬜ |
| 2.9 | [ ] Adicionar doctests em `units.py` | `core/units.py` | 5 | ⬜ |
| 2.10 | [ ] Adicionar doctests em `i18n.py` | `utils/i18n.py` | 3 | ⬜ |
| 2.11 | [ ] Adicionar doctests em `validation.py` | `utils/validation.py` | 5 | ⬜ |
| 2.12 | [ ] Adicionar doctests em `serialization.py` | `utils/serialization.py` | 4 | ⬜ |

**Critério de Aceitação**: 100% dos doctests passando, ~67 exemplos

### Exemplo de Doctest Esperado

```python
def derivative(t: np.ndarray, y: np.ndarray, order: int = 1) -> np.ndarray:
    """
    Calcula a derivada numérica de uma série temporal.
    
    Args:
        t: Array de timestamps
        y: Array de valores
        order: Ordem da derivada (1, 2 ou 3)
    
    Returns:
        Array com valores da derivada
    
    Examples:
        >>> import numpy as np
        >>> t = np.array([0.0, 1.0, 2.0, 3.0])
        >>> y = np.array([0.0, 1.0, 4.0, 9.0])  # y = t²
        >>> dy = derivative(t, y, order=1)
        >>> np.allclose(dy, [1.0, 2.0, 4.0, 6.0], atol=0.5)
        True
    """
```

---

## 3. TESTES UNITÁRIOS

**Comando**: `pytest tests/unit/ -v --cov=src/platform_base`

### 3.1 Casos Normais (Happy Path)

| # | Tarefa | Arquivo de Teste | Casos | Status |
|---|--------|------------------|-------|--------|
| 3.1.1 | [ ] Testar derivative() com dados lineares | `test_calculus.py` | 5 | ⬜ |
| 3.1.2 | [ ] Testar integral() com dados constantes | `test_calculus.py` | 5 | ⬜ |
| 3.1.3 | [ ] Testar interpolate_linear() | `test_interpolation.py` | 5 | ⬜ |
| 3.1.4 | [ ] Testar interpolate_spline() | `test_interpolation.py` | 5 | ⬜ |
| 3.1.5 | [ ] Testar lttb_downsample() | `test_downsampling.py` | 5 | ⬜ |
| 3.1.6 | [ ] Testar synchronize() | `test_synchronization.py` | 5 | ⬜ |
| 3.1.7 | [ ] Testar load_csv() | `test_loader.py` | 5 | ⬜ |
| 3.1.8 | [ ] Testar load_xlsx() | `test_loader.py` | 5 | ⬜ |
| 3.1.9 | [ ] Testar export_csv() | `test_export.py` | 5 | ⬜ |
| 3.1.10 | [ ] Testar SignalHub signals | `test_signal_hub.py` | 10 | ⬜ |

### 3.2 Casos de Borda (Edge Cases)

| # | Tarefa | Arquivo de Teste | Casos | Status |
|---|--------|------------------|-------|--------|
| 3.2.1 | [ ] Testar derivative() com 2 pontos | `test_calculus.py` | 3 | ⬜ |
| 3.2.2 | [ ] Testar derivative() com NaN | `test_calculus.py` | 3 | ⬜ |
| 3.2.3 | [ ] Testar integral() com array vazio | `test_calculus.py` | 2 | ⬜ |
| 3.2.4 | [ ] Testar interpolate() com 1 ponto | `test_interpolation.py` | 2 | ⬜ |
| 3.2.5 | [ ] Testar downsample() para tamanho maior | `test_downsampling.py` | 2 | ⬜ |
| 3.2.6 | [ ] Testar load_csv() com arquivo vazio | `test_loader.py` | 2 | ⬜ |
| 3.2.7 | [ ] Testar load_csv() com encoding errado | `test_loader.py` | 2 | ⬜ |
| 3.2.8 | [ ] Testar export() sem permissão de escrita | `test_export.py` | 2 | ⬜ |
| 3.2.9 | [ ] Testar Series com valores extremos (1e308) | `test_models.py` | 2 | ⬜ |
| 3.2.10 | [ ] Testar TimeWindow com start > end | `test_models.py` | 2 | ⬜ |

### 3.3 Testes de Exceção

| # | Tarefa | Arquivo de Teste | Exceção | Status |
|---|--------|------------------|---------|--------|
| 3.3.1 | [ ] `derivative()` com array 0 elementos | `test_calculus.py` | `ValueError` | ⬜ |
| 3.3.2 | [ ] `derivative()` com order=0 | `test_calculus.py` | `ValueError` | ⬜ |
| 3.3.3 | [ ] `derivative()` com order=4 | `test_calculus.py` | `ValueError` | ⬜ |
| 3.3.4 | [ ] `integral()` com method inválido | `test_calculus.py` | `ValueError` | ⬜ |
| 3.3.5 | [ ] `load_csv()` arquivo não existe | `test_loader.py` | `FileNotFoundError` | ⬜ |
| 3.3.6 | [ ] `load_csv()` arquivo corrompido | `test_loader.py` | `LoaderError` | ⬜ |
| 3.3.7 | [ ] `interpolate()` com t não monotônico | `test_interpolation.py` | `ValueError` | ⬜ |
| 3.3.8 | [ ] `synchronize()` com séries vazias | `test_sync.py` | `ValueError` | ⬜ |
| 3.3.9 | [ ] `Dataset` com series_id duplicado | `test_models.py` | `ValueError` | ⬜ |
| 3.3.10 | [ ] `export()` formato não suportado | `test_export.py` | `ValueError` | ⬜ |

### 3.4 Testes Parametrizados

| # | Tarefa | Arquivo de Teste | Parâmetros | Status |
|---|--------|------------------|------------|--------|
| 3.4.1 | [ ] `derivative()` com orders [1,2,3] | `test_calculus.py` | 3 | ⬜ |
| 3.4.2 | [ ] `derivative()` com methods ['finite_diff', 'savgol', 'spline'] | `test_calculus.py` | 3 | ⬜ |
| 3.4.3 | [ ] `integral()` com methods ['trapezoid', 'simpson', 'cumulative'] | `test_calculus.py` | 3 | ⬜ |
| 3.4.4 | [ ] `interpolate()` com methods ['linear', 'spline', 'akima', 'pchip'] | `test_interpolation.py` | 4 | ⬜ |
| 3.4.5 | [ ] `load()` com formats ['csv', 'xlsx', 'parquet'] | `test_loader.py` | 3 | ⬜ |
| 3.4.6 | [ ] `export()` com formats ['csv', 'xlsx', 'parquet', 'hdf5'] | `test_export.py` | 4 | ⬜ |
| 3.4.7 | [ ] `smooth()` com methods ['gaussian', 'savgol', 'moving_avg'] | `test_smoothing.py` | 3 | ⬜ |
| 3.4.8 | [ ] `downsample()` com ratios [2, 5, 10, 100] | `test_downsampling.py` | 4 | ⬜ |
| 3.4.9 | [ ] SignalHub com signal_types [10 tipos] | `test_signal_hub.py` | 10 | ⬜ |
| 3.4.10 | [ ] Units com conversions [15 conversões] | `test_units.py` | 15 | ⬜ |

**Critério de Aceitação**: 100% dos testes unitários passando (~250 testes)

---

## 4. PROPERTY-BASED TESTING (Hypothesis)

**Comando**: `pytest tests/property/ -v --hypothesis-show-statistics`

| # | Tarefa | Arquivo de Teste | Propriedade | Status |
|---|--------|------------------|-------------|--------|
| 4.1 | [ ] `derivative` + `integral` ≈ original | `test_prop_calculus.py` | Inversa | ⬜ |
| 4.2 | [ ] `derivative` de constante ≈ 0 | `test_prop_calculus.py` | Zero | ⬜ |
| 4.3 | [ ] `derivative` de linear = constante | `test_prop_calculus.py` | Linear | ⬜ |
| 4.4 | [ ] `integral` preserva monoticidade | `test_prop_calculus.py` | Monotonic | ⬜ |
| 4.5 | [ ] `interpolate` passa pelos pontos originais | `test_prop_interp.py` | Passthrough | ⬜ |
| 4.6 | [ ] `interpolate` preserva range | `test_prop_interp.py` | Bounded | ⬜ |
| 4.7 | [ ] `downsample(n)` retorna exatamente n pontos | `test_prop_downsample.py` | Size | ⬜ |
| 4.8 | [ ] `downsample` preserva primeiro e último | `test_prop_downsample.py` | Endpoints | ⬜ |
| 4.9 | [ ] `synchronize` alinha timestamps | `test_prop_sync.py` | Alignment | ⬜ |
| 4.10 | [ ] `load` → `export` → `load` = original | `test_prop_io.py` | Roundtrip | ⬜ |
| 4.11 | [ ] `Series.values` sempre tem len == timestamps | `test_prop_models.py` | Consistency | ⬜ |
| 4.12 | [ ] `TimeWindow.duration` sempre >= 0 | `test_prop_models.py` | NonNegative | ⬜ |
| 4.13 | [ ] `smooth` não aumenta amplitude | `test_prop_smooth.py` | Bounded | ⬜ |
| 4.14 | [ ] `units.convert` é reversível | `test_prop_units.py` | Reversible | ⬜ |
| 4.15 | [ ] `undo` + `redo` restaura estado | `test_prop_undo.py` | Inverse | ⬜ |

**Critério de Aceitação**: Todas as propriedades verificadas com 100+ exemplos cada

### Exemplo de Property Test

```python
from hypothesis import given, strategies as st
import numpy as np

@given(
    t=st.lists(st.floats(0, 100), min_size=10, max_size=1000).map(sorted).map(np.array),
    y=st.lists(st.floats(-1e6, 1e6), min_size=10, max_size=1000).map(np.array)
)
def test_derivative_integral_inverse(t, y):
    """Integral da derivada deve aproximar original (menos constante)"""
    if len(t) != len(y):
        y = y[:len(t)]
    dy = derivative(t, y)
    y_reconstructed = integral(t, dy) + y[0]
    assert np.allclose(y, y_reconstructed, rtol=0.1)
```

---

## 5. TESTES DE CONTRATO/SCHEMA

**Comando**: `pytest tests/contract/ -v`

### 5.1 Validação Pydantic

| # | Tarefa | Model | Validações | Status |
|---|--------|-------|------------|--------|
| 5.1.1 | [ ] Validar `Dataset` schema | `Dataset` | 8 | ⬜ |
| 5.1.2 | [ ] Validar `Series` schema | `Series` | 6 | ⬜ |
| 5.1.3 | [ ] Validar `TimeWindow` schema | `TimeWindow` | 4 | ⬜ |
| 5.1.4 | [ ] Validar `SelectionState` schema | `SelectionState` | 5 | ⬜ |
| 5.1.5 | [ ] Validar `SourceInfo` schema | `SourceInfo` | 5 | ⬜ |
| 5.1.6 | [ ] Validar `SeriesMetadata` schema | `SeriesMetadata` | 4 | ⬜ |
| 5.1.7 | [ ] Validar `DataQualityMetrics` schema | `DataQualityMetrics` | 6 | ⬜ |
| 5.1.8 | [ ] Validar `InterpolationResult` schema | `InterpolationResult` | 5 | ⬜ |
| 5.1.9 | [ ] Validar `SyncResult` schema | `SyncResult` | 5 | ⬜ |
| 5.1.10 | [ ] Validar `ExportConfig` schema | `ExportConfig` | 4 | ⬜ |

### 5.2 Contratos de API Interna

| # | Tarefa | Função/Método | Contrato | Status |
|---|--------|---------------|----------|--------|
| 5.2.1 | [ ] `derivative()` input/output contract | `calculus.py` | Types | ⬜ |
| 5.2.2 | [ ] `integral()` input/output contract | `calculus.py` | Types | ⬜ |
| 5.2.3 | [ ] `interpolate()` input/output contract | `interpolation.py` | Types | ⬜ |
| 5.2.4 | [ ] `load_file()` return contract | `loader.py` | Dataset | ⬜ |
| 5.2.5 | [ ] `export_data()` input contract | `export.py` | Types | ⬜ |
| 5.2.6 | [ ] `SignalHub.emit_*()` contracts | `signal_hub.py` | Signals | ⬜ |
| 5.2.7 | [ ] `ProcessingWorker.run()` contract | `workers/` | Result | ⬜ |
| 5.2.8 | [ ] `SessionState.save/load` contract | `session_state.py` | JSON | ⬜ |

**Critério de Aceitação**: 100% dos schemas validados, 0 violações de contrato

---

## 6. TESTES DE INTEGRAÇÃO

**Comando**: `pytest tests/integration/ -v`

### 6.1 Integração de Componentes

| # | Tarefa | Componentes | Status |
|---|--------|-------------|--------|
| 6.1.1 | [ ] Loader → Dataset → Series | IO → Core | ⬜ |
| 6.1.2 | [ ] Dataset → Calculus → Result | Core → Processing | ⬜ |
| 6.1.3 | [ ] Dataset → Interpolation → Dataset | Core → Processing | ⬜ |
| 6.1.4 | [ ] Dataset → Downsample → Dataset | Core → Processing | ⬜ |
| 6.1.5 | [ ] Dataset → Export → File | Core → IO | ⬜ |
| 6.1.6 | [ ] SignalHub → Workers → Results | Desktop → Processing | ⬜ |
| 6.1.7 | [ ] SessionState → Save → Load → SessionState | Desktop → IO | ⬜ |
| 6.1.8 | [ ] OperationsPanel → Signal → Worker → Result | UI → Desktop | ⬜ |
| 6.1.9 | [ ] DataPanel → Selection → VizPanel | UI → Desktop | ⬜ |
| 6.1.10 | [ ] StreamingPanel → Timer → VizPanel | UI → Desktop | ⬜ |

### 6.2 Integração de Pipeline Completo

| # | Tarefa | Pipeline | Status |
|---|--------|----------|--------|
| 6.2.1 | [ ] CSV → Load → Interpolate → Derivative → Export CSV | Full | ⬜ |
| 6.2.2 | [ ] XLSX → Load → Smooth → Downsample → Export XLSX | Full | ⬜ |
| 6.2.3 | [ ] Parquet → Load → Sync → Calculate → Export Parquet | Full | ⬜ |
| 6.2.4 | [ ] Multiple Files → Load → Combine → Analyze → Export | Full | ⬜ |
| 6.2.5 | [ ] Load → Stream → Filter → Visualize | Streaming | ⬜ |

### 6.3 Integração GUI (com pytest-qt)

| # | Tarefa | Componentes GUI | Status |
|---|--------|-----------------|--------|
| 6.3.1 | [ ] MainWindow inicializa corretamente | MainWindow | ⬜ |
| 6.3.2 | [ ] Menu File → Open executa loader | Menu → IO | ⬜ |
| 6.3.3 | [ ] DataPanel checkbox → VizPanel visibility | Panel → Panel | ⬜ |
| 6.3.4 | [ ] OperationsPanel button → Calculation | Panel → Processing | ⬜ |
| 6.3.5 | [ ] Context Menu → Action execution | Menu → Action | ⬜ |
| 6.3.6 | [ ] Streaming controls → Playback | Panel → Timer | ⬜ |
| 6.3.7 | [ ] Undo/Redo menu → State change | Menu → UndoStack | ⬜ |
| 6.3.8 | [ ] Export dialog → File creation | Dialog → IO | ⬜ |

**Critério de Aceitação**: 100% dos testes de integração passando (~40 testes)

---

## 7. TESTES DE SNAPSHOT/GOLDEN

**Comando**: `pytest tests/snapshot/ -v --snapshot-update` (primeira vez)

| # | Tarefa | Arquivo Golden | Tipo | Status |
|---|--------|----------------|------|--------|
| 7.1 | [ ] Snapshot de derivative() output | `golden/derivative_linear.npy` | NumPy | ⬜ |
| 7.2 | [ ] Snapshot de integral() output | `golden/integral_sine.npy` | NumPy | ⬜ |
| 7.3 | [ ] Snapshot de interpolate() output | `golden/interpolate_spline.npy` | NumPy | ⬜ |
| 7.4 | [ ] Snapshot de downsample() output | `golden/downsample_lttb.npy` | NumPy | ⬜ |
| 7.5 | [ ] Snapshot de load_csv() Dataset | `golden/dataset_sample.json` | JSON | ⬜ |
| 7.6 | [ ] Snapshot de export_csv() output | `golden/export_sample.csv` | CSV | ⬜ |
| 7.7 | [ ] Snapshot de SessionState serializado | `golden/session_state.json` | JSON | ⬜ |
| 7.8 | [ ] Snapshot de SyncResult | `golden/sync_result.json` | JSON | ⬜ |
| 7.9 | [ ] Snapshot de DataQualityMetrics | `golden/quality_metrics.json` | JSON | ⬜ |
| 7.10 | [ ] Snapshot de InterpolationResult | `golden/interp_result.json` | JSON | ⬜ |

**Critério de Aceitação**: 100% dos snapshots correspondem às referências

### Exemplo de Snapshot Test

```python
def test_derivative_snapshot(snapshot):
    """Verifica que derivative produz resultado consistente"""
    t = np.linspace(0, 10, 100)
    y = np.sin(t)
    result = derivative(t, y)
    snapshot.assert_match(result.tolist(), 'derivative_sine')
```

---

## 8. TESTES DE CONCORRÊNCIA

**Comando**: `pytest tests/concurrency/ -v -n auto`

### 8.1 Testes Async

| # | Tarefa | Componente | Cenário | Status |
|---|--------|------------|---------|--------|
| 8.1.1 | [ ] Múltiplos workers simultâneos | Workers | 5 workers | ⬜ |
| 8.1.2 | [ ] Load + Process em paralelo | IO + Processing | 2 threads | ⬜ |
| 8.1.3 | [ ] Export enquanto processa | IO + Processing | 2 threads | ⬜ |
| 8.1.4 | [ ] Streaming + Calculation | UI + Processing | 2 threads | ⬜ |
| 8.1.5 | [ ] Múltiplos signals simultâneos | SignalHub | 10 signals | ⬜ |

### 8.2 Race Conditions

| # | Tarefa | Componente | Cenário | Status |
|---|--------|------------|---------|--------|
| 8.2.1 | [ ] SessionState access from multiple threads | SessionState | 4 threads | ⬜ |
| 8.2.2 | [ ] DatasetStore concurrent add/remove | DatasetStore | 4 threads | ⬜ |
| 8.2.3 | [ ] SignalHub emit during connect/disconnect | SignalHub | 4 threads | ⬜ |
| 8.2.4 | [ ] UndoStack push during undo | UndoStack | 2 threads | ⬜ |
| 8.2.5 | [ ] Worker cancel during execution | Workers | 2 threads | ⬜ |
| 8.2.6 | [ ] Cache write during read | Cache | 4 threads | ⬜ |
| 8.2.7 | [ ] VizPanel update during series add | VizPanel | 2 threads | ⬜ |
| 8.2.8 | [ ] StreamingPanel seek during play | StreamingPanel | 2 threads | ⬜ |

**Critério de Aceitação**: 0 deadlocks, 0 race conditions detectadas

### Exemplo de Concurrency Test

```python
import threading
import pytest

def test_session_state_thread_safety():
    """Verifica que SessionState é thread-safe"""
    state = SessionState()
    errors = []
    
    def writer():
        for i in range(100):
            try:
                state.set_selection(f"dataset_{i}", [f"series_{i}"])
            except Exception as e:
                errors.append(e)
    
    threads = [threading.Thread(target=writer) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0, f"Thread safety violated: {errors}"
```

---

## 9. COBERTURA (Coverage)

**Comando**: `pytest tests/ --cov=src/platform_base --cov-report=html --cov-fail-under=95`

| # | Módulo | Cobertura Atual | Meta | Status |
|---|--------|-----------------|------|--------|
| 9.1 | [ ] `core/` | ~92% | 95% | ⬜ |
| 9.2 | [ ] `processing/` | ~98% | 95% | ✅ |
| 9.3 | [ ] `io/` | ~95% | 95% | ✅ |
| 9.4 | [ ] `desktop/` | ~85% | 95% | ⬜ |
| 9.5 | [ ] `ui/` | ~80% | 95% | ⬜ |
| 9.6 | [ ] `viz/` | ~75% | 95% | ⬜ |
| 9.7 | [ ] `utils/` | ~90% | 95% | ⬜ |
| 9.8 | [ ] `caching/` | ~88% | 95% | ⬜ |
| 9.9 | [ ] `streaming/` | ~82% | 95% | ⬜ |
| 9.10 | [ ] **TOTAL** | ~87% | **95%** | ⬜ |

### Arquivos que Precisam de Mais Cobertura

| Arquivo | Cobertura | Linhas Faltando |
|---------|-----------|-----------------|
| `desktop/main_window.py` | 78% | 250 |
| `desktop/widgets/viz_panel.py` | 72% | 200 |
| `ui/panels/streaming_panel.py` | 75% | 150 |
| `viz/figures_3d.py` | 65% | 180 |
| `desktop/menus/plot_context_menu.py` | 80% | 200 |

**Critério de Aceitação**: Cobertura global ≥ 95%

---

## 10. TESTES DE PERFORMANCE/BENCHMARK

**Comando**: `pytest tests/performance/ -v --benchmark-autosave`

| # | Tarefa | Função | Baseline | Meta | Status |
|---|--------|--------|----------|------|--------|
| 10.1 | [ ] `derivative()` 10K pontos | `derivative` | 2ms | <5ms | ⬜ |
| 10.2 | [ ] `derivative()` 100K pontos | `derivative` | 15ms | <50ms | ⬜ |
| 10.3 | [ ] `derivative()` 1M pontos | `derivative` | 150ms | <500ms | ⬜ |
| 10.4 | [ ] `integral()` 1M pontos | `integral` | 100ms | <500ms | ⬜ |
| 10.5 | [ ] `interpolate_linear()` 100K pontos | `interpolate` | 50ms | <200ms | ⬜ |
| 10.6 | [ ] `interpolate_spline()` 100K pontos | `interpolate` | 200ms | <500ms | ⬜ |
| 10.7 | [ ] `lttb_downsample()` 1M→10K | `downsample` | 500ms | <1s | ⬜ |
| 10.8 | [ ] `synchronize()` 3 séries 100K | `sync` | 1s | <2s | ⬜ |
| 10.9 | [ ] `load_csv()` 10MB | `load` | 500ms | <2s | ⬜ |
| 10.10 | [ ] `load_xlsx()` 10MB | `load` | 2s | <5s | ⬜ |
| 10.11 | [ ] `export_csv()` 1M rows | `export` | 1s | <3s | ⬜ |
| 10.12 | [ ] `smooth_gaussian()` 100K | `smooth` | 20ms | <100ms | ⬜ |
| 10.13 | [ ] VizPanel render 100K pontos | `render` | 100ms | <200ms | ⬜ |
| 10.14 | [ ] VizPanel render 1M pontos | `render` | 300ms | <500ms | ⬜ |
| 10.15 | [ ] SessionState save 10 datasets | `save` | 200ms | <500ms | ⬜ |

**Critério de Aceitação**: 100% dos benchmarks dentro da meta

---

## 11. TESTES DE MUTAÇÃO

**Comando**: `mutmut run --paths-to-mutate=src/platform_base/processing/`

### 11.1 Mutação em Módulos Críticos

| # | Tarefa | Módulo | Mutantes | Kill Rate Meta | Status |
|---|--------|--------|----------|----------------|--------|
| 11.1.1 | [ ] Mutar `calculus.py` | `processing/` | ~100 | >90% | ⬜ |
| 11.1.2 | [ ] Mutar `interpolation.py` | `processing/` | ~80 | >90% | ⬜ |
| 11.1.3 | [ ] Mutar `downsampling.py` | `processing/` | ~60 | >90% | ⬜ |
| 11.1.4 | [ ] Mutar `synchronization.py` | `processing/` | ~50 | >90% | ⬜ |
| 11.1.5 | [ ] Mutar `smoothing.py` | `processing/` | ~40 | >90% | ⬜ |
| 11.1.6 | [ ] Mutar `loader.py` | `io/` | ~70 | >85% | ⬜ |
| 11.1.7 | [ ] Mutar `validator.py` | `io/` | ~50 | >85% | ⬜ |
| 11.1.8 | [ ] Mutar `models.py` | `core/` | ~60 | >85% | ⬜ |

### 11.2 Análise de Mutantes Sobreviventes

| # | Tarefa | Status |
|---|--------|--------|
| 11.2.1 | [ ] Identificar mutantes sobreviventes | ⬜ |
| 11.2.2 | [ ] Criar testes para matar mutantes | ⬜ |
| 11.2.3 | [ ] Documentar mutantes equivalentes | ⬜ |
| 11.2.4 | [ ] Atingir kill rate > 90% em processing/ | ⬜ |
| 11.2.5 | [ ] Atingir kill rate > 85% em io/ | ⬜ |

**Critério de Aceitação**: Kill rate ≥ 85% global, ≥ 90% em `processing/`

---

## 12. FUZZING

**Comando**: `python -m atheris tests/fuzz/fuzz_loader.py` (execução prolongada)

| # | Tarefa | Target | Duração | Status |
|---|--------|--------|---------|--------|
| 12.1 | [ ] Fuzz `load_csv()` com dados aleatórios | `io/loader.py` | 2h | ⬜ |
| 12.2 | [ ] Fuzz `load_xlsx()` com dados aleatórios | `io/loader.py` | 2h | ⬜ |
| 12.3 | [ ] Fuzz `derivative()` com arrays extremos | `processing/calculus.py` | 1h | ⬜ |
| 12.4 | [ ] Fuzz `interpolate()` com timestamps inválidos | `processing/interpolation.py` | 1h | ⬜ |
| 12.5 | [ ] Fuzz JSON deserialization | `core/models.py` | 1h | ⬜ |
| 12.6 | [ ] Fuzz `validate_file()` | `io/validator.py` | 1h | ⬜ |

**Critério de Aceitação**: 0 crashes não tratados após 8h de fuzzing

### Exemplo de Fuzzer

```python
import atheris
import sys

with atheris.instrument_imports():
    from platform_base.io.loader import load_csv

def fuzz_csv_loader(data):
    """Fuzz test para CSV loader"""
    try:
        # Criar arquivo temporário com dados fuzzed
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            f.write(data)
            f.flush()
            try:
                load_csv(f.name)
            except (ValueError, IOError):
                pass  # Exceções esperadas
    except Exception as e:
        if not isinstance(e, (ValueError, IOError, UnicodeDecodeError)):
            raise  # Crash inesperado

if __name__ == "__main__":
    atheris.Setup(sys.argv, fuzz_csv_loader)
    atheris.Fuzz()
```

---

## 13. TESTES DE CONFIGURAÇÃO/AMBIENTE

**Comando**: `tox` ou `nox`

### 13.1 Múltiplas Versões Python

| # | Tarefa | Python Version | Status |
|---|--------|----------------|--------|
| 13.1.1 | [ ] Testar com Python 3.12 | 3.12 | ⬜ |
| 13.1.2 | [ ] Testar com Python 3.13 | 3.13 | ⬜ |
| 13.1.3 | [ ] Testar com Python 3.14-dev | 3.14 | ⬜ |

### 13.2 Múltiplos Sistemas Operacionais

| # | Tarefa | OS | Status |
|---|--------|---|--------|
| 13.2.1 | [ ] Testar em Windows 11 | Windows | ⬜ |
| 13.2.2 | [ ] Testar em Ubuntu 22.04 | Linux | ⬜ |
| 13.2.3 | [ ] Testar em macOS 14 | macOS | ⬜ |

### 13.3 Configuração de tox.ini

```ini
[tox]
envlist = py312, py313, lint, type

[testenv]
deps = 
    pytest
    pytest-cov
    pytest-qt
    hypothesis
commands = pytest tests/ --cov=src/platform_base

[testenv:lint]
deps = ruff
commands = ruff check src/

[testenv:type]
deps = mypy
commands = mypy src/platform_base --strict
```

**Critério de Aceitação**: Todos os testes passam em Python 3.12+ e Windows/Linux

---

## 📊 RESUMO FINAL

### Totais de Testes por Categoria

| Categoria | Testes Estimados |
|-----------|------------------|
| Análise Estática | ~50 verificações |
| Doctests | ~67 exemplos |
| Unitários | ~250 testes |
| Property-based | ~15 propriedades × 100 exemplos |
| Contrato/Schema | ~50 validações |
| Integração | ~40 testes |
| Snapshot | ~10 comparações |
| Concorrência | ~15 cenários |
| Performance | ~15 benchmarks |
| Mutação | ~500 mutantes |
| Fuzzing | ~8 horas contínuas |
| Config/Ambiente | ~6 combinações |

### Ordem de Execução Recomendada

```
1. Análise Estática (30 min)
   └── Deve passar 100% antes de continuar

2. Doctests (1 hora)
   └── Valida documentação e exemplos

3. Unitários (2 horas)
   └── Base da pirâmide de testes

4. Property-based (1.5 horas)
   └── Encontra edge cases automaticamente

5. Contrato/Schema (1 hora)
   └── Valida interfaces entre componentes

6. Integração (2 horas)
   └── Valida fluxos completos

7. Snapshot (1 hora)
   └── Detecta regressões de output

8. Concorrência (1.5 horas)
   └── Valida thread-safety

9. Cobertura (30 min)
   └── Meta: ≥95%

10. Performance (45 min)
    └── Valida SLAs de tempo

11. Mutação (4 horas)
    └── Valida qualidade dos testes

12. Fuzzing (8 horas - background)
    └── Encontra crashes inesperados

13. Config/Ambiente (2 horas)
    └── Valida portabilidade
```

### Critérios Globais de Sucesso

| Critério | Valor |
|----------|-------|
| Cobertura de código | ≥ 95% |
| Testes passando | 100% |
| Erros mypy | 0 |
| Erros ruff | 0 |
| Vulnerabilidades bandit HIGH | 0 |
| Kill rate mutação | ≥ 85% |
| Benchmarks dentro da meta | 100% |
| Race conditions | 0 |
| Crashes de fuzzing | 0 |

---

*TODO List gerada em: 02/02/2026*  
*Baseada em: RELATORIO_TESTES_COMPLETO.md*  
*Meta: 95% de cobertura*
