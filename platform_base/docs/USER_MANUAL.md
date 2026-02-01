# Platform Base v2.0 - Manual do Usuário

## Guia Completo de Utilização

---

## Índice

1. [Introdução](#introdução)
2. [Instalação](#instalação)
3. [Início Rápido](#início-rápido)
4. [Interface do Usuário](#interface-do-usuário)
5. [Carregando Dados](#carregando-dados)
6. [Visualização 2D](#visualização-2d)
7. [Visualização 3D](#visualização-3d)
8. [Análises e Cálculos](#análises-e-cálculos)
9. [Streaming e Playback](#streaming-e-playback)
10. [Exportação](#exportação)
11. [Configurações](#configurações)
12. [Atalhos de Teclado](#atalhos-de-teclado)
13. [Solução de Problemas](#solução-de-problemas)
14. [FAQ](#faq)

---

## Introdução

O **Platform Base** é uma aplicação desktop para análise e visualização de séries temporais, desenvolvida especialmente para dados de navegação, sensores e sistemas embarcados.

### Principais Recursos

- 📈 **Visualização 2D** - Gráficos interativos com zoom, pan e seleção
- 🌐 **Visualização 3D** - Trajetórias tridimensionais com PyVista
- 📊 **Análises** - Derivadas, integrais, estatísticas, filtros
- 🎬 **Streaming** - Reprodução animada dos dados temporais
- 📁 **Múltiplos Formatos** - CSV, XLSX, MAT, HDF5
- 🌙 **Temas** - Modo claro e escuro
- 🌍 **Internacionalização** - Português e Inglês

---

## Instalação

### Requisitos do Sistema

- **Sistema Operacional**: Windows 10/11, Linux, macOS
- **Python**: 3.10 ou superior
- **RAM**: Mínimo 4GB, recomendado 8GB+
- **Disco**: 500MB para instalação

### Instalação via pip

```bash
pip install platform-base
```

### Instalação do Código Fonte

```bash
git clone https://github.com/thiagoarcan/Warp.git
cd Warp/platform_base
pip install -e .
```

### Dependências Opcionais

```bash
# Para visualização 3D
pip install pyvista pyvistaqt vtk

# Para exportação de vídeo
pip install moviepy imageio

# Para formatos adicionais
pip install h5py scipy
```

---

## Início Rápido

### 1. Iniciando a Aplicação

```bash
python -m platform_base.desktop.main
# ou
platform-base
```

### 2. Carregando seu Primeiro Arquivo

1. Clique em **Arquivo → Abrir** (ou `Ctrl+O`)
2. Selecione um arquivo CSV ou XLSX
3. Configure as colunas no diálogo de preview
4. Clique em **Carregar**

### 3. Visualizando os Dados

1. No painel de dados à esquerda, marque as séries desejadas
2. As séries aparecerão no gráfico automaticamente
3. Use o scroll do mouse para zoom
4. Arraste para navegar (pan)

### 4. Realizando uma Análise

1. Selecione uma série no painel de dados
2. Vá em **Análise → Calcular Derivada**
3. O resultado aparecerá como uma nova série

---

## Interface do Usuário

### Layout Principal

```
┌─────────────────────────────────────────────────────────────┐
│  Menu                                                       │
├─────────────────────────────────────────────────────────────┤
│  Toolbar                                                    │
├───────────────┬─────────────────────────────────────────────┤
│               │                                             │
│  Painel de    │           Área de Visualização              │
│  Dados        │                                             │
│               │                                             │
│               ├─────────────────────────────────────────────┤
│               │           Painel de Resultados              │
├───────────────┴─────────────────────────────────────────────┤
│  Status Bar                               Memória: 45%      │
└─────────────────────────────────────────────────────────────┘
```

### Painel de Dados

Lista hierárquica de datasets e séries:

- **Dataset**: Arquivo carregado
  - **Série 1**: Coluna de dados
  - **Série 2**: Outra coluna
  - ...

**Ações:**

- ✓ Checkbox: Mostrar/ocultar série no gráfico
- Duplo-clique: Renomear série
- Click direito: Menu de contexto

### Área de Visualização

Abas para diferentes tipos de visualização:

- **2D**: Gráficos de linhas padrão
- **3D**: Visualização tridimensional
- **Multi-View**: Múltiplos gráficos sincronizados

### Painel de Resultados

Exibe:

- Resultados de cálculos
- Estatísticas
- Logs de operações

---

## Carregando Dados

### Formatos Suportados

| Formato | Extensão | Notas |
|---------|----------|-------|
| CSV | .csv | Delimitador configurável |
| Excel | .xlsx, .xls | Múltiplas planilhas |
| MATLAB | .mat | v7.3 (HDF5) |
| HDF5 | .h5, .hdf5 | Estrutura hierárquica |

### Diálogo de Import

Ao abrir um arquivo, o diálogo de import permite:

1. **Preview**: Visualizar primeiras linhas
2. **Colunas**: Selecionar colunas a importar
3. **Coluna de Tempo**: Definir eixo X
4. **Tipos**: Configurar tipos de dados
5. **Encoding**: Escolher codificação (UTF-8, Latin1)

### Lazy Loading

Para arquivos grandes (>100MB):

- O sistema carrega apenas o necessário
- Dados são carregados conforme você navega
- Indicador mostra "Carregando..." durante operações

---

## Visualização 2D

### Navegação

| Ação | Mouse | Teclado |
|------|-------|---------|
| Zoom | Scroll | `Ctrl++` / `Ctrl+-` |
| Pan | Arrastar | Setas |
| Reset zoom | Duplo-clique | `Ctrl+0` |

### Seleção de Dados

1. **Seleção de Tempo**: `Ctrl+Arrastar` horizontalmente
2. **Seleção Retangular**: `Shift+Arrastar`
3. **Seleção por Lasso**: `Alt+Arrastar`

### Legenda

- Clique em item da legenda para ocultar/mostrar série
- Arraste legenda para reposicionar
- `L` para mostrar/ocultar legenda

### Multi-Eixo Y

Para séries com escalas diferentes:

1. Click direito na série
2. Selecione "Mover para Eixo Y2"
3. Até 4 eixos Y são suportados

### Grid

- `G` para mostrar/ocultar grade
- Configurar densidade em Configurações

---

## Visualização 3D

### Requisitos

Necessita PyVista instalado:

```bash
pip install pyvista pyvistaqt vtk
```

### Plotando Trajetória 3D

1. Selecione 3 séries (X, Y, Z)
2. Vá em **Visualização → Plot 3D**
3. A trajetória será renderizada

### Controles 3D

| Ação | Mouse |
|------|-------|
| Rotacionar | Arrastar |
| Zoom | Scroll |
| Pan | Shift+Arrastar |
| Reset | `R` |

### Colormap

Selecione o mapa de cores no dropdown:

- Viridis (padrão)
- Plasma
- Jet
- Turbo
- E mais...

---

## Análises e Cálculos

### Derivada

Calcula a derivada numérica:

1. Selecione uma série
2. **Análise → Derivada** (ou `Alt+D`)
3. Nova série criada: "Derivada de [nome]"

**Métodos disponíveis:**

- Diferenças finitas
- Diferenças centrais
- Spline derivativa

### Integral

Calcula a integral numérica:

1. Selecione uma série
2. **Análise → Integral** (ou `Alt+I`)
3. Resultado no painel de resultados

**Métodos:**

- Trapezoidal
- Simpson
- Romberg

### Estatísticas

Exibe estatísticas da série:

- Mínimo, Máximo
- Média, Mediana
- Desvio padrão
- Percentis

### Filtros

**Passa-Baixa:**

- Remove altas frequências
- Configure frequência de corte

**Passa-Alta:**

- Remove baixas frequências
- Para remover drift

**Passa-Banda:**

- Mantém faixa específica
- Configure min e max

---

## Streaming e Playback

### Controles

| Botão | Ação | Atalho |
|-------|------|--------|
| ▶️ | Play | `Space` |
| ⏸️ | Pause | `Space` |
| ⏹️ | Stop | `Escape` |
| ⏪ | -1s | `,` |
| ⏩ | +1s | `.` |

### Velocidade

Ajuste a velocidade de reprodução:

- 0.25x (muito lento)
- 0.5x (lento)
- 1x (tempo real)
- 2x (rápido)
- 4x, 8x, 16x (muito rápido)

Use `[` e `]` para ajustar.

### Timeline

- Arraste o slider para navegar
- Clique para pular para posição
- Minimap mostra overview dos dados

---

## Exportação

### Exportar Dados

1. **Arquivo → Exportar** (ou `Ctrl+E`)
2. Selecione formato:
   - CSV
   - Excel (XLSX)
   - MATLAB (MAT)
3. Configure opções
4. Escolha destino

### Exportar Imagem

1. **Arquivo → Exportar Imagem**
2. Formatos:
   - PNG (raster)
   - SVG (vetorial)
   - PDF (vetorial)
3. Configure resolução (DPI)

### Exportar Vídeo

1. **Arquivo → Exportar Vídeo**
2. Formatos:
   - MP4 (H.264)
   - AVI
   - GIF animado
3. Configure:
   - FPS (15-60)
   - Resolução
   - Duração

---

## Configurações

### Acessando Configurações

**Editar → Preferências** (ou `Ctrl+,`)

### Aparência

- **Tema**: Claro, Escuro, Sistema
- **Idioma**: Português, English
- **Fonte**: Tamanho e família

### Performance

- **Decimação**: Automática ou manual
- **Cache**: Tamanho máximo
- **Threads**: Número de workers

### Visualização

- **Cores**: Paleta de cores padrão
- **Grid**: Estilo e densidade
- **Legenda**: Posição padrão

### Auto-Save

- **Intervalo**: 1-30 minutos
- **Manter versões**: Últimas N
- **Local**: Pasta de backup

---

## Atalhos de Teclado

### Arquivo

| Ação | Atalho |
|------|--------|
| Novo | `Ctrl+N` |
| Abrir | `Ctrl+O` |
| Salvar | `Ctrl+S` |
| Salvar Como | `Ctrl+Shift+S` |
| Exportar | `Ctrl+E` |
| Fechar | `Ctrl+W` |
| Sair | `Ctrl+Q` |

### Edição

| Ação | Atalho |
|------|--------|
| Desfazer | `Ctrl+Z` |
| Refazer | `Ctrl+Y` |
| Copiar | `Ctrl+C` |
| Colar | `Ctrl+V` |
| Deletar | `Delete` |
| Selecionar Tudo | `Ctrl+A` |

### Visualização

| Ação | Atalho |
|------|--------|
| Zoom In | `Ctrl++` |
| Zoom Out | `Ctrl+-` |
| Ajustar | `Ctrl+0` |
| Tela Cheia | `F11` |
| Grid | `G` |
| Legenda | `L` |

### Análise

| Ação | Atalho |
|------|--------|
| Derivada | `Alt+D` |
| Integral | `Alt+I` |
| Estatísticas | `Alt+S` |
| Filtro | `Alt+F` |

### Playback

| Ação | Atalho |
|------|--------|
| Play/Pause | `Space` |
| Stop | `Escape` |
| +1 segundo | `.` |
| -1 segundo | `,` |
| Mais rápido | `]` |
| Mais lento | `[` |

### Personalização

Vá em **Ajuda → Atalhos de Teclado** para customizar.

---

## Solução de Problemas

### Aplicação não inicia

1. Verifique versão do Python: `python --version`
2. Reinstale: `pip install --force-reinstall platform-base`
3. Verifique logs em `~/.platform_base/logs/`

### Arquivo não carrega

1. Verifique formato suportado
2. Teste encoding (UTF-8 vs Latin1)
3. Verifique se arquivo não está corrompido

### Gráfico lento

1. Habilite decimação automática
2. Reduza número de pontos visíveis
3. Feche séries não utilizadas

### Erro de memória

1. Feche datasets não utilizados
2. Reduza cache em Configurações
3. Use lazy loading para arquivos grandes

### 3D não funciona

1. Instale PyVista: `pip install pyvista pyvistaqt vtk`
2. Verifique drivers de vídeo
3. Tente: `pyvista.global_theme.allow_empty_mesh = True`

---

## FAQ

### P: Qual o tamanho máximo de arquivo suportado?

R: Com lazy loading, não há limite teórico. Arquivos de até 10GB foram testados com sucesso. O sistema carrega dados sob demanda.

### P: Como sincronizo dois gráficos?

R: Use Multi-View. Clique direito em um gráfico → "Sincronizar com..." → Selecione o outro gráfico.

### P: Posso usar com dados de tempo real?

R: Sim, use o módulo de streaming. Dados podem ser adicionados em tempo real via API Python.

### P: Como recupero uma sessão perdida?

R: O auto-save cria backups em `~/.platform_base/backups/`. Vá em Arquivo → Abrir Backup.

### P: Posso criar plugins?

R: Sim! Veja a documentação de plugins em `docs/plugins/`. Plugins são módulos Python que implementam a interface `PluginBase`.

### P: Qual a licença do software?

R: MIT License. Uso livre para fins comerciais e não-comerciais.

---

## Suporte

- **Documentação**: <https://github.com/thiagoarcan/Warp/docs>
- **Issues**: <https://github.com/thiagoarcan/Warp/issues>
- **Email**: <suporte@platformbase.io>

---

*Manual do Platform Base v2.0*  
*Última atualização: Janeiro 2026*
