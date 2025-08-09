# Code Style Guide

## Context
Global code style rules for Agent OS projects.  
Applies to backend (Python), frontend (Svelte/TypeScript), infrastructure (Docker/YAML), and shared configuration files.

---

## General Formatting

### Indentation
- **Python, YAML, JSON, Markdown:** 2 spaces for indentation (never tabs)
- **Dockerfiles:** No indentation for top-level instructions
- Maintain consistent indentation throughout all files
- Align nested structures for readability

### Naming Conventions

#### Python
- **Methods and Variables:** `snake_case` (e.g., `user_profile`, `calculate_total`)
- **Classes:** `PascalCase` (e.g., `UserProfile`, `PaymentProcessor`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)
- **Private Members:** Prefix with `_` (e.g., `_internal_state`)

#### TypeScript / Svelte
- **Variables and Functions:** `camelCase`
- **Components:** `PascalCase` (e.g., `UserProfile.svelte`)
- **Constants:** `UPPER_SNAKE_CASE`
- **Event Names:** `kebab-case` (HTML attributes, e.g., `on:form-submit`)

#### Files & Directories
- Use lowercase with hyphens for directories and filenames (e.g., `user-service`, `order-api`)
- Python modules use `snake_case.py`
- Svelte components use `PascalCase.svelte`
- Each microservice must have:
  - Its own top-level directory
  - Dedicated `Dockerfile`, configuration, and source code folder

---

## Project Structure & Microservices
- Each service must be a standalone Docker container.
- Services must be **logically separated in the folder structure**, one directory per microservice.
- All services are orchestrated via `docker-compose.yml`.
- **Environment variables:** `.env` files for secrets.
- **Service configuration:** YAML files for static or non-sensitive settings.
- Docker Compose must load environment variables from `.env` and configuration from `.yml` files and pass them to relevant services.

---

## String Formatting

#### Python
- Prefer single quotes `'...'`
- Use double quotes `"..."` only when:
  - String contains single quotes
  - f-strings or `.format()` require interpolation
- For multi-line strings: triple quotes `"""..."""` with indentation matching code block

#### TypeScript / Svelte
- Prefer single quotes `'...'`
- Use template literals `` `...` `` for:
  - Multi-line strings
  - Interpolation

---

## Documentation

### Language & Style
- All code, comments, and docstrings must be written in **English**.
- Use **NumPy style docstrings** for:
  - Modules
  - Classes
  - Functions and methods

Example:
```python
def calculate_total(price: float, tax: float) -> float:
    """
    Calculate the total price including tax.

    Parameters
    ----------
    price : float
        The base price of the item.
    tax : float
        Tax rate as a decimal (e.g., 0.2 for 20%).

    Returns
    -------
    float
        Total price including tax.

    Raises
    ------
    ValueError
        If price or tax is negative.
    """
    if price < 0 or tax < 0:
        raise ValueError("Price and tax must be non-negative")
    return price * (1 + tax)


---

Issue Tracking in Code
	•	Use standardized comment tags:
	•	# TODO: – Pending tasks
	•	# FIXME: – Known bugs
	•	# BUG: – Confirmed issues
	•	# NOTE: – Important clarifications
	•	# OPTIMIZE: – Code that could be improved
	•	# SECURITY: – Security concerns
	•	Each tag must include:
	•	Brief description
	•	Date (YYYY-MM-DD)
	•	Author initials

Example:

# TODO: Implement Redis caching for session data
# Date: 2025-08-02
# Author: DF


---

Backend (Python)
	•	Imports: Group in the following order:
	1.	Standard library
	2.	Third-party packages
	3.	Local application imports
	•	Separate groups with a blank line
	•	Sort alphabetically within each group (isort)
	•	Typing: Always use Python type hints
	•	Testing: pytest
	•	Code Quality: black, isort, flake8, mypy

---

Frontend (Svelte / TypeScript)
	•	Component Structure:
	•	<script> block first
	•	<style> block second (scoped if needed)
	•	Markup last
	•	Imports: Group logically (libraries → stores → components → utilities)
	•	TailwindCSS:
	•	Use utility-first approach
	•	Extract repeated classes via @apply in .css or tailwind.config.js
	•	Group classes logically in markup (layout → spacing → typography → colors → states)

---

Infrastructure (Docker, YAML)
	•	Dockerfiles:
	•	Minimal, version-pinned base images
	•	One logical instruction per line
	•	Combine related RUN commands to reduce layers
	•	docker-compose.yml:
	•	Explicitly specify version and services
	•	Load environment variables from .env files
	•	Mount volumes explicitly

---

Best Practices
	•	Follow industry best practices for:
	•	Security
	•	Code readability
	•	Performance
	•	Maintainability
	•	No secrets in source control
	•	Lint & type-check before committing
	•	Automated tests must pass before merge

---
