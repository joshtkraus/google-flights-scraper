[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![pre-commit](https://github.com/joshtkraus/google-flights-scraper/workflows/pre-commit/badge.svg)](https://github.com/joshtkraus/google-flights-scraper/actions)
[![tests](https://github.com/joshtkraus/google-flights-scraper/workflows/tests/badge.svg)](https://github.com/joshtkraus/google-flights-scraper/actions)
[![coverage](https://codecov.io/gh/joshtkraus/google-flights-scraper/graph/badge.svg)](https://codecov.io/gh/joshtkraus/google-flights-scraper)

# Google Flights Web Scraper

A Python-based web scraper for Google Flights using Selenium that collects flight information including prices, times, airlines, connections, and price relativity.

See `examples/` directory for usage examples.

## Installation
1. **Install UV:**
   ```bash
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Set up Project:**
   ```bash
   # Navigate to project directory
   cd google-flights-scraper

   # Create virtual environment
   uv venv

   # Activate virtual environment
   source .venv/bin/activate  # On macOS/Linux
   .venv\Scripts\activate     # On Windows

   # Install dependencies
   uv sync
   ```

## Contributing
1. Create feature branch from `dev`

2. Install pre-commit
   ```bash
   uv run pre-commit install
   ```

3. Make changes

4. Run pre-commit locally
   ```bash
   pre-commit run --all-files
   ```
   Note: These will also run on push and PR.

5. Run unit tests locally
   ```bash
   uv run pytest -xv
   ```
   Note: These will also run on PR.

6. Create PR to merge to `dev`
