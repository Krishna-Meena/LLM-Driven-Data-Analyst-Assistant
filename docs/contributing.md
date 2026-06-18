# Contributing Guidelines

Thank you for contributing to the **Local LLM Data Analyst** project! To maintain code quality, type-safety, and smooth integration, please follow these guidelines.

---

## Code Quality Standards

We enforce styling and strict type checking using `ruff` and `mypy`.

### 1. Formatting and Linting
We use `ruff` to automatically check for style issues, unused imports, and format code files.
- Run Ruff check locally:
  ```bash
  uv run ruff check .
  ```
- Auto-fix linting issues:
  ```bash
  uv run ruff check --fix .
  ```
- Format code files:
  ```bash
  uv run ruff format .
  ```

### 2. Static Type Checking
All public functions, arguments, and return variables must have explicit Python type hints. We use `mypy` for static type checking.
- Run type checks locally:
  ```bash
  uv run mypy app tests
  ```

---

## Testing

All new features (analytics calculations, file loaders, prompts) should be covered by unit tests. We write tests using `pytest` inside the `tests/` directory.

- Run all unit tests:
  ```bash
  uv run pytest tests/
  ```
- Run tests with coverage:
  ```bash
  uv run pytest --cov=app tests/
  ```

---

## Git Workflow & Commits

We follow clean commits. When writing commits, use standard prefix types:
- `feat:` for new capabilities or engines.
- `fix:` for bug fixes.
- `test:` for writing unit tests.
- `docs:` for guides and code comments.
- `style:` for UI design adjustments.

Pre-commit hooks are configured to run automatically. If your code is not compliant, the commit will be rejected with suggestions. Fix the formatting issues and commit again.
