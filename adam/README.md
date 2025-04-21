# Letter String Domain Term Rewriting System 

This project implements a **Term Rewriting System (TRS)** for the **Letter String Domain (LSD)**, a symbolic computation model focused on symbolic transformation, pattern matching, and analogical reasoning.

## Features
- Term Rewriting System (TRS) supporting rule-based transformations.
- Automated testing framework to verify correctness of term transformations.
- Modular architecture for symbolic manipulation and method-based reasoning.
- Makefile automation for building, testing, and generating reports.

## Project Structure

```
.
├── lsd/                # Main project code
├── tests/              # Unit tests for the TRS and related components
├── Makefile            # Automation for build, test, and coverage tasks
├── pyproject.toml      # Python project configuration (dependencies, build system)
├── readme.org          # Project documentation (Org-mode format)
├── shell.nix           # Nix environment configuration for the project
└── todo.org            # Task management and project TODOs
```

## Requirements

### Python Dependencies

Ensure you have the required Python dependencies by installing from `pyproject.toml`:

```bash
pip install -r requirements.txt  # If using a pip-compatible tool
```

Alternatively, the project uses `pyproject.toml` for dependency management. You can install dependencies using `pip` or `poetry`:

```bash
# Using pip
pip install .
```

### Nix Environment (Optional)

The project includes a `shell.nix` configuration for managing dependencies in a Nix environment. To use the Nix shell, run:

```bash
nix-shell
```

## Building and Running

### Makefile Targets

The project includes a `Makefile` for automating common tasks. Available targets include:

- **test**: Run unit tests using `pytest`.
  ```bash
  make test
  ```

- **coverage**: Run tests and generate a code coverage report in XML format.
  ```bash
  make coverage
  ```

- **types**: Perform type checking using `pyright`.
  ```bash
  make types
  ```

- **docs**: Generate project documentation using Sphinx.
  ```bash
  make docs
  ```

- **test-cov-html**: Run tests with coverage and open the coverage report in the default browser.
  ```bash
  make test-cov-html
  ```

- **docs-auto**: Automatically build the documentation.
  ```bash
  make docs-auto
  ```

### Running Tests

You can run the tests directly with `pytest`:

```bash
pytest tests/
```
