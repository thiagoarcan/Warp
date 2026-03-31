# Warp

## What This Is

Warp e uma plataforma desktop para engenharia, operacao e analise de dados de sinais com arquitetura em camadas e extensibilidade por plugins. O produto oferece ingestao, processamento e visualizacao (2D/3D) em ambiente PySide6, com API local para automacao. Nesta iniciativa, o foco e consolidar a camada de UI e reduzir risco tecnico para aumentar estabilidade e velocidade de evolucao.

## Core Value

Manter um fluxo estavel de ingestao -> processamento -> visualizacao para usuarios tecnicos sem regressao operacional.

## Requirements

### Validated

- ✓ Usuarios carregam datasets e executam analises de sinais em fluxo desktop com UI PySide6 — existente
- ✓ Visualizacao 2D/3D e recursos de exploracao grafica ja suportam casos reais no produto — existente
- ✓ Arquitetura plugin-based com descoberta/registro de plugins permite extensao funcional — existente
- ✓ API local (FastAPI) e integrada ao ecossistema interno para automacao programatica — existente

### Active

- [ ] Consolidar a UI em uma trilha unica baseada em `ui/`, removendo dependencia operacional do legado `desktop/`
- [ ] Eliminar duplicacoes criticas (main windows, signal/session e launchers redundantes) com criterio de canonicidade
- [ ] Endurecer confiabilidade tecnica com baseline de testes executavel e sem lacunas nos fluxos principais
- [ ] Concluir migracao em ondas pequenas, com compatibilidade media e comunicacao clara de ajustes pontuais

### Out of Scope

- Novas features de produto — foco atual e estabilizacao/refatoracao, nao expansao funcional
- Grandes mudancas no engine de processamento — risco elevado para o core value nesta fase
- Refatoracao ampla da API FastAPI — manter superficie atual para reduzir impacto sistêmico

## Context

O repositorio apresenta base brownfield com codigo existente e mapeamento arquitetural em `.planning/codebase/`. A arquitetura atual e plugin-based em camadas (core, io, processing, viz, ui/api), com migracao ativa de UI de `desktop/` para `ui/`. Foram identificados problemas criticos de divida tecnica: coexistencia de camadas de UI, multiplas implementacoes de main window, duplicacao de modulos de estado/sinais, multiplicidade de launchers e baseline de testes incompleto. O risco prioritario a mitigar nesta iniciativa e queda de performance/consumo de memoria durante consolidacao.

## Constraints

- **Tech stack**: Manter Python + PySide6 + arquitetura plugin-based — preservar investimento tecnico e compatibilidade do ecossistema
- **Compatibilidade**: Nivel medio com comportamento legado — permitir melhorias com ajustes pontuais controlados
- **Entrega**: Migracao em ondas pequenas — reduzir risco operacional e facilitar rollback
- **Performance**: Evitar degradacao de tempo de resposta e memoria — risco mais critico definido para a fase
- **Operacao**: Sem interrupcao dos fluxos principais de engenharia/operacao/analise — proteger uso diario

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Priorizar consolidacao da UI antes de hardening amplo de testes | Maior concentracao de divida tecnica e fonte de inconsistencias funcionais | — Pending |
| Trabalhar com compatibilidade media (nao estrita) | Permite limpar arquitetura com menor custo de manutencao futura | — Pending |
| Executar migracao por ondas pequenas | Diminui risco de regressao e facilita validacao incremental | — Pending |
| Manter stack atual (Python/PySide6/plugins) | Evita ruptura arquitetural em fase de estabilizacao | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-31 after initialization*