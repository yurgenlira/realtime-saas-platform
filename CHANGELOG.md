# Changelog

All notable changes to this project will be documented in this file.

This project follows an evolving architecture from MVP to Enterprise SaaS.

## [0.1.0]

### Added

- **FastAPI Base**: Initial skeleton with a functional health check endpoint (`/health`) for availability monitoring.
- **Modular Structure**: Repository organization under `apps/server/src` to support service scalability.
- **Modular directory structure
- **Code Quality Automation**: Configuration of `.pre-commit-config.yaml` integrating `black`, `flake8`, and `isort`.
- **Project Governance**: Technical `README.md`, professional `.gitignore`, and `requirements.txt` for dependency management.

### Infrastructure

- **Dev Environment**: Python 3.12 virtual environment setup and dependency isolation.
- **Baseline**: Created Git Tag `v0.1.0` to establish the architectural starting point.

### DevOps

- **Shift-Left Validation**: Activated pre-commit hooks to enforce PEP8 standards and formatting before each commit.
- **Automation**: Integrated automatic validation for structural files (YAML, JSON) via pre-commit hooks.

---

## Versioning Strategy

This project follows semantic versioning:

**MAJOR.MINOR.PATCH**

Example:

**1.0.0**

- **Major** → Architecture changes  
- **Minor** → New features  
- **Patch** → Fixes
