# Platform Base v2.0 - Guia Completo do Usuário

**Guia abrangente para usuários finais**

---

## Índice

1. [Introdução](#introdução)
2. [Começando](#começando)
3. [Instalação](#instalação)
4. [Visão Geral da Interface](#visão-geral-da-interface)
5. [Carregando Dados](#carregando-dados)
6. [Visualização](#visualização)
7. [Análise de Dados](#análise-de-dados)
8. [Streaming e Reprodução](#streaming-e-reprodução)
9. [Exportação e Relatórios](#exportação-e-relatórios)
10. [Atalhos de Teclado](#atalhos-de-teclado)
11. [Configurações](#configurações)
12. [Dicas e Boas Práticas](#dicas-e-boas-práticas)
13. [Perguntas Frequentes](#perguntas-frequentes)
14. [Suporte](#suporte)

---

## Introdução

O Platform Base é uma aplicação desktop para explorar e analisar dados de séries temporais de sensores, sistemas de navegação e equipamentos SCADA. Fornece visualização interativa, cálculos avançados e capacidades de exportação.

### Recursos Principais

- 📊 **Visualização 2D/3D Interativa** - Gráficos em tempo real com zoom, pan e seleção
- 📁 **Suporte Multi-formato** - Arquivos CSV, Excel, Parquet, HDF5, MAT
- 🧮 **Cálculos Avançados** - Derivadas, integrais, interpolação, filtragem
- 🎬 **Streaming Temporal** - Reprodução animada de dados temporais
- 🔄 **Sincronização** - Alinhamento automático de múltiplas séries temporais
- 🌙 **Temas** - Modos claro e escuro
- 🌍 **Multilíngue** - Inglês e Português

### Requisitos do Sistema

- **SO**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.12 ou superior
- **RAM**: 4GB mínimo, 8GB+ recomendado
- **Armazenamento**: 500MB para instalação
- **Monitor**: 1920x1080 ou superior recomendado

---

## Começando

### Início Rápido (5 minutos)

1. **Instale o Platform Base**
   ```bash
   pip install -e .
   ```

2. **Inicie a aplicação**
   ```bash
   python -m platform_base.desktop.main_window
   ```

3. **Carregue dados de exemplo**
   - Clique em "Arquivo → Abrir" ou pressione `Ctrl+O`
   - Selecione um arquivo CSV ou Excel
   - Os dados aparecem no painel esquerdo

4. **Visualize**
   - Dê um duplo clique em uma série na árvore de dados
   - A série aparece no painel de visualização
   - Use o mouse para zoom/pan

5. **Calcule**
   - Selecione uma série
   - Clique em "Operações → Derivada"
   - O resultado aparece como nova série

---

## Instalação

### Instalação Padrão

```bash
# Clone o repositório
git clone https://github.com/thiagoarcan/Warp.git
cd Warp/platform_base

# Instale as dependências
pip install -e .

# Instale ferramentas de desenvolvimento (opcional)
pip install -e ".[dev]"

# Instale extras de visualização (opcional)
pip install -e ".[viz]"
```

### Ambiente Virtual (Recomendado)

```bash
# Crie o ambiente virtual
python -m venv venv

# Ative (Windows)
venv\Scripts\activate

# Ative (Linux/Mac)
source venv/bin/activate

# Instale
pip install -e .
```

### Verificar Instalação

```bash
python -c "import platform_base; print(platform_base.__version__)"
# Deve exibir: 2.0.0
```

---

## Visão Geral da Interface

### Layout da Janela Principal

```
┌─────────────────────────────────────────────────────────────┐
│ Barra de Menu: Arquivo | Editar | Ver | Operações | Ajuda  │
├─────────────────────────────────────────────────────────────┤
│ Barra de Ferramentas: [Abrir] [Salvar] [Zoom] [Config]    │
├──────────────┬──────────────────────────────┬───────────────┤
│              │                              │               │
│  Painel de   │   Painel de Visualização     │  Painel de    │
│  Dados       │                              │  Operações    │
│              │   [Gráficos 2D/3D]          │               │
│  📁 Arquivos │                              │  [Calcular]   │
│  📊 Séries   │   [Controles]               │  [Filtrar]    │
│  ℹ️  Info     │                              │  [Exportar]   │
│              │                              │               │
├──────────────┴──────────────────────────────┴───────────────┤
│ Barra de Status: Pronto | Memória: 120MB | Séries: 3       │
└─────────────────────────────────────────────────────────────┘
```

### Painéis

#### Painel de Dados (Esquerda)
- **Visualização em Árvore**: Visão hierárquica de datasets e séries
- **Abas de Informação**: Resumo, Metadados, Qualidade
- **Botões**: Carregar, Remover, Atualizar

#### Painel de Visualização (Centro)
- **Área de Gráfico**: Gráficos 2D ou 3D interativos
- **Abas**: Múltiplos gráficos em abas
- **Barra de Ferramentas**: Zoom, Pan, Reset, Screenshot
- **Controles**: Espessura de linha, grade, configurações de legenda

#### Painel de Operações (Direita)
- **Cálculos**: Derivada, Integral, Área
- **Filtros**: Passa-baixas, Passa-altas, Passa-faixa
- **Interpolação**: Preencher lacunas nos dados
- **Estatísticas**: Min, Max, Média, Desvio Padrão

---

## Carregando Dados

### Formatos Suportados

| Formato | Extensão | Leitura | Escrita | Notas |
|---------|----------|---------|---------|-------|
| CSV | .csv | ✅ | ✅ | Mais rápido |
| Excel | .xlsx | ✅ | ✅ | Múltiplas planilhas suportadas |
| Parquet | .parquet | ✅ | ✅ | Melhor para arquivos grandes |
| HDF5 | .h5, .hdf5 | ✅ | ✅ | Dados científicos |
| MAT | .mat | ✅ | ❌ | Arquivos MATLAB |

### Carregando Arquivos

**Método 1: Menu**
1. Arquivo → Abrir (ou `Ctrl+O`)
2. Selecione o arquivo
3. Configure as opções de importação (se solicitado)
4. Clique em OK

**Método 2: Arrastar e Soltar**
1. Arraste o arquivo do explorador de arquivos
2. Solte na janela principal
3. Os dados carregam automaticamente

**Método 3: Linha de Comando**
```bash
python launch_app.py --file dados.csv
```

### Configurações de Importação

#### Opções CSV
- **Delimitador**: Vírgula, Tab, Ponto-e-vírgula, Espaço
- **Codificação**: UTF-8, Latin-1, ASCII
- **Linha de Cabeçalho**: Número da linha para nomes de colunas
- **Pular Linhas**: Número de linhas para pular no início

#### Opções Excel
- **Planilha**: Selecione qual planilha carregar
- **Intervalo**: Intervalo específico de células (ex: A1:D1000)
- **Colunas de Data**: Detecção automática ou seleção manual

### Lidando com Arquivos Grandes

Para arquivos > 100MB:

1. **Use formato Parquet** - Mais rápido que CSV/Excel
2. **Habilite decimação** - Configurações → Desempenho → Auto-decimação
3. **Aumente limite de memória** - Configurações → Desempenho → Limite de Memória
4. **Carregue apenas colunas específicas** - Diálogo de importação → Selecionar Colunas

---

## Visualização

### Gráficos 2D

#### Criando um Gráfico

1. **Duplo clique** em uma série na árvore de dados
2. Ou **clique direito** → "Adicionar ao Gráfico"
3. Ou **arraste** a série para a área do gráfico

#### Controles do Gráfico

- **Zoom**: Roda do mouse ou `Ctrl + Arrastar`
- **Pan**: Clicar e arrastar ou teclas de seta
- **Resetar**: Clique direito → Resetar Vista ou pressione `R`
- **Selecionar**: `Ctrl + Arrastar` retângulo

#### Múltiplas Séries

Adicione múltiplas séries ao mesmo gráfico:
1. Clique na primeira série
2. Segure `Ctrl` e clique em séries adicionais
3. Clique direito → "Plotar Selecionadas"

Todas as séries aparecem com cores diferentes.

#### Múltiplos Eixos Y

Para séries com escalas diferentes:
1. Clique direito na série na legenda
2. Selecione "Mover para eixo Y2"
3. O segundo eixo Y aparece à direita

#### Personalização

**Estilo de Linha**
- Espessura: Barra de ferramentas → Spinbox de Espessura de Linha
- Cor: Clique direito na série → Mudar Cor
- Estilo: Sólida, Tracejada, Pontilhada

**Grade**
- Alternar: Barra de ferramentas → Checkbox Mostrar Grade
- Ou pressione `G`

**Legenda**
- Alternar: Barra de ferramentas → Checkbox Mostrar Legenda
- Ou pressione `L`
- Posição: Arraste a legenda para a posição desejada

### Gráficos 3D

#### Criando Gráfico 3D

1. Selecione exatamente 3 séries (eixos X, Y, Z)
2. Operações → Visualização → Trajetória 3D
3. O gráfico 3D abre em nova janela

#### Controles 3D

- **Rotacionar**: Clicar e arrastar
- **Zoom**: Roda do mouse
- **Pan**: `Shift + Arrastar`
- **Resetar Câmera**: Pressione `R`

#### Configurações 3D

- **Mapa de Cores**: Configurações → Dropdown de Mapa de Cores
- **Tamanho do Ponto**: Configurações → Slider de Tamanho do Ponto
- **Mostrar Superfície**: Configurações → Checkbox Mostrar Superfície

### Exportar Gráficos

**Como Imagem**
1. Clique direito no gráfico → Exportar
2. Escolha o formato: PNG, SVG, PDF
3. Selecione a resolução (72-600 DPI)
4. Salvar

**Como Animação**
1. Habilite o modo streaming
2. Ferramentas → Exportar → Vídeo
3. Escolha o formato: MP4, GIF
4. Configure FPS e qualidade
5. Exportar

---

## Análise de Dados

### Interpolação

Preencha lacunas em dados de séries temporais:

1. Selecione a série com lacunas
2. Operações → Interpolação
3. Escolha o método:
   - **Linear**: Rápido, simples
   - **Spline Cúbico**: Curvas suaves
   - **PCHIP**: Preserva monotonicidade
   - **Akima**: Minimiza overshoot
4. Clique em "Aplicar"
5. Nova série interpolada criada

### Derivadas

Calcule a taxa de variação:

1. Selecione a série (ex: posição)
2. Operações → Cálculo → Derivada
3. Selecione a ordem:
   - **1ª**: Velocidade
   - **2ª**: Aceleração
   - **3ª**: Jerk
4. Resultado: Nova série com derivada

**Exemplo**: Posição → Velocidade
- Entrada: Posição GPS (metros)
- Saída: Velocidade (m/s)

### Integrais

Calcule a área sob a curva:

1. Selecione a série (ex: velocidade)
2. Operações → Cálculo → Integral
3. Escolha o método:
   - **Trapezoidal**: Padrão
   - **Simpson**: Mais preciso
4. Resultado: Série integrada

**Exemplo**: Velocidade → Posição
- Entrada: Velocidade (m/s)
- Saída: Deslocamento (metros)

### Filtros

Remova ruído dos sinais:

#### Filtro Passa-Baixas
Remove ruído de alta frequência:
1. Operações → Filtros → Passa-Baixas
2. Defina a frequência de corte (Hz)
3. Visualize o resultado
4. Aplicar

#### Filtro Passa-Altas
Remove deriva de baixa frequência:
1. Operações → Filtros → Passa-Altas
2. Defina a frequência de corte
3. Aplicar

#### Filtro Passa-Faixa
Mantém apenas faixa específica de frequência:
1. Operações → Filtros → Passa-Faixa
2. Defina cortes baixo e alto
3. Aplicar

#### Média Móvel
Suavização simples:
1. Operações → Filtros → Média Móvel
2. Defina o tamanho da janela
3. Aplicar

### Estatísticas

Obtenha estatísticas resumidas:

1. Selecione a série
2. Operações → Estatísticas → Resumo
3. Visualize os resultados:
   - Contagem, Min, Max
   - Média, Mediana, Moda
   - Desvio Padrão, Variância
   - Percentis (25%, 50%, 75%)

### Sincronização

Alinhe múltiplas séries com grades temporais diferentes:

1. Selecione 2+ séries
2. Operações → Sincronização
3. Escolha o método:
   - **Interpolação de Grade Comum**: Reamostra todas para a mesma grade temporal
   - **Vizinho Mais Próximo**: Rápido, menos preciso
4. Aplicar
5. Todas as séries agora têm os mesmos pontos temporais

---

## Streaming e Reprodução

### Visão Geral

O modo streaming permite reprodução animada de dados de séries temporais, útil para:
- Revisar dados de sensores ao longo do tempo
- Criar apresentações
- Encontrar padrões em dados temporais

### Habilitar Streaming

1. Carregue dados de séries temporais
2. Ver → Controles de Streaming
3. Painel de streaming aparece na parte inferior

### Controles

```
[◀◀] [◀] [▶] [▶▶] [■] [Loop]
├─────────────────────────────┤ Linha do Tempo
│         Posição              │
└─────────────────────────────┘

Velocidade: [0.5x] [1x] [2x] [4x]
Janela: [5 seg] [10 seg] [30 seg]
```

- **Play/Pause**: Barra de espaço ou botão ▶
- **Stop**: Botão ■ ou Escape
- **Buscar**: Clique na linha do tempo ou use setas Esquerda/Direita
- **Velocidade**: Ajuste a velocidade de reprodução
- **Janela**: Quantos segundos mostrados de uma vez

### Streaming com Filtros

Aplique filtros em tempo real durante a reprodução:

1. Habilite streaming
2. Operações → Filtros → Tempo Real
3. Selecione o filtro (ex: Passa-Baixas)
4. Configure os parâmetros
5. Play - o filtro se aplica conforme os dados são transmitidos

### Exportar Vídeo de Streaming

1. Configure a janela de streaming
2. Ferramentas → Exportar → Vídeo
3. Escolha:
   - Formato: MP4, GIF
   - Resolução: 720p, 1080p, 4K
   - FPS: 15, 24, 30, 60
4. Clique em "Exportar"
5. Vídeo gerado

---

## Exportação e Relatórios

### Exportar Dados

#### Série Única
1. Clique direito na série → Exportar
2. Escolha o formato: CSV, Excel, Parquet
3. Salvar

#### Múltiplas Séries
1. Selecione séries (Ctrl+Clique)
2. Arquivo → Exportar Selecionadas
3. Opções:
   - **Arquivo único, múltiplas colunas**
   - **Arquivos separados**
4. Salvar

### Configuração de Exportação

**Opções CSV**
- Delimitador: Vírgula, Tab, Ponto-e-vírgula
- Codificação: UTF-8, Latin-1
- Incluir cabeçalho: Sim/Não
- Precisão: Número de casas decimais

**Opções Excel**
- Planilha única: Todas as séries em uma planilha
- Múltiplas planilhas: Uma série por planilha
- Incluir metadados: Adicionar planilha de informações

### Gerar Relatório

Crie relatório em PDF/HTML:

1. Ferramentas → Gerar Relatório
2. Selecione o conteúdo:
   - [ ] Estatísticas resumidas
   - [ ] Gráficos
   - [ ] Resultados de cálculos
   - [ ] Metadados
3. Escolha o modelo: Padrão, Técnico, Executivo
4. Gerar
5. Relatório salvo

---

## Atalhos de Teclado

### Gerais

| Atalho | Ação |
|--------|------|
| `Ctrl+O` | Abrir arquivo |
| `Ctrl+S` | Salvar sessão |
| `Ctrl+W` | Fechar aba atual |
| `Ctrl+Q` | Sair da aplicação |
| `Ctrl+Z` | Desfazer |
| `Ctrl+Y` | Refazer |
| `Ctrl+A` | Selecionar tudo |
| `Escape` | Desselecionar tudo |
| `F1` | Ajuda |
| `F5` | Atualizar dados |
| `F11` | Alternar tela cheia |

### Visualização

| Atalho | Ação |
|--------|------|
| `Espaço` | Play/Pause streaming |
| `R` | Resetar vista |
| `G` | Alternar grade |
| `L` | Alternar legenda |
| `+` / `-` | Aumentar/diminuir zoom |
| `←` `→` | Pan esquerda/direita |
| `↑` `↓` | Pan cima/baixo |
| `Ctrl+Arrastar` | Zoom em caixa |
| `Shift+Arrastar` | Pan no gráfico |

### Dados

| Atalho | Ação |
|--------|------|
| `Ctrl+D` | Duplicar série |
| `Delete` | Remover série selecionada |
| `Ctrl+F` | Encontrar série |
| `Ctrl+E` | Exportar selecionadas |

### Operações

| Atalho | Ação |
|--------|------|
| `Ctrl+1` | Calcular derivada |
| `Ctrl+2` | Calcular integral |
| `Ctrl+3` | Interpolar |
| `Ctrl+4` | Aplicar filtro |

---

## Configurações

### Configurações Gerais

**Arquivo → Preferências** ou `Ctrl+,`

#### Aparência
- **Tema**: Claro, Escuro, Sistema
- **Tamanho da Fonte**: 8-16pt
- **Idioma**: English, Português

#### Desempenho
- **Auto-decimação**: Habilitar para arquivos > 100K pontos
- **Limite de decimação**: Número de pontos
- **Limite de memória**: Uso máximo de RAM (MB)
- **Tamanho do cache**: Tamanho do cache em disco (MB)

#### Dados
- **Delimitador padrão**: Delimitador CSV
- **Formato de data**: ISO, US, EU
- **Fuso horário**: UTC, Local
- **Precisão**: Casas decimais para exibição

#### Visualização
- **Cores padrão**: Esquema de cores para gráficos
- **Espessura de linha**: Espessura padrão da linha
- **Grade**: Mostrar por padrão
- **Legenda**: Mostrar por padrão
- **Anti-aliasing**: Habilitar para gráficos mais suaves

### Configurações Avançadas

#### Interpolação
- **Método padrão**: Linear, Spline, PCHIP
- **Preencher lacunas**: Auto-preencher lacunas > X segundos
- **Tamanho máximo da lacuna**: Não interpolar lacunas maiores que

#### Filtros
- **Corte padrão**: Frequência de corte passa-baixas
- **Ordem do filtro**: Ordem do filtro Butterworth

#### Auto-salvamento
- **Habilitar**: Auto-salvar sessão
- **Intervalo**: Salvar a cada X minutos
- **Manter versões**: Número de versões de backup

---

## Dicas e Boas Práticas

### Dicas de Desempenho

1. **Use Parquet para arquivos grandes** - 5-10x mais rápido que CSV
2. **Habilite auto-decimação** - Para arquivos > 100K pontos
3. **Feche abas não utilizadas** - Reduz uso de memória
4. **Exporte dados filtrados** - Trabalhe com datasets menores
5. **Use atalhos de teclado** - Mais rápido que o mouse

### Qualidade dos Dados

1. **Verifique lacunas** - Ver → Relatório de Qualidade
2. **Interpole dados faltantes** - Operações → Interpolação
3. **Remova outliers** - Operações → Filtros → Detecção de Outliers
4. **Valide timestamps** - Garanta que sejam monotonicamente crescentes
5. **Verifique unidades** - Verifique se as unidades físicas fazem sentido

### Dicas de Fluxo de Trabalho

1. **Salve a sessão regularmente** - `Ctrl+S` após mudanças importantes
2. **Use nomes descritivos** - Renomeie séries para clareza
3. **Adicione metadados** - Clique direito → Editar Metadados
4. **Exporte resultados intermediários** - Salve séries calculadas
5. **Documente seu trabalho** - Use o painel de Notas

---

## Perguntas Frequentes

### Perguntas Gerais

**P: Quais formatos de arquivo são suportados?**
R: CSV, Excel (.xlsx), Parquet, HDF5, arquivos MAT. Veja [Carregando Dados](#carregando-dados).

**P: Quão grandes podem ser os arquivos?**
R: Testado até 10M linhas (1GB). O desempenho depende da RAM disponível.

**P: Posso usar para dados em tempo real?**
R: Sim, o modo streaming suporta reprodução e filtragem em tempo real.

**P: Existe uma API Python?**
R: Sim, veja [Referência da API](API_REFERENCE.md).

### Perguntas sobre Dados

**P: Como lidar com dados faltantes?**
R: Use interpolação: Operações → Interpolação. Escolha o método baseado nas características dos dados.

**P: Posso carregar múltiplos arquivos?**
R: Sim, Arquivo → Abrir Múltiplos ou arraste e solte múltiplos arquivos.

**P: Como mesclar datasets?**
R: Selecione séries → Operações → Sincronização → Grade Comum.

### Perguntas sobre Visualização

**P: Como comparar duas séries?**
R: Adicione ambas ao mesmo gráfico. Para escalas diferentes, use múltiplos eixos Y.

**P: Posso exportar gráficos?**
R: Sim, clique direito no gráfico → Exportar. PNG, SVG, PDF suportados.

**P: Como criar animações?**
R: Habilite streaming, depois Ferramentas → Exportar → Vídeo.

### Perguntas sobre Cálculos

**P: Qual método de interpolação devo usar?**
R: 
- **Linear**: Rápido, bom para a maioria dos casos
- **Spline**: Curvas suaves
- **PCHIP**: Preserva monotonicidade

**P: Quão precisas são as derivadas?**
R: Usa diferenciação numérica (diferenças finitas). A precisão depende da taxa de amostragem e nível de ruído.

**P: Posso escrever operações customizadas?**
R: Sim, use o sistema de plugins. Veja [Desenvolvimento de Plugins](PLUGIN_DEVELOPMENT.md).

---

## Suporte

### Documentação

- **Guia do Usuário**: Este documento
- **Referência da API**: [API_REFERENCE.md](API_REFERENCE.md)
- **Guia de Plugins**: [PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md)
- **Solução de Problemas**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Comunidade

- **Issues no GitHub**: Reporte bugs
- **Discussões**: Faça perguntas, compartilhe dicas
- **Wiki**: Guias contribuídos pela comunidade

### Obtendo Ajuda

1. Verifique as [Perguntas Frequentes](#perguntas-frequentes) acima
2. Leia o [Guia de Solução de Problemas](TROUBLESHOOTING.md)
3. Pesquise [Issues existentes no GitHub](https://github.com/thiagoarcan/Warp/issues)
4. Crie nova issue com:
   - Versão do Platform Base
   - Sistema operacional
   - Passos para reproduzir
   - Mensagens de erro/screenshots

---

## Apêndice

### Glossário

- **Série**: Uma sequência de valores ao longo do tempo
- **Dataset**: Coleção de séries relacionadas
- **Decimação**: Redução do número de pontos para visualização
- **Interpolação**: Estimativa de valores entre pontos conhecidos
- **Sincronização**: Alinhamento de múltiplas séries temporais

### Detalhes dos Formatos de Arquivo

#### Estrutura CSV
```
time,sensor_1,sensor_2
0.0,1.5,2.3
0.1,1.6,2.4
0.2,1.4,2.2
```

#### Estrutura Excel
- Planilha 1: Dados (colunas tempo + valor)
- Planilha 2: Metadados (opcional)

### Métodos de Cálculo

**Métodos de Derivada**
- Diferença progressiva
- Diferença regressiva
- Diferença central (padrão)

**Métodos de Integral**
- Regra trapezoidal (padrão)
- Regra de Simpson
- Integração de Romberg

**Tipos de Filtro**
- Butterworth (resposta de frequência suave)
- Chebyshev (roll-off mais acentuado)
- Bessel (fase linear)

---

*Platform Base v2.0 - Guia do Usuário*  
*Última Atualização: 2026-02-02*  
*Copyright © 2026 Equipe Platform Base*
