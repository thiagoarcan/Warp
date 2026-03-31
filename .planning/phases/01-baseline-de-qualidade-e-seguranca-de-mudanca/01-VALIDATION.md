---
phase: 01
slug: baseline-de-qualidade-e-seguranca-de-mudanca
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-31
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4.2 + pytest-qt |
| **Config file** | platform_base/pyproject.toml |
| **Quick run command** | `cd platform_base && python scripts/validate_all.py` |
| **Full suite command** | `cd platform_base && python scripts/run_tests.py --verbose` |
| **Estimated runtime** | ~60-180 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd platform_base && python scripts/validate_all.py`
- **After every plan wave:** Run `cd platform_base && python scripts/run_tests.py --verbose`
- **Before `/gsd-verify-work`:** Full suite must be green and `docs/reports/performance_baseline.json` must exist
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | RELY-01 | integration | `cd platform_base && python run_test_suite.py` | ✅ | ⬜ pending |
| 01-01-02 | 01 | 1 | RELY-01 | integration | `cd platform_base && python scripts/run_tests.py --verbose` | ✅ | ⬜ pending |
| 01-02-01 | 02 | 1 | PERF-03 | smoke/perf | `cd platform_base && python scripts/capture_runtime_baseline.py --launcher launch_app.py --output-json docs/reports/performance_baseline.json --timeout 20` | ❌ W0 |
| 01-02-02 | 02 | 1 | RELY-02 | smoke/integration | `cd platform_base && python scripts/validate_all.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements except `platform_base/scripts/capture_runtime_baseline.py`, which Plan 02 creates before the phase-level performance sampling command can be considered green.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Review whether baseline numbers are acceptable for future comparison | PERF-03 | Threshold values are product decisions, not just binary execution | Open `docs/reports/performance_baseline.json` and confirm `startup_seconds` and `peak_rss_mb` are recorded with timestamp and launcher name |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 180s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending