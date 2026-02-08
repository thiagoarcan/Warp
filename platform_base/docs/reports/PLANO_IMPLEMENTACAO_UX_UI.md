# 📝 PLANO DE IMPLEMENTAÇÃO - Melhorias UX/UI Platform Base v2.0

**Baseado em:** RELATORIO_AUDITORIA_UX_UI.md  
**Data:** 26 de Janeiro de 2026  
**Versão Alvo:** 2.1.0

---

## 📑 Índice

1. [Visão Geral](#visão-geral)
2. [Backlog Priorizado](#backlog-priorizado)
3. [Sequência de PRs](#sequência-de-prs)
4. [Critérios de Aceite](#critérios-de-aceite)
5. [Estratégia de Testes](#estratégia-de-testes)
6. [Riscos e Mitigações](#riscos-e-mitigações)

---

## Visão Geral

### Objetivo
Implementar melhorias UX/UI de forma incremental, priorizando funcionalidades críticas (P0), seguidas de melhorias de alto impacto (P1) e polimento (P2).

### Princípios
- ✅ **Incremental**: PRs pequenos e revisáveis
- ✅ **Sem breaking changes**: Manter compatibilidade com uso atual
- ✅ **Testável**: Cada PR com critérios de aceite claros
- ✅ **Documentado**: Atualizar docs conforme necessário

### Cronograma Global
- **Sprint 1-2:** Quick Wins (2 semanas)
- **Sprint 3-5:** Melhorias Estruturais (3 semanas)
- **Sprint 6:** Melhorias Avançadas (1 semana)
- **Total:** 6 semanas / 30 dias úteis

---

## Backlog Priorizado

### 🔴 P0 - Crítico (Sprint 2-5)

#### ITEM-001: Implementar OperationsPanel Completo
**Prioridade:** P0  
**Esforço:** 3-5 dias  
**Arquivo:** `platform_base/src/platform_base/ui/panels/operations_panel.py`

**Descrição:**
Substituir stub atual por painel funcional com configuração de operações matemáticas.

**Funcionalidades:**
- Tab "Interpolação" com métodos disponíveis e parâmetros
- Tab "Cálculo" com derivadas/integrais
- Tab "Filtros" com suavização e filtros
- Tab "Export" com opções de exportação
- Histórico de operações executadas
- Botões de ação com preview

**Critérios de Aceite:**
- [ ] Painel com 4 tabs funcionais
- [ ] Cada tab permite configurar parâmetros
- [ ] Histórico mostra últimas 10 operações
- [ ] Botões habilitam/desabilitam conforme contexto
- [ ] Preview mostra resultado antes de aplicar
- [ ] Integrado com SessionState

**Testes:**
- [ ] Carregar dataset → OperationsPanel habilita
- [ ] Selecionar série → Mostrar opções relevantes
- [ ] Configurar interpolação → Preview atualiza
- [ ] Executar operação → Histórico registra
- [ ] Fechar/reabrir → Estado persiste

---

#### ITEM-002: Criar Diálogos de Operações
**Prioridade:** P0  
**Esforço:** 5-7 dias  
**Arquivo:** `platform_base/src/platform_base/ui/operation_dialogs.py`

**Descrição:**
Implementar diálogos especializados para cada tipo de operação matemática.

**Diálogos a Criar:**
1. **InterpolationDialog**
   - Métodos: linear, cubic, smoothing spline, MLS, GPR, Lomb-Scargle
   - Parâmetros: densidade de pontos, handling de gaps
   - Preview: gráfico antes/depois

2. **DerivativeDialog**
   - Ordem: 1ª, 2ª, 3ª
   - Método: finite difference, spline
   - Suavização opcional antes de derivar
   - Preview: original + derivada

3. **IntegralDialog**
   - Método: trapezoid, Simpson, cumulative
   - Limites de integração
   - Preview: área sombreada

4. **FilterDialog**
   - Tipo: Butterworth, outliers, rolling
   - Parâmetros específicos por tipo
   - Preview: antes/depois

5. **SmoothingDialog**
   - Método: Gaussian, Moving Average, Savitzky-Golay
   - Window size, ordem polinomial
   - Preview: original + suavizado

**Critérios de Aceite:**
- [ ] Todos 5 diálogos implementados
- [ ] Layout consistente: Config | Preview | Actions
- [ ] Preview atualiza em tempo real (throttled)
- [ ] Validação de parâmetros antes de OK
- [ ] Botões: OK, Cancelar, Aplicar, Reset
- [ ] Help button com tooltip expandido

**Testes:**
- [ ] Abrir cada diálogo → Layout correto
- [ ] Alterar parâmetros → Preview atualiza
- [ ] Valores inválidos → Botão OK desabilitado
- [ ] Clicar OK → Operação executada
- [ ] Clicar Cancelar → Sem alterações

---

#### ITEM-003: Implementar Funcionalidade de Export
**Prioridade:** P0  
**Esforço:** 2-3 dias  
**Arquivos:** `platform_base/src/platform_base/ui/export.py`, `ui/main_window.py`

**Descrição:**
Criar diálogo e lógica para exportar dados processados.

**Funcionalidades:**
- Seleção de séries (checkbox tree)
- Formatos: CSV, Excel (xlsx), Parquet, HDF5, JSON
- Opções: incluir metadata, timestamps, interpolation flags
- Range temporal customizável (slider com datas)
- Preview: primeiras 10 linhas
- Progress bar para exports grandes

**Critérios de Aceite:**
- [ ] ExportDialog com seleção de séries
- [ ] Dropdown de formatos funcionando
- [ ] Opções checkboxes funcionam
- [ ] Preview mostra dados corretos
- [ ] Progress bar atualiza durante export
- [ ] Arquivo gerado é válido e legível
- [ ] Botão "Exportar" no main_window funciona

**Testes:**
- [ ] Exportar para CSV → Arquivo válido
- [ ] Exportar para Excel → Múltiplas sheets
- [ ] Exportar com metadata → Campos presentes
- [ ] Exportar range → Apenas período selecionado
- [ ] Exportar grande dataset → Progress funciona
- [ ] Cancelar export → Arquivo não criado

---

#### ITEM-004: Refatorar VizPanel para Interatividade
**Prioridade:** P0  
**Esforço:** 4-6 dias  
**Arquivo:** `platform_base/src/platform_base/ui/panels/viz_panel.py`

**Descrição:**
Substituir MatplotlibWidget estático por sistema interativo com pyqtgraph.

**Funcionalidades:**
- Plots interativos (zoom mouse wheel, pan drag)
- Brush selection para análise de sub-região
- Múltiplas views coordenadas (grid layout)
- Sincronização temporal entre plots
- Context menu integrado (PlotContextMenu)
- Toolbar por plot (zoom, reset, export, anotate)
- Drag-and-drop de séries da DataPanel

**Critérios de Aceite:**
- [ ] Zoom com mouse wheel funciona
- [ ] Pan com mouse drag funciona
- [ ] Brush selection cria sub-série
- [ ] Múltiplos plots sincronizam cursor
- [ ] Context menu (click direito) funciona
- [ ] Arrastar série da DataPanel cria plot
- [ ] Toolbar em cada plot funciona
- [ ] Performance: 1M+ pontos sem lag

**Testes:**
- [ ] Zoom in/out → View atualiza
- [ ] Pan → View move
- [ ] Brush selection → Extrai dados corretos
- [ ] 2 plots abertos → Cursor sincronizado
- [ ] Context menu → Todas ações funcionam
- [ ] Drag série → Plot criado
- [ ] 10 plots simultâneos → Sem travamento

---

#### ITEM-005: Adicionar Validação de Entrada
**Prioridade:** P0  
**Esforço:** 1-2 dias  
**Arquivo:** `platform_base/src/platform_base/ui/panels/data_panel.py`

**Descrição:**
Validar arquivos antes de tentar carregar.

**Validações:**
1. **Pré-FileDialog:** Filtros por extensão
2. **Pós-Seleção:**
   - Verificar se arquivo existe
   - Verificar permissões de leitura
   - Verificar tamanho (avisar se > 100MB)
   - Verificar extensão real (não apenas nome)
3. **Início do Worker:**
   - Detectar encoding
   - Verificar estrutura básica (CSV tem colunas, Excel tem sheets)
   - Abortar antes de parsing completo se inválido

**Critérios de Aceite:**
- [ ] FileDialog mostra apenas extensões suportadas
- [ ] Arquivo inexistente → Erro antes de worker
- [ ] Arquivo sem permissão → Erro com sugestão
- [ ] Arquivo > 100MB → Aviso com confirmação
- [ ] CSV sem colunas → Erro com exemplo de formato
- [ ] Encoding inválido → Tenta detect automático

**Testes:**
- [ ] Selecionar .txt → Não aparece no dialog
- [ ] Selecionar arquivo deletado → Erro claro
- [ ] Selecionar Excel corrompido → Erro no worker início
- [ ] Arquivo 200MB → Confirmação aparece
- [ ] CSV UTF-16 → Detecta e converte

---

### 🟡 P1 - Alto (Sprint 1, 4-5)

#### ITEM-006: Adicionar Atalhos de Teclado Essenciais
**Prioridade:** P1 (Quick Win)  
**Esforço:** 1 dia  
**Arquivo:** `platform_base/src/platform_base/ui/main_window.py`

**Descrição:**
Expandir atalhos de teclado para operações comuns.

**Atalhos a Adicionar:**
- `Ctrl+Z` / `Ctrl+Y`: Undo/Redo (integrar com ITEM-011)
- `Ctrl+F`: Find/Filter series
- `Ctrl+E`: Export
- `Ctrl+N`: New visualization
- `Ctrl+W`: Close current view
- `Ctrl+Tab` / `Ctrl+Shift+Tab`: Switch views
- `F5`: Refresh data
- `Delete`: Remove selected series
- `Ctrl+I`: Interpolate
- `Ctrl+D`: Derivative
- `F11`: Fullscreen
- `Esc`: Cancel operation

**Critérios de Aceite:**
- [ ] Todos atalhos funcionam
- [ ] Tooltips mostram atalhos (ex: "Abrir (Ctrl+O)")
- [ ] Help → Keyboard Shortcuts mostra lista
- [ ] Atalhos não conflitam com sistema
- [ ] Funcionam com foco em qualquer widget

**Testes:**
- [ ] Pressionar cada atalho → Ação executa
- [ ] Tooltip hover → Mostra atalho
- [ ] Help menu → Lista completa exibida
- [ ] Foco em campo texto → Ctrl+O ainda funciona

---

#### ITEM-007: Tooltips Consistentes
**Prioridade:** P1 (Quick Win)  
**Esforço:** 1 dia  
**Arquivos:** `main_window.py`, `data_panel.py`, `viz_panel.py`, `operations_panel.py`

**Descrição:**
Adicionar tooltips em todos widgets interativos.

**Padrão de Tooltip:**
```
[Ícone] Ação (Atalho)
Descrição breve do que faz.
```

**Exemplo:**
```python
button.setToolTip("📁 Abrir Dataset (Ctrl+O)
Abre arquivo CSV, Excel, Parquet ou HDF5")
```

**Critérios de Aceite:**
- [ ] Todos botões têm tooltip
- [ ] Todos campos de formulário têm tooltip
- [ ] Todos itens de menu têm tooltip (statusTip)
- [ ] Tooltips consistentes (formato, linguagem)
- [ ] Tooltips aparecem após 500ms hover

**Testes:**
- [ ] Hover cada botão → Tooltip aparece
- [ ] Hover campo → Explica formato esperado
- [ ] Hover item menu → Status bar mostra descrição

---

#### ITEM-008: Persistir Layout com QSettings
**Prioridade:** P1 (Quick Win)  
**Esforço:** 0.5 dia  
**Arquivo:** `platform_base/src/platform_base/ui/main_window.py`

**Descrição:**
Salvar e restaurar estado de janela e painéis.

**Estados a Persistir:**
- Geometria da janela (tamanho e posição)
- Estado do QSplitter (proporções dos painéis)
- Tabs abertas e selecionadas
- Última pasta de arquivos abertos

**Critérios de Aceite:**
- [ ] closeEvent salva estado
- [ ] showEvent restaura estado
- [ ] Redimensionar painéis → Salvo ao fechar
- [ ] Reabrir aplicação → Layout igual
- [ ] Primeira execução → Layout default

**Testes:**
- [ ] Redimensionar janela → Fechar → Reabrir → Tamanho mantido
- [ ] Mover splitter → Fechar → Reabrir → Proporção mantida
- [ ] Abrir 3 tabs → Fechar → Reabrir → 3 tabs restauradas

---

#### ITEM-009: Melhorar Mensagens de Erro
**Prioridade:** P1 (Quick Win)  
**Esforço:** 1-2 dias  
**Arquivo:** `platform_base/src/platform_base/ui/panels/data_panel.py`, `utils/errors.py`

**Descrição:**
Criar sistema de mensagens de erro contextuais com sugestões.

**Estrutura de Erro:**
```python
{
    "title": "Título Amigável",
    "message": "O que aconteceu",
    "suggestion": "Como resolver",
    "actions": ["Ação 1", "Ação 2", "Cancelar"]
}
```

**Erros a Tratar:**
- FileNotFoundError → "Arquivo não encontrado"
- PermissionError → "Sem permissão de leitura"
- EmptyDataError → "Arquivo vazio"
- InvalidFormatError → "Formato inválido"
- MemoryError → "Arquivo muito grande"

**Critérios de Aceite:**
- [ ] Cada tipo de erro tem mensagem específica
- [ ] Mensagem sugere ação corretiva
- [ ] Botões de ação funcionais (ex: "Selecionar Outro")
- [ ] Opção "Ver Exemplo" abre documentação
- [ ] Log técnico disponível via botão "Detalhes"

**Testes:**
- [ ] Arquivo inexistente → Mensagem contextual
- [ ] Arquivo sem permissão → Sugere executar como admin
- [ ] CSV vazio → Sugere exemplo
- [ ] Clicar "Ver Exemplo" → Abre doc

---

#### ITEM-010: Context Menu em VizPanel
**Prioridade:** P1 (Quick Win)  
**Esforço:** 1 dia  
**Arquivo:** `platform_base/src/platform_base/ui/panels/viz_panel.py`

**Descrição:**
Integrar PlotContextMenu aos plots do VizPanel.

**Ações do Context Menu:**
- Zoom In/Out/Reset
- Select Region
- Extract Selection
- Statistics on Selection
- Compare Series
- Hide Interpolated Points
- Apply Visual Smoothing
- Export Plot Image
- Export Selection Data
- Add Annotation

**Critérios de Aceite:**
- [ ] Context menu aparece ao clicar direito no plot
- [ ] Todas ações implementadas (não placeholders)
- [ ] Ações indisponíveis ficam desabilitadas
- [ ] Estatísticas mostra QDialog com métricas
- [ ] Export plot salva PNG/SVG

**Testes:**
- [ ] Click direito → Menu aparece
- [ ] Cada ação → Executa corretamente
- [ ] Sem série selecionada → "Statistics" desabilitado
- [ ] "Export Plot" → Arquivo gerado

---

#### ITEM-011: Implementar Sistema Undo/Redo
**Prioridade:** P1  
**Esforço:** 3-4 dias  
**Arquivos:** `platform_base/src/platform_base/ui/state.py`, `main_window.py`

**Descrição:**
Adicionar QUndoStack para rastrear e reverter operações.

**Comandos a Implementar:**
- InterpolateCommand
- DerivativeCommand
- IntegralCommand
- FilterCommand
- SmoothCommand
- RemoveSeriesCommand

**Funcionalidades:**
- Undo (Ctrl+Z)
- Redo (Ctrl+Y)
- Panel "Histórico" mostrando stack
- Jump para estado específico
- Limitar stack a 50 comandos

**Critérios de Aceite:**
- [ ] QUndoStack integrado ao SessionState
- [ ] Cada operação cria QUndoCommand
- [ ] Ctrl+Z desfaz última operação
- [ ] Ctrl+Y refaz operação desfeita
- [ ] Panel "Histórico" mostra lista de comandos
- [ ] Click em comando → Salta para aquele estado
- [ ] Menu Edit → Undo/Redo funcionam

**Testes:**
- [ ] Interpolar série → Ctrl+Z → Série original restaurada
- [ ] Múltiplas operações → Undo até estado inicial
- [ ] Undo → Redo → Estado correto
- [ ] Histórico → Click comando antigo → Estado restaurado
- [ ] 51ª operação → Primeira removida do stack

---

#### ITEM-012: Melhorar Feedback de Estado
**Prioridade:** P1  
**Esforço:** 2-3 dias  
**Arquivos:** `platform_base/src/platform_base/ui/main_window.py`, `state.py`

**Descrição:**
Expandir status bar para mostrar mais informações de estado.

**Componentes Adicionais:**
- Label "Operação Atual" (ex: "Interpolando série X...")
- Label "Tempo Decorrido" (HH:MM:SS)
- Botão "Cancelar" (aparece durante operações longas)
- Queue indicator (ex: "2 operações na fila")
- Toast notifications (canto inferior direito)

**Critérios de Aceite:**
- [ ] Operação em execução → Status mostra nome
- [ ] Tempo decorrido atualiza a cada segundo
- [ ] Botão "Cancelar" aparece e funciona
- [ ] Queue mostra número de operações pendentes
- [ ] Toast notifications para eventos (sucesso, erro)
- [ ] Toasts desaparecem após 5s

**Testes:**
- [ ] Iniciar operação longa → Status atualiza
- [ ] Tempo decorre → Label atualiza
- [ ] Click "Cancelar" → Operação aborta
- [ ] 3 operações enfileiradas → "2 na fila" mostrado
- [ ] Operação completa → Toast "Concluído" aparece

---

#### ITEM-013: Completar Context Menu de DataPanel
**Prioridade:** P1  
**Esforço:** 2 dias  
**Arquivo:** `platform_base/src/platform_base/ui/context_menu.py`

**Descrição:**
Implementar ações pendentes do PlotContextMenu.

**Ações a Completar:**
- `_extract_selection()` → Criar novo dataset
- `_toggle_hide_interpolated()` → Flag no rendering
- `_apply_visual_smoothing()` → Abrir SmoothingDialog
- `_compare_series()` → Abrir dialog de comparação

**Critérios de Aceite:**
- [ ] Extract selection cria novo dataset
- [ ] Hide interpolated oculta pontos marcados
- [ ] Apply smoothing abre dialog
- [ ] Compare series mostra gráfico lado-a-lado

**Testes:**
- [ ] Selecionar região → Extract → Novo dataset criado
- [ ] Hide interpolated → Pontos desaparecem
- [ ] Apply smoothing → Dialog abre
- [ ] Compare 2 séries → Gráfico dual exibido

---

### 🟢 P2 - Médio (Sprint 6)

#### ITEM-014: Sistema de Temas (Dark/Light)
**Prioridade:** P2  
**Esforço:** 2-3 dias  
**Arquivos:** `themes/light.qss`, `themes/dark.qss`, `main_window.py`

**Descrição:**
Permitir alternar entre tema claro e escuro.

**Critérios de Aceite:**
- [ ] Tema light.qss funcional
- [ ] Tema dark.qss funcional
- [ ] Settings → Tema → Dropdown funcionando
- [ ] Alternância aplica imediatamente
- [ ] Preferência persiste (QSettings)

---

#### ITEM-015: Sistema de Help
**Prioridade:** P2  
**Esforço:** 3-4 dias  
**Arquivos:** Novo módulo `help/`

**Descrição:**
Help contextual e user guide.

**Critérios de Aceite:**
- [ ] F1 abre help do widget com foco
- [ ] Menu Help → User Guide abre HTML
- [ ] Shift+F1 + click → Tooltip expandido
- [ ] First-time wizard (opcional)

---

#### ITEM-016: Presets e Templates
**Prioridade:** P2  
**Esforço:** 2-3 dias  
**Arquivos:** Novo módulo `presets/`

**Descrição:**
Salvar e carregar configurações de operações.

**Critérios de Aceite:**
- [ ] Diálogos têm dropdown "Presets"
- [ ] Botão "Salvar como Preset" funciona
- [ ] Presets salvos em JSON
- [ ] Presets carregam parâmetros corretamente

---

## Sequência de PRs

### 🚀 Fase 1: Quick Wins (Sprint 1)

**PR-001: Atalhos de Teclado + Tooltips + Layout Persistente**
- ITEM-006, ITEM-007, ITEM-008
- Esforço: 2.5 dias
- Arquivos: `main_window.py`, painéis
- Impacto: +10% UX

**PR-002: Validação de Entrada + Mensagens de Erro + Context Menu VizPanel**
- ITEM-005, ITEM-009, ITEM-010
- Esforço: 3-4 dias
- Arquivos: `data_panel.py`, `viz_panel.py`, `errors.py`
- Impacto: +10% UX

**Total Fase 1:** 5-6 dias | **Impacto Acumulado:** +20% UX

---

### 🔨 Fase 2: Estruturais Críticos (Sprint 2-3)

**PR-003: OperationsPanel Funcional**
- ITEM-001
- Esforço: 3-5 dias
- Arquivos: `operations_panel.py`
- Impacto: +15% UX

**PR-004: Diálogos de Operações (Parte 1: Interpolation + Derivative)**
- ITEM-002 (parcial)
- Esforço: 3 dias
- Arquivos: `operation_dialogs.py`
- Impacto: +10% UX

**PR-005: Diálogos de Operações (Parte 2: Integral + Filter + Smoothing)**
- ITEM-002 (restante)
- Esforço: 3 dias
- Arquivos: `operation_dialogs.py`
- Impacto: +10% UX

**Total Fase 2:** 9-11 dias | **Impacto Acumulado:** +55% UX

---

### 🎨 Fase 3: Estruturais Complementares (Sprint 4-5)

**PR-006: Sistema de Export**
- ITEM-003
- Esforço: 2-3 dias
- Arquivos: `export.py`, `main_window.py`
- Impacto: +10% UX

**PR-007: Sistema Undo/Redo**
- ITEM-011
- Esforço: 3-4 dias
- Arquivos: `state.py`, `main_window.py`
- Impacto: +10% UX

**PR-008: VizPanel Interativo (Parte 1: PyQtGraph Integration)**
- ITEM-004 (parcial)
- Esforço: 2-3 dias
- Arquivos: `viz_panel.py`
- Impacto: +5% UX

**PR-009: VizPanel Interativo (Parte 2: Multiple Views + Sync)**
- ITEM-004 (restante)
- Esforço: 2-3 dias
- Arquivos: `viz_panel.py`
- Impacto: +5% UX

**PR-010: Feedback de Estado Melhorado**
- ITEM-012
- Esforço: 2-3 dias
- Arquivos: `main_window.py`, `state.py`
- Impacto: +5% UX

**PR-011: Context Menu Completo**
- ITEM-013
- Esforço: 2 dias
- Arquivos: `context_menu.py`
- Impacto: +5% UX

**Total Fase 3:** 13-18 dias | **Impacto Acumulado:** +95% UX

---

### 🌟 Fase 4: Polimento (Sprint 6)

**PR-012: Temas + Help + Presets (Opcional)**
- ITEM-014, ITEM-015, ITEM-016
- Esforço: 7-10 dias
- Arquivos: Novos módulos
- Impacto: +5% UX

**Total Fase 4:** 7-10 dias | **Impacto Acumulado:** +100% UX

---

## Critérios de Aceite

### Checklist Geral por PR

Cada PR deve atender:
- [ ] ✅ Código compila sem erros
- [ ] ✅ Todos testes passam (unitários + integração)
- [ ] ✅ Linter sem warnings (flake8, mypy)
- [ ] ✅ Documentação atualizada (docstrings, README)
- [ ] ✅ Sem regressões em funcionalidades existentes
- [ ] ✅ Performance mantida ou melhorada
- [ ] ✅ Screenshots de UI changes anexados
- [ ] ✅ Critérios de aceite do item atendidos

### Checklist de Validação Manual

Após cada PR merge:
- [ ] Smoke test: Abrir app, carregar dataset, criar plot
- [ ] Funcionalidade nova: Testar todos caminhos do usuário
- [ ] Edge cases: Testar inputs inválidos, dados vazios, operações concorrentes
- [ ] Performance: Carregar dataset grande (10K+ linhas)
- [ ] Acessibilidade: Navegar com Tab, usar atalhos

---

## Estratégia de Testes

### Testes Unitários (pytest)

Criar testes para:
- Lógica de negócio em diálogos (validação, cálculos)
- SessionState operations (add dataset, execute operation)
- QUndoCommand implementation (undo, redo)
- Export functions (CSV, Excel, Parquet)

**Localização:** `platform_base/tests/ui/`

**Exemplo:**
```python
def test_interpolation_dialog_validation():
    dialog = InterpolationDialog()
    dialog.set_method("invalid_method")
    assert not dialog.is_valid()
    assert "OK" button is disabled
```

### Testes de Integração

Testar fluxos completos:
- Carregar dataset → Interpolar → Visualizar → Exportar
- Múltiplas operações → Undo → Redo
- Configurar operação → Preview → Aplicar

**Localização:** `platform_base/tests/integration/test_ui_flows.py`

### Testes Manuais

Roteiro de validação em checklist:
- [ ] Fresh install → First run wizard
- [ ] Carregar CSV → Dados aparecem
- [ ] Selecionar série → Context menu funciona
- [ ] Interpolar → Preview mostra resultado
- [ ] Exportar → Arquivo gerado válido
- [ ] Fechar → Reabrir → Layout mantido

---

## Riscos e Mitigações

### Risco 1: PyQtGraph Performance
**Probabilidade:** Média  
**Impacto:** Alto  
**Mitigação:**
- Implementar downsampling inteligente (LTTB já existe)
- Lazy loading de dados para plots
- Throttle de repaints durante zoom/pan
- Fallback para Matplotlib se performance ruim

### Risco 2: Complexidade de Undo/Redo
**Probabilidade:** Alta  
**Impacto:** Médio  
**Mitigação:**
- Começar com comandos simples (InterpolateCommand)
- Incrementar gradualmente
- Limitar tamanho do stack (50 comandos)
- Permitir desabilitar undo em Settings

### Risco 3: Breaking Changes Acidentais
**Probabilidade:** Média  
**Impacto:** Alto  
**Mitigação:**
- Testes de regressão robustos
- Code review obrigatório
- Smoke tests automatizados
- Branch protection rules

### Risco 4: Timeline Otimista
**Probabilidade:** Alta  
**Impacto:** Médio  
**Mitigação:**
- Buffer de 20% em cada estimativa
- Priorização rígida (P0 > P1 > P2)
- Daily standups para detectar bloqueios cedo
- MVP incremental (lançar fases 1-3 antes de fase 4)

---

## Checklist de Conclusão do Projeto

Projeto considerado completo quando:
- [ ] ✅ Todos itens P0 implementados e testados
- [ ] ✅ Todos itens P1 implementados e testados
- [ ] ✅ Score de heurísticas ≥ 70/100
- [ ] ✅ Cobertura funcional ≥ 90%
- [ ] ✅ Todos PRs merged sem conflitos
- [ ] ✅ Documentação atualizada (README, User Guide)
- [ ] ✅ Screenshots/GIFs de novas funcionalidades
- [ ] ✅ Release notes publicadas
- [ ] ✅ Tag v2.1.0 criada

---

**Elaborado por:** Copilot Agent  
**Aprovado por:** _Pendente_  
**Última Atualização:** 26/01/2026  
**Próxima Revisão:** Após Sprint 1
