# Codebase Concerns

**Analysis Date:** 2026-03-31

> Sources consulted: `DIAGNOSTICO_APLICACOES.md` (2026-02-25), `platform_base/docs/TROUBLESHOOTING.md`,
> `platform_base/pyproject.toml`, `platform_base/README.md`, `platform_base/test_run_results.txt`,
> direct file-system inspection of all modules, scripts, tests, and docs.

---

## Critical Issues

**Incomplete UI Stack Migration (Dual Active UI Layers):**
- Issue: Two parallel UI implementations coexist and are both actively maintained.
  - Legacy layer: `platform_base/src/platform_base/desktop/` — `app.py`, `main_window.py`, `session_state.py`, `signal_hub.py`, full `widgets/`, `dialogs/`, `menus/`, `selection/`, `workers/` subtrees.
  - Current layer: `platform_base/src/platform_base/ui/` — `app.py`, `main_window.py`, `main_window_unified.py`, `main_window_old.py`, `themes.py`, `accessibility.py`, `shortcuts.py`, `tooltips.py`, `multi_view_sync.py`, `undo_redo.py`, `panels/`, `export.py`, `video_export.py`.
- Evidence: `platform_base/docs/UI_MIGRATION.md`; migration scripts `platform_base/scripts/migrate_to_ui.py`, `platform_base/scripts/auto_migrate_ui.py`, `platform_base/scripts/validate_ui_migration.py`; `platform_base/docs/reports/MIGRATION_STATUS.md`.
- Impact: Feature changes must be applied to both stacks until migration completes. Bugs may be fixed in one layer and remain in the other.
- Fix approach: Complete migration to `ui/` layer; remove entire `desktop/` subtree.

**Three Versions of Main Window in Active Use:**
- Issue: `platform_base/src/platform_base/ui/main_window.py` (70.3 KB), `main_window_old.py` (58.6 KB), and `main_window_unified.py` (78.6 KB) all exist under `ui/`. `DIAGNOSTICO_APLICACOES.md` detected both `main_window_old` and `main_window_unified` as live entry points.
- Files: `platform_base/src/platform_base/ui/main_window.py`, `platform_base/src/platform_base/ui/main_window_old.py`, `platform_base/src/platform_base/ui/main_window_unified.py`
- Impact: Developers cannot determine which implementation is canonical. Changes made to one are not reflected in others. Test coverage uncertain.
- Fix approach: Designate `main_window_unified.py` as canonical; delete `main_window.py` and `main_window_old.py`; update all imports.

**Spacer Layout Bug Unresolved in Source:**
- Issue: Root-level scripts `platform_base/fix_spacers.py` and `platform_base/check_spacers.py` exist to detect and patch a UI spacer bug. Workaround launcher `platform_base/fixed_launch.py` was added rather than fixing the root cause.
- Files: `platform_base/fix_spacers.py`, `platform_base/check_spacers.py`, `platform_base/fixed_launch.py`
- Impact: Root cause lives in Qt widget layout code; workaround scripts mask it. New UI changes may reintroduce the bug silently.
- Fix approach: Identify the specific widget or `.ui` file generating broken spacers; fix in source; remove the three workaround scripts.

**Test Run Not Fully Validated:**
- Issue: `platform_base/test_run_results.txt` shows `collected 231 items` but the file contains only the first two test file results. The test run was interrupted or failed mid-run.
- Files: `platform_base/test_run_results.txt`
- Impact: No confirmed passing baseline for the automated suite.
- Fix approach: Run `pytest tests/automated/` fully and record a clean pass before any new feature work.

---

## Technical Debt

**Proliferated Root-Level Entry Points (12 Detected):**
- Issue: `DIAGNOSTICO_APLICACOES.md` detected 12 entry points, including 6+ ad-hoc launchers at root: `launch_app.py`, `run_app.py`, `fixed_launch.py`, `debug_launch.py`, `test_launch.py`, `visual_test.py`, `simple_test.py`.
- Impact: Canonical launch path unclear; `fixed_launch.py` is a workaround; informal tests not in pytest.
- Fix approach: Single production launcher; delete `fixed_launch.py` after spacer fix; promote informal tests to `tests/` or delete.

**Duplicated Core Modules (desktop/ vs core/):**
- Issue: Signal hub and session state are implemented in both the core and desktop layers:
  - `platform_base/src/platform_base/core/signal_hub.py` vs `platform_base/src/platform_base/desktop/signal_hub.py`
  - `platform_base/src/platform_base/core/session_state.py` vs `platform_base/src/platform_base/desktop/session_state.py`
- Impact: Authoritative implementation unclear; changes must be applied twice; divergence causes state bugs.
- Fix approach: Consolidate to core layer; delete desktop-layer duplicates as part of UI migration.

**Split Config System (Two Sources + Two Managers):**
- Issue: Config split across `platform_base/configs/platform.yaml` and `platform_base/.platform_config/system/platform.yaml` / `.platform_config/user/default.yaml`. Two manager classes: `platform_base/src/platform_base/core/config.py` and `platform_base/src/platform_base/core/config_manager.py`.
- Impact: Unclear which file wins on conflict; adding a setting requires updating multiple locations.
- Fix approach: Single config manager with explicit precedence chain (system < user < runtime).

**Multiple YAML Parsing Libraries:**
- Issue: Both `PyYAML` and `ruamel.yaml` are dependencies, used inconsistently for the same config files.
- Files: `platform_base/src/platform_base/core/config.py`, `platform_base/src/platform_base/core/config_manager.py`
- Fix approach: Standardize on one library; use `ruamel.yaml` only where round-trip comment preservation is needed.

**No Dependency Lockfile:**
- Issue: Project relies on Anaconda `base` environment with no `conda-lock`, `pixi`, or `requirements.txt` lockfile.
- Files: `platform_base/pyproject.toml` (only loose version ranges declared)
- Impact: Environment not reproducible; transitive updates can silently break the application.
- Fix approach: Generate `conda-lock.yml` or adopt `pixi` for deterministic environments.

**Overly Broad Ruff Ruleset with Excessive Suppressions:**
- Issue: `platform_base/pyproject.toml` enables 40+ ruff rule groups including `DJ` (Django) despite no Django usage. 60+ rules are ignored — including `BLE001` (blind except), `PLR0912` (too many branches), `PLR0915` (too many statements), `ERA001` (commented-out code).
- Impact: Linting provides false confidence; widely-suppressed rules mask real code quality issues.
- Fix approach: Remove `DJ` group; enable only rules with zero suppressions; incrementally clean code.

**Docs/Reports Directory Accumulation (27+ Files):**
- Issue: `platform_base/docs/reports/` contains 27+ accumulated report files including multiple superseded TODO lists, debugging sessions, and sprint audits.
- Impact: Developers may find outdated task information; maintenance overhead.
- Fix approach: Archive completed reports; consolidate active TODOs into `.planning/`.

---

## Known Bugs

**Spacer Layout Bug (Confirmed, Root Cause Unaddressed):**
- Symptoms: Qt layout spacers render incorrectly in one or more dialogs/panels.
- Files: `platform_base/fix_spacers.py`, `platform_base/check_spacers.py`, `platform_base/fixed_launch.py`
- Trigger: Application launch via normal `launch_app.py`.
- Workaround: Use `platform_base/fixed_launch.py` or pre-run `fix_spacers.py`.

**Segmentation Fault on Startup (Driver-Related):**
- Symptoms: `Segmentation fault (core dumped)` on Linux/macOS, documented in `TROUBLESHOOTING.md`.
- Trigger: Outdated graphics drivers or broken OpenGL context.
- Workaround: `export QT_QPA_PLATFORM=offscreen`; update GPU drivers.
- Root cause: No automatic software rendering fallback.

**Memory Usage Grows Continuously:**
- Symptoms: RAM increases over time; application slows and eventually crashes. Documented in `TROUBLESHOOTING.md` as requiring periodic restart.
- Files: `platform_base/src/platform_base/core/memory_manager.py`
- Trigger: Opening many series tabs without closing; large undo history accumulation.
- Workaround: Manually clear undo history; restart periodically.

**3D Visualization Fails Without Optional VTK:**
- Symptoms: `"VTK not available"` error or blank 3D window. Documented in `TROUBLESHOOTING.md`.
- Files: `platform_base/src/platform_base/viz/figures_3d.py`
- Trigger: Opening 3D chart without `pip install -e ".[viz]"`.
- Root cause: VTK is in optional extras but no clear error message guides users to install it.

**CSV Export Corruption on Encoding Mismatch:**
- Symptoms: Exported CSV contains garbage characters or fails to open in Excel. Documented in `TROUBLESHOOTING.md`.
- Trigger: Default UTF-8 without BOM vs. Excel's Latin-1 expectation on Windows.
- Workaround: Select UTF-8 BOM explicitly in export dialog.

**`.bak` Test Files Blocking Pytest Discovery:**
- Symptoms: Pytest may attempt to collect `.bak` files with broad glob patterns.
- Files: `platform_base/tests/_legacy/ui/test_data_panel_complete.py.bak`, `test_main_window_complete.py.bak`, `test_viz_panel_complete.py.bak`, `tests/_legacy/integration/test_integration_complete_old.py.bak`
- Workaround: Exclude via `pyproject.toml` `testpaths` or explicit pattern exclusions.

---

## Security Concerns

**subprocess.run for macOS Theme Detection:**
- Risk: `platform_base/src/platform_base/ui/themes.py` line 327 calls `subprocess.run(["defaults", "read", "-g", "AppleInterfaceStyle"], ...)`. Arguments are hardcoded literals — no shell injection risk. However, subprocess for OS detection is brittle compared to native APIs.
- Files: `platform_base/src/platform_base/ui/themes.py`
- Current mitigation: `check=False`, `capture_output=True`; wrapped in `try/except`; no `shell=True`.
- Recommendation: Replace with `ctypes`/`objc` macOS API to eliminate subprocess dependency.

**FastAPI REST Server Without Confirmed Authentication:**
- Risk: `platform_base/src/platform_base/api/server.py` starts a local HTTP server. If it binds to `0.0.0.0`, any host on the network can call API endpoints with no authentication.
- Files: `platform_base/src/platform_base/api/server.py`, `platform_base/src/platform_base/api/endpoints.py`
- Current mitigation: Not confirmed — security libraries (`bcrypt`, `cryptography`) present but no auth middleware visible.
- Recommendations: Ensure `host="127.0.0.1"` only; add API key or session-token validation.

**Pickle Deserialization for Session/Cache:**
- Risk: Deserializing pickled data from modified files (e.g., tampered session files on shared OneDrive) allows arbitrary code execution.
- Files: `platform_base/src/platform_base/caching/disk.py`, `platform_base/src/platform_base/core/session_state.py`
- Current mitigation: Internal use only; no network-sourced pickle apparent.
- Recommendations: Replace with `orjson`, `msgpack`, or Pydantic serialization; add HMAC signature for cache file integrity.

**User-Supplied Expression Evaluation (Custom Sandbox):**
- Risk: `platform_base/src/platform_base/utils/safe_eval.py` implements a custom Python expression sandbox. A flaw enables arbitrary Python injection.
- Files: `platform_base/src/platform_base/utils/safe_eval.py`
- Current mitigation: Dedicated sandboxed evaluator rather than raw `eval()`.
- Recommendations: Audit against known AST-escape techniques; prefer proven library (`numexpr`, `asteval`).

**Telemetry with Unclear Scope:**
- Risk: `platform_base/src/platform_base/analytics/telemetry.py` collects and presumably transmits usage data. Scope and destination are undocumented.
- Files: `platform_base/src/platform_base/analytics/telemetry.py`
- Recommendations: Document what is collected; provide opt-out; ensure no PII, file paths, or dataset content is included.

---

## Performance Issues

**Very Large Source Files (Maintenance and Load Concern):**
- Problem: Generated `operationsPanel_ui.py` (99.5 KB), `viz_panel.py` (89.7 KB); hand-written `main_window_unified.py` (78.6 KB), `main_window.py` (70.3 KB), `registry.py` (59.7 KB), `operations_panel.py` (54.7 KB), `data_panel.py` (53.8 KB).
- Files: `platform_base/src/platform_base/desktop/ui_files/operationsPanel_ui.py`, `platform_base/src/platform_base/desktop/widgets/viz_panel.py`, `platform_base/src/platform_base/ui/main_window_unified.py`
- Cause: No size discipline enforced; generated files include all widget initialization inline.
- Improvement path: Split oversized widgets into sub-components; lazy-initialize tab content.

**Multiple Visualization Backends Loaded at Import:**
- Problem: `matplotlib`, `PyVista` (VTK), and `pyqtgraph` are all in `[dependencies]`. Each carries significant import cost and memory even when unused.
- Files: `platform_base/src/platform_base/viz/figures_2d.py`, `platform_base/src/platform_base/viz/figures_3d.py`, `platform_base/src/platform_base/viz/heatmaps.py`
- Cause: No lazy-import pattern enforced at module boundaries.
- Improvement path: Move heavyweight backends to optional extras; lazy-load on first use.

**Downsampling Required for Interactive Render Performance:**
- Problem: Raw dataset sizes exceed interactive render capacity. LTTB downsampling threshold and algorithm must be correct at all render paths to preserve signal peaks.
- Files: `platform_base/src/platform_base/processing/downsampling.py`
- Cause: Industrial time-series at high sample rates can contain millions of points.
- Improvement path: Enforce LTTB at every 2D/heatmap render path; make threshold configurable; validate no peaks are dropped.

**Memory Growth Without Eviction Policy:**
- Problem: `platform_base/src/platform_base/core/memory_manager.py` and visible MemoryIndicator widget indicate memory is a user-facing concern. Datasets loaded without LRU eviction; undo history grows unbounded.
- Improvement path: Implement LRU eviction in `DatasetStore`; cap undo history depth; profile with `platform_base/src/platform_base/profiling/`.

**Profiling Artifacts Committed to Repository:**
- Problem: `platform_base/test_profiling/` contains 20+ `.prof` and `.txt` files from February 2026 committed to the repo.
- Impact: Repository bloat; stale performance data provides misleading baseline.
- Improvement path: Add `test_profiling/` to `.gitignore`; regenerate as CI artifacts.

---

## Incomplete Features

**UI Migration (desktop/ → ui/) Not Complete:**
- Problem: Both `desktop/` and `ui/` layers implement the full application. Documentation acknowledges the migration is in progress.
- Missing: All `desktop/` widgets, dialogs, menus, workers, and selection panels without a confirmed `ui/` counterpart.
- Blocks: UI feature work requires knowing which layer to modify; features may need to be implemented twice.
- Files: `platform_base/src/platform_base/desktop/`, `platform_base/src/platform_base/ui/`, `platform_base/scripts/migrate_to_ui.py`

**Spacer Fix Not Applied to Source:**
- Problem: Workaround `platform_base/fixed_launch.py` is in active use; proper fix never applied to widget source.
- Blocks: Using `launch_app.py` as canonical entry point.
- Files: `platform_base/fix_spacers.py`, `platform_base/check_spacers.py`, `platform_base/fixed_launch.py`

**Many `.ui` Files Are Still Placeholders:**
- Problem: Some `.ui` files are empty templates with ≤3 widgets. Loading them at runtime produces blank or non-functional widgets.
- Files: `platform_base/src/platform_base/desktop/ui_files/` (80+ generated `*_ui.py`), `platform_base/src/platform_base/ui/designer/`
- Fix approach: Run `python scripts/migrate_to_ui.py` to identify remaining placeholders; complete each form in Qt Designer.

**Plugin System with Minimal Built-in Plugins:**
- Problem: Full plugin infrastructure (registry, hooks, manifests) exists but only two plugins are present: `platform_base/plugins/dtw_plugin/` and `platform_base/plugins/advanced_sync/`.
- Impact: Infrastructure overhead with minimal return.

---

## Fragile Areas

**Generated UI File Pipeline (Must Stay in Sync):**
- Files: 80+ `*_ui.py` in `platform_base/src/platform_base/desktop/ui_files/`; `platform_base/scripts/compile_ui.py`, `platform_base/scripts/generate_ui_files.py`
- Why fragile: Any change to a `.ui` XML file requires re-running the compile script. Stale generated files cause silent widget reference mismatches at runtime.
- Safe modification: Always run `python scripts/compile_ui.py` after any `.ui` edit; verify with `scripts/validate_ui_files.py`.
- Test coverage: `platform_base/tests/automated/test_01_ui_loading.py` covers basic load only.

**Signal Hub (Global Event Bus):**
- Files: `platform_base/src/platform_base/core/signal_hub.py`, `platform_base/src/platform_base/desktop/signal_hub.py` (duplicate)
- Why fragile: All inter-component communication flows through the signal hub. An unhandled exception in a subscriber blocks all subsequent subscribers. Widgets must disconnect in `closeEvent`.
- Safe modification: Wrap all signal handlers in `try/except`; always disconnect in `closeEvent`; never emit during `__init__`.

**ZeroMQ Streaming Layer:**
- Files: `platform_base/src/platform_base/streaming/` (stream_filters, temporal_sync, controls)
- Why fragile: ZMQ sockets are stateful. Application crash without `socket.close()` / `context.term()` leaves the port bound; next launch fails to rebind.
- Safe modification: Manage ZMQ lifecycle in `try/finally`; test reconnection explicitly.
- Test coverage: `_legacy/unit/test_streaming_filters_complete.py` only — legacy, not in active automated suite.

**Downsampling Module (Safety-Relevant for Industrial Data):**
- Files: `platform_base/src/platform_base/processing/downsampling.py`
- Why fragile: Incorrect threshold or algorithm silently distorts industrial sensor peaks (PT/FT/TT readings). This is safety-relevant in pipeline monitoring.
- Safe modification: Validate max/min of downsampled series against original before display; never apply lossy downsampling to export data.
- Test coverage: `_legacy/unit/test_downsampling_complete.py` only — legacy, not in active automated suite.

**OneDrive Cloud-Only Storage of Entire Workspace:**
- Files: All files in `platform_base/` carry the `RecallOnOpen` filesystem attribute (cloud-only placeholders)
- Why fragile: When the OneDrive cloud provider is not running, ALL source files return `"O provedor do arquivo de nuvem não está em execução"`. This blocks IDEs, linters, test runners, and any shell-based tooling until OneDrive initializes.
- Impact: Development, CI, and editors fail with confusing IO errors. File content can change asynchronously if synced from another device concurrently.
- Recommendation: Pin `platform_base/src/` locally using `attrib -P -U`; configure OneDrive "Always keep on this device" for the project folder; or migrate source to a local drive with git remote as backup.

---

## Migration / Cleanup Needed

**`tests/_legacy/` — 100+ Legacy Test Files:**
- What: 11 subdirectories: `e2e/`, `functional/`, `gui/`, `integration/`, `performance/`, `property/`, `smoke/`, `stress/`, `ui/`, `ui_validation/`, `unit/`
- Status: Not referenced by active pytest config; pre-migration architecture.
- Action: Audit for unique coverage; migrate to `tests/automated/`; delete remainder including four `.bak` files.

**Root-Level Utility/Debug Scripts:**
- What: `platform_base/fix_spacers.py`, `platform_base/check_spacers.py`, `platform_base/visual_test.py`, `platform_base/simple_test.py`, `platform_base/debug_launch.py`, `platform_base/test_launch.py`
- Status: Ad-hoc scripts at root; not part of any CI or build workflow.
- Action: Fix spacer bug in source → delete `fix_spacers.py`/`check_spacers.py`; promote informal tests to `tests/` or delete; remove `debug_launch.py`/`test_launch.py`.

**`scripts/` UI Migration Scripts (9 of 19 are Migration/Debug Only):**
- What: `migrate_to_ui.py`, `auto_migrate_ui.py`, `validate_ui_migration.py`, `complete_ui_files.py`, `connect_ui_files.py`, `debug_ui_update.py`, `compile_ui.py`, `generate_ui_files.py`, `validate_ui_files.py`
- Action: After migration completes, delete all migration-only scripts; retain only `compile_ui.py` and `validate_ui_files.py`.

**`docs/reports/` Accumulated Reports:**
- What: 27+ `.md` report files — multiple superseded TODO lists, completed sprints, debugging sessions.
- Action: Archive `COMPLETED`/`DEBUG`/`STATUS` reports; consolidate active TODOs into `.planning/`.

**`test_profiling/` Committed Artifacts:**
- What: 20+ `.prof` and `.txt` profiling files from February 2026.
- Action: Add `test_profiling/` to `.gitignore`; delete committed files; regenerate as CI artifacts.

**`profiling_reports/` Empty Directory:**
- What: `platform_base/profiling_reports/` appears to contain no files.
- Action: Delete empty directory; clarify role versus `test_profiling/` and `src/platform_base/profiling/`.

**Dual Config Source:**
- What: `platform_base/configs/platform.yaml` duplicates parts of `platform_base/.platform_config/system/platform.yaml`.
- Action: Determine authoritative location; consolidate and remove duplicate.

**`main_window_old.py` in Active `ui/` Module:**
- What: `platform_base/src/platform_base/ui/main_window_old.py` (58.6 KB) sits alongside current files; detected as a live entry point by `DIAGNOSTICO_APLICACOES.md`.
- Action: Confirm no runtime import; delete file; update any remaining references.

---

*Concerns audit: 2026-03-31 (compiled from DIAGNOSTICO_APLICACOES.md, TROUBLESHOOTING.md, source and directory inspection)*