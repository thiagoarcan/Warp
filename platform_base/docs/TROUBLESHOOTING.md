# Platform Base v2.0 - Guia de SoluÃ§Ã£o de Problemas

**SoluÃ§Ãµes para problemas e questÃµes comuns**

---

## Ãndice

1. [Problemas de InstalaÃ§Ã£o](#problemas-de-instalaÃ§Ã£o)
2. [Problemas de InicializaÃ§Ã£o](#problemas-de-inicializaÃ§Ã£o)
3. [Problemas de Carregamento de Dados](#problemas-de-carregamento-de-dados)
4. [Problemas de Desempenho](#problemas-de-desempenho)
5. [Problemas de VisualizaÃ§Ã£o](#problemas-de-visualizaÃ§Ã£o)
6. [Erros de CÃ¡lculo](#erros-de-cÃ¡lculo)
7. [Problemas de MemÃ³ria](#problemas-de-memÃ³ria)
8. [Problemas de UI/Display](#problemas-de-uidisplay)
9. [Problemas de ExportaÃ§Ã£o](#problemas-de-exportaÃ§Ã£o)
10. [Problemas de Plugins](#problemas-de-plugins)
11. [Problemas EspecÃ­ficos do Sistema](#problemas-especÃ­ficos-do-sistema)
12. [Obtendo Mais Ajuda](#obtendo-mais-ajuda)

---

## Problemas de InstalaÃ§Ã£o

### Problema: pip install falha com "No module named 'platform_base'"

**Sintomas**:
```
ModuleNotFoundError: No module named 'platform_base'
```

**SoluÃ§Ãµes**:
1. Certifique-se de estar no diretÃ³rio correto:
   ```bash
   cd /caminho/para/Warp/platform_base
   pwd  # Deve mostrar diretÃ³rio platform_base
   ```

2. Instale em modo editÃ¡vel:
   ```bash
   pip install -e .
   ```

3. Verifique versÃ£o do Python:
   ```bash
   python --version  # Deve ser 3.12+
   ```

### Problema: Conflitos de dependÃªncias durante instalaÃ§Ã£o

**Sintomas**:
```
ERROR: pacote X requer Y<2.0, mas vocÃª tem Y 2.1
```

**SoluÃ§Ãµes**:
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

3. Instale com versÃµes especÃ­ficas:
   ```bash
   pip install -e . --no-deps
   pip install -r requirements.txt
   ```

### Problema: PyQt6 nÃ£o instala

**Sintomas**:
```
ERROR: Could not build wheels for PyQt6
```

**SoluÃ§Ãµes**:

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
- Certifique-se que Visual C++ Redistributable estÃ¡ instalado
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## Problemas de InicializaÃ§Ã£o

### Problema: AplicaÃ§Ã£o nÃ£o inicia

**Sintomas**:
- Janela nÃ£o aparece
- Comando trava
- SaÃ­da imediata

**SoluÃ§Ãµes**:

1. **Verifique mensagens de erro**:
   ```bash
   python launch_app.py --debug
   ```

2. **Verifique logs**:
   ```bash
   cat ~/.platform_base/logs/app.log
   ```

3. **Teste instalaÃ§Ã£o do Qt**:
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

### Problema: AplicaÃ§Ã£o trava na inicializaÃ§Ã£o

**Sintomas**:
```
Segmentation fault (core dumped)
```

**SoluÃ§Ãµes**:

1. **Atualize drivers grÃ¡ficos** (causa mais comum)

2. **Tente renderizaÃ§Ã£o por software**:
   ```bash
   export QT_QPA_PLATFORM=offscreen
   python launch_app.py

   No Windows (PowerShell):
   $env:QT_QPA_PLATFORM = 'offscreen'
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

### Problema: Arquivo CSV nÃ£o carrega

**Sintomas**:
- Erro "Unable to parse file"
- Dataset vazio
- Colunas erradas

**SoluÃ§Ãµes**:

1. **Verifique codificaÃ§Ã£o do arquivo**:
   ```bash
   file -i seu_arquivo.csv
   # ou
   chardet seu_arquivo.csv
   ```

2. **Tente delimitador diferente**:
   - DiÃ¡logo de carregamento â†’ Delimitador â†’ Tente Tab, Ponto-e-vÃ­rgula, EspaÃ§o

3. **Verifique BOM (Byte Order Mark)**:
   ```python
   with open('file.csv', 'rb') as f:
       primeiros_bytes = f.read(3)
       if primeiros_bytes == b'\xef\xbb\xbf':
           print("UTF-8 BOM detectado")
   ```
   SoluÃ§Ã£o: Re-salve arquivo sem BOM

4. **Valide estrutura CSV**:
   ```bash
   head -5 seu_arquivo.csv
   # Verifique:
   # - NÃºmero consistente de colunas
   # - Sem linhas vazias no inÃ­cio
   # - Linha de cabeÃ§alho presente
   ```

### Problema: Arquivo Excel carrega mas dados estÃ£o errados

**Sintomas**:
- Colunas faltando
- Planilha errada carregada
- Datas aparecendo como nÃºmeros

**SoluÃ§Ãµes**:

1. **Especifique planilha correta**:
   - DiÃ¡logo de carregamento â†’ Dropdown de Planilha â†’ Selecione planilha correta

2. **Verifique formato de data**:
   - DiÃ¡logo de carregamento â†’ Colunas de data â†’ SeleÃ§Ã£o manual
   - Ou: Formate datas como ISO no Excel (AAAA-MM-DD)

3. **Trate cÃ©lulas mescladas**:
   - CÃ©lulas mescladas do Excel nÃ£o sÃ£o suportadas
   - Desmescle no Excel antes de carregar

4. **Verifique cÃ©lulas com fÃ³rmulas**:
   - FÃ³rmulas nÃ£o sÃ£o avaliadas
   - Copie-cole como valores no Excel primeiro

### Problema: Arquivo grande demora muito para carregar

**Sintomas**:
- Progresso de carregamento travado
- AplicaÃ§Ã£o nÃ£o responde
- MemÃ³ria cresce continuamente

**SoluÃ§Ãµes**:

1. **Habilite decimaÃ§Ã£o**:
   ```python
   load(file, config={"max_rows": 100000})
   ```

2. **Use Parquet ao invÃ©s de CSV**:
   ```python
   # Converta primeiro
   import pandas as pd
   df = pd.read_csv("grande.csv")
   df.to_parquet("grande.parquet")
   ```

3. **Carregue apenas colunas especÃ­ficas**:
   - DiÃ¡logo de carregamento â†’ Selecionar Colunas â†’ Escolha apenas colunas necessÃ¡rias

4. **Divida arquivo em chunks**:
   ```bash
   split -l 100000 grande.csv chunk_
   ```

---

## Problemas de Desempenho

### Problema: AplicaÃ§Ã£o estÃ¡ lenta/travando

**Sintomas**:
- UI congela
- AtualizaÃ§Ãµes de grÃ¡fico lentas
- OperaÃ§Ãµes demoram muito

**SoluÃ§Ãµes**:

1. **Habilite auto-decimaÃ§Ã£o**:
   - ConfiguraÃ§Ãµes â†’ Desempenho â†’ Auto-decimaÃ§Ã£o: ON
   - Limite de decimaÃ§Ã£o: 10000 pontos

2. **Feche abas nÃ£o utilizadas**:
   - Cada grÃ¡fico usa memÃ³ria
   - Fechar: Clique direito na aba â†’ Fechar

3. **Reduza tamanho dos dados**:
   - Exporte versÃ£o decimada
   - Trabalhe com subconjunto filtrado

4. **Verifique uso de CPU**:
   ```bash
   top -p $(pgrep -f platform_base)
   ```

5. **Desabilite anti-aliasing**:
   - ConfiguraÃ§Ãµes â†’ VisualizaÃ§Ã£o â†’ Anti-aliasing: OFF

### Problema: RenderizaÃ§Ã£o de grÃ¡fico estÃ¡ lenta

**Sintomas**:
- Zoom/pan com lag
- GrÃ¡fico demora segundos para atualizar

**SoluÃ§Ãµes**:

1. **Habilite aceleraÃ§Ã£o de GPU**:
   - ConfiguraÃ§Ãµes â†’ Desempenho â†’ GPU: ON

2. **Use downsampling LTTB**:
   ```python
   from platform_base.processing.downsampling import downsample_lttb
   downsampled = downsample_lttb(data, time, n_out=2000)
   ```

3. **Reduza nÃºmero de sÃ©ries**:
   - Muitas sÃ©ries (>10) desaceleram renderizaÃ§Ã£o
   - Plote subconjuntos separadamente

4. **Verifique driver grÃ¡fico**:
   ```bash
   glxinfo | grep "renderer"
   ```

---

## Problemas de VisualizaÃ§Ã£o

### Problema: GrÃ¡fico estÃ¡ em branco/vazio

**Sintomas**:
- Canvas branco
- Sem dados visÃ­veis
- Eixos presentes mas sem linhas

**SoluÃ§Ãµes**:

1. **Verifique range de dados**:
   - Dados podem estar fora da vista
   - Clique direito â†’ Resetar Vista (ou pressione `R`)

2. **Verifique se sÃ©rie foi adicionada**:
   - Procure por sÃ©rie na legenda
   - Se faltando, dÃª duplo clique na sÃ©rie na Ã¡rvore de dados

3. **Verifique valores NaN**:
   ```python
   import numpy as np
   has_nan = np.any(np.isnan(series.values))
   ```

4. **Verifique escalas de eixos**:
   - Incompatibilidade de escala Linear vs Log
   - Clique direito no eixo â†’ Escala Linear

### Problema: Cores nÃ£o estÃ£o sendo exibidas corretamente

**Sintomas**:
- Todas sÃ©ries mesma cor
- Cores muito similares
- NÃ£o consegue distinguir sÃ©ries

**SoluÃ§Ãµes**:

1. **Resete esquema de cores**:
   - ConfiguraÃ§Ãµes â†’ VisualizaÃ§Ã£o â†’ Cores â†’ Resetar para PadrÃ£o

2. **Configure cores manualmente**:
   - Clique direito na sÃ©rie na legenda
   - Mudar Cor â†’ Escolha cor distinta

3. **Use paleta amigÃ¡vel para daltÃ´nicos**:
   - ConfiguraÃ§Ãµes â†’ VisualizaÃ§Ã£o â†’ Paleta de Cores â†’ DaltÃ´nicos

4. **Verifique tema**:
   - Tema escuro pode afetar visibilidade
   - Tente: ConfiguraÃ§Ãµes â†’ AparÃªncia â†’ Tema â†’ Claro

### Problema: GrÃ¡fico 3D nÃ£o renderiza

**Sintomas**:
- Erro: "VTK not available"
- Janela 3D em branco
- Trava ao abrir 3D

**SoluÃ§Ãµes**:

1. **Instale VTK**:
   ```bash
   pip install vtk pyvista
   ```

2. **Verifique suporte OpenGL**:
   ```bash
   glxinfo | grep "OpenGL"
   # Deve mostrar OpenGL 3.0+
   ```

3. **Use renderizaÃ§Ã£o por software**:
   ```bash
   export PYVISTA_OFF_SCREEN=true
   ```

4. **Atualize drivers grÃ¡ficos**

---

## Erros de CÃ¡lculo

### Problema: Derivada retorna NaN

**Sintomas**:
```
RuntimeWarning: invalid value encountered
Resultado contÃ©m NaN
```

**SoluÃ§Ãµes**:

1. **Verifique entrada para NaN**:
   - OperaÃ§Ãµes â†’ InterpolaÃ§Ã£o â†’ Preencha lacunas primeiro

2. **Verifique array de tempo**:
   - Deve ser monotonicamente crescente
   - Sem timestamps duplicados

3. **Use mÃ©todo diferente**:
   - Tente: DiferenÃ§a progressiva ao invÃ©s de central

4. **Filtre ruÃ­do primeiro**:
   - OperaÃ§Ãµes â†’ Filtros â†’ Passa-Baixas
   - Depois calcule derivada

### Problema: InterpolaÃ§Ã£o falha

**Sintomas**:
```
ValueError: x must be strictly increasing
```

**SoluÃ§Ãµes**:

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
   - Lacunas grandes (>10x espaÃ§amento mediano) podem causar problemas
   - Considere: OperaÃ§Ãµes â†’ InterpolaÃ§Ã£o â†’ MÃ©todo â†’ Linear (mais robusto)

### Problema: Erro "Out of bounds"

**Sintomas**:
```
IndexError: index out of bounds
```

**SoluÃ§Ãµes**:

1. **Verifique comprimentos de arrays correspondem**:
   ```python
   len(time) == len(values)  # Deve ser true
   ```

2. **Verifique arrays vazios**:
   ```python
   if len(data) == 0:
       # Trate caso vazio
   ```

3. **Valide Ã­ndices**:
   - NÃ£o acesse data[len(data)]
   - Use data[-1] para Ãºltimo elemento

---

## Problemas de MemÃ³ria

### Problema: Erro de falta de memÃ³ria

**Sintomas**:
```
MemoryError
killed
```

**SoluÃ§Ãµes**:

1. **Aumente limite de memÃ³ria**:
   - ConfiguraÃ§Ãµes â†’ Desempenho â†’ Limite de MemÃ³ria â†’ 80% da RAM

2. **Use carregamento em chunks**:
   ```python
   load(file, config={"max_rows": 50000, "chunked": True})
   ```

3. **Feche outras aplicaÃ§Ãµes**

4. **Use Python 64-bit**:
   ```bash
   python -c "import struct; print(struct.calcsize('P') * 8)"
   # Deve exibir: 64
   ```

5. **Habilite cache em disco**:
   - ConfiguraÃ§Ãµes â†’ Desempenho â†’ Cache em Disco: ON

### Problema: Uso de memÃ³ria continua crescendo

**Sintomas**:
- Uso de RAM aumenta ao longo do tempo
- AplicaÃ§Ã£o desacelera
- Eventualmente trava

**SoluÃ§Ãµes**:

1. **Limpe histÃ³rico de desfazer**:
   - Editar â†’ Limpar HistÃ³rico de Desfazer

2. **Feche abas nÃ£o utilizadas**:
   - Cada aba mantÃ©m dados na memÃ³ria

3. **Reinicie aplicaÃ§Ã£o periodicamente**

4. **Verifique vazamentos de memÃ³ria**:
   ```bash
   python -m memory_profiler launch_app.py
   ```

5. **Desabilite auto-salvamento**:
   - ConfiguraÃ§Ãµes â†’ Auto-salvamento â†’ Desabilitado

---

## Problemas de UI/Display

### Problema: Elementos de UI muito pequenos/grandes

**Sintomas**:
- Texto ilegÃ­vel
- BotÃµes minÃºsculos
- Widgets sobrepÃµem

**SoluÃ§Ãµes**:

1. **Ajuste escala DPI** (Windows):
   - Clique direito no app â†’ Propriedades â†’ Compatibilidade
   - Substituir escala de alto DPI: AplicaÃ§Ã£o

2. **Mude tamanho da fonte**:
   - ConfiguraÃ§Ãµes â†’ AparÃªncia â†’ Tamanho da Fonte â†’ Ajustar

3. **Use zoom de UI**:
   - ConfiguraÃ§Ãµes â†’ Acessibilidade â†’ Zoom de UI â†’ 125% ou 150%

### Problema: Tema nÃ£o estÃ¡ sendo aplicado

**Sintomas**:
- Tema mudou mas sem efeito
- Elementos mistos claro/escuro

**SoluÃ§Ãµes**:

1. **Reinicie aplicaÃ§Ã£o** (necessÃ¡rio para mudanÃ§a de tema)

2. **Verifique arquivos de tema**:
   ```bash
   ls ~/.platform_base/themes/
   ```

3. **Resete para padrÃ£o**:
   - ConfiguraÃ§Ãµes â†’ AparÃªncia â†’ Tema â†’ Resetar para PadrÃ£o

### Problema: Menus/diÃ¡logos aparecem fora da tela

**Sintomas**:
- NÃ£o consegue ver diÃ¡logo
- Menu cortado

**SoluÃ§Ãµes**:

1. **Resete posiÃ§Ãµes de janela**:
   - ConfiguraÃ§Ãµes â†’ Geral â†’ Resetar PosiÃ§Ãµes de Janela

2. **Mude monitor** (configuraÃ§Ã£o multi-monitor):
   ```bash
   # Mova janela para monitor principal
   xrandr --output HDMI-1 --primary
   ```

3. **Use navegaÃ§Ã£o por teclado**:
   - `Tab` para percorrer elementos
   - `Enter` para ativar

---

## Problemas de ExportaÃ§Ã£o

### Problema: ExportaÃ§Ã£o falha silenciosamente

**Sintomas**:
- BotÃ£o de exportaÃ§Ã£o clicado
- Nenhum arquivo criado
- Sem mensagem de erro

**SoluÃ§Ãµes**:

1. **Verifique permissÃµes de arquivo**:
   ```bash
   ls -l /diretorio/exportacao/
   # Deve ter permissÃ£o de escrita
   ```

2. **Verifique espaÃ§o em disco**:
   ```bash
   df -h
   ```

3. **Tente local diferente**:
   - Exporte para diretÃ³rio home primeiro
   - Depois mova arquivo

4. **Verifique logs**:
   ```bash
   tail ~/.platform_base/logs/export.log
   ```

### Problema: CSV exportado estÃ¡ corrompido

**Sintomas**:
- Arquivo nÃ£o abre
- Colunas desalinhadas
- Caracteres extras

**SoluÃ§Ãµes**:

1. **Especifique codificaÃ§Ã£o explicitamente**:
   - DiÃ¡logo de exportaÃ§Ã£o â†’ CodificaÃ§Ã£o â†’ UTF-8 (BOM)

2. **Verifique delimitador**:
   - DiÃ¡logo de exportaÃ§Ã£o â†’ Delimitador â†’ Corresponda ferramenta de importaÃ§Ã£o

3. **Valide arquivo exportado**:
   ```bash
   head -10 exported.csv
   wc -l exported.csv
   ```

---

## Problemas de Plugins

### Problema: Plugin nÃ£o carrega

**Sintomas**:
- Plugin nÃ£o estÃ¡ no menu
- Erro de importaÃ§Ã£o
- "Plugin failed to load"

**SoluÃ§Ãµes**:

1. **Verifique diretÃ³rio de plugins**:
   ```bash
   ls ~/.platform_base/plugins/
   ```

2. **Verifique plugin.yaml**:
   ```bash
   cat ~/.platform_base/plugins/meuplugin/plugin.yaml
   # Valide sintaxe YAML
   ```

3. **Verifique dependÃªncias**:
   ```bash
   pip list | grep nome-plugin
   ```

4. **Habilite logging de plugin**:
   - ConfiguraÃ§Ãµes â†’ AvanÃ§ado â†’ Debug de Plugin: ON

5. **Reinstale plugin**:
   ```bash
   python -m platform_base.plugins uninstall meuplugin
   python -m platform_base.plugins install /caminho/para/meuplugin
   ```

---

## Problemas EspecÃ­ficos do Sistema

### Linux

**Problema**: Erro libEGL
```
ImportError: libEGL.so.1: cannot open shared object file
```

**SoluÃ§Ã£o**:
```bash
sudo apt-get install libegl1-mesa libgl1-mesa-glx
```

**Problema**: Erro de conexÃ£o X11
```
qt.qpa.xcb: could not connect to display
```

**SoluÃ§Ã£o**:
```bash
export DISPLAY=:0
xhost +local:
```

### macOS

**Problema**: App nÃ£o autorizado
```
"Platform Base" cannot be opened because the developer cannot be verified
```

**SoluÃ§Ã£o**:
```bash
xattr -cr /caminho/para/platform_base.app
```

**Problema**: Problemas de display Retina
**SoluÃ§Ã£o**:
- ConfiguraÃ§Ãµes â†’ Display â†’ Usar ResoluÃ§Ã£o Nativa: ON

### Windows

**Problema**: Falha ao carregar DLL
```
ImportError: DLL load failed while importing QtCore
```

**SoluÃ§Ã£o**:
- Instale Visual C++ Redistributable 2015-2022
- https://aka.ms/vs/17/release/vc_redist.x64.exe

**Problema**: AntivÃ­rus bloqueando
**SoluÃ§Ã£o**:
- Adicione exceÃ§Ã£o para platform_base.exe
- Ou desabilite antivÃ­rus temporariamente

---

## Obtendo Mais Ajuda

### Antes de Pedir Ajuda

1. **Verifique logs**:
   ```bash
   # Log da aplicaÃ§Ã£o
   cat ~/.platform_base/logs/app.log
   
   # Log de erros
   cat ~/.platform_base/logs/errors.log
   ```

2. **Tente modo verbose**:
   ```bash
   python launch_app.py --verbose --debug
   ```

3. **Verifique informaÃ§Ãµes do sistema**:
   ```bash
   python -c "import platform; print(platform.platform())"
   python -c "import platform_base; print(platform_base.__version__)"
   ```

### Reportando Issues

Ao criar issue no GitHub, inclua:

1. **VersÃ£o do Platform Base**
2. **Sistema operacional** (nome + versÃ£o)
3. **VersÃ£o do Python**
4. **Passos para reproduzir**
5. **Comportamento esperado vs real**
6. **Mensagens de erro** (traceback completo)
7. **Arquivos de log** (se relevante)
8. **Screenshots** (se problema de UI)

### Recursos da Comunidade

- **Issues no GitHub**: https://github.com/thiagoarcan/Warp/issues
- **DiscussÃµes**: https://github.com/thiagoarcan/Warp/discussions
- **DocumentaÃ§Ã£o**: Todos os docs no diretÃ³rio `/docs`

### Suporte Profissional

Para suporte empresarial, contate: support@platform-base.com

---

## Ferramentas de DiagnÃ³stico

### Script de InformaÃ§Ãµes do Sistema

```python
#!/usr/bin/env python3
"""Imprime informaÃ§Ãµes de diagnÃ³stico."""

import sys
import platform
import platform_base

print("InformaÃ§Ãµes do Sistema")
print("=" * 50)
print(f"SO: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print(f"Platform Base: {platform_base.__version__}")

try:
    from PyQt6 import QtCore
    print(f"PyQt6: {QtCore.PYQT_VERSION_STR}")
except ImportError:
    print("PyQt6: NÃƒO INSTALADO")

try:
    import numpy as np
    print(f"NumPy: {np.__version__}")
except ImportError:
    print("NumPy: NÃƒO INSTALADO")

print("\nDiretÃ³rio de instalaÃ§Ã£o:")
print(platform_base.__file__)
```

### VerificaÃ§Ã£o RÃ¡pida de SaÃºde

```bash
#!/bin/bash
echo "VerificaÃ§Ã£o de SaÃºde do Platform Base"
echo "============================"

# Verifique Python
python --version || echo "ERRO: Python nÃ£o encontrado"

# Verifique instalaÃ§Ã£o
python -c "import platform_base" && echo "âœ“ Pacote instalado" || echo "âœ— Pacote nÃ£o instalado"

# Verifique Qt
python -c "from PyQt6.QtWidgets import QApplication" && echo "âœ“ Qt disponÃ­vel" || echo "âœ— Qt nÃ£o disponÃ­vel"

# Verifique dependÃªncias
pip check && echo "âœ“ Sem conflitos de dependÃªncias" || echo "âœ— Problemas de dependÃªncias"

# Verifique logs
if [ -f ~/.platform_base/logs/app.log ]; then
    echo "âœ“ DiretÃ³rio de logs existe"
    echo "Ãšltima entrada de log:"
    tail -1 ~/.platform_base/logs/app.log
else
    echo "âœ— Sem logs encontrados"
fi
```

---

*Platform Base v2.0 - Guia de SoluÃ§Ã£o de Problemas*  
*Ãšltima AtualizaÃ§Ã£o: 2026-02-02*

