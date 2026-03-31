# Research Summary

## Stack

Preservar stack existente (Python 3.12, PySide6, pluggy, FastAPI local) e concentrar a iniciativa em consolidacao de UI e limpeza de duplicacoes. Evitar replatforming e redesign arquitetural amplo nesta etapa.

## Table Stakes For This Initiative

- Fluxo estavel de ingestao -> processamento -> visualizacao.
- Runtime em trilha unica de UI (`ui/`) com paridade dos fluxos criticos.
- Eliminacao de duplicacoes canonicamente definidas.
- Baseline de testes repetivel para bloquear regressao.

## Watch Out For

- Acoplamentos ocultos entre `desktop/` e `ui/`.
- Remocao prematura de codigo duplicado sem prova de paridade.
- Regressao de performance e memoria durante migracao.
- Illusion of green: execucoes de teste parciais tratadas como baseline.

## Recommended Sequencing

1. Fixar runtime canonicamente em `ui/` e launcher unico com smoke tests.
2. Consolidar main window em um modulo oficial.
3. Unificar signal/session sob ownership do core.
4. Remover launchers/workarounds obsoletos apos validacao.
5. Endurecer testes funcionais e guardrails de performance para manter ganhos.

## Confidence

- Direcao geral: alta.
- Risco de implementacao: medio/alto, mitigado por rollout em ondas pequenas e gates de validacao.