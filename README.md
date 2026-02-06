[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![pre-commit](https://github.com/joshtkraus/google-flights-scraper/workflows/pre-commit/badge.svg)](https://github.com/joshtkraus/google-flights-scraper/actions)
[![coverage](https://codecov.io/gh/joshtkraus/google-flights-scraper/graph/badge.svg)](https://codecov.io/gh/joshtkraus/google-flights-scraper)

# Google Flights Web Scraper

A Python-based end-to-end web scraping of Google Flights using Selenium selecting the "best" flight options, and collecting flight information including prices, times, airlines, connections, and price relativity.

## Use Cases
- Single Search: Enter a departure and arrival destination along with departure and return dates, recieve information for the flight options that Google Flights deems are "best".
- Multiple Destinations: Search multiple destinations on certain dates. Helpful if you know when you want to travel, but don't know where and are looking for good deals.
- Multiple Dates: Search all date combinations for a specific route between certain dates. Helpful if you're flexible on timing and looking for finding cheaper days to fly.

## Examples
See `docs/tutorial` for usage examples.

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

6. OPTIONAL: Run integration tests and upload coverage
   Create a .env file in your project root:
   ```bash
   CODECOV_TOKEN=your_token_here
   ```

   Run tests and upload coverage:
   ```bash

   # Run all tests with coverage
   uv run pytest --cov=src --cov-report=xml

   # Load CODECOV_TOKEN
   uv run python -c "from dotenv import load_dotenv; import os; load_dotenv(); CODECOV_TOKEN = os.getenv('CODECOV_TOKEN')"

   # Upload to Codecov
   codecovcli upload-process
   ```

7. Create PR to merge to `dev`
