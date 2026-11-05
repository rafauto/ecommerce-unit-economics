# Product brief — E-commerce Unit Economics Calculator

> All data in this project is **fictional**. "Lumi Custom" is an invented online store of
> personalised products (mugs, bottles, notebooks and pens) created only to demonstrate the calculations.

## Problem

Product and growth teams at small and mid-sized online stores decide on prices, free-shipping
rules and ad budgets without knowing whether **each order actually makes money** once product
cost, payment fees, taxes, shipping subsidies and customer acquisition cost (CAC) are counted.
The math usually lives in a fragile spreadsheet that nobody trusts.

## User

**Persona — Marina, Product Manager at a 15-person online store of personalised gifts.** She owns the checkout and the
promotions calendar. Every week someone asks her "can we afford free shipping above R$149?" or
"should we push more budget into paid social?". She is comfortable with numbers but is not a
finance analyst, and she needs an answer she can defend in a meeting in minutes, not days.

## Success criteria

- From raw order and product data to a full unit-economics view in **under 2 minutes**.
- Answers five questions on one screen: average order value, contribution margin per order,
  margin per product, CAC (blended and per channel) and break-even orders per month.
- A what-if scenario (e.g. "+5% price") recalculates every metric instantly.

## Hypothesis

> We believe that **a calculator that turns order data into contribution margin, CAC and
> break-even, with what-if scenarios**, solves **the lack of trusted per-order economics** for
> **product managers at small e-commerce stores**; we'll know when **a user can answer "does this
> promotion or channel pay for itself?" in under 2 minutes without opening a spreadsheet**.

## MVP scope (main flow only)

1. Load a product catalog and an order history (sample data or CSV upload).
2. Set cost assumptions: payment fee, taxes, average discount, shipping cost, shipping fee,
   free-shipping threshold, packaging, monthly fixed costs and monthly marketing spend per channel.
3. See the dashboard: AOV, contribution per order, product margins, CAC, LTV/CAC, payback and
   break-even.
4. Run a what-if scenario and see which lever moves the monthly result the most.
5. Run the same calculation from the command line (CLI) for automation and CI.

## Out of scope for the MVP (roadmap, "nice to have")

- Returns and chargebacks rate.
- Demand elasticity (price changes currently keep volume constant).
- Cohort-based LTV with retention curves.
- Multiple shipping zones and carriers.
- Exporting a PDF report.
- Marketplace fees (e.g. selling on third-party marketplaces).

## Validation

Before expanding scope, show the demo to at least one person who works with e-commerce or
product and record their feedback in the backlog.

## Delivery plan

The MVP is planned to fit in **one focused day** (single cycle), with a working result at each step:

| Step | Outcome |
| --- | --- |
| 1 | Brief, backlog and architecture written |
| 2 | Calculation engine + sample data + tests passing |
| 3 | CLI and Streamlit app on top of the engine |
| 4 | README, CI and review; publish only after approval |
