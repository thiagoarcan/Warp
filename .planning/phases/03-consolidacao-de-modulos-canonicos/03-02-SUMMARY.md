---
phase: 03-consolidacao-de-modulos-canonicos
plan: 02
subsystem: main-window
tags: [main-window, wrappers, entrypoints, canonical-module]
requires: []
provides:
  - Legacy main window modules converted to compatibility wrappers
  - UI and desktop app entrypoints aligned to canonical unified main window module
  - Circular-import safety for desktop package export path
affects: [startup, ui-runtime, navigation-tests]
tech-stack:
  added: []
  patterns: [single-canonical-main-window, lazy-import-guard]
key-files:
  created: []
  modified:
    - platform_base/src/platform_base/ui/main_window_old.py
    - platform_base/src/platform_base/desktop/main_window.py
    - platform_base/src/platform_base/ui/app.py
    - platform_base/src/platform_base/desktop/app.py
    - platform_base/src/platform_base/desktop/__init__.py
key-decisions:
  - "Keep ui/main_window_unified.py as the only implementation body"
  - "Use lazy import in desktop package export path to prevent circular initialization"
patterns-established:
  - "Legacy main window modules expose re-exports only"
  - "Entry points resolve canonical implementation from ui.main_window_unified"
requirements-completed: [DEDU-01]
duration: 40min
completed: 2026-04-03
---

# Phase 03 Plan 02 Summary

Main window duplication was removed by turning legacy modules into wrappers and aligning app entrypoints to the canonical unified module.

## Verification

- Command: `cd platform_base && python -m pytest tests/automated/test_03_navigation.py -q --tb=short`
- Result: `20 passed, 10 skipped, 0 failed`
- Command: `cd platform_base && python scripts/validate_all.py`
- Result: `98 passed, 21 skipped, 0 failed` and baseline capture exit 0

## Task Commits

1. Task 1 (wrapper modules): `f56fd2c`
2. Task 2 (entrypoints): `29f2e57`

## Files Modified

- `platform_base/src/platform_base/ui/main_window_old.py`
- `platform_base/src/platform_base/desktop/main_window.py`
- `platform_base/src/platform_base/ui/app.py`
- `platform_base/src/platform_base/desktop/app.py`
- `platform_base/src/platform_base/desktop/__init__.py`

## Deviations from Plan

### [Rule 1 - Bug] Circular import during canonical main window import

- Found during: Task 2 verification (`import platform_base.ui.main_window_unified`)
- Issue: `desktop.__init__` eagerly imported `desktop.main_window`, which now re-exported from `ui.main_window_unified`, causing circular initialization.
- Fix: Added lazy `MainWindow` export through `__getattr__` in `platform_base/src/platform_base/desktop/__init__.py`.
- Verification: direct import check succeeded and `test_03_navigation` passed.
- Commit hash: `29f2e57`

Total deviations: 1 auto-fixed (Rule 1).
