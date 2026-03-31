# Phase 1 Research: Baseline de Qualidade e Seguranca de Mudanca

**Date:** 2026-03-31
**Phase requirements:** RELY-01, RELY-02, PERF-03

## Research Question

What do we need to know to plan a reliable validation and performance baseline for this brownfield desktop app?

## Findings

### 1. The current automated suite exists, but the stored evidence is incomplete

- The active suite is `platform_base/tests/automated/` with 10 numbered files.
- `platform_base/test_run_results.txt` shows `collected 231 items` and then stops after the first two files, so the repo does not currently contain trustworthy proof of a full green run.
- `platform_base/run_test_suite.py` is a temporary runner with a hard-coded absolute path pointing outside the current workspace path, which makes it non-reproducible across clones.

### 2. The canonical runner should be script-based, not ad-hoc terminal usage

- `platform_base/scripts/run_tests.py` already knows how to set `QT_QPA_PLATFORM=offscreen`, configure `PYTHONPATH`, and generate reports under `docs/reports/`.
- This script is the best anchor for RELY-01 because it is path-aware and already supports `--fast`, `--cov`, and module filtering.
- The temporary `run_test_suite.py` still matters because it is the shortest entrypoint for local confirmation and currently contains the path bug.

### 3. The existing validation orchestrator is stale for the current test topology

- `platform_base/scripts/validate_all.py` still assumes historical "Fase 1/2/3" checks such as `tests/unit`, while the active pytest config in `platform_base/pyproject.toml` points to `tests/automated`.
- That makes it unsuitable as the current regression gate without refactoring.

### 4. Performance validation exists, but it is not the phase baseline we need

- `platform_base/scripts/validate_performance.py` benchmarks processing algorithms, not application startup/runtime memory.
- Phase 1 requirement `PERF-03` needs before/after indicators that can be reused in future migration waves.
- The most practical metric pair for this phase is:
  - startup time of the current launcher in offscreen mode
  - peak or sampled RSS memory of that launcher process during startup window

### 5. The launcher path is measurable, even before UI consolidation

- `platform_base/launch_app.py` starts the current mixed runtime and prints startup messages after showing the main window.
- That makes it a viable baseline target for a headless subprocess harness using `QT_QPA_PLATFORM=offscreen`, `psutil`, and a startup timeout.
- This should be treated as the temporary baseline command for Phase 1 only; later phases may replace it with the canonical launcher.

## Recommended Planning Direction

1. Fix the two runner entrypoints first so the team has one short command and one report-oriented command that both work from any checkout.
2. Rebuild `scripts/validate_all.py` as a current-state regression gate around critical-path automated tests, not historical phase labels.
3. Add a dedicated runtime-baseline harness that launches `launch_app.py` headlessly, measures startup seconds and RSS memory, and writes machine-readable output to `docs/reports/`.
4. Record baseline evidence in checked-in report files so later waves can compare like-for-like numbers.

## Exact Commands To Anchor The Phase

### Full automated suite

`cd platform_base && python scripts/run_tests.py --verbose`

### Critical-path regression gate

`cd platform_base && python scripts/validate_all.py`

### Runtime baseline capture

`cd platform_base && python scripts/capture_runtime_baseline.py --launcher launch_app.py --output-json docs/reports/performance_baseline.json --timeout 20`

## Risks

- Qt startup in offscreen mode may still block or hang if the launcher waits indefinitely for the event loop; the baseline harness must enforce a timeout and kill the subprocess cleanly.
- UI tests currently import PyQt6-based code while higher-level project notes mention PySide6; Phase 1 should avoid framework migration and instead stabilize the existing runnable path.
- `test_08_memory_leaks.py` contains non-failing assertions (`assert True`) and should not be treated as sufficient proof of memory health by itself.

## Validation Architecture

- Quick check after each task: run the task-specific command defined in PLAN.md.
- Full validation after each wave: run `cd platform_base && python scripts/validate_all.py` and `cd platform_base && python scripts/run_tests.py --verbose`.
- Performance sampling contract for this phase: compare `startup_seconds` and `peak_rss_mb` values written to `docs/reports/performance_baseline.json`.

## Planning Implications

- The phase can be split into two independent plans:
  - Plan 01 for reproducible automated test execution and evidence capture.
  - Plan 02 for regression gate plus runtime-performance baseline capture.
- These plans can run in parallel because they touch different files and satisfy different requirements, but both should write artifacts into `docs/reports/` using distinct filenames.
- Later phases should depend on the resulting baseline artifacts before removing duplicated UI/runtime paths.