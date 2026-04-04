# Roadmap: Warp

**Created:** 2026-03-31
**Granularity:** Standard
**Execution:** Parallel where independent

## Summary

- Phases: 5
- v1 requirements: 12
- Coverage: 12/12 (100%)

## Phase Table

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Baseline de Qualidade e Seguranca de Mudanca | Criar base confiavel de validacao funcional e performance para reduzir risco de refatoracao | RELY-01, RELY-02, PERF-03 | 4 |
| 2 | Consolidacao do Runtime de UI | Tornar \ui/\ o caminho operacional canonico com launcher unico | UICO-01, UICO-02 | 4 |
| 3 | Consolidacao de Modulos Canonicos | Remover duplicacoes estruturais em janela principal e ownership de estado/sinal | DEDU-01, DEDU-02, UICO-03 | 4 |
| 4 | Limpeza de Divida Tecnica de Entrada | Eliminar launchers/workarounds redundantes apos prova de equivalencia | DEDU-03 | 3 |
| 5 | Hardening Final de Confiabilidade e Performance | Fechar lacunas de cobertura essencial e comprovar nao regressao de startup/memoria | RELY-03, PERF-01, PERF-02 | 4 |

## Phase Details

## Phase 1: Baseline de Qualidade e Seguranca de Mudanca

**Status:** passed (2026-04-03) — 2/2 planos completos, 4/4 critérios verificados

Goal: Criar base confiavel de validacao funcional e performance para reduzir risco de refatoracao.

Requirements:
- RELY-01 ✓
- RELY-02 ✓
- PERF-03 ✓

Success criteria:
1. ✓ Existe pipeline/rotina reproduzivel para execucao completa de testes automatizados com evidencia de resultado.
2. ✓ Existe gate minimo de regressao para impedir remocoes sem cobertura dos fluxos criticos.
3. ✓ Baseline inicial de startup e memoria foi capturado para comparacao de ondas. (startup_detected=true, 11.56s)
4. ✓ O time consegue repetir a validacao local com resultados consistentes.

## Phase 2: Consolidacao do Runtime de UI

**Status:** executed (2026-04-03) — 3/3 planos completos, 4/4 critérios verificados

Goal: Tornar \ui/\ o caminho operacional canonico com launcher unico.

Requirements:
- UICO-01 ✓
- UICO-02 ✓

Success criteria:
1. ✓ Fluxo de inicializacao principal passa por caminho unico definido e documentado.
2. ✓ Fluxos criticos operacionais executam sem runtime obrigatorio da camada \desktop/\.
3. ✓ Smoke tests de startup e fluxo basico validam o caminho canonico.
4. ✓ Plano de deprecacao do caminho antigo esta declarado sem interromper operacao.

Plans:
- [x] 02-01-PLAN.md
- [x] 02-02-PLAN.md
- [x] 02-03-PLAN.md

## Phase 3: Consolidacao de Modulos Canonicos

**Status:** executed (2026-04-03) — 3/3 planos completos, 4/4 critérios verificados

Goal: Remover duplicacoes estruturais em janela principal e ownership de estado/sinal.

Requirements:
- DEDU-01 ✓
- DEDU-02 ✓
- UICO-03 ✓

Success criteria:
1. ✓ Existe apenas uma implementacao canonica de main window em uso de producao.
2. ✓ Ownership de signal/session esta centralizado no local definido como fonte da verdade.
3. ✓ Fluxos funcionais acordados mantem comportamento esperado apos consolidacao.
4. ✓ Mudancas foram validadas por testes/smokes definidos no baseline.

Plans:
- [x] 03-01-PLAN.md
- [x] 03-02-PLAN.md
- [x] 03-03-PLAN.md

## Phase 4: Limpeza de Divida Tecnica de Entrada

**Status:** planned (2026-04-04) — plans criados, pronto para execucao

Goal: Eliminar launchers/workarounds redundantes apos prova de equivalencia.

Requirements:
- DEDU-03

Success criteria:
1. Scripts/entrypoints redundantes foram removidos ou marcados como obsoletos de forma segura.
2. Qualquer workaround legado removido possui substituicao validada na fonte canonica.
3. Documentacao de execucao aponta apenas para caminho suportado.

Plans:
- [ ] 04-01-PLAN.md — Arquivar/remover debug_launch.py e fixed_launch.py historicos [Wave 1]
- [ ] 04-02-PLAN.md — Deprecate test_launch.py; migrar para pytest fixtures padrao [Wave 1]
- [ ] 04-03-PLAN.md — Marcar run_app.py como deprecated; atualizar documentacao [Wave 2]

## Phase 5: Hardening Final de Confiabilidade e Performance

**Status:** pending — pronto para planejamento apos Fase 4

Goal: Fechar lacunas de cobertura essencial e comprovar nao regressao de startup/memoria.

Requirements:
- RELY-03
- PERF-01
- PERF-02

Success criteria:
1. Suites essenciais cobrem startup, carga de dados, processamento e visualizacao com rastreabilidade.
2. Indicadores de startup permanecem dentro do limite aceito frente ao baseline.
3. Indicadores de memoria permanecem dentro do limite aceito frente ao baseline.
4. Relatorio final de estabilidade confirma aptidao para continuidade da evolucao.

## Coverage Validation

| Requirement | Phase |
|-------------|-------|
| UICO-01 | Phase 2 |
| UICO-02 | Phase 2 |
| UICO-03 | Phase 3 |
| DEDU-01 | Phase 3 |
| DEDU-02 | Phase 3 |
| DEDU-03 | Phase 4 |
| RELY-01 | Phase 1 |
| RELY-02 | Phase 1 |
| RELY-03 | Phase 5 |
| PERF-01 | Phase 5 |
| PERF-02 | Phase 5 |
| PERF-03 | Phase 1 |

All v1 requirements mapped exactly once: yes.
