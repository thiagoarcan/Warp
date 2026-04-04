# Warp

## What This Is

Warp e uma plataforma desktop consolidada para engenharia, operacao e analise de dados de sinais com arquitetura em camadas e extensibilidade por plugins. O produto oferece ingestao, processamento e visualizacao (2D/3D) em ambiente PyQt6, com API local para automacao. Apos v1.0, a camada de UI foi consolidada em trilha unica (ui/), a divida tecnica critica foi eliminada (duplicacoes de main window, canonicalizacao de estado/sinais), e baseline de testes automatizados foi estabelecido com validacao de performance.

## Core Value

Manter um fluxo estavel de ingestao -> processamento -> visualizacao para usuarios tecnicos sem regressao operacional.

## Current State (v1.0 — SHIPPED ✅)

**Version:** v1.0 (2026-04-04)  
**Status:** Production Ready

**Technical Foundation:**
- ✅ 202+ automated tests with critical-path gate (98 passed)
- ✅ Single canonical launcher: launch_app.py
- ✅ Consolidated core modules: SessionState, SignalHub, MainWindow
- ✅ Eliminated redundant entrypoints and legacy workarounds
- ✅ Performance baselines established: startup 15.14s, memory 185MB (stable, improved)
- ✅ All documentation current (README, USER_GUIDE, TROUBLESHOOTING, IMPLEMENTATION_SUMMARY)

**Ready For:**
- Production deployment
- v1.1 enhancement planning
- v2.0 feature development

---

## Requirements

### Validated (v1.0 Shipped ✅)

- ✓ Usuarios carregam datasets e executam analises de sinais em fluxo desktop com UI PyQt6 — existente
- ✓ Visualizacao 2D/3D e recursos de exploracao grafica suportam casos reais no produto — existente
- ✓ Arquitetura plugin-based com descoberta/registro permite extensao funcional — existente
- ✓ API local (FastAPI) integrada ao ecossistema interno para automacao — existente
- ✓ UI consolidada em trilha unica baseada em ui/, sem dependencia operacional de desktop/ legado — **v1.0 Phase 2**
- ✓ Duplicacoes criticas removidas (main windows, signal/session, launchers redundantes) — **v1.0 Phases 3-4**
- ✓ Baseline de testes executavel com ciclo critico completo e cobertura de fluxos principais — **v1.0 Phases 1, 5**
- ✓ Migracao em ondas pequenas com compatibilidade media e comunicacao clara — **v1.0 completion**

### Active (v1.1+ Planning)

- [ ] Retroactive Nyquist validation for phases 2-5 (documentation enhancement)
- [ ] User feedback integration from v1.0 deployment
- [ ] Minor performance optimizations based on production metrics
- [ ] Additional edge-case error handling

### Out of Scope (Deferred to v2.0+)

- Novas features de produto — estabilizacao v1.0 completa; expansao em v2.0
- Refatoracao ampla do engine de processamento — risco elevado; possivel em v2.0 com baseline estavel
- Redesenho amplo da API FastAPI — manter superficie atual; mudancas significativas em v2.0

## Context (Post-v1.0)

O repositorio agora apresenta base estruturada com divida tecnica v1.0 eliminada. Arquitetura consolidada em camadas (core, io, processing, viz, ui/api) com trilha unica de UI em ui/. 

**v1.0 Accomplishments:**
1. Estabeleceu pipeline de validacao confiavel com 202+ testes automatizados
2. Consolidou UI em trilha unica com launcher canonico (launch_app.py)
3. Centralizou ownership de SessionState e SignalHub no core layer
4. Unificou MainWindow com implementacao unica em ui/
5. Limpou entrypoints redundantes e documentou caminho canonico
6. Validou ausencia de regressao de startup/memoria

**Riscos Resolvidos:**
- Windows access violation em testes (fixed)
- Duplicate module ownership (consolidated)
- Redundant entrypoints (archived)
- Implicit runtime dependencies (eliminated)

**Baseline Established:**
- Startup: 15.14s (stable)
- Memory: 185MB (improved)
- Test Coverage: 202 passing + 98 critical-path
- Documentation: All current

## Constraints (Maintained from v1.0)

- **Tech stack**: Python + PyQt6 + arquitetura plugin-based — preservado e estavel
- **Compatibilidade**: Nivel medio com comportamento legado — v1.0 concluiu migracao maior
- **Entrega**: Migracao concluida em ondas; v1.1+ pode iterar mais rapidamente
- **Performance**: Baseline estabelecido; futuras mudancas validadas contra timeline
- **Operacao**: Fluxos principais protegidos; nenhuma interrupcao conhecida

## Key Decisions (v1.0 Outcomes)

| Decision | Rationale | v1.0 Outcome | Status |
|----------|-----------|--------------|--------|
| Priorizar consolidacao da UI antes de hardening amplo de testes | Maior concentracao de divida tecnica | ✅ Completado: UI consolidada, tests estabelecidos | Active |
| Trabalhar com compatibilidade media (nao estrita) | Permite limpar com menor custo | ✅ Executado: Wrappers mantiveram compatividade | Active |
| Executar migracao por ondas pequenas | Diminui risco; facilita validacao | ✅ Completado: 5 fases, 13 planos, incrementais | Active |
| Manter stack atual (Python/PyQt6/plugins) | Evita ruptura em fase de estabilizacao | ✅ Preservado: Stack estavel, consolidado | Active |
| Estabelecer baseline de testes antes de refatoracoes | Detectar regressoes; validar migracao | ✅ Completado: 202 tests + 98 critical-path | Active |
| Core module ownership pattern para estado/sinais | Eliminar duplicidade; reduzir coupling | ✅ Implementado: SessionState, SignalHub centralizados | Active |
| Decimal phase numbering para insercoes urgentes | Suporte para hotfixes post-launch | ℹ️ Padrão disponivel; nao necessario v1.0 | Ready |

## Evolution

Document evolved at v1.0 completion (2026-04-04).

**Milestones tracked in .planning/ROADMAP.md and .planning/milestones/**

**For next milestone (v1.1):**
1. Run '/gsd-new-milestone' to start requirements planning
2. Define v1.1 scope (enhancements vs v2.0 features)
3. Update this document at v1.1 transition points

---
*Last updated: 2026-04-04 after v1.0 completion*
*Archive: See .planning/milestones/v1.0-* for detailed v1.0 phase and requirement information*
