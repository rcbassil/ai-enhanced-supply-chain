# Project Constitution: AI-Enhanced Supply Chain

This document defines the core principles, standards, and rules for all development within this repository. All AI agents and human contributors must adhere to these guidelines.

## 1. Architectural Principles
- **Modular Design**: The project is organized into independent modules (`demand-forecasting`, `inventory-optimization`, `routing-optimization`).
- **Workspace Management**: Use `uv` for dependency management and workspace coordination.
- **Data-Driven**: All optimization logic must be validated against the datasets in the `data/` directory.

## 2. Coding Standards
- **Language**: Python 3.12+.
- **Typing**: Use type hints for all function signatures.
- **Documentation**: All public functions and classes must have docstrings following the Google style.
- **Structure**: Logic should be separated into `src/<module_name>/` and executed via `__main__.py` or root entry points.

## 3. Workflow (Spec-Driven Development)
We follow the GitHub Spec Kit workflow:
1. **Specify**: Define requirements in `spec.md`.
2. **Plan**: Define technical architecture and data models in `plan.md`.
3. **Tasks**: Break the plan into granular, testable tasks in `tasks.md`.
4. **Implement**: Execute code changes incrementally, referencing tasks.

## 4. Security & Performance
- **API Keys**: Never hardcode secrets. Use environment variables (e.g., `ANTHROPIC_API_KEY`).
- **Optimization**: Prioritize algorithmic efficiency for solver logic.
