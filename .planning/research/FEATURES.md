# Features Research

## Milestone Context

Subsequent milestone: hardening and migration completion, not net-new product feature expansion.

## Table Stakes (must-have for this initiative)

- Stable end-to-end flow: data load -> processing -> visualization.
- Single UI path in runtime (`ui/`) with parity for critical workflows.
- No critical regressions in existing operator workflows.
- Testable baseline: core suites run and pass with repeatability.
- Clear canonical modules for main window, signal/session, and launch path.

## Differentiators (nice-to-have after stabilization)

- Better developer ergonomics (faster contributor onboarding via clearer structure).
- Better observability around migration quality and performance drift.
- Reduced maintenance cost from duplicated code elimination.

## Anti-Features (explicitly avoid now)

- New user-facing product capabilities unrelated to migration/stability.
- Major algorithmic rework in processing engine.
- Deep API behavioral changes in local REST endpoints.

## Complexity and Dependencies

- High complexity: migrating UI while preserving behavior.
- Medium complexity: removing module duplication safely.
- High dependency: test baseline and regression checks before each removal wave.
- High dependency: clear rollout order to keep operational continuity.