---
phase: 03
slug: consolidacao-de-modulos-canonicos
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-03
---

# Phase 03 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | platform_base/pyproject.toml |
| **Quick run command** | `cd platform_base && python -m pytest tests/automated/test_03_navigation.py tests/automated/test_05_initialization.py -q --tb=short` |
| **Full suite command** | `cd platform_base && python scripts/validate_all.py && python scripts/run_tests.py --verbose` |
| **Estimated runtime** | ~180-300 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command
- **After every plan wave:** Run full suite command
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 300 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | DEDU-02 | integration | `cd platform_base && python -m pytest tests/automated/test_04_signals_slots.py tests/automated/test_05_initialization.py -q --tb=short` | yes | pending |
| 03-01-02 | 01 | 1 | DEDU-02 | integration | `cd platform_base && python scripts/validate_all.py` | yes | pending |
| 03-02-01 | 02 | 1 | DEDU-01 | integration | `cd platform_base && python -m pytest tests/automated/test_03_navigation.py -q --tb=short` | yes | pending |
| 03-02-02 | 02 | 1 | DEDU-01 | integration | `cd platform_base && python scripts/validate_all.py` | yes | pending |
| 03-03-01 | 03 | 2 | UICO-03 | integration | `cd platform_base && python -m pytest tests/automated/test_03_navigation.py tests/automated/test_05_initialization.py -q --tb=short` | yes | pending |
| 03-03-02 | 03 | 2 | UICO-03 | full-gate | `cd platform_base && python scripts/validate_all.py && python scripts/run_tests.py --verbose` | yes | pending |

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Main window launches and panels are interactable | UICO-03 | visual ergonomics and manual smoke | `cd platform_base && python launch_app.py`, then open dataset, render one series, run one operation |

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 300s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
