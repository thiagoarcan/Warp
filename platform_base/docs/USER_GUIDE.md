# Platform Base v2.0 - Guia Completo do UsuÃ¡rio

**Guia abrangente para usuÃ¡rios finais**

---

## Ãndice

1. [IntroduÃ§Ã£o](#introduÃ§Ã£o)
2. [ComeÃ§ando](#comeÃ§ando)
3. [InstalaÃ§Ã£o](#instalaÃ§Ã£o)
4. [VisÃ£o Geral da Interface](#visÃ£o-geral-da-interface)
5. [Carregando Dados](#carregando-dados)
6. [VisualizaÃ§Ã£o](#visualizaÃ§Ã£o)
7. [AnÃ¡lise de Dados](#anÃ¡lise-de-dados)
8. [Streaming e ReproduÃ§Ã£o](#streaming-e-reproduÃ§Ã£o)
9. [ExportaÃ§Ã£o e RelatÃ³rios](#exportaÃ§Ã£o-e-relatÃ³rios)
10. [Atalhos de Teclado](#atalhos-de-teclado)
11. [ConfiguraÃ§Ãµes](#configuraÃ§Ãµes)
12. [Dicas e Boas PrÃ¡ticas](#dicas-e-boas-prÃ¡ticas)
13. [Perguntas Frequentes](#perguntas-frequentes)
14. [Suporte](#suporte)

---

## IntroduÃ§Ã£o

O Platform Base Ã© uma aplicaÃ§Ã£o desktop para explorar e analisar dados de sÃ©ries temporais de sensores, sistemas de navegaÃ§Ã£o e equipamentos SCADA. Fornece visualizaÃ§Ã£o interativa, cÃ¡lculos avanÃ§ados e capacidades de exportaÃ§Ã£o.

### Recursos Principais

- ðŸ“Š **VisualizaÃ§Ã£o 2D/3D Interativa** - GrÃ¡ficos em tempo real com zoom, pan e seleÃ§Ã£o
- ðŸ“ **Suporte Multi-formato** - Arquivos CSV, Excel, Parquet, HDF5, MAT
- ðŸ§® **CÃ¡lculos AvanÃ§ados** - Derivadas, integrais, interpolaÃ§Ã£o, filtragem
- ðŸŽ¬ **Streaming Temporal** - ReproduÃ§Ã£o animada de dados temporais
- ðŸ”„ **SincronizaÃ§Ã£o** - Alinhamento automÃ¡tico de mÃºltiplas sÃ©ries temporais
- ðŸŒ™ **Temas** - Modos claro e escuro
- ðŸŒ **MultilÃ­ngue** - InglÃªs e PortuguÃªs

### Requisitos do Sistema

- **SO**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.12 ou superior
- **RAM**: 4GB mÃ­nimo, 8GB+ recomendado
- **Armazenamento**: 500MB para instalaÃ§Ã£o
- **Monitor**: 1920x1080 ou superior recomendado

---

## ComeÃ§ando

### InÃ­cio RÃ¡pido (5 minutos)

1. **Instale o Platform Base**
   ```bash
   pip install -e .
   ```

2. **Inicie a aplicaÃ§Ã£o**
   ```bash
   python launch_app.py
   ```

   `run_app.py` permanece disponível apenas como wrapper de compatibilidade.

3. **Carregue dados de exemplo**
   - Clique em "Arquivo â†’ Abrir" ou pressione `Ctrl+O`
   - Selecione um arquivo CSV ou Excel
   - Os dados aparecem no painel esquerdo

4. **Visualize**
   - DÃª um duplo clique em uma sÃ©rie na Ã¡rvore de dados
   - A sÃ©rie aparece no painel de visualizaÃ§Ã£o
   - Use o mouse para zoom/pan

5. **Calcule**
   - Selecione uma sÃ©rie
   - Clique em "OperaÃ§Ãµes â†’ Derivada"
   - O resultado aparece como nova sÃ©rie

---

## InstalaÃ§Ã£o

### InstalaÃ§Ã£o PadrÃ£o

```bash
# Clone o repositÃ³rio
git clone https://github.com/thiagoarcan/Warp.git
cd Warp/platform_base

# Instale as dependÃªncias
pip install -e .

# Instale ferramentas de desenvolvimento (opcional)
pip install -e ".[dev]"

# Instale extras de visualizaÃ§Ã£o (opcional)
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

### Verificar InstalaÃ§Ã£o

```bash
python -c "import platform_base; print(platform_base.__version__)"
# Deve exibir: 2.0.0
```

---

## VisÃ£o Geral da Interface

### Layout da Janela Principal

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Barra de Menu: Arquivo | Editar | Ver | OperaÃ§Ãµes | Ajuda  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Barra de Ferramentas: [Abrir] [Salvar] [Zoom] [Config]    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚              â”‚                              â”‚               â”‚
â”‚  Painel de   â”‚   Painel de VisualizaÃ§Ã£o     â”‚  Painel de    â”‚
â”‚  Dados       â”‚                              â”‚  OperaÃ§Ãµes    â”‚
â”‚              â”‚   [GrÃ¡ficos 2D/3D]          â”‚               â”‚
â”‚  ðŸ“ Arquivos â”‚                              â”‚  [Calcular]   â”‚
â”‚  ðŸ“Š SÃ©ries   â”‚   [Controles]               â”‚  [Filtrar]    â”‚
â”‚  â„¹ï¸  Info     â”‚                              â”‚  [Exportar]   â”‚
â”‚              â”‚                              â”‚               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Barra de Status: Pronto | MemÃ³ria: 120MB | SÃ©ries: 3       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### PainÃ©is

#### Painel de Dados (Esquerda)
- **VisualizaÃ§Ã£o em Ãrvore**: VisÃ£o hierÃ¡rquica de datasets e sÃ©ries
- **Abas de InformaÃ§Ã£o**: Resumo, Metadados, Qualidade
- **BotÃµes**: Carregar, Remover, Atualizar

#### Painel de VisualizaÃ§Ã£o (Centro)
- **Ãrea de GrÃ¡fico**: GrÃ¡ficos 2D ou 3D interativos
- **Abas**: MÃºltiplos grÃ¡ficos em abas
- **Barra de Ferramentas**: Zoom, Pan, Reset, Screenshot
- **Controles**: Espessura de linha, grade, configuraÃ§Ãµes de legenda

#### Painel de OperaÃ§Ãµes (Direita)
- **CÃ¡lculos**: Derivada, Integral, Ãrea
- **Filtros**: Passa-baixas, Passa-altas, Passa-faixa
- **InterpolaÃ§Ã£o**: Preencher lacunas nos dados
- **EstatÃ­sticas**: Min, Max, MÃ©dia, Desvio PadrÃ£o

---

## Carregando Dados

### Formatos Suportados

| Formato | ExtensÃ£o | Leitura | Escrita | Notas |
|---------|----------|---------|---------|-------|
| CSV | .csv | âœ… | âœ… | Mais rÃ¡pido |
| Excel | .xlsx | âœ… | âœ… | MÃºltiplas planilhas suportadas |
| Parquet | .parquet | âœ… | âœ… | Melhor para arquivos grandes |
| HDF5 | .h5, .hdf5 | âœ… | âœ… | Dados cientÃ­ficos |
| MAT | .mat | âœ… | âŒ | Arquivos MATLAB |

### Carregando Arquivos

**MÃ©todo 1: Menu**
1. Arquivo â†’ Abrir (ou `Ctrl+O`)
2. Selecione o arquivo
3. Configure as opÃ§Ãµes de importaÃ§Ã£o (se solicitado)
4. Clique em OK

**MÃ©todo 2: Arrastar e Soltar**
1. Arraste o arquivo do explorador de arquivos
2. Solte na janela principal
3. Os dados carregam automaticamente

**MÃ©todo 3: Linha de Comando**
```bash
python launch_app.py --file dados.csv
```

### ConfiguraÃ§Ãµes de ImportaÃ§Ã£o

#### OpÃ§Ãµes CSV
- **Delimitador**: VÃ­rgula, Tab, Ponto-e-vÃ­rgula, EspaÃ§o
- **CodificaÃ§Ã£o**: UTF-8, Latin-1, ASCII
- **Linha de CabeÃ§alho**: NÃºmero da linha para nomes de colunas
- **Pular Linhas**: NÃºmero de linhas para pular no inÃ­cio

#### OpÃ§Ãµes Excel
- **Planilha**: Selecione qual planilha carregar
- **Intervalo**: Intervalo especÃ­fico de cÃ©lulas (ex: A1:D1000)
- **Colunas de Data**: DetecÃ§Ã£o automÃ¡tica ou seleÃ§Ã£o manual

### Lidando com Arquivos Grandes

Para arquivos > 100MB:

1. **Use formato Parquet** - Mais rÃ¡pido que CSV/Excel
2. **Habilite decimaÃ§Ã£o** - ConfiguraÃ§Ãµes â†’ Desempenho â†’ Auto-decimaÃ§Ã£o
3. **Aumente limite de memÃ³ria** - ConfiguraÃ§Ãµes â†’ Desempenho â†’ Limite de MemÃ³ria
4. **Carregue apenas colunas especÃ­ficas** - DiÃ¡logo de importaÃ§Ã£o â†’ Selecionar Colunas

---

## VisualizaÃ§Ã£o

### GrÃ¡ficos 2D

#### Criando um GrÃ¡fico

1. **Duplo clique** em uma sÃ©rie na Ã¡rvore de dados
2. Ou **clique direito** â†’ "Adicionar ao GrÃ¡fico"
3. Ou **arraste** a sÃ©rie para a Ã¡rea do grÃ¡fico

#### Controles do GrÃ¡fico

- **Zoom**: Roda do mouse ou `Ctrl + Arrastar`
- **Pan**: Clicar e arrastar ou teclas de seta
- **Resetar**: Clique direito â†’ Resetar Vista ou pressione `R`
- **Selecionar**: `Ctrl + Arrastar` retÃ¢ngulo

#### MÃºltiplas SÃ©ries

Adicione mÃºltiplas sÃ©ries ao mesmo grÃ¡fico:
1. Clique na primeira sÃ©rie
2. Segure `Ctrl` e clique em sÃ©ries adicionais
3. Clique direito â†’ "Plotar Selecionadas"

Todas as sÃ©ries aparecem com cores diferentes.

#### MÃºltiplos Eixos Y

Para sÃ©ries com escalas diferentes:
1. Clique direito na sÃ©rie na legenda
2. Selecione "Mover para eixo Y2"
3. O segundo eixo Y aparece Ã  direita

#### PersonalizaÃ§Ã£o

**Estilo de Linha**
- Espessura: Barra de ferramentas â†’ Spinbox de Espessura de Linha
- Cor: Clique direito na sÃ©rie â†’ Mudar Cor
- Estilo: SÃ³lida, Tracejada, Pontilhada

**Grade**
- Alternar: Barra de ferramentas â†’ Checkbox Mostrar Grade
- Ou pressione `G`

**Legenda**
- Alternar: Barra de ferramentas â†’ Checkbox Mostrar Legenda
- Ou pressione `L`
- PosiÃ§Ã£o: Arraste a legenda para a posiÃ§Ã£o desejada

### GrÃ¡ficos 3D

#### Criando GrÃ¡fico 3D

1. Selecione exatamente 3 sÃ©ries (eixos X, Y, Z)
2. OperaÃ§Ãµes â†’ VisualizaÃ§Ã£o â†’ TrajetÃ³ria 3D
3. O grÃ¡fico 3D abre em nova janela

#### Controles 3D

- **Rotacionar**: Clicar e arrastar
- **Zoom**: Roda do mouse
- **Pan**: `Shift + Arrastar`
- **Resetar CÃ¢mera**: Pressione `R`

#### ConfiguraÃ§Ãµes 3D

- **Mapa de Cores**: ConfiguraÃ§Ãµes â†’ Dropdown de Mapa de Cores
- **Tamanho do Ponto**: ConfiguraÃ§Ãµes â†’ Slider de Tamanho do Ponto
- **Mostrar SuperfÃ­cie**: ConfiguraÃ§Ãµes â†’ Checkbox Mostrar SuperfÃ­cie

### Exportar GrÃ¡ficos

**Como Imagem**
1. Clique direito no grÃ¡fico â†’ Exportar
2. Escolha o formato: PNG, SVG, PDF
3. Selecione a resoluÃ§Ã£o (72-600 DPI)
4. Salvar

**Como AnimaÃ§Ã£o**
1. Habilite o modo streaming
2. Ferramentas â†’ Exportar â†’ VÃ­deo
3. Escolha o formato: MP4, GIF
4. Configure FPS e qualidade
5. Exportar

---

## AnÃ¡lise de Dados

### InterpolaÃ§Ã£o

Preencha lacunas em dados de sÃ©ries temporais:

1. Selecione a sÃ©rie com lacunas
2. OperaÃ§Ãµes â†’ InterpolaÃ§Ã£o
3. Escolha o mÃ©todo:
   - **Linear**: RÃ¡pido, simples
   - **Spline CÃºbico**: Curvas suaves
   - **PCHIP**: Preserva monotonicidade
   - **Akima**: Minimiza overshoot
4. Clique em "Aplicar"
5. Nova sÃ©rie interpolada criada

### Derivadas

Calcule a taxa de variaÃ§Ã£o:

1. Selecione a sÃ©rie (ex: posiÃ§Ã£o)
2. OperaÃ§Ãµes â†’ CÃ¡lculo â†’ Derivada
3. Selecione a ordem:
   - **1Âª**: Velocidade
   - **2Âª**: AceleraÃ§Ã£o
   - **3Âª**: Jerk
4. Resultado: Nova sÃ©rie com derivada

**Exemplo**: PosiÃ§Ã£o â†’ Velocidade
- Entrada: PosiÃ§Ã£o GPS (metros)
- SaÃ­da: Velocidade (m/s)

### Integrais

Calcule a Ã¡rea sob a curva:

1. Selecione a sÃ©rie (ex: velocidade)
2. OperaÃ§Ãµes â†’ CÃ¡lculo â†’ Integral
3. Escolha o mÃ©todo:
   - **Trapezoidal**: PadrÃ£o
   - **Simpson**: Mais preciso
4. Resultado: SÃ©rie integrada

**Exemplo**: Velocidade â†’ PosiÃ§Ã£o
- Entrada: Velocidade (m/s)
- SaÃ­da: Deslocamento (metros)

### Filtros

Remova ruÃ­do dos sinais:

#### Filtro Passa-Baixas
Remove ruÃ­do de alta frequÃªncia:
1. OperaÃ§Ãµes â†’ Filtros â†’ Passa-Baixas
2. Defina a frequÃªncia de corte (Hz)
3. Visualize o resultado
4. Aplicar

#### Filtro Passa-Altas
Remove deriva de baixa frequÃªncia:
1. OperaÃ§Ãµes â†’ Filtros â†’ Passa-Altas
2. Defina a frequÃªncia de corte
3. Aplicar

#### Filtro Passa-Faixa
MantÃ©m apenas faixa especÃ­fica de frequÃªncia:
1. OperaÃ§Ãµes â†’ Filtros â†’ Passa-Faixa
2. Defina cortes baixo e alto
3. Aplicar

#### MÃ©dia MÃ³vel
SuavizaÃ§Ã£o simples:
1. OperaÃ§Ãµes â†’ Filtros â†’ MÃ©dia MÃ³vel
2. Defina o tamanho da janela
3. Aplicar

### EstatÃ­sticas

Obtenha estatÃ­sticas resumidas:

1. Selecione a sÃ©rie
2. OperaÃ§Ãµes â†’ EstatÃ­sticas â†’ Resumo
3. Visualize os resultados:
   - Contagem, Min, Max
   - MÃ©dia, Mediana, Moda
   - Desvio PadrÃ£o, VariÃ¢ncia
   - Percentis (25%, 50%, 75%)

### SincronizaÃ§Ã£o

Alinhe mÃºltiplas sÃ©ries com grades temporais diferentes:

1. Selecione 2+ sÃ©ries
2. OperaÃ§Ãµes â†’ SincronizaÃ§Ã£o
3. Escolha o mÃ©todo:
   - **InterpolaÃ§Ã£o de Grade Comum**: Reamostra todas para a mesma grade temporal
   - **Vizinho Mais PrÃ³ximo**: RÃ¡pido, menos preciso
4. Aplicar
5. Todas as sÃ©ries agora tÃªm os mesmos pontos temporais

---

## Streaming e ReproduÃ§Ã£o

### VisÃ£o Geral

O modo streaming permite reproduÃ§Ã£o animada de dados de sÃ©ries temporais, Ãºtil para:
- Revisar dados de sensores ao longo do tempo
- Criar apresentaÃ§Ãµes
- Encontrar padrÃµes em dados temporais

### Habilitar Streaming

1. Carregue dados de sÃ©ries temporais
2. Ver â†’ Controles de Streaming
3. Painel de streaming aparece na parte inferior

### Controles

```
[â—€â—€] [â—€] [â–¶] [â–¶â–¶] [â– ] [Loop]
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤ Linha do Tempo
â”‚         PosiÃ§Ã£o              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Velocidade: [0.5x] [1x] [2x] [4x]
Janela: [5 seg] [10 seg] [30 seg]
```

- **Play/Pause**: Barra de espaÃ§o ou botÃ£o â–¶
- **Stop**: BotÃ£o â–  ou Escape
- **Buscar**: Clique na linha do tempo ou use setas Esquerda/Direita
- **Velocidade**: Ajuste a velocidade de reproduÃ§Ã£o
- **Janela**: Quantos segundos mostrados de uma vez

### Streaming com Filtros

Aplique filtros em tempo real durante a reproduÃ§Ã£o:

1. Habilite streaming
2. OperaÃ§Ãµes â†’ Filtros â†’ Tempo Real
3. Selecione o filtro (ex: Passa-Baixas)
4. Configure os parÃ¢metros
5. Play - o filtro se aplica conforme os dados sÃ£o transmitidos

### Exportar VÃ­deo de Streaming

1. Configure a janela de streaming
2. Ferramentas â†’ Exportar â†’ VÃ­deo
3. Escolha:
   - Formato: MP4, GIF
   - ResoluÃ§Ã£o: 720p, 1080p, 4K
   - FPS: 15, 24, 30, 60
4. Clique em "Exportar"
5. VÃ­deo gerado

---

## ExportaÃ§Ã£o e RelatÃ³rios

### Exportar Dados

#### SÃ©rie Ãšnica
1. Clique direito na sÃ©rie â†’ Exportar
2. Escolha o formato: CSV, Excel, Parquet
3. Salvar

#### MÃºltiplas SÃ©ries
1. Selecione sÃ©ries (Ctrl+Clique)
2. Arquivo â†’ Exportar Selecionadas
3. OpÃ§Ãµes:
   - **Arquivo Ãºnico, mÃºltiplas colunas**
   - **Arquivos separados**
4. Salvar

### ConfiguraÃ§Ã£o de ExportaÃ§Ã£o

**OpÃ§Ãµes CSV**
- Delimitador: VÃ­rgula, Tab, Ponto-e-vÃ­rgula
- CodificaÃ§Ã£o: UTF-8, Latin-1
- Incluir cabeÃ§alho: Sim/NÃ£o
- PrecisÃ£o: NÃºmero de casas decimais

**OpÃ§Ãµes Excel**
- Planilha Ãºnica: Todas as sÃ©ries em uma planilha
- MÃºltiplas planilhas: Uma sÃ©rie por planilha
- Incluir metadados: Adicionar planilha de informaÃ§Ãµes

### Gerar RelatÃ³rio

Crie relatÃ³rio em PDF/HTML:

1. Ferramentas â†’ Gerar RelatÃ³rio
2. Selecione o conteÃºdo:
   - [ ] EstatÃ­sticas resumidas
   - [ ] GrÃ¡ficos
   - [ ] Resultados de cÃ¡lculos
   - [ ] Metadados
3. Escolha o modelo: PadrÃ£o, TÃ©cnico, Executivo
4. Gerar
5. RelatÃ³rio salvo

---

## Atalhos de Teclado

### Gerais

| Atalho | AÃ§Ã£o |
|--------|------|
| `Ctrl+O` | Abrir arquivo |
| `Ctrl+S` | Salvar sessÃ£o |
| `Ctrl+W` | Fechar aba atual |
| `Ctrl+Q` | Sair da aplicaÃ§Ã£o |
| `Ctrl+Z` | Desfazer |
| `Ctrl+Y` | Refazer |
| `Ctrl+A` | Selecionar tudo |
| `Escape` | Desselecionar tudo |
| `F1` | Ajuda |
| `F5` | Atualizar dados |
| `F11` | Alternar tela cheia |

### VisualizaÃ§Ã£o

| Atalho | AÃ§Ã£o |
|--------|------|
| `EspaÃ§o` | Play/Pause streaming |
| `R` | Resetar vista |
| `G` | Alternar grade |
| `L` | Alternar legenda |
| `+` / `-` | Aumentar/diminuir zoom |
| `â†` `â†’` | Pan esquerda/direita |
| `â†‘` `â†“` | Pan cima/baixo |
| `Ctrl+Arrastar` | Zoom em caixa |
| `Shift+Arrastar` | Pan no grÃ¡fico |

### Dados

| Atalho | AÃ§Ã£o |
|--------|------|
| `Ctrl+D` | Duplicar sÃ©rie |
| `Delete` | Remover sÃ©rie selecionada |
| `Ctrl+F` | Encontrar sÃ©rie |
| `Ctrl+E` | Exportar selecionadas |

### OperaÃ§Ãµes

| Atalho | AÃ§Ã£o |
|--------|------|
| `Ctrl+1` | Calcular derivada |
| `Ctrl+2` | Calcular integral |
| `Ctrl+3` | Interpolar |
| `Ctrl+4` | Aplicar filtro |

---

## ConfiguraÃ§Ãµes

### ConfiguraÃ§Ãµes Gerais

**Arquivo â†’ PreferÃªncias** ou `Ctrl+,`

#### AparÃªncia
- **Tema**: Claro, Escuro, Sistema
- **Tamanho da Fonte**: 8-16pt
- **Idioma**: English, PortuguÃªs

#### Desempenho
- **Auto-decimaÃ§Ã£o**: Habilitar para arquivos > 100K pontos
- **Limite de decimaÃ§Ã£o**: NÃºmero de pontos
- **Limite de memÃ³ria**: Uso mÃ¡ximo de RAM (MB)
- **Tamanho do cache**: Tamanho do cache em disco (MB)

#### Dados
- **Delimitador padrÃ£o**: Delimitador CSV
- **Formato de data**: ISO, US, EU
- **Fuso horÃ¡rio**: UTC, Local
- **PrecisÃ£o**: Casas decimais para exibiÃ§Ã£o

#### VisualizaÃ§Ã£o
- **Cores padrÃ£o**: Esquema de cores para grÃ¡ficos
- **Espessura de linha**: Espessura padrÃ£o da linha
- **Grade**: Mostrar por padrÃ£o
- **Legenda**: Mostrar por padrÃ£o
- **Anti-aliasing**: Habilitar para grÃ¡ficos mais suaves

### ConfiguraÃ§Ãµes AvanÃ§adas

#### InterpolaÃ§Ã£o
- **MÃ©todo padrÃ£o**: Linear, Spline, PCHIP
- **Preencher lacunas**: Auto-preencher lacunas > X segundos
- **Tamanho mÃ¡ximo da lacuna**: NÃ£o interpolar lacunas maiores que

#### Filtros
- **Corte padrÃ£o**: FrequÃªncia de corte passa-baixas
- **Ordem do filtro**: Ordem do filtro Butterworth

#### Auto-salvamento
- **Habilitar**: Auto-salvar sessÃ£o
- **Intervalo**: Salvar a cada X minutos
- **Manter versÃµes**: NÃºmero de versÃµes de backup

---

## Dicas e Boas PrÃ¡ticas

### Dicas de Desempenho

1. **Use Parquet para arquivos grandes** - 5-10x mais rÃ¡pido que CSV
2. **Habilite auto-decimaÃ§Ã£o** - Para arquivos > 100K pontos
3. **Feche abas nÃ£o utilizadas** - Reduz uso de memÃ³ria
4. **Exporte dados filtrados** - Trabalhe com datasets menores
5. **Use atalhos de teclado** - Mais rÃ¡pido que o mouse

### Qualidade dos Dados

1. **Verifique lacunas** - Ver â†’ RelatÃ³rio de Qualidade
2. **Interpole dados faltantes** - OperaÃ§Ãµes â†’ InterpolaÃ§Ã£o
3. **Remova outliers** - OperaÃ§Ãµes â†’ Filtros â†’ DetecÃ§Ã£o de Outliers
4. **Valide timestamps** - Garanta que sejam monotonicamente crescentes
5. **Verifique unidades** - Verifique se as unidades fÃ­sicas fazem sentido

### Dicas de Fluxo de Trabalho

1. **Salve a sessÃ£o regularmente** - `Ctrl+S` apÃ³s mudanÃ§as importantes
2. **Use nomes descritivos** - Renomeie sÃ©ries para clareza
3. **Adicione metadados** - Clique direito â†’ Editar Metadados
4. **Exporte resultados intermediÃ¡rios** - Salve sÃ©ries calculadas
5. **Documente seu trabalho** - Use o painel de Notas

---

## Perguntas Frequentes

### Perguntas Gerais

**P: Quais formatos de arquivo sÃ£o suportados?**
R: CSV, Excel (.xlsx), Parquet, HDF5, arquivos MAT. Veja [Carregando Dados](#carregando-dados).

**P: QuÃ£o grandes podem ser os arquivos?**
R: Testado atÃ© 10M linhas (1GB). O desempenho depende da RAM disponÃ­vel.

**P: Posso usar para dados em tempo real?**
R: Sim, o modo streaming suporta reproduÃ§Ã£o e filtragem em tempo real.

**P: Existe uma API Python?**
R: Sim, veja [ReferÃªncia da API](API_REFERENCE.md).

### Perguntas sobre Dados

**P: Como lidar com dados faltantes?**
R: Use interpolaÃ§Ã£o: OperaÃ§Ãµes â†’ InterpolaÃ§Ã£o. Escolha o mÃ©todo baseado nas caracterÃ­sticas dos dados.

**P: Posso carregar mÃºltiplos arquivos?**
R: Sim, Arquivo â†’ Abrir MÃºltiplos ou arraste e solte mÃºltiplos arquivos.

**P: Como mesclar datasets?**
R: Selecione sÃ©ries â†’ OperaÃ§Ãµes â†’ SincronizaÃ§Ã£o â†’ Grade Comum.

### Perguntas sobre VisualizaÃ§Ã£o

**P: Como comparar duas sÃ©ries?**
R: Adicione ambas ao mesmo grÃ¡fico. Para escalas diferentes, use mÃºltiplos eixos Y.

**P: Posso exportar grÃ¡ficos?**
R: Sim, clique direito no grÃ¡fico â†’ Exportar. PNG, SVG, PDF suportados.

**P: Como criar animaÃ§Ãµes?**
R: Habilite streaming, depois Ferramentas â†’ Exportar â†’ VÃ­deo.

### Perguntas sobre CÃ¡lculos

**P: Qual mÃ©todo de interpolaÃ§Ã£o devo usar?**
R: 
- **Linear**: RÃ¡pido, bom para a maioria dos casos
- **Spline**: Curvas suaves
- **PCHIP**: Preserva monotonicidade

**P: QuÃ£o precisas sÃ£o as derivadas?**
R: Usa diferenciaÃ§Ã£o numÃ©rica (diferenÃ§as finitas). A precisÃ£o depende da taxa de amostragem e nÃ­vel de ruÃ­do.

**P: Posso escrever operaÃ§Ãµes customizadas?**
R: Sim, use o sistema de plugins. Veja [Desenvolvimento de Plugins](PLUGIN_DEVELOPMENT.md).

---

## Suporte

### DocumentaÃ§Ã£o

- **Guia do UsuÃ¡rio**: Este documento
- **ReferÃªncia da API**: [API_REFERENCE.md](API_REFERENCE.md)
- **Guia de Plugins**: [PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md)
- **SoluÃ§Ã£o de Problemas**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Comunidade

- **Issues no GitHub**: Reporte bugs
- **DiscussÃµes**: FaÃ§a perguntas, compartilhe dicas
- **Wiki**: Guias contribuÃ­dos pela comunidade

### Obtendo Ajuda

1. Verifique as [Perguntas Frequentes](#perguntas-frequentes) acima
2. Leia o [Guia de SoluÃ§Ã£o de Problemas](TROUBLESHOOTING.md)
3. Pesquise [Issues existentes no GitHub](https://github.com/thiagoarcan/Warp/issues)
4. Crie nova issue com:
   - VersÃ£o do Platform Base
   - Sistema operacional
   - Passos para reproduzir
   - Mensagens de erro/screenshots

---

## ApÃªndice

### GlossÃ¡rio

- **SÃ©rie**: Uma sequÃªncia de valores ao longo do tempo
- **Dataset**: ColeÃ§Ã£o de sÃ©ries relacionadas
- **DecimaÃ§Ã£o**: ReduÃ§Ã£o do nÃºmero de pontos para visualizaÃ§Ã£o
- **InterpolaÃ§Ã£o**: Estimativa de valores entre pontos conhecidos
- **SincronizaÃ§Ã£o**: Alinhamento de mÃºltiplas sÃ©ries temporais

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

### MÃ©todos de CÃ¡lculo

**MÃ©todos de Derivada**
- DiferenÃ§a progressiva
- DiferenÃ§a regressiva
- DiferenÃ§a central (padrÃ£o)

**MÃ©todos de Integral**
- Regra trapezoidal (padrÃ£o)
- Regra de Simpson
- IntegraÃ§Ã£o de Romberg

**Tipos de Filtro**
- Butterworth (resposta de frequÃªncia suave)
- Chebyshev (roll-off mais acentuado)
- Bessel (fase linear)

---

*Platform Base v2.0 - Guia do UsuÃ¡rio*  
*Ãšltima AtualizaÃ§Ã£o: 2026-02-02*  
*Copyright Â© 2026 Equipe Platform Base*


