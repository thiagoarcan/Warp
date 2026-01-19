# Platform Base Plugins System

Sistema de plugins para extensão da Platform Base v2.0 com isolamento, validação e hot-reloading conforme especificado no PRD seção 14.

## Arquitetura

### Plugin Protocol

Todos os plugins devem implementar o `PluginProtocol`:

```python
from platform_base.plugins.base import PluginProtocol
from platform_base.core.models import ProcessingResult

class MyPlugin(PluginProtocol):
    def execute(self, inputs: dict) -> ProcessingResult:
        """Executa processamento principal do plugin"""
        pass
    
    def validate_inputs(self, inputs: dict) -> bool:
        """Valida entradas antes da execução"""
        pass
    
    def get_manifest(self) -> dict:
        """Retorna metadados do plugin"""
        pass
```

### Estrutura de Diretórios

```
plugins/
├── README.md                    # Este arquivo
├── template/                    # Template para novos plugins
│   ├── manifest.json
│   ├── plugin_template.py
│   └── README.md
├── advanced_sync/               # Plugin DTW exemplo
│   ├── manifest.json
│   ├── dtw_plugin.py
│   ├── README.md
│   └── examples/
│       └── dtw_example.py
└── custom_filters/              # Plugin de filtros customizados
    ├── manifest.json
    ├── filters_plugin.py
    └── README.md
```

## Manifest Schema (v1.0)

Cada plugin deve ter um `manifest.json` seguindo este schema:

```json
{
  "plugin_id": "unique_plugin_id",
  "version": "1.0.0",
  "core_min_version": "2.0.0",
  "core_max_version": null,
  "requires": ["numpy", "scipy"],
  "produces": ["result_type"],
  "entry_point": "module.PluginClass",
  "description": "Plugin description",
  "author": "Author Name",
  "license": "MIT",
  "tags": ["tag1", "tag2"],
  "documentation": {
    "readme": "README.md",
    "examples": ["examples/example.py"]
  },
  "configuration": {
    "param_name": {
      "type": "string|integer|float|boolean|array",
      "default": null,
      "options": ["opt1", "opt2"],
      "description": "Parameter description"
    }
  }
}
```

## Desenvolvimento de Plugins

### 1. Criar Estrutura

```bash
# Copiar template
cp -r plugins/template plugins/meu_plugin

# Renomear arquivos
mv plugins/meu_plugin/plugin_template.py plugins/meu_plugin/meu_plugin.py
```

### 2. Implementar Plugin

```python
from platform_base.plugins.base import PluginProtocol
from platform_base.core.models import ProcessingResult
import numpy as np

class MeuPlugin(PluginProtocol):
    def __init__(self):
        self.config = {}
    
    def execute(self, inputs: dict) -> ProcessingResult:
        """Implementa a lógica principal"""
        series = inputs["series"]
        params = inputs.get("params", {})
        
        # Seu processamento aqui
        result = self._processar(series, params)
        
        return ProcessingResult(
            values=result,
            metadata={"plugin": "meu_plugin"}
        )
    
    def validate_inputs(self, inputs: dict) -> bool:
        """Valida entradas"""
        required = ["series"]
        return all(key in inputs for key in required)
    
    def get_manifest(self) -> dict:
        """Retorna metadados"""
        return {
            "plugin_id": "meu_plugin",
            "version": "1.0.0",
            "description": "Meu plugin customizado"
        }
    
    def _processar(self, series, params):
        """Lógica de processamento interna"""
        return np.array(series) * 2  # Exemplo simples
```

### 3. Configurar Manifest

```json
{
  "plugin_id": "meu_plugin",
  "version": "1.0.0",
  "core_min_version": "2.0.0",
  "requires": ["numpy"],
  "produces": ["processed_series"],
  "entry_point": "meu_plugin.MeuPlugin",
  "description": "Plugin de exemplo que dobra os valores",
  "author": "Seu Nome",
  "configuration": {
    "multiplier": {
      "type": "float",
      "default": 2.0,
      "description": "Fator de multiplicação"
    }
  }
}
```

### 4. Adicionar Testes

```python
# tests/test_meu_plugin.py
import pytest
from plugins.meu_plugin.meu_plugin import MeuPlugin

def test_plugin_execution():
    plugin = MeuPlugin()
    inputs = {"series": [1, 2, 3, 4]}
    
    result = plugin.execute(inputs)
    
    assert result.values.tolist() == [2, 4, 6, 8]

def test_plugin_validation():
    plugin = MeuPlugin()
    
    assert plugin.validate_inputs({"series": [1, 2, 3]}) == True
    assert plugin.validate_inputs({"other": [1, 2, 3]}) == False
```

## Plugin Registry

### Carregamento Automático

```python
from platform_base.plugins.registry import PluginRegistry

registry = PluginRegistry()
registry.discover_plugins("plugins/")
registry.load_all()

# Listar plugins disponíveis
plugins = registry.list_plugins()
for plugin_info in plugins:
    print(f"{plugin_info['id']}: {plugin_info['description']}")
```

### Execução Isolada

```python
# Executar plugin com isolamento
result = registry.execute_plugin(
    plugin_id="dtw_align",
    inputs={
        "reference": ref_series,
        "target": target_series
    },
    params={
        "distance_metric": "euclidean",
        "window_size": 100
    },
    timeout=30  # Timeout em segundos
)
```

## Isolamento e Segurança

### Sandboxing

- **Process Isolation**: Cada plugin roda em processo separado
- **Resource Limits**: CPU, memory e tempo limitados
- **Network Access**: Controlado via configuração
- **File System**: Acesso restrito a diretórios específicos

### Configuração de Segurança

```yaml
# config/plugins.yaml
security:
  enable_sandboxing: true
  default_timeout: 30
  max_memory_mb: 512
  max_cpu_percent: 50
  allowed_modules:
    - numpy
    - scipy
    - pandas
  blocked_modules:
    - os
    - subprocess
    - socket
```

## Hot-Reloading

### Desenvolvimento Dinâmico

```python
# Registry suporta hot-reload automaticamente
registry.enable_hot_reload()

# Modificar plugin no disco
# -> Reload automático detectado
# -> Plugin recarregado sem restart
```

### Versionamento

```python
# Carregar versão específica
registry.load_plugin("dtw_align", version="1.0.0")

# Atualizar para nova versão
registry.update_plugin("dtw_align", version="1.1.0")
```

## Plugins Incluídos

### 1. DTW Alignment (advanced_sync)

**Funcionalidade**: Dynamic Time Warping para sincronização avançada

```python
inputs = {
    "reference": reference_series,
    "target": target_series
}
params = {
    "distance_metric": "euclidean",
    "window_size": 100,
    "step_pattern": "symmetric"
}
```

**Saída**: Série alinhada + informações de warping path

### 2. TWED Distance (time_elastic)

**Funcionalidade**: Time Warp Edit Distance

```python
inputs = {
    "series1": first_series,
    "series2": second_series
}
params = {
    "nu": 1.0,
    "lambda": 1.0
}
```

**Saída**: Distância TWED + matriz de custo

### 3. Custom Filters (signal_processing)

**Funcionalidade**: Filtros digitais customizados

```python
inputs = {
    "series": input_series
}
params = {
    "filter_type": "butterworth",
    "cutoff": 0.1,
    "order": 4
}
```

## Debugging e Profiling

### Logs Detalhados

```python
import logging
logging.getLogger('platform_base.plugins').setLevel(logging.DEBUG)

# Logs incluem:
# - Plugin loading/unloading
# - Execution times
# - Memory usage
# - Error stacktraces
```

### Performance Monitoring

```python
# Registry coleta métricas automaticamente
stats = registry.get_plugin_stats("dtw_align")
print(f"Execuções: {stats['execution_count']}")
print(f"Tempo médio: {stats['avg_execution_time']:.3f}s")
print(f"Uso de memória: {stats['memory_usage_mb']:.1f}MB")
```

## Melhores Práticas

### 1. Design do Plugin

- **Single Responsibility**: Um plugin = uma funcionalidade
- **Idempotência**: Mesmas entradas = mesmo resultado
- **Error Handling**: Falhas gracefuls com mensagens claras
- **Documentação**: README completo + docstrings

### 2. Performance

- **Lazy Loading**: Carregar dependências apenas quando necessário
- **Caching**: Cache resultados custosos internamente
- **Numba/Cython**: Use JIT compilation para hotspots
- **Memory Management**: Libere recursos grandes explicitamente

### 3. Compatibilidade

- **Versioning**: Use semantic versioning (x.y.z)
- **Backward Compatibility**: Mantenha compatibilidade entre minor versions
- **Graceful Degradation**: Funcione com dependências opcionais ausentes
- **Testing**: Testes abrangentes em multiple environments

### 4. Configuração

- **Defaults Sensatos**: Parâmetros que funcionem na maioria dos casos
- **Validação**: Valide tipos e ranges de parâmetros
- **Documentação**: Documente cada parâmetro claramente
- **Environment Aware**: Adapte-se ao ambiente (dev/prod)

## Solução de Problemas

### Plugin Não Carrega

1. Verificar `manifest.json` sintaxe
2. Confirmar `entry_point` correto
3. Verificar dependências instaladas
4. Checar logs de erro detalhados

### Erro de Execução

1. Validar inputs com `validate_inputs()`
2. Verificar configuração de parâmetros
3. Testar isoladamente fora do registry
4. Revisar logs de sandboxing

### Performance Baixa

1. Ativar profiling detalhado
2. Verificar gargalos de I/O
3. Considerar otimizações Numba
4. Revisar uso de memória

## API Reference

### PluginProtocol

```python
class PluginProtocol(Protocol):
    def execute(self, inputs: dict) -> ProcessingResult: ...
    def validate_inputs(self, inputs: dict) -> bool: ...
    def get_manifest(self) -> dict: ...
```

### PluginRegistry

```python
class PluginRegistry:
    def discover_plugins(self, path: str) -> None: ...
    def load_plugin(self, plugin_id: str, version: str = None) -> None: ...
    def execute_plugin(self, plugin_id: str, inputs: dict, params: dict = None) -> ProcessingResult: ...
    def list_plugins(self) -> List[dict]: ...
    def unload_plugin(self, plugin_id: str) -> None: ...
```

## Roadmap

- [ ] **v1.1**: Plugin marketplace integration
- [ ] **v1.2**: GPU plugins support (CUDA/OpenCL)
- [ ] **v1.3**: Distributed plugin execution
- [ ] **v1.4**: Plugin composition pipelines
- [ ] **v2.0**: Machine learning plugins framework

---

Para mais informações, consulte a documentação completa em `/docs/plugins/` ou abra uma issue no repositório.
