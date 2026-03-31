# Pitfalls Research

## Pitfall 1: Hidden Coupling Between Legacy and New UI

- Warning signs:
  - Imports crossing from `ui/` back into `desktop/` at runtime.
  - Fixes applied in only one UI stack.
- Prevention:
  - Static import scan + runtime smoke tests through canonical launcher.
  - Ban new dependencies from `ui/` to `desktop/`.
- Phase mapping:
  - Early migration phases.

## Pitfall 2: Deleting Duplicates Before Parity Proof

- Warning signs:
  - Missing workflow after removing duplicate module.
  - Increased bug reports on common operations.
- Prevention:
  - Require explicit parity checklist and tests before each deletion.
  - Keep reversible wave boundaries.
- Phase mapping:
  - Consolidation/removal phases.

## Pitfall 3: Performance Regression During Refactor

- Warning signs:
  - Higher startup time, memory growth, UI latency spikes.
- Prevention:
  - Establish baseline metrics before major removals.
  - Add lightweight perf checks to regression suite.
- Phase mapping:
  - Before and after each wave.

## Pitfall 4: Launcher/Config Drift

- Warning signs:
  - Multiple launch scripts in active use.
  - Conflicting config precedence behavior.
- Prevention:
  - Canonical launcher declaration and deprecation plan.
  - Tests for config precedence and startup path.
- Phase mapping:
  - Early and mid phases.

## Pitfall 5: Test Illusion (partial suite treated as green)

- Warning signs:
  - Interrupted runs accepted as baseline.
  - Missing summary evidence for full collection.
- Prevention:
  - Enforce full run evidence and failure triage policy.
  - Gate deletions/refactors on full suite status.
- Phase mapping:
  - Throughout all phases.