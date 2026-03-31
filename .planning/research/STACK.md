# Stack Research

## Scope

Research focus: consolidar UI (`desktop/` -> `ui/`) e estabilizar base brownfield sem alterar stack principal.

## Recommended Technical Direction (2026)

- Keep: Python 3.12 + PySide6 + plugin architecture via pluggy.
- Keep: FastAPI local API compatibility as-is in this milestone.
- Keep: Existing processing/viz stack (numpy/scipy/matplotlib/pyvista) unchanged, except bug fixes.
- Add/Strengthen:
  - `pytest` as single test entrypoint for confidence gates.
  - `ruff` + `mypy` in CI/local preflight for consistency and regression prevention.
  - Optional `pytest-benchmark` and lightweight perf checks for memory/latency guardrails.

## Prescriptive Choices

1. Canonical UI runtime must be `platform_base/src/platform_base/ui/`.
2. Legacy `desktop/` remains read-only during transition waves, then removed.
3. Single canonical launcher should remain after cleanup.
4. Config source-of-truth should be documented and enforced by tests.

## What Not To Use In This Milestone

- No framework rewrite (e.g., moving away from PySide6).
- No large architecture split/replatform.
- No broad API redesign in FastAPI layer.

## Confidence

- High: preserving stack and consolidating UI path minimizes risk.
- Medium: migration sequencing details depend on hidden coupling in current code.
- Medium: performance risk requires explicit baseline and budget assertions.