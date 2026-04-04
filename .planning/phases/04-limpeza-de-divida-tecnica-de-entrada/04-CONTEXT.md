# Phase 4: Limpeza de Divida Tecnica de Entrada - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning/execution
**Mode:** Auto-generated (autonomous flow)

<domain>
## Phase Boundary

Eliminar launchers/workarounds redundantes apos prova de equivalencia das fases 2-3, mantendo caminho canonico de execucao em `launch_app.py`.

</domain>

<decisions>
## Implementation Decisions

### Entrypoints
- `launch_app.py` permanece como launcher canonico.
- `run_app.py` permanece temporariamente como wrapper de compatibilidade, com status deprecated.

### Limpeza de Legado
- `debug_launch.py`, `fixed_launch.py` e `test_launch.py` saem da raiz operacional e vao para `_deprecated/`.
- Scripts legados arquivados recebem cabecalho DEPRECATED.

### the agent's Discretion
Detalhes de formato de mensagem, organização de seções e redação de avisos de depreciação ficam a critério do agente.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `launch_app.py` já usado como caminho principal validado.
- Suite em `tests/automated/` cobre startup, navegação e inicialização.

### Established Patterns
- Wrapper de compatibilidade para não quebrar chamadas antigas.
- Validação por `pytest` focado em gates críticos.

### Integration Points
- `run_app.py` delega para `launch_app.main()`.
- Documentação operacional em `platform_base/README.md`.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None.

</deferred>
