# Platform Base v2.0 - Guia de Desenvolvimento de Plugins

**Guia completo para desenvolver plugins customizados**

---

## Índice

1. [Introdução](#introdução)
2. [Arquitetura de Plugins](#arquitetura-de-plugins)
3. [Início Rápido](#início-rápido)
4. [Tipos de Plugins](#tipos-de-plugins)
5. [Referência da API](#referência-da-api)
6. [Exemplos](#exemplos)
7. [Testando Plugins](#testando-plugins)
8. [Distribuição](#distribuição)
9. [Boas Práticas](#boas-práticas)
10. [Solução de Problemas](#solução-de-problemas)

---

## Introdução

O Platform Base suporta um sistema de plugins que permite estender funcionalidades sem modificar o código principal. Plugins podem:

- Adicionar operações customizadas de processamento de dados
- Criar novos tipos de visualização
- Implementar carregadores de formatos de arquivo customizados
- Adicionar painéis e diálogos de UI
- Integrar ferramentas e serviços externos

### Recursos do Sistema de Plugins

- ✅ **Hot reloading** - Carregue plugins sem reiniciar
- ✅ **Isolamento** - Plugins executam em processo separado (opcional)
- ✅ **Segurança de tipo** - Type hints e validação completos
- ✅ **Auto-descoberta** - Detecção automática de plugins
- ✅ **Tratamento de erros** - Falha graciosa sem travar a aplicação
- ✅ **Metadados** - Informações de versão, dependências, descrições

---

## Arquitetura de Plugins

### Estrutura de Plugin

```
meu_plugin/
├── __init__.py           # Ponto de entrada do plugin
├── plugin.yaml           # Metadados do plugin
├── operations.py         # Operações customizadas
├── ui.py                 # Componentes de UI (opcional)
├── tests/               # Testes unitários (opcional)
│   └── test_operations.py
└── README.md            # Documentação
```

### Ciclo de Vida do Plugin

```
1. Descoberta → 2. Validação → 3. Carregamento → 4. Registro → 5. Execução
```

### Registro de Plugins

Plugins se registram no `PluginRegistry` central:

```python
from platform_base.plugins.registry import PluginRegistry

registry = PluginRegistry()
registry.register_plugin(MeuPlugin)
```

---

## Início Rápido

### Crie Seu Primeiro Plugin (5 minutos)

#### Passo 1: Criar Diretório do Plugin

```bash
mkdir meu_primeiro_plugin
cd meu_primeiro_plugin
```

#### Passo 2: Criar plugin.yaml

```yaml
name: meu_primeiro_plugin
version: 1.0.0
author: Seu Nome
description: Meu primeiro plugin do Platform Base
type: operation
entry_point: meu_primeiro_plugin:MeuPlugin

dependencies:
  - numpy>=1.24.0
  - scipy>=1.10.0

platform_base_version: ">=2.0.0"
```

#### Passo 3: Criar __init__.py

```python
"""Meu Primeiro Plugin - Suavização simples de dados."""

from platform_base.plugins.base import OperationPlugin
from platform_base.core.models import Series
import numpy as np


class MeuPlugin(OperationPlugin):
    """Plugin de suavização de dados simples."""
    
    name = "Suavização Simples"
    description = "Suaviza dados usando média móvel"
    category = "Filtros"
    
    def get_parameters(self):
        """Define parâmetros do plugin."""
        return {
            "window_size": {
                "type": "int",
                "default": 5,
                "min": 3,
                "max": 100,
                "description": "Tamanho da janela de média móvel"
            }
        }
    
    def execute(self, series: Series, params: dict) -> Series:
        """Executa operação do plugin."""
        window = params["window_size"]
        
        # Calcula média móvel
        smoothed = np.convolve(
            series.values,
            np.ones(window) / window,
            mode='same'
        )
        
        # Retorna nova série
        return Series(
            series_id=f"{series.series_id}_smoothed",
            name=f"{series.name} (Suavizado)",
            values=smoothed,
            unit=series.unit
        )


# Exporta classe do plugin
__plugin__ = MeuPlugin
```

#### Passo 4: Instalar Plugin

```bash
# Da raiz do Platform Base
python -m platform_base.plugins install /caminho/para/meu_primeiro_plugin
```

#### Passo 5: Usar Plugin

1. Inicie o Platform Base
2. Carregue dados
3. Selecione série
4. Operações → Filtros → Suavização Simples
5. Defina tamanho da janela → Aplicar

**Parabéns!** Você criou seu primeiro plugin!

---

## Tipos de Plugins

### 1. Plugins de Operação

Processam dados e retornam resultados.

**Classe Base**: `OperationPlugin`

**Exemplo**: Derivada, Integral, Filtro Customizado

```python
from platform_base.plugins.base import OperationPlugin
from platform_base.core.models import Series

class PluginDerivada(OperationPlugin):
    name = "Derivada Customizada"
    category = "Cálculo"
    
    def get_parameters(self):
        return {
            "order": {"type": "int", "default": 1}
        }
    
    def execute(self, series: Series, params: dict) -> Series:
        # Implementação
        pass
```

### 2. Plugins de Visualização

Criam tipos de gráficos customizados.

**Classe Base**: `VisualizationPlugin`

**Exemplo**: Gráfico 3D customizado, Mapa de calor, Waterfall

```python
from platform_base.plugins.base import VisualizationPlugin

class PluginMapaCalor(VisualizationPlugin):
    name = "Mapa de Calor Customizado"
    category = "Gráficos 2D"
    
    def create_plot(self, data, params):
        # Cria figura matplotlib/plotly
        pass
```

### 3. Plugins de Carregamento

Suportam formatos de arquivo customizados.

**Classe Base**: `LoaderPlugin`

**Exemplo**: Formato binário customizado, Conexão com banco de dados

```python
from platform_base.plugins.base import LoaderPlugin
from platform_base.core.models import Dataset

class CarregadorFormatoCustomizado(LoaderPlugin):
    name = "Formato Customizado"
    extensions = [".meuformato"]
    
    def load(self, filepath: str) -> Dataset:
        # Analisa arquivo e retorna Dataset
        pass
```

### 4. Plugins de Exportação

Exportam dados em formatos customizados.

**Classe Base**: `ExportPlugin`

**Exemplo**: Formato de relatório customizado, Upload para API

```python
from platform_base.plugins.base import ExportPlugin

class ExportadorCustomizado(ExportPlugin):
    name = "Exportação Customizada"
    extensions = [".custom"]
    
    def export(self, dataset, filepath: str):
        # Escreve dados em arquivo
        pass
```

### 5. Plugins de UI

Adicionam painéis e diálogos customizados.

**Classe Base**: `UIPlugin`

**Exemplo**: Painel de estatísticas, Dashboard de qualidade de dados

```python
from platform_base.plugins.base import UIPlugin
from PyQt6.QtWidgets import QWidget

class PluginPainelEstatisticas(UIPlugin):
    name = "Painel de Estatísticas"
    location = "right"
    
    def create_widget(self) -> QWidget:
        # Cria e retorna widget Qt
        pass
```

---

## Referência da API

### Classes Base de Plugins

#### OperationPlugin

```python
class OperationPlugin:
    """Classe base para operações de dados."""
    
    name: str                    # Nome de exibição
    description: str             # Descrição curta
    category: str                # Categoria para o menu
    
    def get_parameters(self) -> dict:
        """Retorna definições de parâmetros."""
        pass
    
    def validate_input(self, series: Series) -> bool:
        """Valida dados de entrada (opcional)."""
        return True
    
    def execute(self, series: Series, params: dict) -> Series:
        """Executa operação e retorna resultado."""
        pass
    
    def get_preview(self, series: Series, params: dict) -> Series:
        """Retorna resultado de preview (opcional)."""
        return self.execute(series, params)
```

#### Tipos de Parâmetros

```python
# Parâmetro inteiro
{
    "param_name": {
        "type": "int",
        "default": 10,
        "min": 1,
        "max": 100,
        "description": "Descrição do parâmetro"
    }
}

# Parâmetro float
{
    "frequency": {
        "type": "float",
        "default": 1.0,
        "min": 0.1,
        "max": 100.0,
        "step": 0.1,
        "description": "Frequência de corte (Hz)"
    }
}

# Parâmetro de escolha
{
    "method": {
        "type": "choice",
        "options": ["linear", "cubic", "quintic"],
        "default": "cubic",
        "description": "Método de interpolação"
    }
}

# Parâmetro booleano
{
    "normalize": {
        "type": "bool",
        "default": False,
        "description": "Normalizar saída"
    }
}
```

### Modelos Principais

#### Series

```python
from platform_base.core.models import Series

series = Series(
    series_id="unique_id",
    name="Nome de Exibição",
    values=np.array([1, 2, 3]),
    unit="m/s",
    metadata={"sensor": "IMU-001"}
)

# Propriedades
series.values       # array numpy
series.name         # str
series.unit         # str
series.metadata     # dict
```

#### Dataset

```python
from platform_base.core.models import Dataset, Series

dataset = Dataset(
    dataset_id="ds_001",
    name="Nome do Dataset",
    series={"s1": series1, "s2": series2},
    t_seconds=np.array([0, 0.1, 0.2]),
    metadata={"source": "file.csv"}
)

# Propriedades
dataset.series      # dict[str, Series]
dataset.t_seconds   # array numpy
dataset.metadata    # dict
```

---

## Exemplos

### Exemplo 1: Plugin FFT

```python
"""Plugin de Análise FFT."""

from platform_base.plugins.base import OperationPlugin
from platform_base.core.models import Series
import numpy as np
from scipy import fft


class PluginFFT(OperationPlugin):
    """Calcula Transformada Rápida de Fourier."""
    
    name = "Análise FFT"
    description = "Calcula espectro de frequência"
    category = "Processamento de Sinal"
    
    def get_parameters(self):
        return {
            "window": {
                "type": "choice",
                "options": ["hann", "hamming", "blackman", "none"],
                "default": "hann",
                "description": "Função de janela"
            },
            "normalize": {
                "type": "bool",
                "default": True,
                "description": "Normalizar amplitudes"
            }
        }
    
    def execute(self, series: Series, params: dict) -> Series:
        """Calcula FFT."""
        # Obtém parâmetros
        window_type = params["window"]
        normalize = params["normalize"]
        
        # Aplica janela
        if window_type != "none":
            window = getattr(np, window_type)(len(series.values))
            windowed = series.values * window
        else:
            windowed = series.values
        
        # Calcula FFT
        spectrum = fft.rfft(windowed)
        amplitudes = np.abs(spectrum)
        
        # Normaliza se solicitado
        if normalize:
            amplitudes = amplitudes / np.max(amplitudes)
        
        # Cria série resultado
        return Series(
            series_id=f"{series.series_id}_fft",
            name=f"{series.name} (FFT)",
            values=amplitudes,
            unit="normalized" if normalize else series.unit
        )
```

### Exemplo 2: Plugin de Detecção de Picos

```python
"""Plugin de Detecção de Picos."""

from platform_base.plugins.base import OperationPlugin
from platform_base.core.models import Series
from scipy.signal import find_peaks
import numpy as np


class PluginDeteccaoPicos(OperationPlugin):
    """Detecta picos no sinal."""
    
    name = "Detecção de Picos"
    category = "Análise"
    
    def get_parameters(self):
        return {
            "height": {
                "type": "float",
                "default": 0.5,
                "min": 0.0,
                "description": "Altura mínima do pico"
            },
            "distance": {
                "type": "int",
                "default": 10,
                "min": 1,
                "description": "Distância mínima entre picos"
            },
            "prominence": {
                "type": "float",
                "default": 0.1,
                "min": 0.0,
                "description": "Proeminência mínima do pico"
            }
        }
    
    def execute(self, series: Series, params: dict) -> Series:
        """Encontra picos."""
        # Encontra picos
        peaks, properties = find_peaks(
            series.values,
            height=params["height"],
            distance=params["distance"],
            prominence=params["prominence"]
        )
        
        # Cria array booleano marcando picos
        peak_markers = np.zeros_like(series.values)
        peak_markers[peaks] = 1.0
        
        return Series(
            series_id=f"{series.series_id}_peaks",
            name=f"{series.name} (Picos)",
            values=peak_markers,
            metadata={
                "peak_count": len(peaks),
                "peak_indices": peaks.tolist(),
                "peak_heights": properties["peak_heights"].tolist()
            }
        )
```

### Exemplo 3: Plugin de Carregador Customizado

```python
"""Carregador de Formato Binário Customizado."""

from platform_base.plugins.base import LoaderPlugin
from platform_base.core.models import Dataset, Series
import struct
import numpy as np


class CarregadorBinario(LoaderPlugin):
    """Carrega formato binário customizado."""
    
    name = "Binário Customizado"
    extensions = [".bin", ".dat"]
    
    def load(self, filepath: str) -> Dataset:
        """Carrega arquivo binário."""
        with open(filepath, "rb") as f:
            # Lê cabeçalho
            version = struct.unpack("I", f.read(4))[0]
            n_points = struct.unpack("I", f.read(4))[0]
            n_series = struct.unpack("I", f.read(4))[0]
            
            # Lê array de tempo
            time_data = f.read(n_points * 8)  # 8 bytes por double
            t_seconds = np.frombuffer(time_data, dtype=np.float64)
            
            # Lê séries
            series_dict = {}
            for i in range(n_series):
                # Lê nome da série
                name_len = struct.unpack("H", f.read(2))[0]
                name = f.read(name_len).decode("utf-8")
                
                # Lê valores
                values_data = f.read(n_points * 8)
                values = np.frombuffer(values_data, dtype=np.float64)
                
                # Cria série
                series_dict[f"series_{i}"] = Series(
                    series_id=f"series_{i}",
                    name=name,
                    values=values
                )
            
            # Cria dataset
            return Dataset(
                dataset_id=filepath,
                name=filepath,
                series=series_dict,
                t_seconds=t_seconds,
                metadata={"version": version}
            )
```

---

## Testando Plugins

### Testes Unitários

Crie `tests/test_meuplugin.py`:

```python
"""Testes para MeuPlugin."""

import pytest
import numpy as np
from platform_base.core.models import Series
from meu_plugin import MeuPlugin


@pytest.fixture
def sample_series():
    """Cria série de teste."""
    t = np.linspace(0, 10, 100)
    y = np.sin(t)
    return Series(
        series_id="test",
        name="Teste",
        values=y
    )


def test_plugin_creation():
    """Testa se o plugin pode ser instanciado."""
    plugin = MeuPlugin()
    assert plugin.name == "Meu Plugin"


def test_plugin_parameters():
    """Testa definição de parâmetros."""
    plugin = MeuPlugin()
    params = plugin.get_parameters()
    
    assert "window_size" in params
    assert params["window_size"]["type"] == "int"


def test_plugin_execution(sample_series):
    """Testa execução do plugin."""
    plugin = MeuPlugin()
    params = {"window_size": 5}
    
    result = plugin.execute(sample_series, params)
    
    assert result is not None
    assert len(result.values) == len(sample_series.values)
    assert result.series_id != sample_series.series_id


def test_plugin_validation(sample_series):
    """Testa validação de entrada."""
    plugin = MeuPlugin()
    
    # Entrada válida
    assert plugin.validate_input(sample_series)
    
    # Entrada inválida (série vazia)
    empty_series = Series("empty", "Empty", np.array([]))
    assert not plugin.validate_input(empty_series)
```

### Executar Testes

```bash
pytest tests/
```

---

## Distribuição

### Empacotar Plugin

```bash
# Criar pacote de distribuição
python setup.py sdist bdist_wheel
```

### Exemplo de setup.py

```python
from setuptools import setup, find_packages

setup(
    name="platform-base-meuplugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "platform-base>=2.0.0",
        "numpy>=1.24.0"
    ],
    entry_points={
        "platform_base.plugins": [
            "meuplugin=meu_plugin:MeuPlugin"
        ]
    },
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    description="Meu plugin do Platform Base",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seunome/meuplugin",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ]
)
```

### Publicar no PyPI

```bash
twine upload dist/*
```

### Instalar do PyPI

```bash
pip install platform-base-meuplugin
```

---

## Boas Práticas

### 1. Tratamento de Erros

Sempre trate erros graciosamente:

```python
def execute(self, series: Series, params: dict) -> Series:
    try:
        # Seu código
        result = process_data(series.values)
        return Series(...)
    except ValueError as e:
        raise PluginExecutionError(f"Entrada inválida: {e}")
    except Exception as e:
        raise PluginExecutionError(f"Erro inesperado: {e}")
```

### 2. Validação de Entrada

Valide entradas antes de processar:

```python
def validate_input(self, series: Series) -> bool:
    if len(series.values) < 10:
        raise ValidationError("Série muito curta (mín 10 pontos)")
    
    if np.any(np.isnan(series.values)):
        raise ValidationError("Série contém valores NaN")
    
    return True
```

### 3. Documentação

Forneça docstrings claras:

```python
class MeuPlugin(OperationPlugin):
    """
    Resumo de uma linha.
    
    Descrição mais longa explicando o que o plugin faz,
    algoritmo usado e notas importantes.
    
    Parâmetros:
        window_size: Tamanho da janela de média móvel
        
    Retorna:
        Série suavizada com mesmo comprimento da entrada
        
    Exemplo:
        >>> plugin = MeuPlugin()
        >>> result = plugin.execute(series, {"window_size": 5})
    """
```

### 4. Desempenho

Otimize para datasets grandes:

```python
# Use operações NumPy (rápido)
result = np.mean(data)

# Evite loops Python (lento)
result = sum(data) / len(data)

# Use numba para loops customizados
from numba import jit

@jit(nopython=True)
def custom_operation(data):
    # Loop rápido
    pass
```

### 5. Type Hints

Use type hints para melhor suporte de IDE:

```python
from typing import Dict, Any
from platform_base.core.models import Series

def execute(self, series: Series, params: Dict[str, Any]) -> Series:
    pass
```

---

## Solução de Problemas

### Plugin Não Carrega

**Problema**: Plugin não aparece no menu

**Soluções**:
1. Verifique sintaxe do `plugin.yaml`
2. Verifique se o ponto de entrada está correto
3. Veja logs: `~/.platform_base/logs/plugins.log`
4. Garanta que dependências estejam instaladas
5. Verifique compatibilidade de versão do Platform Base

### Erros de Importação

**Problema**: `ModuleNotFoundError`

**Soluções**:
1. Instale dependências do plugin
2. Verifique o Python path
3. Reinstale o plugin

### Erros em Tempo de Execução

**Problema**: Plugin trava durante execução

**Soluções**:
1. Adicione blocos try/except
2. Valide entradas
3. Verifique valores NaN/Inf
4. Teste com dados de exemplo primeiro
5. Habilite logging de depuração

### Problemas de Desempenho

**Problema**: Plugin está lento

**Soluções**:
1. Profile código: `python -m cProfile`
2. Use operações NumPy
3. Considere compilação JIT com numba
4. Reduza cópia de dados
5. Processe em chunks para dados grandes

---

## Recursos

### Documentação
- [Referência da API](API_REFERENCE.md)
- [Guia do Usuário](USER_GUIDE.md)
- [Modelos Principais](../src/platform_base/core/models.py)

### Exemplos
- [Plugins de Exemplo](../plugins/examples/)
- [Plugins da Comunidade](https://github.com/platform-base/plugins)

### Suporte
- [Issues no GitHub](https://github.com/thiagoarcan/Warp/issues)
- [Discussões](https://github.com/thiagoarcan/Warp/discussions)

---

*Platform Base v2.0 - Guia de Desenvolvimento de Plugins*  
*Última Atualização: 2026-02-02*
