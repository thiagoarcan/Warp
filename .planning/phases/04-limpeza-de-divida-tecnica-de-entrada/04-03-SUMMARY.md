---
phase: 04-limpeza-de-divida-tecnica-de-entrada
plan: 03
subsystem: docs-entrypoint
tags: [docs, deprecation, compatibility]
requires: [04-01, 04-02]
provides:
  - run_app marked deprecated while preserving compatibility
  - README points to canonical launcher
affects: [docs, startup]
key-files:
  modified:
    - platform_base/run_app.py
    - platform_base/README.md
requirements-completed: [DEDU-03]
completed: 2026-04-04
---

# Phase 04 Plan 03 Summary

`run_app.py` foi mantido como wrapper de compatibilidade, com aviso explícito de depreciação. A documentação passou a indicar `launch_app.py` como entrypoint canonico.

## Verification

- `python -c "from launch_app import main as launch_main; print('launch ok')"`
- `python -c "from run_app import main as run_main; print('run wrapper ok')"`
- Comportamento de delegação preservado.
