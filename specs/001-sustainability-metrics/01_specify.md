# Feature Specification: Sustainability Metrics Integration

**Feature Branch**: `001-sustainability-metrics`
**Created**: 2026-04-19
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 - ESG Route Emissions Reporting (Priority: P1)

As a Logistics Manager, I want to see the total CO2 emissions for the optimized route so I can include them in ESG reports.

**Why this priority**: Core deliverable — without route emissions data, no sustainability reporting is possible. Unblocks all downstream stories.

**Independent Test**: Can be tested by running `uv run routing-optimization` and verifying a "Total Carbon Footprint (kg CO2)" line appears in stdout and `total_emissions_kg` is present in `routing_optimization_results.csv`.

**Acceptance Scenarios**:

1. **Given** a valid distance matrix and `sustainability_config.json`, **When** the routing solver runs, **Then** total CO2 emissions are printed to stdout and saved to the results CSV.
2. **Given** a missing or malformed `sustainability_config.json`, **When** the routing solver runs, **Then** a clear error is raised describing the missing configuration.

---

### User Story 2 - Carbon-Aware Inventory Allocation (Priority: P2)

As an Inventory Analyst, I want to compare standard LP allocation against a Carbon-Aware allocation so I can understand the trade-off between revenue and environmental cost.

**Why this priority**: Depends on the configuration established in US1. Delivers direct decision-support value for inventory planning.

**Independent Test**: Can be tested by running `uv run inventory-optimization` and verifying that results include both the "LP Max Revenue" scenario and a "Carbon-Efficient" scenario with lower total emissions.

**Acceptance Scenarios**:

1. **Given** a valid inventory dataset and `sustainability_config.json`, **When** the inventory solver runs, **Then** three scenarios are produced: LP Revenue Max, Proportional, and Carbon-Efficient.
2. **Given** the Carbon-Efficient scenario runs, **When** results are saved, **Then** total emissions are at most 90% of the LP Max Revenue scenario's emissions.
3. **Given** the LP Revenue Max scenario, **When** both scenarios are compared, **Then** the storage carbon cost metric is present in both output CSVs.

---

### User Story 3 - Sustainability Metrics via Natural Language Interface (Priority: P3)

As a Logistics Manager or Inventory Analyst, I want to ask sustainability questions in natural language via `query.py` and receive carbon data in the response.

**Why this priority**: Depends on US1 and US2 producing carbon data. Enhances accessibility but is not required for data correctness.

**Independent Test**: Can be tested by running `uv run python query.py` and asking "What is the CO2 footprint for distance matrix 1?" — response must include a numeric emissions value.

**Acceptance Scenarios**:

1. **Given** routing and inventory results have been generated, **When** a user asks "What is the greenest route?", **Then** `query.py` returns a response referencing `total_emissions_kg`.
2. **Given** inventory results are available, **When** a user asks "Which product has the highest carbon footprint per unit?", **Then** `query.py` returns the product name and its storage emission value.

---

### Edge Cases

- What happens when `sustainability_config.json` is missing or has invalid emission factor values (negative, zero, non-numeric)?
- How does the Carbon-Efficient solver behave when the emission cap is already met by the LP Max Revenue solution?
- How does the system handle a route with zero distance (local delivery)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load emission factors from a configurable `data/sustainability_config.json` before running any solver.
- **FR-002**: The routing solver MUST calculate and output total CO2 emissions (kg) per optimized route.
- **FR-003**: The routing solver MUST append `total_emissions_kg` to `routing_optimization_results.csv`.
- **FR-004**: The inventory solver MUST calculate storage carbon cost per product category.
- **FR-005**: The inventory solver MUST produce a Carbon-Efficient allocation scenario that caps emissions at 90% of the LP Max Revenue scenario's emissions.
- **FR-006**: [consolidated into FR-001]
- **FR-007**: `query.py` MUST expose carbon metrics in tool responses for natural language queries.
- **FR-008**: System MUST NOT degrade existing solver wall-clock performance by more than 10%.

### Key Entities

- **EmissionConfig**: Holds `shipping_emission_factor` (kg CO2/km), `storage_emission_factor` (kg CO2/unit/month), and `emissions_target_reduction` (% cap). Loaded from `sustainability_config.json`.
- **RouteEmission**: Derived from a solved route — total distance × shipping factor = `total_emissions_kg`.
- **StorageEmission**: Per-product storage allocation × storage factor = carbon cost per product category.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run routing-optimization` prints "Total Carbon Footprint (kg CO2)" and `routing_optimization_results.csv` contains `total_emissions_kg` with no regressions in existing columns.
- **SC-002**: `uv run inventory-optimization` produces a third scenario ("Carbon-Efficient") with total emissions ≤ 90% of LP Max Revenue emissions.
- **SC-003**: `uv run python query.py` correctly answers "Which product has the highest carbon footprint per unit?" using live CSV data.
- **SC-004**: Full pipeline (demand → inventory → routing) runs end-to-end with no errors after all changes.

## Assumptions

- Emission factors in `sustainability_config.json` are static per run; real-time API lookups are out of scope.
- Mobile or web UI support is out of scope; all output is via CLI and CSV.
- The 90% emission cap for the Carbon-Efficient scenario uses the LP Max Revenue scenario's total emissions as baseline (computed in the same solver run).
- Existing `uv` workspace structure and module boundaries are preserved — no new top-level packages will be introduced.
