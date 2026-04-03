# Phase 3 Research: Consolidacao de Modulos Canonicos

**Date:** 2026-04-03
**Phase requirements:** DEDU-01, DEDU-02, UICO-03

## Research Question

How can we eliminate structural duplication in main window and session/signal ownership while keeping runtime behavior stable after Phase 2?

## Findings

### 1. Main window logic is still duplicated across UI and desktop modules

- Active files:
  - `platform_base/src/platform_base/ui/main_window_unified.py` (current production path used by `launch_app.py`)
  - `platform_base/src/platform_base/ui/main_window_old.py` (full legacy implementation)
  - `platform_base/src/platform_base/desktop/main_window.py` (full legacy implementation)
- `platform_base/src/platform_base/ui/main_window.py` already re-exports unified symbols, but other duplicate modules still contain full implementations.
- This keeps DEDU-01 open because there is not a single canonical implementation with compatibility wrappers only.

### 2. Session/signal ownership is inverted relative to intent

- Current behavior:
  - `platform_base/src/platform_base/core/session_state.py` re-exports from desktop module.
  - `platform_base/src/platform_base/core/signal_hub.py` re-exports from desktop module.
  - `launch_app.py` imports `SessionState` and `SignalHub` from `platform_base.desktop.*`.
- Expected for DEDU-02:
  - `core` must become source of truth.
  - `desktop` should become compatibility wrapper.

### 3. Test and fixture imports still pin desktop ownership

- Found references in:
  - `platform_base/tests/automated/conftest.py`
  - `platform_base/tests/fixtures/qt_fixtures.py`
  - multiple legacy tests under `tests/_legacy/`
- Automated gates already emphasize modern tests (`validate_all.py`), so migration should prioritize non-legacy paths and keep legacy imports backwards-compatible.

### 4. Existing Phase 2 patterns should be reused

- Canonical path + compatibility wrapper approach worked for launchers and panels.
- Incremental wave strategy with `validate_all.py` proved stable.
- For this phase, apply the same pattern to main window and session/signal modules.

## Recommended Planning Direction

1. Canonicalize ownership first (core session/signal as source, desktop as wrapper).
2. Canonicalize main window implementation second (unified is source, legacy modules become wrappers).
3. Migrate critical runtime/test imports to canonical modules and run full baseline gates.

## Validation Architecture

- After each task: `cd platform_base && python -m pytest tests/automated/test_03_navigation.py tests/automated/test_05_initialization.py -q --tb=short`
- After each wave: `cd platform_base && python scripts/validate_all.py`
- Final confirmation: `cd platform_base && python scripts/run_tests.py --verbose`

## Risks

- Legacy tests and scripts may rely on concrete class names from desktop modules.
- Constructor contracts (`SessionState(dataset_store)` and `MainWindow(session_state, signal_hub)`) must remain unchanged while ownership changes.
- UI components with incomplete `.ui` wiring (ex. ConfigPanel) can surface unrelated noise; keep skip semantics already adopted in Phase 2.

## Planning Implications

- Plan 03-01 (Wave 1): canonical ownership of `SessionState` and `SignalHub` in core.
- Plan 03-02 (Wave 1): canonical main window implementation (`ui/main_window_unified.py`) with wrappers for legacy modules.
- Plan 03-03 (Wave 2): migrate critical imports (launchers/tests/fixtures) to canonical modules and verify no regression.
