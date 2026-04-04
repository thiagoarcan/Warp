---
phase: 04-limpeza-de-divida-tecnica-de-entrada
plan: 01
subsystem: launcher-cleanup
tags: [cleanup, launchers, deprecation, canonical-entrypoint]
requires: []
provides:
  - Legacy launchers archived under _deprecated
  - Canonical launcher path preserved
affects: [developer-ux, startup, docs]
key-files:
  modified:
    - platform_base/debug_launch.py
    - platform_base/fixed_launch.py
    - platform_base/_deprecated/debug_launch.py
    - platform_base/_deprecated/fixed_launch.py
requirements-completed: [DEDU-03]
completed: 2026-04-04
---

# Phase 04 Plan 01 Summary

Arquivados os launchers históricos de workaround (`debug_launch.py` e `fixed_launch.py`) para `_deprecated/`, preservando apenas o caminho canonico operacional com `launch_app.py`.

## Verification

- `python -m pytest tests/automated/test_01_ui_loading.py tests/automated/test_03_navigation.py -q --tb=short`
- Resultado (execução combinada com Plan 02): testes verdes dentro do esperado (pass + skips conhecidos).
