# Contributing

Thanks for your interest! This is a small portfolio project, so issues and pull requests are
welcome but kept simple.

## Opening an issue

- Use the templates in `.github/ISSUE_TEMPLATE/` (bug report or feature request).
- Describe the decision the change helps with: this tool exists to answer business questions.

## Setup

```bash
git clone https://github.com/rafauto/ecommerce-unit-economics.git
cd ecommerce-unit-economics
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Pull request flow

1. Create a branch from `main` (e.g. `feat/returns-rate`).
2. Make small commits using [Conventional Commits](https://www.conventionalcommits.org/):
   `feat:`, `fix:`, `docs:`, `test:`, `ci:`, `chore:`, `style:`, `refactor:`.
3. Before opening the PR, run:

   ```bash
   ruff check .
   ruff format --check .
   pytest
   ```

4. Open the PR, link the issue and fill in the checklist. PRs are merged only with CI green.

## Guiding principles

- **Calculations stay pure.** Everything in `src/unit_economics/` is free of UI and I/O side
  effects (except `data.py`, which only reads files). The Streamlit app and the CLI are thin.
- **Every number is tested.** New metrics come with a hand-checked unit test; bug fixes come
  with a regression test.
- **Explain the business meaning.** Metric names and docstrings say what the number means for a
  decision, not just how it is computed.
- **Keep it simple.** No new dependency or layer unless the MVP needs it.

## Privacy

Never paste real customer data, personal data, real company figures or API keys into issues,
pull requests or test fixtures. Use the fictional sample store or a small invented example.
