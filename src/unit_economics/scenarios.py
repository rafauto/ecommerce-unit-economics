"""What-if scenarios and lever impact analysis."""

from __future__ import annotations

from dataclasses import dataclass, fields

import pandas as pd

from unit_economics.metrics import UnitEconomics, summarize
from unit_economics.models import Dataset


@dataclass(frozen=True)
class Scenario:
    """Relative changes applied to the baseline. 0.05 means +5%.

    Order volume and basket composition stay the same: this MVP does not model how
    customers react to a new price (see "Limitations" in the README).
    """

    price_change: float = 0.0
    unit_cost_change: float = 0.0
    cac_change: float = 0.0
    shipping_cost_change: float = 0.0
    free_shipping_threshold: float | None = None  # None keeps the baseline threshold

    def __post_init__(self) -> None:
        for item in fields(self):
            value = getattr(self, item.name)
            if item.name != "free_shipping_threshold" and value <= -1:
                raise ValueError(f"'{item.name}' must be greater than -100%.")
        if self.free_shipping_threshold is not None and self.free_shipping_threshold < 0:
            raise ValueError("'free_shipping_threshold' cannot be negative.")

    @property
    def is_baseline(self) -> bool:
        return self == Scenario()


def apply_scenario(dataset: Dataset, scenario: Scenario) -> Dataset:
    """Return a new dataset with the scenario applied. The input is not modified."""
    products = dataset.products.copy()
    products["price"] = products["price"] * (1 + scenario.price_change)
    products["unit_cost"] = products["unit_cost"] * (1 + scenario.unit_cost_change)

    a = dataset.assumptions
    # CAC = spend / new customers. With the same customers, changing CAC means changing spend.
    spend = {k: v * (1 + scenario.cac_change) for k, v in a.monthly_marketing_spend.items()}
    threshold = (
        a.free_shipping_threshold
        if scenario.free_shipping_threshold is None
        else scenario.free_shipping_threshold
    )
    assumptions = a.with_changes(
        shipping_cost_per_order=a.shipping_cost_per_order * (1 + scenario.shipping_cost_change),
        free_shipping_threshold=threshold,
        monthly_marketing_spend=spend,
    )
    return Dataset(products=products, orders=dataset.orders, assumptions=assumptions)


COMPARED_METRICS = {
    "average_order_value": "Average order value",
    "contribution_per_order": "Contribution per order",
    "contribution_margin": "Contribution margin",
    "blended_cac": "Blended CAC",
    "ltv_to_cac": "LTV / CAC",
    "payback_orders": "Payback (orders)",
    "break_even_orders_per_month": "Break-even orders / month",
    "monthly_operating_result": "Monthly operating result",
}


def compare(baseline: UnitEconomics, scenario: UnitEconomics) -> pd.DataFrame:
    """Side-by-side table of the main metrics for baseline and scenario."""
    rows = []
    for attribute, label in COMPARED_METRICS.items():
        before = getattr(baseline, attribute)
        after = getattr(scenario, attribute)
        change = None if before is None or after is None else after - before
        rows.append({"metric": label, "baseline": before, "scenario": after, "change": change})
    return pd.DataFrame(rows)


LEVERS = {
    "Price": "price_change",
    "Product cost": "unit_cost_change",
    "CAC": "cac_change",
    "Shipping cost": "shipping_cost_change",
}


def lever_impact(dataset: Dataset, delta: float = 0.10) -> pd.DataFrame:
    """Change in monthly operating result when each lever moves by -delta and +delta.

    Sorted from the lever with the biggest impact to the smallest.
    """
    base = summarize(dataset).monthly_operating_result
    rows = []
    for label, attribute in LEVERS.items():
        down = summarize(apply_scenario(dataset, Scenario(**{attribute: -delta})))
        up = summarize(apply_scenario(dataset, Scenario(**{attribute: delta})))
        rows.append(
            {
                "lever": label,
                "minus": down.monthly_operating_result - base,
                "plus": up.monthly_operating_result - base,
            }
        )
    table = pd.DataFrame(rows)
    table["impact"] = table[["minus", "plus"]].abs().max(axis=1)
    return table.sort_values("impact", ascending=False).reset_index(drop=True)
