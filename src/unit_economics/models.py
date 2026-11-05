"""Domain models: cost assumptions and the dataset the calculations run on."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

import pandas as pd

_RATE_FIELDS = ("payment_fee_rate", "tax_rate", "average_discount_rate")
_MONEY_FIELDS = (
    "shipping_cost_per_order",
    "shipping_fee_charged",
    "free_shipping_threshold",
    "packaging_cost_per_order",
    "monthly_fixed_costs",
)


@dataclass(frozen=True)
class CostAssumptions:
    """Variable and fixed cost assumptions for the store (all money values in BRL).

    Rates are fractions: 0.039 means 3.9%.
    """

    payment_fee_rate: float = 0.039
    tax_rate: float = 0.06
    average_discount_rate: float = 0.0
    shipping_cost_per_order: float = 0.0
    shipping_fee_charged: float = 0.0
    free_shipping_threshold: float | None = None
    packaging_cost_per_order: float = 0.0
    monthly_fixed_costs: float = 0.0
    monthly_marketing_spend: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in _RATE_FIELDS:
            value = getattr(self, name)
            if not 0 <= value < 1:
                raise ValueError(f"'{name}' must be between 0 and 1 (got {value}).")
        for name in _MONEY_FIELDS:
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"'{name}' cannot be negative (got {value}).")
        for channel, spend in self.monthly_marketing_spend.items():
            if spend < 0:
                raise ValueError(f"Marketing spend for '{channel}' cannot be negative.")

    @property
    def total_monthly_marketing_spend(self) -> float:
        return float(sum(self.monthly_marketing_spend.values()))

    def with_changes(self, **changes: Any) -> CostAssumptions:
        """Return a copy with some fields changed (validation runs again)."""
        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CostAssumptions:
        known = set(cls.__dataclass_fields__)
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"Unknown assumption field(s): {', '.join(sorted(unknown))}.")
        spend = {str(k): float(v) for k, v in data.get("monthly_marketing_spend", {}).items()}
        values = {
            k: (None if v is None else float(v))
            for k, v in data.items()
            if k != "monthly_marketing_spend"
        }
        return cls(**values, monthly_marketing_spend=spend)


@dataclass(frozen=True)
class Dataset:
    """Everything the calculator needs: catalog, order lines and assumptions.

    ``products`` columns: sku, name, category, price, unit_cost.
    ``orders`` columns: order_id, order_date, customer_id, channel, sku, quantity
    (one row per order line).
    """

    products: pd.DataFrame
    orders: pd.DataFrame
    assumptions: CostAssumptions

    @property
    def months(self) -> int:
        """Number of calendar months covered by the orders (at least 1)."""
        periods = self.orders["order_date"].dt.to_period("M").nunique()
        return max(int(periods), 1)
