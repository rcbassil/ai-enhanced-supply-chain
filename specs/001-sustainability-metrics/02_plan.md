# Implementation Plan: Sustainability Metrics Integration

**Branch**: `001-sustainability-metrics` | **Date**: 2026-04-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-sustainability-metrics/spec.md`

## Summary

Integrate carbon emissions tracking into the routing and inventory solvers by loading a shared `sustainability_config.json`, appending CO2 metrics to existing output CSVs, adding a Carbon-Efficient allocation scenario to the inventory solver, and exposing carbon data through the `query.py` natural language interface.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: `scipy` (LP solver via `linprog`), `anthropic` (Claude API in `query.py`), `uv` workspaces
**Storage**: CSV files under `data/`; JSON config at `data/sustainability_config.json`
**Testing**: `pytest` (existing test suites per module)
**Target Platform**: macOS / Linux (local CLI)
**Project Type**: CLI / data pipeline
**Performance Goals**: Solver wall-clock time increase ≤ 10% vs baseline
**Constraints**: No new top-level packages; emission factors must be config-driven; no external API calls for emission data
**Scale/Scope**: Single-node, single-run pipeline; ~3 existing solver files to modify

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No new packages or modules introduced beyond the existing `uv` workspace structure.
- Config loading is a pure I/O side-effect isolated to solver entry points — no cross-module imports added.
- Carbon-Efficient scenario reuses the existing `linprog` infrastructure; no new solver frameworks needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-sustainability-metrics/
├── plan.md       # This file
├── spec.md       # Feature specification
└── tasks.md      # Task list (/speckit.tasks command output)
```

### Source Code (repository root)

```text
data/
└── sustainability_config.json          # Emission factors config (already created)

routing-optimization/src/routing_optimization/
└── solver.py                           # Add calculate_emissions(), update CSV output

inventory-optimization/src/inventory_optimization/
└── solver.py                           # Add storage carbon cost + Carbon-Efficient scenario

query.py                                # Expose carbon metrics in tool responses + system prompt
```

**Structure Decision**: Single-project layout. All changes are confined to existing solver files and the shared data directory — no new directories or packages are needed.

## Complexity Tracking

> No constitution violations identified — all changes are within existing module boundaries.
