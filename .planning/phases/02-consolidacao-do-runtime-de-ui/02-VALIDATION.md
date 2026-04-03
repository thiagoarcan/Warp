---
phase: 02
slug: consolidacao-do-runtime-de-ui
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-03
---

# Phase 02 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4.2 + pytest-qt |
| **Config file** | platform_base/pyproject.toml |
| **Quick run command** | `cd platform_base && python scripts/validate_all.py` |
| **Full suite command** | `cd platform_base && python scripts/run_tests.py --verbose` |
| **Estimated runtime** | ~180-420 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd platform_base && python scripts/validate_all.py`
- **After every plan wave:** Run `cd platform_base && python scripts/run_tests.py --verbose`
- **Before `/gsd-verify-work`:** Full suite must be green and baseline reports updated
- **Max feedback latency:** 420 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | UICO-02 | smoke | `cd platform_base && python run_app.py` | ✅ | ⬜ pending |
| 02-01-02 | 01 | 1 | UICO-02 | integration | `cd platform_base && python scripts/validate_all.py` | ✅ | ⬜ pending |
| 02-02-01 | 02 | 1 | UICO-01 | unit/integration | `cd platform_base && python -m pytest tests/automated/test_03_navigation.py -q --tb=short` | ✅ | ⬜ pending |
| 02-02-02 | 02 | 1 | UICO-01 | integration | `cd platform_base && python scripts/validate_all.py` | ✅ | ⬜ pending |
| 02-03-01 | 03 | 2 | UICO-01 | integration | `cd platform_base && python -m pytest tests/automated/test_05_initialization.py -q --tb=short` | ✅ | ⬜ pending |
| 02-03-02 | 03 | 2 | UICO-01, UICO-02 | full | `cd platform_base && python scripts/run_tests.py --verbose` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Confirm canonical startup docs are clear for operators | UICO-02 | Operational clarity and wording quality cannot be fully automated | Open docs that mention startup and verify `launch_app.py` is presented as canonical while `run_app.py` is compatibility/deprecated |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 420s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
