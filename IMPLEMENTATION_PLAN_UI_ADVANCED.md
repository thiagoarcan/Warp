# Plano de Implementação - Requisitos UI e Funcionalidades Avançadas

## Status: EM PROGRESSO
Data de Início: 2026-02-05

---

## Requisitos Gerais

### UI e Responsividade
- [ ] Corrigir responsividade para monitores 29" ultrawide
- [ ] Seleção múltipla de arquivos Excel simultâneos
- [ ] Migração de funcionalidades para toolbar (reduzir exposição)
- [ ] Eixos X com formato datetime
- [ ] Sistema de 4 gráficos independentes por aba
  - [ ] Redimensionáveis
  - [ ] Responsivos
  - [ ] Botão adicionar/remover gráficos
- [ ] Sistema de cores consistente
  - [ ] Mesma série = mesma cor em gráficos diferentes
  - [ ] Sem cores repetidas entre séries diferentes
- [ ] Legenda móvel (drag-and-drop)
- [ ] Escalas dinâmicas nos eixos Y
  - [ ] Ajuste automático ao ocultar/mostrar séries
  - [ ] Durante streaming
- [ ] Tooltips interativos mostrando todas as séries

### Menu de Contexto - Séries Plotadas
Ao clicar com botão direito sobre uma série:

#### Cálculos Matemáticos
- [ ] Derivadas
  - [ ] 1ª derivada
  - [ ] 2ª derivada
  - [ ] 3ª derivada
- [ ] Integrais
  - [ ] Área sob a curva
  - [ ] Área entre curvas (com seleção de curva limite via combobox)
- [ ] Estatísticas
  - [ ] Linha média
  - [ ] Linha mediana
  - [ ] Máximo
  - [ ] Mínimo
  - [ ] Moda
  - [ ] Desvio padrão (com multiplicador: 1x, 1.5x, 2x, etc)
- [ ] Análise
  - [ ] Tendência
  - [ ] Taxa de variação
- [ ] Regressões (≥5 tipos)
  - [ ] Linear
  - [ ] Polinomial (com seleção de ordem)
  - [ ] Exponencial
  - [ ] Logarítmica
  - [ ] Potência
  - [ ] Seletor de ordem ajustável
- [ ] Interpolações (diversos tipos)
  - [ ] Linear
  - [ ] Cubic Spline
  - [ ] Smoothing Spline
  - [ ] MLS
  - [ ] GPR
  - [ ] Lomb-Scargle
  - [ ] Outros conforme disponíveis

#### Operações sobre Cálculos
- [ ] Aplicar qualquer cálculo acima sobre resultados já calculados
- [ ] Árvore de operações recursivas

#### Configurações Visuais
- [ ] Trocar série para eixo secundário
- [ ] Criar eixos Y adicionais
- [ ] Trocar tipo de traço da série
  - [ ] Linha contínua
  - [ ] Linha tracejada
  - [ ] Pontos
  - [ ] Linha + pontos

#### Anotações
- [ ] Clicar em ponto específico para adicionar comentário
  - [ ] Registro associado ao ponto
  - [ ] Indicação visual no gráfico
  - [ ] Timestamp do ponto
  - [ ] Valor do ponto
  - [ ] Opção de exclusão

#### Export
- [ ] Exportar dados em XLSX
- [ ] Exportar dados em CSV
- [ ] Incluir anotações no export (se existirem)

### Menu de Contexto - Legenda
Ao clicar com botão esquerdo na legenda:
- [ ] Ocultar/mostrar série

Ao clicar com botão direito na legenda:
- [ ] Abrir mesmo menu do clique na série plotada

---

## Teste de Validação End-to-End

### Arquivos de Entrada
Localização: `/` (raiz do projeto)

1. ✅ BAR_FT-OP10.xlsx (39927 bytes)
2. ✅ BAR_PT-OP10.xlsx (137649 bytes)
3. ✅ PLN_FT-OP10.xlsx (376150 bytes)
4. ✅ PLN_PT-OP10.xlsx (1454923 bytes)

### Processamento Requerido

#### 1-4: Para cada arquivo (BAR_FT, BAR_PT, PLN_FT, PLN_PT)

##### Grupo A: Cálculos Básicos
- [ ] Dados brutos
- [ ] 1ª derivada
- [ ] 2ª derivada
- [ ] 3ª derivada
- [ ] Área sob a curva
- [ ] Tendência
- [ ] Taxa de variação
- [ ] Todas as interpolações (intervalo: 15 segundos)
- [ ] Todos os tipos de regressão

##### Grupo B: Estatísticas
- [ ] Desvio padrão 1x
- [ ] Desvio padrão 1.5x
- [ ] Média
- [ ] Mediana
- [ ] Moda

#### 5: Áreas Entre Curvas
- [ ] BAR_FT-OP10 x BAR_PT-OP10
- [ ] BAR_FT-OP10 x PLN_FT-OP10
- [ ] PLN_FT-OP10 x PLN_PT-OP10
- [ ] PLN_PT-OP10 x BAR_PT-OP10

#### 6: Sincronização Temporal (5 segundos)
- [ ] BAR_FT-OP10
- [ ] BAR_PT-OP10
- [ ] PLN_FT-OP10
- [ ] PLN_PT-OP10

#### 7: Interpolação Sincronizada (13 segundos)
- [ ] BAR_FT-OP10
- [ ] BAR_PT-OP10
- [ ] PLN_FT-OP10
- [ ] PLN_PT-OP10

#### 8: Cálculos Recursivos
Para cada série gerada nos itens 6 e 7:
- [ ] Repetir Grupo A (derivadas, área, tendência, etc)
- [ ] Repetir Grupo B (estatísticas)

### Arquivo de Saída
- [ ] Nome: `validation_results_[timestamp].xlsx`
- [ ] Sheets organizadas por tipo de cálculo
- [ ] Incluir metadados de processamento
- [ ] Incluir timestamps e parâmetros usados

---

## Fases de Implementação

### Fase 1: Fundação (Dias 1-3)
- [ ] Sistema de layout multi-plot (até 4 por aba)
- [ ] Gerenciador de cores consistente
- [ ] Responsividade para ultrawide
- [ ] Eixos datetime
- [ ] Seleção múltipla de arquivos

### Fase 2: Cálculos Core (Dias 4-7)
- [ ] Módulo de derivadas (1ª, 2ª, 3ª)
- [ ] Módulo de integrais (área sob/entre curvas)
- [ ] Módulo de estatísticas (média, mediana, moda, std dev)
- [ ] Módulo de regressões (≥5 tipos)
- [ ] Módulo de interpolações (todos os tipos)

### Fase 3: UI Interativa (Dias 8-10)
- [ ] Menu de contexto completo
- [ ] Sistema de anotações
- [ ] Legenda interativa e móvel
- [ ] Tooltips multi-série
- [ ] Escalas dinâmicas

### Fase 4: Export e Sincronização (Dias 11-12)
- [ ] Export XLSX/CSV com anotações
- [ ] Sincronização temporal
- [ ] Interpolação sincronizada
- [ ] Sistema de operações recursivas

### Fase 5: Teste de Validação (Dia 13)
- [ ] Script de teste automatizado
- [ ] Processamento dos 4 arquivos Excel
- [ ] Geração de arquivo de resultados
- [ ] Validação de todos os cálculos

---

## Notas Técnicas

### Dependências Críticas
- PyQt6 para UI
- pandas para manipulação de dados
- numpy/scipy para cálculos matemáticos
- matplotlib/pyqtgraph para visualização
- openpyxl para Excel

### Considerações de Arquitetura
1. **ColorManager**: Serviço centralizado para gerenciar cores de séries
2. **MultiPlotLayout**: Widget container para gerenciar até 4 plots
3. **CalculationEngine**: Motor unificado para todos os cálculos
4. **ContextMenuBuilder**: Factory para construir menus dinâmicos
5. **AnnotationManager**: Sistema de anotações persistentes
6. **ExportService**: Serviço unificado de exportação

### Performance
- Otimizar para arquivos grandes (PLN_PT-OP10.xlsx = 1.4MB)
- Caching de cálculos intermediários
- Processamento assíncrono para operações pesadas
- Lazy loading de dados quando possível

---

## Checklist de Revisão Final

Antes de solicitar revisão:
- [ ] Todos os itens de UI implementados
- [ ] Todos os cálculos funcionando
- [ ] Teste de validação executado com sucesso
- [ ] Arquivo Excel de resultados gerado
- [ ] Validação visual em monitor ultrawide
- [ ] Testes unitários para cálculos críticos
- [ ] Testes de integração para workflows completos
- [ ] Documentação atualizada
- [ ] Performance validada (< 5s para operações comuns)
- [ ] Sem regressões em funcionalidades existentes
