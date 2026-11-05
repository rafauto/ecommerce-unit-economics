# ADR 0002 — Metric definitions and simplifications

- **Status:** accepted
- **Date:** 2026-11-04

## Context

Unit economics can be defined in several ways. The MVP needs definitions that are standard,
explainable in one sentence and computable from two CSV files.

## Decision

| Metric | Definition used |
| --- | --- |
| AOV | Net product revenue (after average discount, excluding shipping) / orders |
| Contribution per order | Net revenue − product cost − payment fee − taxes − net shipping cost − packaging |
| Net shipping cost | Shipping cost paid by the store − shipping fee charged (zero fee above the free-shipping threshold) |
| Product margin | Per unit, before order-level costs (shipping and packaging are shared by the basket) |
| CAC | Marketing spend in the period / new customers, crediting each customer to the channel of their first order |
| Contribution LTV | Contribution per order × orders per customer **in the analysed period** |
| Payback | CAC / contribution per order (in orders) |
| Break-even | (Monthly fixed costs + monthly marketing spend) / contribution per order |

Money is handled as `float` and rounded only for display.

## Consequences

- Simple, transparent and easy to audit against a spreadsheet.
- LTV is conservative because it only counts repeat orders inside the period.
- All customers in the data are treated as new in the period.
- Price scenarios keep volume constant (no demand elasticity).
- `float` can differ from cent-exact accounting by fractions of a cent; acceptable for a
  decision tool, not for invoicing.
