# Platform Base v2.0 - Guia de Solução de Problemas

**Soluções para problemas e questões comuns**

---

## Índice

1. [Problemas de Instalação](#problemas-de-instalação)
2. [Problemas de Inicialização](#problemas-de-inicialização)
3. [Problemas de Carregamento de Dados](#problemas-de-carregamento-de-dados)
4. [Problemas de Desempenho](#problemas-de-desempenho)
5. [Problemas de Visualização](#problemas-de-visualização)
6. [Erros de Cálculo](#erros-de-cálculo)
7. [Problemas de Memória](#problemas-de-memória)
8. [Problemas de UI/Display](#problemas-de-uidisplay)
9. [Problemas de Exportação](#problemas-de-exportação)
10. [Problemas de Plugins](#problemas-de-plugins)
11. [Problemas Específicos do Sistema](#problemas-específicos-do-sistema)
12. [Obtendo Mais Ajuda](#obtendo-mais-ajuda)

---

## Problemas de Instalação

### Problema: pip install falha com "No module named 'platform_base'"

**Sintomas**:
```
ModuleNotFoundError: No module named 'platform_base'
```

**Soluções**:
1. Certifique-se de estar no diretório correto:
   ```bash
   cd /caminho/para/Warp/platform_base
   pwd  # Deve mostrar diretório platform_base
   ```

2. Instale em modo editável:
   ```bash
   pip install -e .
   ```

3. Verifique versão do Python:
   ```bash
   python --version  # Deve ser 3.12+
   ```

### Problema: Conflitos de dependências durante instalação

**Sintomas**:
```
ERROR: pacote X requer Y<2.0, mas você tem Y 2.1
```

**Soluções**:
1. Crie ambiente virtual limpo:
   ```bash
   python -m venv venv_limpo
   source venv_limpo/bin/activate
   pip install -e .
   ```

2. Atualize pip:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

3. Instale com versões específicas:
   ```bash
   pip install -e . --no-deps
   pip install -r requirements.txt
   ```

### Problema: PyQt6 não instala

**Sintomas**:
```
ERROR: Could not build wheels for PyQt6
```

**Soluções**:

**Linux**:
```bash
sudo apt-get update
sudo apt-get install python3-pyqt6 libgl1-mesa-glx
pip install PyQt6
```

**macOS**:
```bash
brew install qt6
pip install PyQt6
```

**Windows**:
- Certifique-se que Visual C++ Redistributable está instalado
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## Problemas de Inicialização

### Problema: Aplicação não inicia

**Sintomas**:
- Janela não aparece
- Comando trava
- Saída imediata

**Soluções**:

1. **Verifique mensagens de erro**:
   ```bash
   python -m platform_base.desktop.main_window --debug
   ```

2. **Verifique logs**:
   ```bash
   cat ~/.platform_base/logs/app.log
   ```

3. **Teste instalação do Qt**:
   ```python
   from PyQt6.QtWidgets import QApplication
   import sys
   app = QApplication(sys.argv)
   print("Qt funcionando!")
   ```

4. **Verifique display**:
   ```bash
   echo $DISPLAY  # Linux
   # Deve mostrar :0 ou similar
   ```

### Problema: Aplicação trava na inicialização

**Sintomas**:
```
Segmentation fault (core dumped)
```

**Soluções**:

1. **Atualize drivers gráficos** (causa mais comum)

2. **Tente renderização por software**:
   ```bash
   export QT_QPA_PLATFORM=offscreen
   python launch_app.py
   ```

3. **Verifique OpenGL**:
   ```bash
   glxinfo | grep "OpenGL version"
   ```

4. **Reinstale PyQt6**:
   ```bash
   pip uninstall PyQt6
   pip install PyQt6 --no-cache-dir
   ```

---

## Problemas de Carregamento de Dados

### Problema: Arquivo CSV não carrega

**Sintomas**:
- Erro "Unable to parse file"
- Dataset vazio
- Colunas erradas

**Soluções**:

1. **Verifique codificação do arquivo**:
   ```bash
   file -i seu_arquivo.csv
   # ou
   chardet seu_arquivo.csv
   ```

2. **Tente delimitador diferente**:
   - Diálogo de carregamento → Delimitador → Tente Tab, Ponto-e-vírgula, Espaço

3. **Verifique BOM (Byte Order Mark)**:
   ```python
   with open('file.csv', 'rb') as f:
       primeiros_bytes = f.read(3)
       if primeiros_bytes == b'\xef\xbb\xbf':
           print("UTF-8 BOM detectado")
   ```
   Solução: Re-salve arquivo sem BOM

4. **Valide estrutura CSV**:
   ```bash
   head -5 seu_arquivo.csv
   # Verifique:
   # - Número consistente de colunas
   # - Sem linhas vazias no início
   # - Linha de cabeçalho presente
   ```

### Problema: Arquivo Excel carrega mas dados estão errados

**Sintomas**:
- Colunas faltando
- Planilha errada carregada
- Datas aparecendo como números

**Soluções**:

1. **Especifique planilha correta**:
   - Diálogo de carregamento → Dropdown de Planilha → Selecione planilha correta

2. **Verifique formato de data**:
   - Diálogo de carregamento → Colunas de data → Seleção manual
   - Ou: Formate datas como ISO no Excel (AAAA-MM-DD)

3. **Trate células mescladas**:
   - Células mescladas do Excel não são suportadas
   - Desmescle no Excel antes de carregar

4. **Verifique células com fórmulas**:
   - Fórmulas não são avaliadas
   - Copie-cole como valores no Excel primeiro

### Problema: Arquivo grande demora muito para carregar

**Sintomas**:
- Progresso de carregamento travado
- Aplicação não responde
- Memória cresce continuamente

**Soluções**:

1. **Habilite decimação**:
   ```python
   load(file, config={"max_rows": 100000})
   ```

2. **Use Parquet ao invés de CSV**:
   ```python
   # Converta primeiro
   import pandas as pd
   df = pd.read_csv("grande.csv")
   df.to_parquet("grande.parquet")
   ```

3. **Carregue apenas colunas específicas**:
   - Diálogo de carregamento → Selecionar Colunas → Escolha apenas colunas necessárias

4. **Divida arquivo em chunks**:
   ```bash
   split -l 100000 grande.csv chunk_
   ```

---

## Problemas de Desempenho

### Problema: Aplicação está lenta/travando

**Sintomas**:
- UI congela
- Atualizações de gráfico lentas
- Operações demoram muito

**Soluções**:

1. **Habilite auto-decimação**:
   - Configurações → Desempenho → Auto-decimação: ON
   - Limite de decimação: 10000 pontos

2. **Feche abas não utilizadas**:
   - Cada gráfico usa memória
   - Fechar: Clique direito na aba → Fechar

3. **Reduza tamanho dos dados**:
   - Exporte versão decimada
   - Trabalhe com subconjunto filtrado

4. **Verifique uso de CPU**:
   ```bash
   top -p $(pgrep -f platform_base)
   ```

5. **Desabilite anti-aliasing**:
   - Configurações → Visualização → Anti-aliasing: OFF

### Problema: Renderização de gráfico está lenta

**Sintomas**:
- Zoom/pan com lag
- Gráfico demora segundos para atualizar

**Soluções**:

1. **Habilite aceleração de GPU**:
   - Configurações → Desempenho → GPU: ON

2. **Use downsampling LTTB**:
   ```python
   from platform_base.processing.downsampling import downsample_lttb
   downsampled = downsample_lttb(data, time, n_out=2000)
   ```

3. **Reduza número de séries**:
   - Muitas séries (>10) desaceleram renderização
   - Plote subconjuntos separadamente

4. **Verifique driver gráfico**:
   ```bash
   glxinfo | grep "renderer"
   ```

---

## Problemas de Visualização

### Problema: Gráfico está em branco/vazio

**Sintomas**:
- Canvas branco
- Sem dados visíveis
- Eixos presentes mas sem linhas

**Soluções**:

1. **Verifique range de dados**:
   - Dados podem estar fora da vista
   - Clique direito → Resetar Vista (ou pressione `R`)

2. **Verifique se série foi adicionada**:
   - Procure por série na legenda
   - Se faltando, dê duplo clique na série na árvore de dados

3. **Verifique valores NaN**:
   ```python
   import numpy as np
   has_nan = np.any(np.isnan(series.values))
   ```

4. **Verifique escalas de eixos**:
   - Incompatibilidade de escala Linear vs Log
   - Clique direito no eixo → Escala Linear

### Problema: Cores não estão sendo exibidas corretamente

**Sintomas**:
- Todas séries mesma cor
- Cores muito similares
- Não consegue distinguir séries

**Soluções**:

1. **Resete esquema de cores**:
   - Configurações → Visualização → Cores → Resetar para Padrão

2. **Configure cores manualmente**:
   - Clique direito na série na legenda
   - Mudar Cor → Escolha cor distinta

3. **Use paleta amigável para daltônicos**:
   - Configurações → Visualização → Paleta de Cores → Daltônicos

4. **Verifique tema**:
   - Tema escuro pode afetar visibilidade
   - Tente: Configurações → Aparência → Tema → Claro

### Problema: Gráfico 3D não renderiza

**Sintomas**:
- Erro: "VTK not available"
- Janela 3D em branco
- Trava ao abrir 3D

**Soluções**:

1. **Instale VTK**:
   ```bash
   pip install vtk pyvista
   ```

2. **Verifique suporte OpenGL**:
   ```bash
   glxinfo | grep "OpenGL"
   # Deve mostrar OpenGL 3.0+
   ```

3. **Use renderização por software**:
   ```bash
   export PYVISTA_OFF_SCREEN=true
   ```

4. **Atualize drivers gráficos**

---

## Erros de Cálculo

### Problema: Derivada retorna NaN

**Sintomas**:
```
RuntimeWarning: invalid value encountered
Resultado contém NaN
```

**Soluções**:

1. **Verifique entrada para NaN**:
   - Operações → Interpolação → Preencha lacunas primeiro

2. **Verifique array de tempo**:
   - Deve ser monotonicamente crescente
   - Sem timestamps duplicados

3. **Use método diferente**:
   - Tente: Diferença progressiva ao invés de central

4. **Filtre ruído primeiro**:
   - Operações → Filtros → Passa-Baixas
   - Depois calcule derivada

### Problema: Interpolação falha

**Sintomas**:
```
ValueError: x must be strictly increasing
```

**Soluções**:

1. **Ordene array de tempo**:
   ```python
   sorted_indices = np.argsort(t)
   t_sorted = t[sorted_indices]
   y_sorted = y[sorted_indices]
   ```

2. **Remova duplicatas**:
   ```python
   unique_indices = np.unique(t, return_index=True)[1]
   t_unique = t[unique_indices]
   y_unique = y[unique_indices]
   ```

3. **Verifique lacunas**:
   - Lacunas grandes (>10x espaçamento mediano) podem causar problemas
   - Considere: Operações → Interpolação → Método → Linear (mais robusto)

### Problema: Erro "Out of bounds"

**Sintomas**:
```
IndexError: index out of bounds
```

**Soluções**:

1. **Verifique comprimentos de arrays correspondem**:
   ```python
   len(time) == len(values)  # Deve ser true
   ```

2. **Verifique arrays vazios**:
   ```python
   if len(data) == 0:
       # Trate caso vazio
   ```

3. **Valide índices**:
   - Não acesse data[len(data)]
   - Use data[-1] para último elemento

---

## Problemas de Memória

### Problema: Erro de falta de memória

**Sintomas**:
```
MemoryError
killed
```

**Soluções**:

1. **Aumente limite de memória**:
   - Configurações → Desempenho → Limite de Memória → 80% da RAM

2. **Use carregamento em chunks**:
   ```python
   load(file, config={"max_rows": 50000, "chunked": True})
   ```

3. **Feche outras aplicações**

4. **Use Python 64-bit**:
   ```bash
   python -c "import struct; print(struct.calcsize('P') * 8)"
   # Deve exibir: 64
   ```

5. **Habilite cache em disco**:
   - Configurações → Desempenho → Cache em Disco: ON

### Problema: Uso de memória continua crescendo

**Sintomas**:
- Uso de RAM aumenta ao longo do tempo
- Aplicação desacelera
- Eventualmente trava

**Soluções**:

1. **Limpe histórico de desfazer**:
   - Editar → Limpar Histórico de Desfazer

2. **Feche abas não utilizadas**:
   - Cada aba mantém dados na memória

3. **Reinicie aplicação periodicamente**

4. **Verifique vazamentos de memória**:
   ```bash
   python -m memory_profiler launch_app.py
   ```

5. **Desabilite auto-salvamento**:
   - Configurações → Auto-salvamento → Desabilitado

---

## Problemas de UI/Display

### Problema: Elementos de UI muito pequenos/grandes

**Sintomas**:
- Texto ilegível
- Botões minúsculos
- Widgets sobrepõem

**Soluções**:

1. **Ajuste escala DPI** (Windows):
   - Clique direito no app → Propriedades → Compatibilidade
   - Substituir escala de alto DPI: Aplicação

2. **Mude tamanho da fonte**:
   - Configurações → Aparência → Tamanho da Fonte → Ajustar

3. **Use zoom de UI**:
   - Configurações → Acessibilidade → Zoom de UI → 125% ou 150%

### Problema: Tema não está sendo aplicado

**Sintomas**:
- Tema mudou mas sem efeito
- Elementos mistos claro/escuro

**Soluções**:

1. **Reinicie aplicação** (necessário para mudança de tema)

2. **Verifique arquivos de tema**:
   ```bash
   ls ~/.platform_base/themes/
   ```

3. **Resete para padrão**:
   - Configurações → Aparência → Tema → Resetar para Padrão

### Problema: Menus/diálogos aparecem fora da tela

**Sintomas**:
- Não consegue ver diálogo
- Menu cortado

**Soluções**:

1. **Resete posições de janela**:
   - Configurações → Geral → Resetar Posições de Janela

2. **Mude monitor** (configuração multi-monitor):
   ```bash
   # Mova janela para monitor principal
   xrandr --output HDMI-1 --primary
   ```

3. **Use navegação por teclado**:
   - `Tab` para percorrer elementos
   - `Enter` para ativar

---

## Problemas de Exportação

### Problema: Exportação falha silenciosamente

**Sintomas**:
- Botão de exportação clicado
- Nenhum arquivo criado
- Sem mensagem de erro

**Soluções**:

1. **Verifique permissões de arquivo**:
   ```bash
   ls -l /diretorio/exportacao/
   # Deve ter permissão de escrita
   ```

2. **Verifique espaço em disco**:
   ```bash
   df -h
   ```

3. **Tente local diferente**:
   - Exporte para diretório home primeiro
   - Depois mova arquivo

4. **Verifique logs**:
   ```bash
   tail ~/.platform_base/logs/export.log
   ```

### Problema: CSV exportado está corrompido

**Sintomas**:
- Arquivo não abre
- Colunas desalinhadas
- Caracteres extras

**Soluções**:

1. **Especifique codificação explicitamente**:
   - Diálogo de exportação → Codificação → UTF-8 (BOM)

2. **Verifique delimitador**:
   - Diálogo de exportação → Delimitador → Corresponda ferramenta de importação

3. **Valide arquivo exportado**:
   ```bash
   head -10 exported.csv
   wc -l exported.csv
   ```

---

## Problemas de Plugins

### Problema: Plugin não carrega

**Sintomas**:
- Plugin não está no menu
- Erro de importação
- "Plugin failed to load"

**Soluções**:

1. **Verifique diretório de plugins**:
   ```bash
   ls ~/.platform_base/plugins/
   ```

2. **Verifique plugin.yaml**:
   ```bash
   cat ~/.platform_base/plugins/meuplugin/plugin.yaml
   # Valide sintaxe YAML
   ```

3. **Verifique dependências**:
   ```bash
   pip list | grep nome-plugin
   ```

4. **Habilite logging de plugin**:
   - Configurações → Avançado → Debug de Plugin: ON

5. **Reinstale plugin**:
   ```bash
   python -m platform_base.plugins uninstall meuplugin
   python -m platform_base.plugins install /caminho/para/meuplugin
   ```

---

## Problemas Específicos do Sistema

### Linux

**Problema**: Erro libEGL
```
ImportError: libEGL.so.1: cannot open shared object file
```

**Solução**:
```bash
sudo apt-get install libegl1-mesa libgl1-mesa-glx
```

**Problema**: Erro de conexão X11
```
qt.qpa.xcb: could not connect to display
```

**Solução**:
```bash
export DISPLAY=:0
xhost +local:
```

### macOS

**Problema**: App não autorizado
```
"Platform Base" cannot be opened because the developer cannot be verified
```

**Solução**:
```bash
xattr -cr /caminho/para/platform_base.app
```

**Problema**: Problemas de display Retina
**Solução**:
- Configurações → Display → Usar Resolução Nativa: ON

### Windows

**Problema**: Falha ao carregar DLL
```
ImportError: DLL load failed while importing QtCore
```

**Solução**:
- Instale Visual C++ Redistributable 2015-2022
- https://aka.ms/vs/17/release/vc_redist.x64.exe

**Problema**: Antivírus bloqueando
**Solução**:
- Adicione exceção para platform_base.exe
- Ou desabilite antivírus temporariamente

---

## Obtendo Mais Ajuda

### Antes de Pedir Ajuda

1. **Verifique logs**:
   ```bash
   # Log da aplicação
   cat ~/.platform_base/logs/app.log
   
   # Log de erros
   cat ~/.platform_base/logs/errors.log
   ```

2. **Tente modo verbose**:
   ```bash
   python launch_app.py --verbose --debug
   ```

3. **Verifique informações do sistema**:
   ```bash
   python -c "import platform; print(platform.platform())"
   python -c "import platform_base; print(platform_base.__version__)"
   ```

### Reportando Issues

Ao criar issue no GitHub, inclua:

1. **Versão do Platform Base**
2. **Sistema operacional** (nome + versão)
3. **Versão do Python**
4. **Passos para reproduzir**
5. **Comportamento esperado vs real**
6. **Mensagens de erro** (traceback completo)
7. **Arquivos de log** (se relevante)
8. **Screenshots** (se problema de UI)

### Recursos da Comunidade

- **Issues no GitHub**: https://github.com/thiagoarcan/Warp/issues
- **Discussões**: https://github.com/thiagoarcan/Warp/discussions
- **Documentação**: Todos os docs no diretório `/docs`

### Suporte Profissional

Para suporte empresarial, contate: support@platform-base.com

---

## Ferramentas de Diagnóstico

### Script de Informações do Sistema

```python
#!/usr/bin/env python3
"""Imprime informações de diagnóstico."""

import sys
import platform
import platform_base

print("Informações do Sistema")
print("=" * 50)
print(f"SO: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print(f"Platform Base: {platform_base.__version__}")

try:
    from PyQt6 import QtCore
    print(f"PyQt6: {QtCore.PYQT_VERSION_STR}")
except ImportError:
    print("PyQt6: NÃO INSTALADO")

try:
    import numpy as np
    print(f"NumPy: {np.__version__}")
except ImportError:
    print("NumPy: NÃO INSTALADO")

print("\nDiretório de instalação:")
print(platform_base.__file__)
```

### Verificação Rápida de Saúde

```bash
#!/bin/bash
echo "Verificação de Saúde do Platform Base"
echo "============================"

# Verifique Python
python --version || echo "ERRO: Python não encontrado"

# Verifique instalação
python -c "import platform_base" && echo "✓ Pacote instalado" || echo "✗ Pacote não instalado"

# Verifique Qt
python -c "from PyQt6.QtWidgets import QApplication" && echo "✓ Qt disponível" || echo "✗ Qt não disponível"

# Verifique dependências
pip check && echo "✓ Sem conflitos de dependências" || echo "✗ Problemas de dependências"

# Verifique logs
if [ -f ~/.platform_base/logs/app.log ]; then
    echo "✓ Diretório de logs existe"
    echo "Última entrada de log:"
    tail -1 ~/.platform_base/logs/app.log
else
    echo "✗ Sem logs encontrados"
fi
```

---

*Platform Base v2.0 - Guia de Solução de Problemas*  
*Última Atualização: 2026-02-02*
