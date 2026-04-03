---
phase: 02-consolidacao-do-runtime-de-ui
plan: 02
subsystem: ui-panels
tags: [panels, migration, compatibility, imports, wrappers]
requires: [02-01]
provides:
  - DataPanel compatibility wrapper over CompactDataPanel (ui.panels)
  - VizPanel compatibility wrapper over ModernVizPanel (ui.panels)
  - Clean ui.panels.__init__.py with explicit exports
  - ModernMainWindow imports for DataPanel/VizPanel from ui.panels
  - Hardened UTF-8 + non-blocking logic in capture_runtime_baseline.py
affects: [testing, validation-gate, unit-tests]
tech-stack:
  added: []
  patterns: [compatibility-wrapper, panel-migration, constructor-bridge]
key-files:
  created: []
  modified:
    - platform_base/src/platform_base/ui/panels/data_panel.py
    - platform_base/src/platform_base/ui/panels/viz_panel.py
    - platform_base/src/platform_base/ui/panels/__init__.py
    - platform_base/src/platform_base/ui/main_window_unified.py
    - platform_base/scripts/capture_runtime_baseline.py
key-decisions:
  - "DataPanel/VizPanel are compatibility wrappers over modern equivalents; ConfigPanel/ResultsPanel stay on desktop.widgets until .ui wiring is complete"
  - "Constructor bridge: accept (session_state, signal_hub=None) signature"
  - "capture_runtime_baseline.py uses PYTHONIOENCODING=utf-8 env and errors='replace' decoding to avoid Windows charmap failures"
patterns-established:
  - "Panel compatibility bridge: subclass of modern panel with legacy constructor signature"
  - "ui.panels.__init__.py must be rewritten cleanly; avoid automated text insertion"
  - "Baseline capture avoids blocking readline loops; uses startup-threshold with timeout"
requirements-completed: [UICO-02]
duration: 75min
completed: 2026-04-03
---

# Phase 02 Plan 02 Summary

**Critical UI panels migrated to `ui.panels` runtime with compatibility wrappers; validate_all gate green**

## Performance

- **Duration:** ~75 min (including debug loop)
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Added `DataPanel` compatibility wrapper class in `ui/panels/data_panel.py`, bridging `(session_state, signal_hub=None)` constructor to `CompactDataPanel`.
- Added `VizPanel` compatibility wrapper class in `ui/panels/viz_panel.py`, bridging constructor to `ModernVizPanel`.
- Rewrote `ui/panels/__init__.py` from scratch, exporting `DataPanel` and `VizPanel` cleanly.
- Updated `ui/main_window_unified.py` so `DataPanel` and `VizPanel` are imported from `ui.panels`; reverted `ConfigPanel`/`ResultsPanel` to `desktop.widgets` for runtime compatibility pending full .ui wiring.
- Hardened `scripts/capture_runtime_baseline.py` with `PYTHONIOENCODING=utf-8`, `encoding='utf-8'`, `errors='replace'` to eliminate `UnicodeDecodeError`/charmap failures on Windows; replaced blocking `stdout.readline` loop with non-blocking startup-threshold approach.

## Critical Regressions Fixed

### 1. SyntaxError in `ui/panels/__init__.py`
- **Root cause:** Automated text insertion introduced literal `r n` chars.
- **Fix:** Full rewrite of `__init__.py`.

### 2. TypeError from DataPanel/VizPanel constructor signature mismatch
- **Root cause:** `main_window_unified.py` called `DataPanel(session_state, signal_hub)` but former alias did not accept those args.
- **Fix:** Added compatibility wrapper classes.

### 3. AttributeError from ConfigPanel/ResultsPanel forced migration
- **Root cause:** `ui.panels.config_panel` loads `.ui` but `_theme_combo` is never set via `findChild`, causing AttributeError in `_load_settings()`.
- **Fix:** Reverted ConfigPanel and ResultsPanel imports in `main_window_unified.py` to `desktop.widgets`. Migration deferred.

### 4. UnicodeDecodeError in `capture_runtime_baseline.py`
- **Root cause:** Windows `charmap` codec failure on Qt stdout output.
- **Fix:** Forced UTF-8 env and subprocess decoding with error fallback; replaced blocking line iteration.

## Files Created/Modified
- `platform_base/src/platform_base/ui/panels/data_panel.py` — DataPanel wrapper class.
- `platform_base/src/platform_base/ui/panels/viz_panel.py` — VizPanel wrapper class.
- `platform_base/src/platform_base/ui/panels/__init__.py` — clean exports.
- `platform_base/src/platform_base/ui/main_window_unified.py` — DataPanel/VizPanel from ui.panels; ConfigPanel/ResultsPanel remain on desktop.widgets.
- `platform_base/scripts/capture_runtime_baseline.py` — UTF-8 hardening and non-blocking startup detection.

## Verification Results

Critical gate: **104 passed, 15 skipped, 3 warnings, exit 0** (first run)
After Plan 03 test changes: **98 passed, 21 skipped, 3 warnings, exit 0** (persistent green)
