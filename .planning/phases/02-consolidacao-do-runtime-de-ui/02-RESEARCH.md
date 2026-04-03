# Phase 2 Research: Consolidacao do Runtime de UI

**Date:** 2026-04-03
**Phase requirements:** UICO-01, UICO-02

## Research Question

What needs to change so startup and critical flows are truly routed through the UI layer, with a single canonical launcher and no mandatory desktop runtime dependency?

## Findings

### 1. The current startup path is split between UI and desktop entrypoints

- `platform_base/launch_app.py` already uses `platform_base.ui.main_window_unified.ModernMainWindow`, but still depends on `platform_base.desktop.session_state.SessionState` and `platform_base.desktop.signal_hub.SignalHub`.
- `platform_base/run_app.py` still imports `platform_base.desktop.app.main`, creating a second startup path.
- This violates the intent of UICO-02 (single canonical launcher) and keeps ambiguity for operators.

### 2. The unified window still imports desktop widgets directly

- `platform_base/src/platform_base/ui/main_window_unified.py` imports:
  - `platform_base.desktop.widgets.data_panel.DataPanel`
  - `platform_base.desktop.widgets.viz_panel.VizPanel`
  - `platform_base.desktop.widgets.config_panel.ConfigPanel`
  - `platform_base.desktop.widgets.results_panel.ResultsPanel`
  - desktop dialogs (`about_dialog`, `settings_dialog`, `upload_dialog`)
- The `ui/panels/` package already contains modern equivalents (`ConfigPanel`, `ResultsPanel`, `StreamingPanel`) and near-equivalents (`CompactDataPanel`, `ModernVizPanel`).
- This indicates the migration can be done by adding compatibility exports in `ui/panels/` and then swapping imports in `main_window_unified.py`.

### 3. Tests still validate desktop runtime as canonical in critical initialization checks

- `platform_base/tests/automated/test_05_initialization.py` imports `platform_base.desktop.app.PlatformApplication`.
- `TestPanelsInit` in the same file parametrizes modules under `platform_base.desktop.widgets.*`.
- If unchanged, tests will preserve desktop runtime as required behavior and block UICO-01 completion.

### 4. Existing reliability baseline can be reused as migration safety net

- `platform_base/scripts/validate_all.py` already gates a critical subset including:
  - `test_01_ui_loading.py`
  - `test_03_navigation.py`
  - `test_04_signals_slots.py`
  - `test_05_initialization.py`
  - `test_09_exceptions_errors.py`
- This allows phased migration with immediate regression detection after each plan.

## Recommended Planning Direction

1. Establish the canonical startup contract first:
   - Keep `launch_app.py` as canonical launcher.
   - Convert `run_app.py` into a compatibility wrapper that delegates to `launch_app.main()` and logs deprecation guidance.
2. Create UI-layer compatibility exports so `main_window_unified.py` can stop importing `desktop.widgets.*` directly.
3. Migrate initialization/smoke tests to validate UI runtime imports (not desktop runtime imports), then run the existing baseline gate.
4. Update operational docs to point only to canonical launcher flow.

## Exact Commands To Anchor The Phase

### Canonical launcher smoke

`cd platform_base && python launch_app.py`

### Compatibility wrapper smoke

`cd platform_base && python run_app.py`

### Critical-path gate

`cd platform_base && python scripts/validate_all.py`

### Full automated baseline

`cd platform_base && python scripts/run_tests.py --verbose`

## Risks

- `ui.panels` currently has naming mismatches (`CompactDataPanel`, `ModernVizPanel`) relative to existing imports (`DataPanel`, `VizPanel`). A compatibility alias layer is required to avoid broad refactors.
- `ui.signal_hub.SignalHub` API differs from `desktop.signal_hub.SignalHub`; this phase should avoid simultaneous API migration unless required by failing tests.
- Hidden references to `desktop.app` in debug scripts can reintroduce non-canonical startup if not updated.

## Validation Architecture

- After each task: run `cd platform_base && python scripts/validate_all.py`.
- After each wave: run `cd platform_base && python scripts/run_tests.py --verbose`.
- Canonical-launcher assertion for this phase:
  - `run_app.py` delegates to `launch_app.main()`
  - docs reference `launch_app.py` as canonical path
  - `test_05_initialization.py` validates `platform_base.ui.app.PlatformApplication`

## Planning Implications

- This phase should be planned in 3 plans:
  - Plan 01 (Wave 1): Canonical launcher consolidation (UICO-02).
  - Plan 02 (Wave 1): UI runtime compatibility exports for panel imports (UICO-01).
  - Plan 03 (Wave 2): Main window import migration + critical test migration + smoke verification (UICO-01/UICO-02).
- Wave 2 depends on both Wave 1 plans to avoid merge conflicts and to keep verification targeted.
