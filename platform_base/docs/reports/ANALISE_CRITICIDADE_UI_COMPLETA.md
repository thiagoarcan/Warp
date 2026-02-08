# 🔴 Análise de Criticidade - Arquivos .ui com contentLayout Vazio

**Data:** 05/02/2026  
**Objetivo:** Identificar os TOP 10 arquivos .ui mais críticos que precisam de correção imediata

---

## Critérios de Avaliação

| Critério | Peso | Descrição |
|----------|------|-----------|
| RuntimeError | 🔴 CRÍTICO | Classe lança `raise RuntimeError` se `.ui` falhar |
| UiLoaderMixin | ⚠️ ALTO | Classe usa mixin obrigatório de carregamento |
| Visibilidade | 📊 MÉDIO | Componente visível/usado diretamente pelo usuário |
| Core Feature | ⭐ ALTO | Afeta visualização, dados ou streaming |

---

## 🏆 TOP 10 MAIS CRÍTICOS (Ordem de Prioridade)

### 1. 🔴 `baseOperationDialog.ui` - **CRÍTICO MÁXIMO**

| Campo | Valor |
|-------|-------|
| **Classe Python** | `BaseOperationDialog` |
| **Arquivo .py** | `src/platform_base/ui/operation_dialogs.py` (linha 294) |
| **Usa UiLoaderMixin** | ✅ SIM |
| **RuntimeError** | ✅ SIM - linha 320 |
| **Widgets findChild** | `splitter`, `resetBtn`, `previewBtn`, `cancelBtn`, `applyBtn`, `previewContainer`, `previewStatus` |

**Por que é crítico:**
- **CLASSE BASE** para TODOS os diálogos de operações matemáticas
- 6+ classes herdam desta: `InterpolationDialog`, `SynchronizationDialog`, `DerivativeDialog`, `IntegralDialog`, `CalculusDialog`, `FilterDialog`, `SmoothingDialog`
- Falha aqui **quebra todas** as operações matemáticas do sistema

---

### 2. 🔴 `previewWidget.ui` - **CRÍTICO MÁXIMO**

| Campo | Valor |
|-------|-------|
| **Classe Python** | `PreviewWidget` |
| **Arquivo .py** | `src/platform_base/ui/operation_dialogs.py` (linha 228) |
| **Usa UiLoaderMixin** | ✅ SIM |
| **RuntimeError** | ✅ SIM - linha 248 |
| **Widgets findChild** | `contentLayout` (QVBoxLayout) |

**Por que é crítico:**
- Usado por `BaseOperationDialog` para preview em tempo real
- Exibe matplotlib canvas para visualização de operações
- Componente de feedback visual essencial para o usuário

---

### 3. 🔴 `operationPreviewDialog.ui` - **CRÍTICO MÁXIMO**

| Campo | Valor |
|-------|-------|
| **Classe Python** | `OperationPreviewDialog` |
| **Arquivo .py** | `src/platform_base/ui/preview_dialog.py` (linha 120) |
| **Usa UiLoaderMixin** | ✅ SIM |
| **RuntimeError** | ✅ SIM - linha 152 |
| **Widgets findChild** | `contentWidget`, `buttonBox` |

**Por que é crítico:**
- Diálogo principal de preview para operações matemáticas
- Exibe comparação antes/depois
- Mostra estatísticas do resultado
- Emite signal `apply_requested` para aplicar operações

---

### 4. 🔴 `selectionManagerWidget.ui` - **CRÍTICO ALTO**

| Campo | Valor |
|-------|-------|
| **Classe Python** | `SelectionManagerWidget` |
| **Arquivo .py** | `src/platform_base/ui/selection_widgets.py` (linha 545) |
| **Usa UiLoaderMixin** | ✅ SIM |
| **RuntimeError** | ✅ SIM - linha 570 |
| **Widgets findChild** | `datasetCombo`, `selectionTabs` |

**Por que é crítico:**
- **Sistema central de seleção de dados**
- Contém: `RangePickerWidget`, `BrushSelectionWidget`, `QueryBuilderWidget`, `SelectionHistoryWidget`
- Emite signals `selection_made`, `selection_changed`
- Integração direta com `SessionState`

---

### 5. 🔴 `shortcutsDialog.ui` - **CRÍTICO ALTO**

| Campo | Valor |
|-------|-------|
| **Classe Python** | `ShortcutsDialog` |
| **Arquivo .py** | `src/platform_base/ui/shortcuts.py` (linha 573) |
| **Usa UiLoaderMixin** | ✅ SIM |
| **RuntimeError** | ✅ SIM - linha 595 |
| **Widgets findChild** | `searchEdit`, `shortcutsTable`, `resetBtn`, `resetAllBtn`, `buttonBox` |

**Por que é crítico:**
- Diálogo de personalização de atalhos de teclado
- Acessível via menu principal
- Usa `ShortcutManager` para persistência

---

### 6. 🔴 `compareSeriesDialog.ui` - **CRÍTICO ALTO**

| Campo | Valor |
|-------|-------|
| **Classe Python** | `CompareSeriesDialog` |
| **Arquivo .py** | `src/platform_base/ui/context_menu.py` (linha 37) |
| **Usa UiLoaderMixin** | ✅ SIM |
| **RuntimeError** | ✅ SIM - linha 56 |
| **Widgets findChild** | `series1Combo`, `series2Combo`, `correlationCheck`, `rmseCheck`, `maeCheck`, `dtwCheck`, `resultText`, `compareBtn`, `closeBtn` |

**Por que é crítico:**
- Funcionalidade core de **comparação de séries**
- Calcula: Correlação Pearson, RMSE, MAE, DTW Distance
- Acessível via menu de contexto do plot

---

### 7. 🔴 `annotationDialog.ui` - **CRÍTICO MÉDIO-ALTO**

| Campo | Valor |
|-------|-------|
| **Classe Python** | `AnnotationDialog` |
| **Arquivo .py** | `src/platform_base/ui/context_menu.py` (linha 146) |
| **Usa UiLoaderMixin** | ✅ SIM |
| **RuntimeError** | ✅ SIM - linha 165 |
| **Widgets findChild** | `xSpin`, `ySpin`, `textEdit`, `arrowCheck`, `colorCombo`, `addBtn`, `cancelBtn` |

**Por que é crítico:**
- Permite adicionar **anotações em gráficos**
- Acessível via menu de contexto
- Funcionalidade de documentação visual

---

### 8. ⚠️ `modernMainWindow.ui` - **ALTO** (mas com fallback)

| Campo | Valor |
|-------|-------|
| **Classe Python** | `MainWindow` |
| **Arquivo .py** | `src/platform_base/desktop/main_window.py` (linha 50) |
| **Usa UiLoaderMixin** | ✅ SIM |
| **RuntimeError** | ❌ NÃO - tem fallback programático |
| **Widgets findChild** | `dataDock`, `dataPanelPlaceholder`, `vizPanelPlaceholder`, `configDock`, `configPanelPlaceholder`, `operationsDock`, `operationsPanelPlaceholder`, `streamingDock`, `streamingPanelPlaceholder`, `resultsDock`, `resultsPanelPlaceholder` |

**Por que é crítico:**
- **Janela principal** da aplicação
- Contém todos os docks e painéis
- ⚠️ TEM FALLBACK: Se `.ui` falhar, cria UI programaticamente (linha 88-93)
- Menos urgente que outros, mas ainda importante

---

### 9. ⚠️ `plot2DWidget.ui` - **MÉDIO** (classe NÃO usa UiLoaderMixin)

| Campo | Valor |
|-------|-------|
| **Classe Python** | `Plot2DWidget` (2 versões) |
| **Arquivos .py** | `desktop/widgets/viz_panel.py` (linha 56), `viz/figures_2d.py` (linha 68) |
| **Usa UiLoaderMixin** | ❌ NÃO |
| **RuntimeError** | ❌ NÃO |

**Por que ainda importa:**
- Arquivo `.ui` existe mas **não é usado** pelas classes
- Classes criam UI programaticamente via PyQtGraph
- ⚠️ **Inconsistência**: arquivo `.ui` não corresponde à implementação
- **Ação:** Remover `.ui` ou migrar classe para usar UiLoaderMixin

---

### 10. ⚠️ `plot3DWidget.ui` - **MÉDIO** (classe NÃO usa UiLoaderMixin)

| Campo | Valor |
|-------|-------|
| **Classe Python** | `Plot3DWidget` (2 versões) |
| **Arquivos .py** | `desktop/widgets/viz_panel.py` (linha 242), `viz/figures_3d.py` (linha 67) |
| **Usa UiLoaderMixin** | ❌ NÃO |
| **RuntimeError** | ❌ NÃO |

**Por que ainda importa:**
- Mesmo caso do `plot2DWidget.ui`
- Classes criam UI programaticamente via PyVista
- ⚠️ **Inconsistência**: arquivo `.ui` órfão
- **Ação:** Remover `.ui` ou migrar classe

---

## 📋 Diálogos Filhos de BaseOperationDialog (Herdam o problema)

Estes diálogos **herdam** de `BaseOperationDialog` e serão afetados se a base estiver quebrada:

| Diálogo | Arquivo | Linha |
|---------|---------|-------|
| `InterpolationDialog` | `operation_dialogs.py` | 483 |
| `SynchronizationDialog` | `operation_dialogs.py` | 544 |
| `DerivativeDialog` | `operation_dialogs.py` | 605 |
| `IntegralDialog` | `operation_dialogs.py` | 714 |
| `CalculusDialog` | `operation_dialogs.py` | 962 |
| `FilterDialog` | `operation_dialogs.py` | 823 |
| `SmoothingDialog` | `operation_dialogs.py` | 890 |

⚠️ **Nota:** Estes diálogos filhos **não têm arquivos `.ui` próprios** - dependem apenas do `.ui` da classe base.

---

## 🎯 Plano de Ação Recomendado

### Fase 1 - URGENTE (Impede uso da aplicação)
1. ✅ Corrigir `baseOperationDialog.ui`
2. ✅ Corrigir `previewWidget.ui`
3. ✅ Corrigir `operationPreviewDialog.ui`

### Fase 2 - ALTA PRIORIDADE (Funcionalidades core)
4. ✅ Corrigir `selectionManagerWidget.ui`
5. ✅ Corrigir `shortcutsDialog.ui`
6. ✅ Corrigir `compareSeriesDialog.ui`

### Fase 3 - MÉDIA PRIORIDADE (UX importante)
7. ✅ Corrigir `annotationDialog.ui`
8. ✅ Corrigir `modernMainWindow.ui`

### Fase 4 - LIMPEZA (Consistência)
9. 🔄 Decidir: `plot2DWidget.ui` - remover ou migrar classe
10. 🔄 Decidir: `plot3DWidget.ui` - remover ou migrar classe

---

## 📊 Resumo de Widgets Necessários por Arquivo

```
baseOperationDialog.ui:
├── splitter (QSplitter)
├── resetBtn (QPushButton)
├── previewBtn (QPushButton)
├── cancelBtn (QPushButton)
├── applyBtn (QPushButton)
├── previewContainer (QWidget)
└── previewStatus (QLabel)

previewWidget.ui:
└── contentLayout (QVBoxLayout) ← para inserir matplotlib canvas

operationPreviewDialog.ui:
├── contentWidget (QWidget)
└── buttonBox (QDialogButtonBox)

selectionManagerWidget.ui:
├── datasetCombo (QComboBox)
└── selectionTabs (QTabWidget)

shortcutsDialog.ui:
├── searchEdit (QLineEdit)
├── shortcutsTable (QTableWidget)
├── resetBtn (QPushButton)
├── resetAllBtn (QPushButton)
└── buttonBox (QDialogButtonBox)

compareSeriesDialog.ui:
├── series1Combo (QComboBox)
├── series2Combo (QComboBox)
├── correlationCheck (QCheckBox)
├── rmseCheck (QCheckBox)
├── maeCheck (QCheckBox)
├── dtwCheck (QCheckBox)
├── resultText (QTextEdit)
├── compareBtn (QPushButton)
└── closeBtn (QPushButton)

annotationDialog.ui:
├── xSpin (QDoubleSpinBox)
├── ySpin (QDoubleSpinBox)
├── textEdit (QTextEdit)
├── arrowCheck (QCheckBox)
├── colorCombo (QComboBox)
├── addBtn (QPushButton)
└── cancelBtn (QPushButton)

modernMainWindow.ui:
├── dataDock (QDockWidget)
├── dataPanelPlaceholder (QWidget)
├── vizPanelPlaceholder (QWidget)
├── configDock (QDockWidget)
├── configPanelPlaceholder (QWidget)
├── operationsDock (QDockWidget)
├── operationsPanelPlaceholder (QWidget)
├── streamingDock (QDockWidget)
├── streamingPanelPlaceholder (QWidget)
├── resultsDock (QDockWidget)
└── resultsPanelPlaceholder (QWidget)
```

---

## 📈 Estatísticas

| Métrica | Valor |
|---------|-------|
| Total de arquivos analisados | 15 |
| Com RuntimeError (críticos) | 7 |
| Com UiLoaderMixin | 9 |
| Órfãos (sem uso por classe) | 2 |
| Classes afetadas por herança | 7+ |
| **Prioridade URGENTE** | 3 |
| **Prioridade ALTA** | 3 |
| **Prioridade MÉDIA** | 2 |
| **Inconsistentes/Órfãos** | 2 |

---

## 🔍 Arquivos .ui Não Críticos (Fora do TOP 10)

Os seguintes arquivos também têm `contentLayout"/>` vazio mas **não lançam RuntimeError** ou **não são usados**:

| Arquivo | Status |
|---------|--------|
| `interpolationDialog.ui` | Classe herda de `BaseOperationDialog` - não carrega .ui próprio |
| `derivativeDialog.ui` | Classe herda de `BaseOperationDialog` - não carrega .ui próprio |
| `integralDialog.ui` | Classe herda de `BaseOperationDialog` - não carrega .ui próprio |
| `synchronizationDialog.ui` | Classe herda de `BaseOperationDialog` - não carrega .ui próprio |
| `calculusDialog.ui` | Classe herda de `BaseOperationDialog` - não carrega .ui próprio |

**Nota:** Estes arquivos `.ui` **não precisam existir** porque as classes filhas herdam da `BaseOperationDialog` e não fazem carregamento próprio de `.ui`.
