# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

Unit economics calculator for e-commerce (AOV, product margin, CAC, LTV/CAC, break-even and
what-if scenarios). Python package in `src/unit_economics/`, Streamlit UI in `app.py`, CLI
`unit-economics`. All sample data is fictional.

## Commands

- Install: `pip install -e ".[dev]"`
- Lint/format: `ruff check .` and `ruff format .`
- Tests: `pytest` (offline, a few seconds; the app smoke test needs Streamlit installed)
- CLI: `unit-economics --data-dir examples/sample-store --price-change 5`
- App: `streamlit run app.py`
- Regenerate sample data: `python examples/generate_sample_data.py`

## Rules

- Everything in the repo is written in English.
- Keep calculations in `metrics.py`/`scenarios.py` as pure functions; UI code only formats.
- If you change a calculation, update `tests/test_regression.py` and the README numbers together.
- Never add real company, customer or personal data. Author is "Rafaela Uto".
- Commits follow Conventional Commits.
