# ADR 0001 — Pure calculation core with thin interfaces

- **Status:** accepted
- **Date:** 2026-11-04

## Context

The same numbers must appear in the Streamlit app, in the CLI and in automated tests. Finance
logic mixed with UI code is hard to test and easy to break.

## Decision

All calculations live in pure functions (`metrics.py`, `scenarios.py`) that take a `Dataset`
and return numbers or DataFrames. `data.py` is the only module that reads files. `app.py` and
`cli.py` only collect inputs and format outputs.

## Consequences

- Every metric is unit-tested offline in milliseconds, without Streamlit.
- A new interface (an API, a notebook) can reuse the core without changes.
- Trade-off: a little duplication in formatting between the app and the CLI, kept small by the
  shared `report.py`.
