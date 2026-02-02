# TODO LIST COMPLETA PARA PRODUÇÃO - Platform Base v2.0

**Versão 2.0 - Com Critérios de Aceitação e Instruções para Copilot**  
**Data da Revisão: 01/02/2026**

---

> ⚠️ **AVISO**: Esta lista representa o que precisa ser implementado para colocar a aplicação em produção real.
> Nenhum workaround, nenhuma simplificação, nenhum jeitinho.
>
> Cada item inclui **critérios de aceitação** que DEVEM ser atendidos.
>
> **Estado Atual Estimado**: ~20% funcional  
> **TODOs/Stubs identificados no código**: 176+  
> **Componentes UI a migrar para .ui**: 60 classes → ~45 arquivos .ui  
> **Data da Auditoria Original**: 30/01/2026

---

## 📊 SUMÁRIO EXECUTIVO

| Módulo | Status | Funcional | A Implementar |
|--------|--------|-----------|---------------|
| **Visualização 2D** | 🟡 Parcial | 40% | Cores, Legenda, Multi-eixo, Seleção |
| **Visualização 3D** | 🔴 Crítico | 10% | Toda implementação de renderização |
| **Cálculos** | 🟡 Parcial | 60% | Conexão UI↔Backend |
| **Streaming** | 🔴 Crítico | 5% | Implementação completa |
| **Exportação** | 🔴 Crítico | 20% | Todas as funcionalidades |
| **Menu de Contexto** | 🔴 Crítico | 5% | Todas as ações |
| **Undo/Redo** | 🔴 Crítico | 0% | Sistema completo |
| **Seleção de Dados** | 🟡 Parcial | 30% | Sincronização, Multi-seleção |
| **Configurações** | 🟡 Parcial | 50% | Persistência, Temas |
| **Results Panel** | 🔴 Crítico | 10% | Exibição de resultados |
| **Testes** | 🔴 Crítico | 15% | Cobertura e integração |
| **Logging/Telemetria** | 🔴 Crítico | 0% | **NOVO** - Implementação completa |
| **Acessibilidade** | 🔴 Crítico | 0% | **NOVO** - Implementação completa |

---

## 🎯 PRIORIDADE DE EXECUÇÃO OBRIGATÓRIA

A execução **DEVE** seguir esta ordem estrita. **NÃO AVANÇAR** para o próximo item sem completar 100% do anterior.

| Prioridade | Item | Quantidade | Criticidade |
|------------|------|------------|-------------|
| **1º** | Implementar todos os `NotImplementedError` | 7 | 🔴 CRÍTICO |
| **2º** | Resolver todos os stubs/TODOs | 172 | 🔴 CRÍTICO |
| **3º** | Migrar UI para arquivos .ui | 45 arquivos | 🔴 ALTO |
| **4º** | Conectar UI↔Backend (signals) | Todos pendentes | 🔴 ALTO |
| **5º** | Aumentar cobertura de testes para 95% | ~490 testes | 🔴 CRÍTICO |

### Detalhamento das Prioridades

**1º - NotImplementedError (7 itens)**
- Estes são bloqueadores absolutos - a aplicação não funciona com eles
- Cada `raise NotImplementedError` deve ser substituído por implementação completa
- Não aceitar implementações parciais ou mocks

**2º - Stubs/TODOs (172 itens)**
- Todo método com `pass` deve ser implementado
- Todo comentário `# TODO` deve ser resolvido
- Todo `...` (ellipsis) deve ser substituído por código real

**3º - Migração .ui (45 arquivos)**
- Criar todos os arquivos .ui no Qt Designer
- Implementar UiLoaderMixin
- Migrar toda criação programática de UI

**4º - Conexões UI↔Backend**
- Conectar todos os signals pendentes
- Verificar que cada ação de UI tem resposta do backend
- Testar fluxo completo de dados

**5º - Cobertura de Testes 95%**
- Implementar todos os ~490 testes listados
- Nenhum teste pode ser pulado, simplificado ou ignorado
- Coverage mínimo de 95% obrigatório

---

# 🤖 INSTRUÇÕES OBRIGATÓRIAS PARA COPILOT

> **COPIE ESTA SEÇÃO PARA `.github/copilot-instructions.md`**

---

## MODO DE OPERAÇÃO: AUTÔNOMO CONTÍNUO

O Copilot DEVE operar em modo autônomo contínuo até a conclusão de 100% da aplicação.

### REGRA FUNDAMENTAL DE OPERAÇÃO

```
┌────────────────────────────────────────────────────────────────────┐
│  ❌ NÃO PARAR para perguntar se deve continuar                     │
│  ❌ NÃO PARAR para reportar progresso parcial                      │
│  ❌ NÃO PARAR para pedir confirmação                               │
│  ❌ NÃO PARAR para mostrar o que foi feito                         │
│  ❌ NÃO PARAR para aguardar instruções                             │
│                                                                    │
│  ✅ CONTINUAR automaticamente para a próxima tarefa                │
│  ✅ CONTINUAR até que TODA a aplicação esteja 100% pronta          │
│  ✅ PARAR SOMENTE quando 100% completo para produção               │
└────────────────────────────────────────────────────────────────────┘
```

### DEFINIÇÃO DE "100% PRONTO PARA PRODUÇÃO"

A aplicação só está pronta quando **TODOS** os critérios abaixo forem atendidos:

- [ ] 0 (zero) `NotImplementedError` no código
- [ ] 0 (zero) métodos com apenas `pass`
- [ ] 0 (zero) comentários `# TODO` não resolvidos
- [ ] 0 (zero) `...` (ellipsis) em implementações
- [ ] 0 (zero) mensagens "coming soon" ou "not implemented"
- [ ] 45 arquivos .ui criados e funcionando
- [ ] Todos os signals UI↔Backend conectados
- [ ] Cobertura de testes ≥ 95%
- [ ] Todos os ~490 testes passando
- [ ] 0 (zero) testes pulados (@pytest.mark.skip)
- [ ] 0 (zero) warnings ignorados no pyproject.toml
- [ ] Aplicação executa sem crashes por 8 horas contínuas

---

## 🚫 PROIBIÇÕES ABSOLUTAS - TESTES

As seguintes ações são **TERMINANTEMENTE PROIBIDAS** e constituem **VIOLAÇÃO GRAVE**:

### ❌ NUNCA SIMPLIFICAR TESTES

| Ação Proibida | Por que é proibido |
|---------------|-------------------|
| Reduzir número de assertions | Diminui cobertura de casos |
| Remover casos de teste "problemáticos" | Esconde bugs reais |
| Diminuir cobertura de edge cases | Deixa código frágil |
| Usar valores mais "fáceis" para passar | Mascara problemas |
| Reduzir escopo do teste | Perde validação |

### ❌ NUNCA RELAXAR REQUISITOS

| Ação Proibida | Por que é proibido |
|---------------|-------------------|
| Aumentar tolerâncias (atol, rtol) | Aceita resultados imprecisos |
| Mudar assertEquals para assertAlmostEquals sem justificativa | Esconde erros numéricos |
| Aceitar "close enough" | O correto é possível |
| Ignorar decimais significativos | Perde precisão |

### ❌ NUNCA ALTERAR TESTE PARA PASSAR

```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   O TESTE ESTÁ CORRETO. O CÓDIGO ESTÁ ERRADO.                    ║
║                                                                   ║
║   Quando um teste falha, o problema está SEMPRE no código de     ║
║   produção, NUNCA no teste.                                      ║
║                                                                   ║
║   O teste representa o comportamento ESPERADO.                   ║
║   O código deve ser CORRIGIDO para atender ao teste.             ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

| Ação Proibida | O que fazer em vez disso |
|---------------|--------------------------|
| Modificar valor esperado para corresponder ao obtido | Corrigir o código |
| Ajustar assertion para aceitar resultado errado | Corrigir o código |
| Mudar lógica do teste para acomodar bug | Corrigir o código |

### ❌ NUNCA PULAR OU IGNORAR

| Ação Proibida | O que fazer em vez disso |
|---------------|--------------------------|
| @pytest.mark.skip | Implementar o que falta |
| @pytest.mark.skipif | Corrigir a condição |
| Comentar testes que falham | Corrigir o código |
| Remover testes de arquivos | Corrigir o código |
| Excluir arquivos do pytest.ini | Corrigir o código |

### ❌ NUNCA SEPARAR PARA ESCONDER FALHAS

| Ação Proibida | O que fazer em vez disso |
|---------------|--------------------------|
| Rodar unitários separados de integração | Rodar todos juntos |
| Criar suítes "lite" ou "quick" | Rodar suíte completa |
| Usar markers para excluir testes | Corrigir os testes |
| Configurar CI para ignorar falhas | Corrigir as falhas |

### ❌ NUNCA IGNORAR CLASSES/MÉTODOS FALTANTES

| Ação Proibida | O que fazer em vez disso |
|---------------|--------------------------|
| Pular teste porque classe não existe | **CRIAR A CLASSE** |
| Pular teste porque método não existe | **CRIAR O MÉTODO** |
| Pular teste porque fixture não existe | **CRIAR A FIXTURE** |
| Mockar o que deveria ser implementado | **IMPLEMENTAR** |

### ❌ NUNCA REMOVER TESTES PROBLEMÁTICOS

| Ação Proibida | O que fazer em vez disso |
|---------------|--------------------------|
| Deletar testes de IO que falham | Corrigir IO |
| Remover testes de encoding | Corrigir encoding |
| Excluir testes de edge cases | Corrigir edge cases |
| Eliminar testes de concorrência | Corrigir concorrência |
| Apagar testes de performance | Otimizar performance |

### ❌ NUNCA AJUSTAR PARA APIs QUE EXISTEM

```
O TESTE DEFINE A API.
A API DEVE SER IMPLEMENTADA CONFORME O TESTE.
NÃO O CONTRÁRIO.
```

| Ação Proibida | O que fazer em vez disso |
|---------------|--------------------------|
| Mudar teste para usar API existente | Implementar API correta |
| Adaptar teste a limitações | Remover limitações |

### ❌ NUNCA SUPRIMIR WARNINGS

| Ação Proibida | O que fazer em vez disso |
|---------------|--------------------------|
| filterwarnings = ["ignore::..."] | Corrigir causa do warning |
| warnings.filterwarnings("ignore") | Corrigir causa do warning |
| pytest.mark.filterwarnings | Corrigir causa do warning |
| Suprimir warnings de cupy/dask/numpy | Corrigir uso da biblioteca |

**WARNINGS SÃO BUGS. CORRIGI-LOS.**

### ❌ NUNCA DEIXAR DESIGNS PARA DEPOIS

| Ação Proibida | O que fazer em vez disso |
|---------------|--------------------------|
| "Arquivo .ui não existe, ignorar" | **CRIAR O ARQUIVO .UI** |
| "Classe não existe, pular" | **CRIAR A CLASSE** |
| "Deixar para depois" | **FAZER AGORA** |

---

## ✅ COMPORTAMENTO OBRIGATÓRIO

### QUANDO UM TESTE FALHA:

```
1. ANALISAR a mensagem de erro
2. IDENTIFICAR o bug no código de produção
3. CORRIGIR o código de produção (NÃO O TESTE)
4. RODAR o teste novamente
5. REPETIR até passar
6. NUNCA modificar o teste
```

### QUANDO UMA CLASSE NÃO EXISTE:

```
1. CRIAR a classe imediatamente
2. IMPLEMENTAR todos os métodos necessários
3. ADICIONAR docstrings completas
4. ADICIONAR type hints
5. CRIAR testes para a nova classe
```

### QUANDO UM ARQUIVO .UI NÃO EXISTE:

```
1. CRIAR o arquivo .ui imediatamente
2. DEFINIR todos os widgets necessários
3. CONFIGURAR layouts apropriados
4. CONECTAR signals no código Python
5. TESTAR a renderização
```

### QUANDO UM WARNING APARECE:

```
1. IDENTIFICAR a causa raiz
2. CORRIGIR o código que gera o warning
3. VERIFICAR que o warning não aparece mais
4. NUNCA suprimir o warning
```

### QUANDO UMA API NÃO EXISTE:

```
1. CRIAR a API conforme especificada no teste
2. IMPLEMENTAR completamente
3. DOCUMENTAR a nova API
4. O TESTE DEFINE O CONTRATO - IMPLEMENTAR CONFORME
```

---

## 📊 MÉTRICAS DE QUALIDADE INEGOCIÁVEIS

| Métrica | Valor Mínimo | Tolerância |
|---------|--------------|------------|
| Cobertura de código | 95% | **ZERO** |
| Testes passando | 100% | **ZERO** |
| Testes pulados | 0 | **ZERO** |
| Warnings suprimidos | 0 | **ZERO** |
| NotImplementedError | 0 | **ZERO** |
| Métodos com pass | 0 | **ZERO** |
| TODOs não resolvidos | 0 | **ZERO** |
| Arquivos .ui faltantes | 0 | **ZERO** |

**NÃO HÁ EXCEÇÕES. NÃO HÁ NEGOCIAÇÃO.**

---

## 🔄 CICLO DE TRABALHO CONTÍNUO

```
INÍCIO
  │
  ▼
┌─────────────────────────────────────────┐
│  1. Pegar próximo item da lista         │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  2. Implementar completamente           │
│     - Criar classes faltantes           │
│     - Criar arquivos .ui faltantes      │
│     - Implementar todos os métodos      │
│     - Adicionar type hints              │
│     - Adicionar docstrings              │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  3. Escrever/rodar testes               │
│     - NUNCA simplificar                 │
│     - NUNCA pular                       │
│     - NUNCA modificar para passar       │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  4. Teste passou?                       │
│     NÃO → Corrigir CÓDIGO (não teste)   │
│           Voltar para 3                 │
│     SIM → Continuar                     │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  5. Mais itens na lista?                │
│     SIM → Voltar para 1                 │
│           (SEM PARAR, SEM PERGUNTAR)    │
│     NÃO → Verificar 100% completo       │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  6. Aplicação 100% pronta?              │
│     NÃO → Identificar gaps              │
│           Adicionar à lista             │
│           Voltar para 1                 │
│     SIM → FIM                           │
└─────────────────────────────────────────┘
  │
  ▼
FIM (ÚNICA condição de parada permitida)
```

---

## 🚨 VIOLAÇÕES JÁ COMETIDAS (PARA NÃO REPETIR)

A IA já cometeu as seguintes violações que **NÃO DEVEM SE REPETIR**:

| Violação | Categoria | Severidade |
|----------|-----------|------------|
| Simplificou testes | SIMPLIFICAÇÃO | 🔴 GRAVE |
| Relaxou requisitos de teste | RELAXAMENTO | 🔴 GRAVE |
| Alterou teste para passar | MANIPULAÇÃO | 🔴 GRAVE |
| Pulou testes de classes inexistentes | EVASÃO | 🔴 GRAVE |
| Rodou testes separados para esconder falhas | OCULTAÇÃO | 🔴 GRAVE |
| Simplificou smoke test | SIMPLIFICAÇÃO | 🔴 GRAVE |
| Simplificou teste e2e | SIMPLIFICAÇÃO | 🔴 GRAVE |
| Ignorou falhas por designs não criados | EVASÃO | 🔴 GRAVE |
| Removeu testes de IO problemáticos | REMOÇÃO | 🔴 GRAVE |
| Corrigiu testes para usar APIs existentes | INVERSÃO | 🔴 GRAVE |
| Ajustou pyproject para ignorar warnings | SUPRESSÃO | 🔴 GRAVE |
| Parou para aguardar instruções | INTERRUPÇÃO | 🟡 MÉDIA |
| Reportou progresso parcial e parou | INTERRUPÇÃO | 🟡 MÉDIA |

**TODAS ESTAS AÇÕES ESTÃO PROIBIDAS.**

---

## ⛔ CONSEQUÊNCIAS DE VIOLAÇÃO

1. **TODO o trabalho da sessão será DESCARTADO**
2. **O processo será REINICIADO do zero**
3. **Violações repetidas serão REPORTADAS**

---

## 📝 CHECKLIST ANTES DE DECLARAR TAREFA CONCLUÍDA

- [ ] Não há `NotImplementedError` no código
- [ ] Não há métodos com apenas `pass`
- [ ] Não há `# TODO` não resolvidos
- [ ] Não há `...` (ellipsis) em implementações
- [ ] Todos os testes relacionados passam
- [ ] Cobertura do módulo ≥ 95%
- [ ] Nenhum warning é gerado
- [ ] Nenhum teste foi modificado para passar
- [ ] Nenhum teste foi pulado
- [ ] Todas as classes necessárias existem
- [ ] Todos os arquivos .ui necessários existem
- [ ] Type hints em todas as funções
- [ ] Docstrings em todas as funções públicas

**SE QUALQUER ITEM ACIMA NÃO FOR ATENDIDO, A TAREFA NÃO ESTÁ CONCLUÍDA.**

---

## 🎯 LEMBRETE FINAL PARA COPILOT

```
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   • O TESTE ESTÁ CORRETO. SEMPRE.                                    ║
║   • O CÓDIGO DEVE SER CORRIGIDO. SEMPRE.                             ║
║   • NUNCA PARAR ATÉ 100% COMPLETO.                                   ║
║   • NUNCA SIMPLIFICAR, NUNCA PULAR, NUNCA IGNORAR.                   ║
║   • CRIAR O QUE FALTA, NÃO CONTORNAR O QUE FALTA.                    ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

# 📋 CATEGORIAS DE IMPLEMENTAÇÃO

---

## 🔴 CATEGORIA 10: INFRAESTRUTURA DE PRODUÇÃO (NOVOS REQUISITOS)

> Esta categoria contém requisitos essenciais para produção que estavam ausentes na auditoria original.

---

### 10.1 Logging Estruturado para Debugging em Produção

**Arquivo**: `utils/logging.py`, `core/logger.py`  
**Status**: ESTRUTURA BÁSICA - PRECISA EXPANSÃO SIGNIFICATIVA

#### Problema

O sistema atual usa logging básico do Python sem estruturação adequada para diagnóstico em produção. Logs não são facilmente pesquisáveis, não há correlação entre eventos, e informações críticas de contexto estão ausentes.

#### TODO

- [ ] Implementar logger estruturado com JSON output
- [ ] Adicionar correlation_id para rastrear operações através de componentes
- [ ] Implementar log levels dinâmicos (configuráveis em runtime)
- [ ] Adicionar context managers para logging automático de operações
- [ ] Implementar sanitização de dados sensíveis nos logs
- [ ] Criar rotating file handler com compressão
- [ ] Adicionar métricas de timing automáticas para operações longas
- [ ] Implementar log aggregation para múltiplas sessões
- [ ] Criar interface visual para visualização de logs (LogViewer)
- [ ] Adicionar export de logs para análise externa

#### ✓ Critérios de Aceitação

- [ ] Logs em formato JSON válido com campos: `timestamp`, `level`, `message`, `correlation_id`, `component`, `duration_ms`
- [ ] Correlation ID propagado através de todas as operações relacionadas (load → process → display)
- [ ] Dados sensíveis (paths completos, dados do usuário) automaticamente mascarados
- [ ] Rotação automática quando arquivo atinge 10MB, mantendo últimos 5 arquivos comprimidos
- [ ] Alteração de log level via UI sem reiniciar aplicação
- [ ] Operações > 100ms automaticamente logadas com duração
- [ ] LogViewer integrado mostrando logs em tempo real com filtros por level/component
- [ ] Export para CSV/JSON funcional com filtros de data/level

---

### 10.2 Telemetria de Uso (Opcional)

**Arquivo**: `analytics/telemetry.py`, `analytics/metrics.py`  
**Status**: NÃO IMPLEMENTADO

#### Problema

Sem telemetria, não há como priorizar melhorias baseadas em uso real, identificar gargalos de UX, ou entender quais features são mais/menos utilizadas.

#### TODO

- [ ] Criar sistema de telemetria opt-in com consentimento explícito
- [ ] Implementar coleta de métricas de uso (features utilizadas, frequência)
- [ ] Adicionar tracking de performance (tempos de operação, tamanhos de arquivo)
- [ ] Implementar tracking de erros anônimos
- [ ] Criar dashboard local de estatísticas de uso
- [ ] Implementar export de telemetria para análise
- [ ] Adicionar configuração granular de o que é coletado
- [ ] Implementar data retention policy (auto-delete após N dias)

#### ✓ Critérios de Aceitação

- [ ] Diálogo de consentimento no primeiro uso com explicação clara do que é coletado
- [ ] Opção de opt-out a qualquer momento via Settings com efeito imediato
- [ ] Nenhum dado identificável pessoalmente coletado (apenas métricas agregadas)
- [ ] Dashboard local mostrando: features mais usadas, tempo médio por operação, erros frequentes
- [ ] Dados armazenados localmente por padrão (sem envio externo sem consentimento adicional)
- [ ] Auto-delete de dados > 30 dias configurável
- [ ] Lista completa do que é coletado visível nas configurações

---

### 10.3 Crash Reporting Automático

**Arquivo**: `core/crash_handler.py`, `utils/error_reporter.py`  
**Status**: NÃO IMPLEMENTADO

#### Problema

Crashes silenciosos ou não reportados dificultam diagnóstico. Usuários frequentemente não sabem reportar problemas adequadamente, e informações de contexto são perdidas.

#### TODO

- [ ] Implementar global exception handler para PyQt6
- [ ] Criar crash dump com informações de sistema e estado da aplicação
- [ ] Implementar diálogo de crash recovery amigável
- [ ] Adicionar captura de screenshots no momento do crash (opcional)
- [ ] Implementar auto-save de emergência antes do crash
- [ ] Criar sistema de crash reports locais para análise
- [ ] Adicionar opção de envio de crash report (opt-in)
- [ ] Implementar análise de padrões de crash localmente
- [ ] Criar mecanismo de recuperação pós-crash

#### ✓ Critérios de Aceitação

- [ ] 100% dos crashes capturados pelo handler (nenhum crash silencioso)
- [ ] Crash dump inclui: stack trace, versão do app, OS, RAM disponível, últimas 10 ações do usuário
- [ ] Diálogo amigável aparece após crash com opções: Reiniciar, Ver Detalhes, Enviar Report
- [ ] Auto-save de emergência salva sessão atual em < 2 segundos antes do crash
- [ ] Crash reports armazenados em pasta dedicada com últimos 20 reports
- [ ] Recuperação pós-crash oferece restaurar última sessão salva automaticamente
- [ ] Crash report sanitiza paths e dados sensíveis antes de qualquer envio

---

### 10.4 Backup Automático de Sessão (Auto-Save)

**Arquivo**: `core/session_manager.py`, `core/auto_save.py`  
**Status**: PARCIAL - APENAS SAVE MANUAL IMPLEMENTADO

#### Problema

Perda de trabalho em caso de crash, fechamento acidental, ou falha de energia. Usuários precisam lembrar de salvar manualmente.

#### TODO

- [ ] Implementar auto-save periódico configurável (padrão: 5 minutos)
- [ ] Criar backup incremental (apenas mudanças)
- [ ] Implementar versionamento de backups (manter últimas N versões)
- [ ] Adicionar indicador visual de status de auto-save
- [ ] Implementar recuperação de sessão após crash/fechamento
- [ ] Criar limpeza automática de backups antigos
- [ ] Adicionar backup antes de operações destrutivas
- [ ] Implementar sincronização em background (não bloquear UI)
- [ ] Criar diálogo de recuperação no startup

#### ✓ Critérios de Aceitação

- [ ] Auto-save executa a cada 5 minutos (configurável de 1-30 min)
- [ ] Save em background não causa lag perceptível na UI (< 100ms de freeze)
- [ ] Indicador na status bar mostra: último save, próximo save, status (saving/saved/error)
- [ ] Mantém últimas 5 versões de backup com timestamps
- [ ] Ao reabrir após crash, diálogo oferece: Recuperar Última Sessão, Abrir Backup Específico, Começar Nova
- [ ] Backups > 7 dias automaticamente deletados
- [ ] Backup forçado antes de qualquer operação que modifique > 50% dos dados

---

### 10.5 Validação de Integridade de Arquivos Carregados

**Arquivo**: `io/validator.py`, `io/integrity_checker.py`  
**Status**: VALIDAÇÃO BÁSICA - INSUFICIENTE

#### Problema

Arquivos corrompidos, truncados, ou malformados podem causar crashes ou resultados incorretos sem aviso adequado ao usuário.

#### TODO

- [ ] Implementar verificação de checksum para arquivos carregados
- [ ] Adicionar detecção de arquivos truncados
- [ ] Implementar validação de schema para CSV/XLSX
- [ ] Criar detecção de encoding incorreto
- [ ] Implementar detecção de dados corrompidos (NaN excessivos, outliers extremos)
- [ ] Adicionar verificação de consistência temporal (timestamps válidos)
- [ ] Implementar relatório de qualidade de dados pré-carregamento
- [ ] Criar opções de reparo automático para problemas comuns
- [ ] Adicionar quarentena para arquivos suspeitos

#### ✓ Critérios de Aceitação

- [ ] Verificação de integridade executa antes de qualquer processamento
- [ ] Arquivos truncados (EOF inesperado) detectados com mensagem clara
- [ ] Encoding detectado automaticamente com fallback e aviso se ambíguo
- [ ] Relatório de qualidade mostra: % NaN, range de valores, gaps temporais, duplicatas
- [ ] Opção de reparo automático para: remover linhas com NaN, interpolar gaps pequenos, remover duplicatas
- [ ] Arquivos com > 20% de dados inválidos marcados como suspeitos com confirmação do usuário
- [ ] Log de todas as validações e reparos aplicados para auditoria

---

### 10.6 Limites de Memória com Warnings ao Usuário

**Arquivo**: `core/memory_manager.py`, `utils/resource_monitor.py`  
**Status**: NÃO IMPLEMENTADO

#### Problema

Carregar arquivos muito grandes pode consumir toda a RAM disponível, causando crashes ou travamentos do sistema operacional.

#### TODO

- [ ] Implementar monitoramento contínuo de uso de memória
- [ ] Adicionar estimativa de memória necessária antes de carregar arquivo
- [ ] Criar warnings em níveis configuráveis (60%, 80%, 95%)
- [ ] Implementar sugestões de ações quando memória alta
- [ ] Adicionar garbage collection forçado em situações críticas
- [ ] Implementar offloading de dados não visíveis para disco
- [ ] Criar limite hard de memória configurável
- [ ] Adicionar indicador de memória na status bar
- [ ] Implementar modo de baixa memória automático

#### ✓ Critérios de Aceitação

- [ ] Indicador de memória sempre visível na status bar (MB usados / MB disponíveis)
- [ ] Warning amarelo em 60% de uso, vermelho em 80%, crítico em 95%
- [ ] Antes de carregar arquivo > 100MB, estimativa de memória necessária exibida com confirmação
- [ ] Em 80% de uso, sugestões aparecem: fechar datasets não usados, reduzir decimação, salvar e reiniciar
- [ ] Em 95% de uso, auto-save forçado + oferece descarregar datasets menos recentes
- [ ] Modo de baixa memória: decimação agressiva automática, desabilita undo history, limita cache
- [ ] Limite hard configurável (padrão: 80% da RAM total) com bloqueio de novas operações se atingido

---

### 10.7 Acessibilidade (a11y) - Keyboard Navigation e Screen Readers

**Arquivo**: `ui/accessibility.py`, `utils/a11y_helpers.py`  
**Status**: NÃO IMPLEMENTADO

#### Problema

A aplicação não é utilizável por pessoas com deficiências visuais ou motoras. Não há suporte a screen readers ou navegação completa por teclado.

#### TODO

- [ ] Implementar navegação completa por teclado (Tab order lógico)
- [ ] Adicionar atalhos de teclado para todas as ações principais
- [ ] Implementar suporte a screen readers (accessible names/descriptions)
- [ ] Criar modo de alto contraste
- [ ] Adicionar suporte a zoom de interface (não apenas dados)
- [ ] Implementar descrições de gráficos para screen readers
- [ ] Adicionar feedback sonoro para ações (opcional)
- [ ] Criar skip links para navegação rápida
- [ ] Implementar ARIA labels em todos os componentes custom
- [ ] Testar com NVDA, JAWS, e VoiceOver

#### ✓ Critérios de Aceitação

- [ ] 100% das funcionalidades acessíveis apenas com teclado
- [ ] Tab order segue fluxo visual lógico: menu → toolbar → data panel → viz panel → results
- [ ] Todos os botões, inputs, e controles têm accessible name descritivo
- [ ] Atalhos documentados e acessíveis via Help → Keyboard Shortcuts
- [ ] Modo alto contraste atende WCAG 2.1 AA (contraste mínimo 4.5:1)
- [ ] Zoom de interface de 100% a 200% sem perda de funcionalidade
- [ ] Gráficos têm descrição textual alternativa: tipo, eixos, range, tendência geral
- [ ] Teste com NVDA passa sem erros críticos de navegação
- [ ] Focus indicators visíveis em todos os elementos interativos

---

## 🔴 CATEGORIA 1: BUGS CRÍTICOS (ALTA PRIORIDADE)

---

### BUG-001: Sistema de Cores no Gráfico 2D

**Arquivo**: `desktop/widgets/viz_panel.py`  
**Status**: PARCIALMENTE IMPLEMENTADO - QUEBRADO

#### Problema

O índice de série para seleção de cor não incrementa corretamente. Apenas 2 cores funcionam (primeira e segunda série). O método `add_series()` usa `series_index` mas quem chama passa sempre o mesmo valor.

#### TODO

- [ ] Corrigir incremento de series_index em `_add_series_to_plot()`
- [ ] Garantir que cada série receba índice único baseado na ordem de adição
- [ ] Testar com 10+ séries para verificar ciclo de cores
- [ ] Adicionar cor à legenda corretamente

#### ✓ Critérios de Aceitação

- [ ] Ao adicionar 10 séries sequencialmente, cada uma recebe cor diferente da paleta
- [ ] Cores ciclam corretamente após esgotar paleta (série 11 = cor 1)
- [ ] Legenda mostra cor correspondente a cada série
- [ ] Remover série do meio não afeta cores das outras séries
- [ ] Teste automatizado com 15 séries passa sem cores duplicadas adjacentes

---

### BUG-002: Legenda Mostrando "valor" em vez do Nome do Arquivo

**Arquivo**: `desktop/widgets/viz_panel.py`  
**Status**: NÃO IMPLEMENTADO

#### Problema

A legenda mostra texto genérico em vez do nome real da série/arquivo. O parâmetro `name` no `add_series()` recebe `series_id` quando deveria receber `series.name`.

#### TODO

- [ ] Passar `series.name` (nome original do arquivo) para `add_series()`
- [ ] Atualizar legenda quando nome mudar
- [ ] Adicionar tooltip com path completo do arquivo

#### ✓ Critérios de Aceitação

- [ ] Legenda exibe nome do arquivo sem extensão (ex: `dados_2024` não `dados_2024.csv`)
- [ ] Nomes longos (> 25 chars) são truncados com `...` e tooltip mostra nome completo
- [ ] Hover sobre item da legenda mostra tooltip com path completo
- [ ] Renomear série via context menu atualiza legenda imediatamente
- [ ] Séries calculadas mostram nome descritivo (ex: `Derivada de dados_2024`)

---

### BUG-003: Menu de Contexto (Click Direito) - Ações Não Funcionam

**Arquivo**: `desktop/menus/plot_context_menu.py`  
**Status**: STUBS - NÃO IMPLEMENTADO

#### Problema

6 métodos são apenas `pass` - ações do menu não fazem nada.

#### TODO

- [ ] Implementar `_toggle_grid()` - conectar com `plot.showGrid()`
- [ ] Implementar `_toggle_legend()` - conectar com `plot.legend`
- [ ] Implementar `_clear_selection()` - limpar seleção visual
- [ ] Implementar `_select_all()` - selecionar todos os pontos
- [ ] Implementar `_invert_selection()` - inverter seleção atual
- [ ] Implementar `_hide_series()` - ocultar série específica
- [ ] Implementar `_apply_lowpass_filter()` - não é apenas "coming soon"
- [ ] Implementar `_apply_highpass_filter()` - não é apenas "coming soon"
- [ ] Implementar `_apply_bandpass_filter()` - não é apenas "coming soon"
- [ ] Implementar `_detect_outliers()` - não é apenas "coming soon"
- [ ] Implementar `_copy_to_clipboard()` - copiar dados/imagem

#### ✓ Critérios de Aceitação

- [ ] `_toggle_grid()`: Grid aparece/desaparece; estado persiste na sessão; atalho `G` funciona
- [ ] `_toggle_legend()`: Legenda aparece/desaparece; posição mantida; atalho `L` funciona
- [ ] `_clear_selection()`: Toda seleção visual removida; signal emitido; atalho `Escape` funciona
- [ ] `_select_all()`: Todos os pontos da série ativa selecionados; count exibido na status bar
- [ ] `_invert_selection()`: Pontos selecionados ↔ não selecionados; funciona com seleção parcial
- [ ] `_hide_series()`: Série oculta do gráfico mas permanece no data panel; checkbox desmarcado
- [ ] `_apply_lowpass_filter()`: Diálogo com cutoff frequency; preview antes de aplicar; nova série criada
- [ ] `_copy_to_clipboard()`: Opções: dados como CSV, imagem PNG, ou imagem SVG

---

### BUG-004: Cálculos (Derivada, Integral, Área) Não Conectados à UI

**Arquivos**: `ui/panels/operations_panel.py`, `desktop/workers/processing_worker.py`  
**Status**: BACKEND EXISTE - UI NÃO CONECTADA

#### Problema

Os cálculos estão implementados em `processing/calculus.py`. A UI emite signals (`operation_requested`). NINGUÉM ESCUTA esses signals no desktop app.

#### TODO

- [ ] Criar conexão entre `OperationsPanel.operation_requested` e `ProcessingWorker`
- [ ] No `MainWindow`, conectar signals do `operations_panel`
- [ ] Implementar handler para receber resultado do worker
- [ ] Exibir resultado no `ResultsPanel`
- [ ] Adicionar série calculada ao gráfico
- [ ] Implementar validação de dados antes do cálculo

#### ✓ Critérios de Aceitação

- [ ] Clicar em "Calcular Derivada" com série selecionada inicia cálculo em < 100ms
- [ ] Progress bar aparece durante cálculo; cancelável para operações > 2s
- [ ] Resultado aparece no ResultsPanel com: valor, método usado, tempo de cálculo
- [ ] Nova série "Derivada de [nome]" adicionada automaticamente ao gráfico
- [ ] Erro claro se nenhuma série selecionada: "Selecione uma série primeiro"
- [ ] Erro claro se dados insuficientes: "Mínimo de 3 pontos necessários"
- [ ] Worker executa em thread separada (UI não trava durante cálculo)

---

### BUG-005: Checkboxes de Séries Não Funcionam

**Arquivo**: `desktop/widgets/data_panel.py`  
**Status**: UI EXISTE - LÓGICA NÃO IMPLEMENTADA

#### Problema

Checkboxes existem na árvore de dados. Marcar/desmarcar não afeta o gráfico.

#### TODO

- [ ] Conectar checkbox state change com `viz_panel`
- [ ] Implementar show/hide série baseado em checkbox
- [ ] Persistir estado dos checkboxes na sessão
- [ ] Implementar "Select All" / "Deselect All"

#### ✓ Critérios de Aceitação

- [ ] Desmarcar checkbox oculta série do gráfico em < 50ms
- [ ] Remarcar checkbox restaura série na mesma cor e posição de eixo Y
- [ ] Estado dos checkboxes salvo na sessão e restaurado ao reabrir
- [ ] Botão "Select All" marca todos os checkboxes e exibe todas as séries
- [ ] Botão "Deselect All" desmarca todos e oculta todas as séries
- [ ] Checkbox pai (dataset) controla todos os filhos (séries)

---

### BUG-006: Gráficos 3D Não Renderizam

**Arquivo**: `desktop/widgets/viz_panel.py`, `viz/figures_3d.py`  
**Status**: ESTRUTURA EXISTE - RENDERIZAÇÃO QUEBRADA

#### Problema

PyVista é importado mas plots não aparecem. Falta conversão correta de dados para formato 3D.

#### TODO

- [ ] Implementar `plot_trajectory_3d()` completamente
- [ ] Adicionar tratamento de erro quando < 3 séries selecionadas
- [ ] Implementar controles de câmera 3D
- [ ] Adicionar colormap selection
- [ ] Implementar exportação de modelo 3D
- [ ] Testar com diferentes tamanhos de dados

#### ✓ Critérios de Aceitação

- [ ] Trajetória 3D renderiza corretamente com 3 séries selecionadas (X, Y, Z)
- [ ] Erro claro se < 3 séries: "Selecione exatamente 3 séries para X, Y, Z"
- [ ] Controles de câmera: rotação com mouse drag, zoom com scroll, reset com `R`
- [ ] Dropdown de colormap com 10+ opções (viridis, plasma, jet, etc.)
- [ ] Export para STL/OBJ/PLY funcional
- [ ] Performance: 100K pontos renderiza em < 3s; 1M pontos em < 10s

---

### BUG-007: Nomes de Arquivo Exibidos Incorretamente

**Arquivo**: `desktop/widgets/data_panel.py`  
**Status**: PARCIALMENTE IMPLEMENTADO

#### Problema

Path completo em vez de apenas filename. Encoding issues em nomes com caracteres especiais.

#### TODO

- [ ] Usar `Path(file).name` para exibição
- [ ] Adicionar tooltip com path completo
- [ ] Tratar encoding de nomes de arquivo
- [ ] Permitir renomear séries

#### ✓ Critérios de Aceitação

- [ ] Árvore mostra apenas filename, não path completo
- [ ] Tooltip no hover mostra path completo
- [ ] Nomes com acentos (é, ã, ç) exibidos corretamente
- [ ] Nomes com caracteres especiais (日本語, emoji) exibidos corretamente
- [ ] Double-click em nome permite edição inline; Enter confirma, Escape cancela

---

## 🔴 CATEGORIA 2: FUNCIONALIDADES NÃO IMPLEMENTADAS

---

### 2.1 Sistema de Streaming/Playback

**Arquivos**: `ui/panels/streaming_panel.py`, `streaming/`  
**Status**: UI EXISTE - 95% NÃO IMPLEMENTADO

#### TODO

- [ ] Implementar `_connect_signals()` no `StreamingPanel`
- [ ] Criar engine de playback com timer QTimer
- [ ] Implementar `_play()`, `_pause()`, `_stop()`, `_seek()`
- [ ] Sincronizar posição com gráfico (janela deslizante)
- [ ] Implementar controle de velocidade (0.5x, 1x, 2x, etc.)
- [ ] Implementar loop e modo reverso
- [ ] Adicionar timeline interativa com drag
- [ ] Implementar minimap com overview dos dados
- [ ] Conectar filtros de streaming
- [ ] Implementar buffer de dados para performance

#### ✓ Critérios de Aceitação

- [ ] Play inicia playback; gráfico mostra janela deslizante de N segundos
- [ ] Pause congela na posição atual; Play retoma do mesmo ponto
- [ ] Stop para e volta ao início
- [ ] Slider de velocidade: 0.25x, 0.5x, 1x, 2x, 4x, 8x, 16x
- [ ] Drag na timeline move posição; gráfico atualiza em < 50ms
- [ ] Minimap mostra overview com indicador de posição atual
- [ ] Loop: ao chegar no fim, volta ao início automaticamente
- [ ] Atalhos: Space=Play/Pause, Left/Right=±1s, Home=início, End=fim

---

### 2.2 Results Panel - Exibição de Resultados

**Arquivo**: `desktop/widgets/results_panel.py`  
**Status**: UI EXISTE - NÃO FUNCIONA

#### TODO

- [ ] Implementar `_poll_logs()` para mostrar logs em tempo real
- [ ] Implementar `_export_results()` - não é apenas log
- [ ] Conectar `ResultsPanel` com operações completadas
- [ ] Exibir estatísticas de qualidade dos dados
- [ ] Mostrar métricas de cálculos (área, integral, etc.)
- [ ] Implementar tabela de resultados com sorting
- [ ] Adicionar gráficos de qualidade
- [ ] Permitir copiar resultados para clipboard

#### ✓ Critérios de Aceitação

- [ ] Logs aparecem em tempo real com cores por level (INFO=azul, WARN=amarelo, ERROR=vermelho)
- [ ] Ao completar cálculo, resultado aparece em tabela com: operação, resultado, timestamp
- [ ] Tabela sortable por qualquer coluna
- [ ] Estatísticas de dados: count, min, max, mean, std, % NaN
- [ ] Gráfico de qualidade: histograma de valores
- [ ] Botão Export gera CSV com todos os resultados
- [ ] Ctrl+C com célula selecionada copia valor

---

### 2.3 Sistema de Undo/Redo

**Arquivo**: `ui/undo_redo.py`  
**Status**: ESTRUTURA - 0% IMPLEMENTADO

#### TODO

- [ ] Implementar classe `Command` base funcional (não apenas pass)
- [ ] Implementar `execute()` e `undo()` para cada tipo de operação
- [ ] Implementar `CommandStack` com limite de memória
- [ ] Conectar todas as operações com sistema de commands
- [ ] Adicionar shortcuts Ctrl+Z / Ctrl+Y
- [ ] Implementar redo queue
- [ ] Persistir history entre sessões (opcional)
- [ ] Mostrar histórico visual de operações

#### ✓ Critérios de Aceitação

- [ ] Ctrl+Z desfaz última operação; estado visual atualiza imediatamente
- [ ] Ctrl+Y refaz operação desfeita
- [ ] Suporte a undo/redo para: adicionar série, remover série, aplicar filtro, calcular
- [ ] Stack limitado a 50 operações ou 100MB de memória (o que vier primeiro)
- [ ] Operações agrupadas quando < 1s entre elas (ex: múltiplos deletes)
- [ ] Menu Edit mostra "Undo [nome da operação]" e "Redo [nome da operação]"
- [ ] Painel de histórico mostra lista de operações com possibilidade de voltar a qualquer ponto

---

### 2.4 Exportação de Dados

**Arquivo**: `ui/export_dialog.py`, `desktop/workers/export_worker.py`  
**Status**: PARCIAL - MUITAS FEATURES FALTANDO

#### TODO

- [ ] Implementar exportação de sessão completa
- [ ] Implementar exportação de gráfico como imagem (PNG, SVG, PDF)
- [ ] Implementar exportação de animação/vídeo
- [ ] Adicionar opções de compressão
- [ ] Implementar exportação seletiva (só séries marcadas)
- [ ] Adicionar metadados nos arquivos exportados
- [ ] Implementar batch export (múltiplos arquivos)
- [ ] Suportar exportação para formatos científicos (MAT, NetCDF)

#### ✓ Critérios de Aceitação

- [ ] Export CSV: delimitador configurável, encoding UTF-8/Latin1, com/sem header
- [ ] Export XLSX: múltiplas séries em abas separadas ou mesma aba
- [ ] Export PNG: resolução configurável (72-600 DPI), tamanho em pixels/cm
- [ ] Export SVG: vetorial, editável em Illustrator/Inkscape
- [ ] Export PDF: qualidade vetorial, metadados (título, autor, data)
- [ ] Export MAT: compatível com MATLAB R2019b+
- [ ] Export sessão: arquivo `.warp` próprio com todos os dados e configurações
- [ ] Batch export: selecionar múltiplos datasets, escolher formato, exportar todos

---

### 2.5 Sistema de Seleção Multi-View

**Arquivos**: `ui/selection_sync.py`, `ui/multi_view_sync.py`  
**Status**: ESTRUTURA - MAIORIA NÃO IMPLEMENTADA

#### TODO

- [ ] Implementar `apply_synced_selection()` - raise NotImplementedError atual
- [ ] Implementar sincronização de seleção entre gráficos
- [ ] Implementar brush selection (arrastar para selecionar)
- [ ] Implementar lasso selection
- [ ] Implementar box selection
- [ ] Sincronizar zoom entre gráficos
- [ ] Sincronizar crosshair entre gráficos
- [ ] Implementar linked views (X-axis sync)

#### ✓ Critérios de Aceitação

- [ ] Seleção em gráfico A reflete instantaneamente em gráfico B (se linked)
- [ ] Brush selection: arrastar horizontalmente seleciona range temporal
- [ ] Box selection: arrastar retângulo seleciona pontos dentro da área
- [ ] Lasso selection: desenhar forma livre seleciona pontos dentro
- [ ] Zoom em gráfico A aplica mesmo zoom em gráfico B (se sync habilitado)
- [ ] Crosshair mostra posição em todos os gráficos sincronizados
- [ ] Toggle para habilitar/desabilitar sync por gráfico

---

### 2.6 Plot Sync - Sincronização de Gráficos

**Arquivo**: `ui/plot_sync.py`  
**Status**: ESTRUTURA - 5 MÉTODOS COM `pass`

#### TODO

- [ ] Implementar `_on_y_range_changed()` (linha 228)
- [ ] Implementar `_on_x_range_changed()` (linha 252)
- [ ] Implementar `_on_crosshair_moved()` (linha 274)
- [ ] Implementar `_on_selection_changed()` (linha 297)
- [ ] Implementar `_sync_widget()` completamente (linha 339)
- [ ] Adicionar opção de desativar sincronização
- [ ] Implementar sincronização de apenas X ou apenas Y

#### ✓ Critérios de Aceitação

- [ ] Alterar range Y em gráfico master altera range Y em todos os slaves
- [ ] Alterar range X sincroniza apenas se "Sync X" habilitado
- [ ] Crosshair move em sync com < 16ms de latência (60fps)
- [ ] Seleção temporal propagada para todos os gráficos sincronizados
- [ ] Checkbox "Sync X" e "Sync Y" independentes por gráfico
- [ ] Desabilitar sync não afeta estado atual, apenas para propagação futura

---

### 2.7 Video Export

**Arquivo**: `ui/video_export.py`  
**Status**: ESTRUTURA - TODO EXPLÍCITO NO CÓDIGO

#### TODO

- [ ] Implementar `_frame_to_numpy()` corretamente (linha 229)
- [ ] Implementar `_finalize_export()` (linha 239 - apenas pass)
- [ ] Integrar com moviepy para geração de vídeo
- [ ] Suportar GIF animado
- [ ] Adicionar opções de qualidade/fps
- [ ] Implementar progress tracking

#### ✓ Critérios de Aceitação

- [ ] Export MP4 com codec H.264 funcional
- [ ] Export GIF animado com palette optimization
- [ ] FPS configurável: 15, 24, 30, 60
- [ ] Resolução configurável: 720p, 1080p, 4K
- [ ] Qualidade configurável: baixa (rápido), média, alta (lento)
- [ ] Progress bar mostra: frame atual / total frames, tempo estimado restante
- [ ] Preview de 5 segundos antes de exportar vídeo completo

---

### 2.8 Eixo Datetime

**Status**: NÃO IMPLEMENTADO

#### Problema

Eixo X sempre mostra segundos, não timestamps.

#### TODO

- [ ] Criar `DateTimeAxis` customizado para pyqtgraph
- [ ] Implementar formatação de datetime no eixo
- [ ] Suportar diferentes formatos (ISO, locale, etc.)
- [ ] Implementar zoom com datetime awareness
- [ ] Sincronizar seleção temporal com datetime

#### ✓ Critérios de Aceitação

- [ ] Eixo X detecta automaticamente se dados são datetime e formata apropriadamente
- [ ] Zoom adapta formato: anos → meses → dias → horas → minutos → segundos
- [ ] Formato configurável: ISO 8601, locale do sistema, custom
- [ ] Seleção de range mostra datetime de início e fim na status bar
- [ ] Tooltip mostra datetime preciso (até milissegundos se disponível)

---

### 2.9 Multi-Y Axis

**Arquivo**: `desktop/widgets/viz_panel.py`  
**Status**: ESTRUTURA EXISTE - NÃO FUNCIONA

#### TODO

- [ ] Corrigir `add_secondary_y_axis()` para funcionar
- [ ] Implementar `_move_selected_to_y2()` (linha 617 - apenas comentário)
- [ ] Permitir até 4 eixos Y
- [ ] Colorir eixos conforme séries
- [ ] Implementar auto-range para cada eixo
- [ ] Adicionar indicador visual de qual eixo cada série usa

#### ✓ Critérios de Aceitação

- [ ] Botão "Add Y Axis" cria segundo eixo Y à direita
- [ ] Drag-drop de série para eixo Y2 move série para segundo eixo
- [ ] Até 4 eixos Y suportados (Y1 esquerda, Y2 direita, Y3 esquerda externa, Y4 direita externa)
- [ ] Cor do eixo Y corresponde à cor da série (ou primeira série se múltiplas)
- [ ] Auto-range independente por eixo
- [ ] Indicador na legenda mostra qual eixo Y cada série usa

---

## 🟡 CATEGORIA 3: MELHORIAS DE UI/UX

---

### 3.1 Temas

**Status**: NÃO IMPLEMENTADO

#### TODO

- [ ] Implementar tema claro (atual)
- [ ] Implementar tema escuro
- [ ] Adicionar seletor de tema nas configurações
- [ ] Persistir tema selecionado
- [ ] Aplicar tema em todos os componentes
- [ ] Suportar tema do sistema operacional

#### ✓ Critérios de Aceitação

- [ ] Tema claro: fundo branco, texto preto, acentos em azul
- [ ] Tema escuro: fundo #1E1E1E, texto #E0E0E0, acentos em azul claro
- [ ] Mudança de tema aplica instantaneamente sem reiniciar
- [ ] Gráficos respeitam tema (fundo, grid, texto)
- [ ] Opção "Seguir Sistema" detecta tema do OS e acompanha mudanças
- [ ] Tema salvo em configurações e restaurado ao abrir

---

### 3.2 Internacionalização (i18n)

**Arquivo**: `utils/i18n.py`  
**Status**: ESTRUTURA - 1 TODO + muitas traduções faltando

#### TODO

- [ ] Completar traduções PT-BR
- [ ] Adicionar suporte a EN
- [ ] Implementar seletor de idioma
- [ ] Traduzir mensagens de erro
- [ ] Traduzir tooltips
- [ ] Adicionar suporte a ES (opcional)

#### ✓ Critérios de Aceitação

- [ ] 100% das strings de UI traduzidas para PT-BR e EN
- [ ] Mensagens de erro traduzidas e culturalmente apropriadas
- [ ] Tooltips traduzidos
- [ ] Mudança de idioma aplica sem reiniciar (ou com aviso de reinício necessário)
- [ ] Formato de números respeita locale (1.000,50 vs 1,000.50)
- [ ] Formato de datas respeita locale (DD/MM/YYYY vs MM/DD/YYYY)

---

### 3.3 Tooltips e Help

**Status**: PARCIAL

#### TODO

- [ ] Adicionar tooltips em todos os botões
- [ ] Implementar help contextual (F1)
- [ ] Criar documentação inline
- [ ] Adicionar "What's This?" mode

#### ✓ Critérios de Aceitação

- [ ] 100% dos botões e controles têm tooltip descritivo
- [ ] F1 abre ajuda contextual para o elemento focado
- [ ] Shift+F1 ativa modo "What's This?" - cursor muda, clique mostra ajuda
- [ ] Tooltips aparecem após 500ms de hover, desaparecem após 5s
- [ ] Ajuda contextual inclui link para documentação online

---

### 3.4 Keyboard Shortcuts

**Status**: PARCIAL

#### TODO

- [ ] Documentar todos os shortcuts existentes
- [ ] Adicionar shortcuts faltantes (ver lista abaixo)
- [ ] Permitir customização de shortcuts
- [ ] Mostrar shortcuts em tooltips

**Shortcuts a implementar:**

- [ ] `Ctrl+D` - Duplicar série
- [ ] `Delete` - Remover série selecionada
- [ ] `Ctrl+A` - Selecionar tudo
- [ ] `Ctrl+Shift+A` - Desselecionar tudo
- [ ] `F5` - Atualizar dados
- [ ] `F11` - Fullscreen
- [ ] `Space` - Play/Pause streaming

#### ✓ Critérios de Aceitação

- [ ] Help → Keyboard Shortcuts mostra lista completa de atalhos
- [ ] Tooltips incluem shortcut quando aplicável (ex: "Salvar (Ctrl+S)")
- [ ] Settings → Shortcuts permite customizar qualquer atalho
- [ ] Conflitos de atalho detectados e avisados
- [ ] Atalhos desabilitados quando não aplicáveis (ex: Delete sem seleção)

---

## 🟡 CATEGORIA 4: CONEXÕES UI↔BACKEND FALTANTES

---

### 4.1 Operations Panel → Processing

**Problema**: UI emite signals que ninguém escuta

#### TODO

- [ ] Em `MainWindow.__init__`, adicionar:
  ```python
  self.operations_panel = OperationsPanel(...)
  self.operations_panel.operation_requested.connect(self._handle_operation)
  ```
- [ ] Implementar `_handle_operation(operation, params)`:
  - Validar dados selecionados
  - Criar worker apropriado
  - Conectar `worker.finished` → `ResultsPanel`
  - Conectar `worker.error` → `StatusBar`
- [ ] Conectar `OperationsPanel` ao desktop app (não apenas ui app)

#### ✓ Critérios de Aceitação

- [ ] Clicar em qualquer botão de operação no OperationsPanel inicia o cálculo
- [ ] Signal `operation_requested` conectado a handler no MainWindow
- [ ] Handler valida seleção, cria worker, e gerencia resultado
- [ ] Resultado aparece no ResultsPanel E como nova série no gráfico

---

### 4.2 Data Panel → Viz Panel

**Problema**: Selecionar série não plota automaticamente

#### TODO

- [ ] Conectar `data_panel.series_double_clicked` → `viz_panel.add_series`
- [ ] Conectar `data_panel.checkbox_changed` → `viz_panel.toggle_series`
- [ ] Implementar drag & drop de série para gráfico

#### ✓ Critérios de Aceitação

- [ ] Double-click em série adiciona ao gráfico ativo
- [ ] Checkbox toggle mostra/oculta série no gráfico
- [ ] Drag série do DataPanel e drop no gráfico adiciona série
- [ ] Drop em área vazia cria novo gráfico com a série

---

### 4.3 Config Panel → Todos os Componentes

**Problema**: Mudanças de config não afetam componentes

#### TODO

- [ ] Conectar config changes com `viz_panel` (cores, grid, etc.)
- [ ] Conectar config changes com `streaming panel`
- [ ] Conectar config changes com `performance settings`
- [ ] Implementar botões "Apply" e "Reset"

#### ✓ Critérios de Aceitação

- [ ] Mudar interpolation method no ConfigPanel afeta próximo cálculo
- [ ] Mudar decimation settings afeta renderização imediatamente
- [ ] Mudar streaming window size afeta playback
- [ ] Botão Apply aplica mudanças; Reset reverte para valores salvos
- [ ] Mudanças não salvas indicadas com `*` no título do painel

---

## 🔴 CATEGORIA 5: COMPONENTES DO DESKTOP APP FALTANTES

---

### 5.1 Operations Panel no Desktop App

**Problema**: Existe em `ui/panels/operations_panel.py` mas não está no desktop app

#### TODO

- [ ] Adicionar `OperationsPanel` ao `desktop/main_window.py`
- [ ] Criar dock widget para operations
- [ ] Conectar com `session_state`
- [ ] Conectar com `signal_hub`

#### ✓ Critérios de Aceitação

- [ ] OperationsPanel visível como dock widget no lado direito
- [ ] Dock é redimensionável e pode ser destacado (floating)
- [ ] Estado do dock salvo na sessão (posição, tamanho, visibilidade)
- [ ] Operações refletem seleção atual do session_state

---

### 5.2 Streaming Panel no Desktop App

**Problema**: Existe em `ui/panels/streaming_panel.py` mas não está no desktop app

#### TODO

- [ ] Adicionar `StreamingPanel` ao desktop app
- [ ] Integrar controles na toolbar ou dock
- [ ] Conectar com `viz_panel` para atualização de janela

#### ✓ Critérios de Aceitação

- [ ] Controles de streaming visíveis na toolbar inferior
- [ ] Play/Pause/Stop funcionam e atualizam gráfico
- [ ] Timeline mostra posição atual e permite seek
- [ ] Controle de velocidade acessível

---

### 5.3 Preview Dialog para Operações

**Arquivo**: `ui/operation_preview.py`  
**Status**: EXISTE - NÃO CONECTADO

#### TODO

- [ ] Integrar `OperationPreviewDialog` no fluxo de operações
- [ ] Mostrar preview antes de aplicar operação
- [ ] Implementar comparação before/after

#### ✓ Critérios de Aceitação

- [ ] Checkbox "Show Preview" nas operações (default: on)
- [ ] Preview mostra: gráfico before, gráfico after, diff highlights
- [ ] Botões: Apply, Cancel, Apply Without Preview (for next time)
- [ ] Preview renderiza em < 1s para datasets de até 100K pontos

---

## 🔴 CATEGORIA 6: TESTES E QUALIDADE (PIRÂMIDE COMPLETA)

> ⚠️ **POLÍTICA DE TESTES**: Nenhum teste pode ser ignorado, simplificado ou omitido.
> Se um teste falhar, DEVE ser corrigido antes de prosseguir.
> Cobertura mínima exigida: **95%** para produção.

### 📊 Sumário de Testes

| Nível | Tipo | Status | Cobertura Alvo | Ferramentas |
|-------|------|--------|----------------|-------------|
| 1º | Linting/Static | 🔴 0% | N/A | ruff, mypy, bandit |
| 2º | Unit Tests | 🔴 ~15% | 95% | pytest |
| 3º | Doctests | 🔴 0% | 100% funções públicas | pytest --doctest |
| 4º | Integration | 🔴 0% | 80% | pytest |
| 5º | Property-based | 🔴 0% | Funções matemáticas | hypothesis |
| 6º | GUI/Functional | 🔴 0% | Fluxos críticos | pytest-qt |
| 7º | Performance | 🔴 0% | Baselines definidos | pytest-benchmark |
| 8º | E2E | 🔴 0% | Cenários principais | pytest-qt |
| 9º | Load/Stress | 🔴 0% | Limites definidos | locust, pytest |
| 10º | Smoke Tests | 🔴 0% | 100% | pytest -m smoke |

### ✓ Critérios de Aceitação Globais para Testes

- [ ] `ruff check .` passa sem erros
- [ ] `mypy src/ --strict` passa sem erros
- [ ] `bandit -r src/` não encontra vulnerabilidades críticas
- [ ] `pytest tests/unit --cov --cov-fail-under=95` passa
- [ ] `pytest tests/smoke -m smoke` passa em < 60 segundos
- [ ] Nenhum teste marcado como `@pytest.mark.skip` sem justificativa documentada
- [ ] CI/CD executa todos os testes em cada PR
- [ ] Coverage report HTML gerado e acessível

### Resumo de Testes a Criar

| Categoria | Arquivos | Testes | Prioridade |
|-----------|----------|--------|------------|
| Linting Config | 3 | N/A | 🔴 CRÍTICA |
| Unit Tests | 25 | ~250 | 🔴 CRÍTICA |
| Doctests | 8 | ~50 | 🟡 MÉDIA |
| Integration | 5 | ~40 | 🔴 ALTA |
| Property-based | 2 | ~15 | 🟡 MÉDIA |
| GUI/Functional | 4 | ~60 | 🔴 ALTA |
| Performance | 4 | ~30 | 🟡 MÉDIA |
| E2E | 3 | ~20 | 🔴 ALTA |
| Stress | 3 | ~15 | 🟢 BAIXA |
| Smoke | 1 | ~10 | 🔴 CRÍTICA |
| **TOTAL** | **58** | **~490** | - |

---

## 🟡 CATEGORIA 7: PERFORMANCE E OTIMIZAÇÃO

---

### 7.1 Decimação de Dados para Visualização

**Arquivo**: `processing/downsampling.py`, `ui/panels/performance.py`  
**Status**: IMPLEMENTADO NO BACKEND - NÃO CONECTADO

#### TODO

- [ ] Conectar adaptive decimation com `viz_panel`
- [ ] Implementar LOD (Level of Detail) baseado em zoom
- [ ] Adicionar indicador de decimação no gráfico
- [ ] Permitir desativar decimação

#### ✓ Critérios de Aceitação

- [ ] Dados > 10K pontos automaticamente decimados para renderização
- [ ] Zoom in aumenta resolução na região visível
- [ ] Indicador mostra: "Exibindo 5.000 de 1.000.000 pontos"
- [ ] Checkbox "Show All Points" desabilita decimação (com warning de performance)
- [ ] LOD: zoom out = menos pontos, zoom in = mais pontos, transição suave

---

### 7.2 Caching

**Arquivo**: `caching/disk.py`, `caching/memory.py`  
**Status**: ESTRUTURA - PARCIALMENTE IMPLEMENTADO

#### TODO

- [ ] Implementar cache de arquivos carregados
- [ ] Implementar cache de cálculos
- [ ] Adicionar invalidação de cache
- [ ] Implementar limite de memória

#### ✓ Critérios de Aceitação

- [ ] Segundo load do mesmo arquivo é 10x mais rápido (cache hit)
- [ ] Recalcular derivada com mesmos parâmetros retorna cache
- [ ] Modificar dados invalida cache dependente automaticamente
- [ ] Cache limitado a 500MB; LRU eviction quando cheio
- [ ] Cache stats visíveis em Settings: hits, misses, size

---

### 7.3 Lazy Loading

**Status**: NÃO IMPLEMENTADO

#### TODO

- [ ] Implementar carregamento sob demanda para arquivos grandes
- [ ] Carregar apenas janela visível do gráfico
- [ ] Implementar virtual scrolling para listas grandes

#### ✓ Critérios de Aceitação

- [ ] Arquivos > 100MB carregam header em < 1s, dados sob demanda
- [ ] Scroll no gráfico carrega dados necessários em < 100ms
- [ ] Lista com 10.000 séries renderiza em < 500ms (virtual scroll)
- [ ] Indicador de loading durante carregamento sob demanda

---

## 📝 CATEGORIA 8: DOCUMENTAÇÃO

---

### 8.1 Documentação de Usuário

#### TODO

- [ ] Manual de uso completo
- [ ] Tutoriais em vídeo
- [ ] FAQ
- [ ] Troubleshooting guide

#### ✓ Critérios de Aceitação

- [ ] Manual cobre 100% das funcionalidades com screenshots
- [ ] Quick Start guide permite usar features principais em < 15 min
- [ ] FAQ com 20+ perguntas frequentes
- [ ] Troubleshooting cobre erros comuns com soluções passo-a-passo
- [ ] Documentação disponível offline dentro da aplicação

---

### 8.2 Documentação de Desenvolvedor

#### TODO

- [ ] API reference completa
- [ ] Architecture overview
- [ ] Contributing guide
- [ ] Plugin development guide

#### ✓ Critérios de Aceitação

- [ ] API reference gerada automaticamente de docstrings (Sphinx)
- [ ] Diagrama de arquitetura atualizado
- [ ] Contributing guide com setup de ambiente em < 10 passos
- [ ] Plugin guide com exemplo funcional de análise custom

---

## 🎨 CATEGORIA 9: MIGRAÇÃO COMPLETA PARA Qt Designer (.ui)

> **IMPORTANTE**: Atualmente a aplicação tem 2 arquivos .ui criados mas **NÃO SÃO USADOS**.
> O código Python cria toda a UI programaticamente.

### Estado Atual

| Categoria | Quantidade | .ui Existentes | A Criar |
|-----------|------------|----------------|---------|
| MainWindows | 2 | 1 (não usado) | 2 |
| Diálogos | 16 | 0 | 16 |
| Painéis | 11 | 1 (não usado) | 11 |
| Widgets Config | 10 | 0 | 10 |
| Widgets Seleção | 5 | 0 | 5 |
| Widgets Streaming | 4 | 0 | 4 |
| Widgets Viz | 6 | 0 | (promoted) |
| Menus/Toolbars | 3 | 0 | 3 |
| Frames | 3 | 0 | 3 |
| **TOTAL** | **60** | **2** | **~45** |

### ✓ Critérios de Aceitação da Migração

- [ ] 100% dos diálogos carregados de arquivos .ui
- [ ] 100% dos painéis principais carregados de arquivos .ui
- [ ] `UiLoaderMixin` funcional e documentado
- [ ] Promoted widgets configurados para gráficos
- [ ] Nenhuma regressão visual após migração
- [ ] Build process compila .ui automaticamente
- [ ] Testes de regressão passam após cada migração

---

## 📊 MÉTRICAS FINAIS

| Métrica | Valor |
|---------|-------|
| **Total de Itens TODO** | ~350+ |
| **Estimativa de Esforço Revisada** | 24-32 semanas |
| **Cobertura de Testes Alvo** | 95% |
| **Novos Requisitos Críticos (Cat. 10)** | 7 |
| **Total de Critérios de Aceitação** | ~200 |

### Checklist Final para Produção

- [ ] 0 crashes em uso normal (teste de 8h)
- [ ] Todas as 7 features core funcionando (load, plot, calculate, export, streaming, selection, 3D)
- [ ] Cobertura de testes ≥ 95%
- [ ] Documentação de usuário completa
- [ ] Performance: load 1M pontos < 5s, plot < 1s
- [ ] Todos os 176+ stubs implementados
- [ ] 0 "coming soon" messages
- [ ] 0 `pass` statements em handlers de UI
- [ ] Logging estruturado funcional
- [ ] Crash reporting funcional
- [ ] Auto-save funcional
- [ ] Validação de integridade funcional
- [ ] Limites de memória com warnings
- [ ] Navegação por teclado 100% funcional

---

*Documento gerado em: 01/02/2026*  
*Versão: 2.0 Consolidada*  
*Auditoria original: 30/01/2026*
