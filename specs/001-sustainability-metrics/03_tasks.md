# Tasks: Sustainability Metrics Integration

**Input**: Design documents from `specs/001-sustainability-metrics/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths are included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure the shared emission config is in place before any solver work begins.

- [x] T001 Create `data/sustainability_config.json` with `shipping_emission_factor`, `storage_emission_factor`, and `emissions_target_reduction`

**Checkpoint**: Config file exists and is valid JSON — all solver tasks can proceed.

- [x] T001b [P] Measure baseline solver performance (wall-clock time) for SC-008 verification

---

## Phase 2: User Story 1 - ESG Route Emissions Reporting (Priority: P1) 🎯 MVP

**Goal**: Routing solver calculates and persists CO2 emissions per optimized route.

**Independent Test**: Run `uv run routing-optimization` — verify "Total Carbon Footprint (kg CO2)" in stdout and `total_emissions_kg` column in `data/routing_optimization_results.csv`.

### Implementation for User Story 1

- [x] T002 [US1] Add `calculate_emissions(distance: float, factor: float) -> float` to `routing-optimization/src/routing_optimization/solver.py` and load config at solver entry point
- [x] T003 [US1] Print `Total Carbon Footprint (kg CO2)` to stdout in `routing-optimization/src/routing_optimization/solver.py`
- [x] T004 [US1] Append `total_emissions_kg` column to `data/routing_optimization_results.csv` output logic

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 3: User Story 2 - Carbon-Aware Inventory Allocation (Priority: P2)

**Goal**: Inventory solver produces a Carbon-Efficient scenario capping emissions at 90% of LP Max Revenue baseline.

**Independent Test**: Run `uv run inventory-optimization` — verify three scenarios in output CSVs, with Carbon-Efficient total emissions ≤ 90% of LP Max Revenue emissions.

### Implementation for User Story 2

- [x] T005 [US2] Add storage carbon cost calculation (allocated stock × `storage_emission_factor`) to `inventory-optimization/src/inventory_optimization/solver.py`
- [x] T006 [US2] Implement Carbon-Efficient LP scenario in `solve_inventory_allocation` in `inventory-optimization/src/inventory_optimization/solver.py` (cap = 90% of LP Max Revenue emissions)
- [x] T007 [US2] Save emission metrics (`storage_emissions_kg`) to `data/inventory_optimization_results_scenario_*.csv` for all three scenarios

**Checkpoint**: User Stories 1 AND 2 both work independently (90% emissions cap).

---

## Phase 4: Validation & Edge Cases

**Goal**: Ensure the system handles malformed config inputs and solver edge cases gracefully.

- [x] T007b [US1] Add input validation to `routing_optimization/solver.py` for config factors
- [x] T007c [US2] Add input validation to `inventory_optimization/solver.py` for config factors
- [x] T007d [US2] Handle "Emissions cap already met by optimal solution" edge case in inventory solver

---

## Phase 5: User Story 3 - Sustainability Metrics via Natural Language Interface (Priority: P3)

**Goal**: `query.py` exposes carbon metrics in tool responses and Claude's system prompt understands sustainability queries.

**Independent Test**: Run `uv run python query.py` and ask "Which product has the highest carbon footprint per unit?" — response must include a numeric value derived from live CSV data.

### Implementation for User Story 3

- [x] T008 [US3] Update tool definitions in `query.py` to include CO2 fields (`total_emissions_kg`, `storage_emissions_kg`) in tool responses
- [x] T009 [US3] Update Claude's system prompt in `query.py` to explain carbon metrics and how to answer sustainability questions (e.g., "greenest route", "highest carbon footprint per unit")

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation and any cross-story fixes.

- [x] T010 [P] Run full pipeline: demand → `uv run inventory-optimization` → `uv run routing-optimization` → `uv run python query.py` and verify no errors
- [x] T011 [P] Verify solver performance regression is within 10% of baseline measured in T001b

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **US1 (Phase 2)**: Depends on Phase 1 (config file)
- **US2 (Phase 3)**: Depends on Phase 1 (config file); can run in parallel with US1 since different files
- **US3 (Phase 4)**: Depends on US1 and US2 producing carbon data in CSVs
- **Polish (Phase 5)**: Depends on all user stories being complete

### Parallel Opportunities

- T002–T004 (US1) and T005–T007 (US2) can run in parallel — they modify different solver files
- T008 and T009 within US3 can run in parallel — different sections of `query.py`
- T010 and T011 in Polish can run in parallel

---

## Notes

- [P] tasks = different files, no cross-task dependencies
- [Story] label maps each task to its user story for traceability
- Verify the config loads correctly before running any solver
- Commit after each user story phase is complete and independently validated
