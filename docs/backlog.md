# Initial backlog

Each story is ready to become a GitHub issue. Labels: `mvp` or `roadmap`.

## US-01 — Load sample data (`mvp`)

**As a** product manager, **I want** to open the app with a ready-made sample store,
**so that** I can explore the calculator without preparing any file.

- **Given** I open the app for the first time
- **When** no file has been uploaded
- **Then** the fictional sample store is loaded and every metric is shown

## US-02 — Upload my own CSVs (`mvp`)

**As a** product manager, **I want** to upload a products CSV and an orders CSV,
**so that** I can analyse my own (anonymised) numbers.

- **Given** I upload files with the documented columns
- **When** the files are valid
- **Then** all metrics are recalculated from my data
- **Given** a file is missing a column or references an unknown SKU
- **When** I upload it
- **Then** I see a clear error naming the problem and nothing crashes

## US-03 — Average order value and contribution per order (`mvp`)

**As a** product manager, **I want** to see AOV and contribution margin per order,
**so that** I know how much each order really leaves after variable costs.

- **Given** orders, products and cost assumptions
- **When** the dashboard loads
- **Then** I see AOV, average items per order and contribution per order (value and %)
- **And** the contribution counts product cost, payment fee, taxes, net shipping and packaging

## US-04 — Margin per product (`mvp`)

**As a** product manager, **I want** a table of contribution margin per product,
**so that** I can spot items that lose money or need a price review.

- **Given** the product catalog and assumptions
- **When** I open the product table
- **Then** I see net price, unit cost, fees and taxes, contribution and margin % per SKU
- **And** the table is sorted from lowest to highest margin

## US-05 — CAC by channel (`mvp`)

**As a** growth-minded PM, **I want** CAC per acquisition channel and blended CAC,
**so that** I can compare where new customers are cheapest.

- **Given** monthly marketing spend per channel and orders with a channel
- **When** the dashboard loads
- **Then** each new customer is attributed to the channel of their first order
- **And** I see spend, new customers and CAC per channel (no CAC for zero-spend channels)

## US-06 — LTV/CAC and payback (`mvp`)

**As a** product manager, **I want** LTV/CAC and payback in orders,
**so that** I know whether acquiring a customer pays off.

- **Given** contribution per order, orders per customer and blended CAC
- **When** the dashboard loads
- **Then** I see contribution LTV, LTV/CAC and how many orders pay back the CAC

## US-07 — Break-even (`mvp`)

**As a** product manager, **I want** break-even orders and revenue per month,
**so that** I know how far the store is from covering fixed costs and marketing.

- **Given** monthly fixed costs, marketing spend and contribution per order
- **When** the dashboard loads
- **Then** I see break-even orders per month, current orders per month and the gap
- **And** if contribution per order is zero or negative I see a warning instead of a number

## US-08 — What-if scenarios (`mvp`)

**As a** product manager, **I want** to change price, product cost, CAC and the free-shipping
threshold, **so that** I can test a decision before making it.

- **Given** the baseline metrics
- **When** I move a scenario control
- **Then** every metric shows the scenario value and the difference from baseline

## US-09 — Lever impact (`mvp`)

**As a** product manager, **I want** to see which lever (price, product cost, CAC, shipping cost)
moves the monthly result the most for the same 10% change, **so that** I prioritise the right fight.

- **Given** the baseline
- **When** I open the lever impact chart
- **Then** I see the monthly result change for +10% and −10% of each lever, sorted by impact

## US-10 — CLI report (`mvp`)

**As a** technical user, **I want** to run `unit-economics --data-dir <folder>`,
**so that** I can get the same summary in a terminal or in CI.

- **Given** a folder with `products.csv`, `orders.csv` and `assumptions.json`
- **When** I run the command
- **Then** I see the summary, the five lowest-margin products and the lever impact
- **And** an invalid folder returns a clear error and exit code 1
