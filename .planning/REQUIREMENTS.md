# Requirements: Warp

**Defined:** 2026-03-31
**Core Value:** Manter um fluxo estavel de ingestao -> processamento -> visualizacao para usuarios tecnicos sem regressao operacional.

## v1 Requirements

### UI Consolidation

- [ ] **UICO-01**: Usuario opera os fluxos criticos apenas pela camada `ui/`, sem dependencia de runtime da camada `desktop/`.
- [ ] **UICO-02**: Usuario executa startup da aplicacao por um launcher canonico unico e documentado.
- [ ] **UICO-03**: Usuario conclui os fluxos principais de analise sem regressao funcional em relacao ao comportamento vigente acordado.

### Duplicate Elimination

- [ ] **DEDU-01**: Equipe mantem uma unica implementacao canonica de main window ativa em producao.
- [ ] **DEDU-02**: Equipe centraliza estado/sinal em ownership unico no core, removendo duplicidade operacional.
- [ ] **DEDU-03**: Equipe remove scripts/entrypoints redundantes ou workaround obsoleto apos prova de equivalencia funcional.

### Reliability And Testing

- [ ] **RELY-01**: Equipe executa baseline completo de testes automatizados com resultado rastreavel e repetivel.
- [ ] **RELY-02**: Equipe aplica gates de regressao para impedir remocao de codigo sem cobertura minima dos fluxos criticos.
- [ ] **RELY-03**: Equipe valida que suites essenciais cobrem startup, carga de dados, processamento principal e visualizacao.

### Performance Safety

- [ ] **PERF-01**: Usuario nao observa degradacao relevante de startup apos cada onda de consolidacao.
- [ ] **PERF-02**: Usuario nao observa aumento relevante de uso de memoria nos cenarios principais apos refatoracoes.
- [ ] **PERF-03**: Equipe mede e compara indicadores de performance/memoria antes e depois de cada onda.

## v2 Requirements

### Product Enhancements

- **PROD-01**: Usuario recebe novas funcionalidades de produto alem do escopo de estabilizacao.
- **PROD-02**: Usuario recebe redesign visual amplo da interface.

### Deep Platform Changes

- **PLAT-01**: Equipe executa refatoracao ampla do engine de processamento.
- **PLAT-02**: Equipe redesenha a API local FastAPI com mudancas significativas de comportamento.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Novas features de produto | Objetivo desta iniciativa e estabilizacao/migracao, nao expansao funcional |
| Refatoracao ampla do processing engine | Alto risco ao core value nesta etapa |
| Redesign visual profundo | Nao necessario para eliminar divida tecnica critica atual |
| Redesenho amplo da API FastAPI | Manter compatibilidade e reduzir risco sistemico |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| UICO-01 | Phase 2 | Pending |
| UICO-02 | Phase 2 | Pending |
| UICO-03 | Phase 3 | Pending |
| DEDU-01 | Phase 3 | Pending |
| DEDU-02 | Phase 3 | Pending |
| DEDU-03 | Phase 4 | Pending |
| RELY-01 | Phase 1 | Pending |
| RELY-02 | Phase 1 | Pending |
| RELY-03 | Phase 5 | Pending |
| PERF-01 | Phase 5 | Pending |
| PERF-02 | Phase 5 | Pending |
| PERF-03 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-31*
*Last updated: 2026-03-31 after roadmap creation*