# Architecture Research

## Target Architecture Shape

- Canonical UI layer: `ui/` only.
- Core services remain in `core/` and are consumed by `ui/`, `processing/`, `viz/`, `io/`.
- Plugin contracts remain stable through migration.
- API layer remains compatible and decoupled from UI internals.

## Component Boundaries

- UI (`ui/`): interaction, orchestration calls, rendering integration.
- Core (`core/`): state/session/signal backbone and configuration policy.
- Processing/Viz: domain behavior; no broad refactor in this initiative.
- Launch path: one canonical app entrypoint.

## Data and Control Flow

1. Launcher bootstraps app and config.
2. UI dispatches intents to core/services.
3. Core coordinates processing and viz updates.
4. Results return to UI for user interaction.
5. Optional API calls operate without requiring legacy UI paths.

## Suggested Build Order

1. Define canonical runtime path (`ui/` + launcher) and protect with smoke tests.
2. Consolidate main window implementations to one canonical file.
3. Unify duplicated signal/session modules into core ownership.
4. Remove obsolete launchers/workarounds after source fix validation.
5. Harden automated tests + performance guardrails to lock gains.

## Integration Notes

- Each wave should include behavior parity checks for top operator workflows.
- Remove legacy code only after proving equivalent behavior in canonical path.