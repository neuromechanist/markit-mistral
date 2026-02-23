# Python Development Standards

## Version & Environment
- **Python 3.10+** minimum (supports 3.10-3.13)
- **Virtual Environment:** `uv venv`
- **Package Management:** `uv` with `pyproject.toml` (Hatch build system)
- **Linting/Formatting:** `ruff` (check + format)
- **Type Checking:** `mypy` (strict mode)

## Code Style
- **Formatter:** `ruff format` (Black-compatible)
- **Linter:** `ruff check` with aggressive fixes (`--fix --unsafe-fixes`)
- **Line Length:** 88 characters
- **Imports:** Sorted with `isort` (via ruff)
- **Quote Style:** Double quotes

## Type Hints
- **Required for:** All public functions and methods
- **Tool:** `mypy` with strict settings
- **Example:**
```python
def process_data(items: list[dict[str, Any]]) -> pd.DataFrame:
    """Process raw data into DataFrame."""
    ...
```

## Pre-commit Hook
The git pre-commit hook runs ruff check and format on staged Python files only.
Located at `.git/hooks/pre-commit`.

## Common Patterns
- **Context Managers:** For resource management
- **Dataclasses:** For data structures
- **Pathlib:** For file operations (not os.path)
- **F-strings:** For string formatting

## Error Handling
```python
# Be specific with exceptions
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise or handle appropriately
```

## Documentation
- **Docstrings:** Google or NumPy style
- **Module docs:** At file top
- **Type hints:** Self-documenting code

---
*Follow PEP 8 with ruff enforcement. Real tests only.*
