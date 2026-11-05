"""Unit-economics calculations. Pure functions: data in, numbers out, no I/O."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from unit_economics.models import CostAssumptions, Dataset


@dataclass(frozen=True)
class UnitEconomics:
    """Headline metrics for one dataset. Money values in BRL; ratios as fractions."""

    months: int
    orders: int
    customers: int
    net_revenue: float
    average_order_value: float
    items_per_order: float
    contribution_per_order: float
    contribution_margin: float
    free_shipping_share: float
    orders_per_month: float
    new_customers_per_month: float
    blended_cac: float | None
    orders_per_customer: float
    ltv: float
    ltv_to_cac: float | None
    payback_orders: float | None
    monthly_marketing_spend: float
    monthly_fixed_costs: float
    monthly_contribution: float
    monthly_operating_result: float
    break_even_orders_per_month: float | None
    break_even_revenue_per_month: float | None

    @property
    def break_even_progress(self) -> float | None:
        """Current orders per month as a fraction of the break-even volume."""
        if not self.break_even_orders_per_month:
            return None
        return self.orders_per_month / self.break_even_orders_per_month


def _safe_divide(numerator: float, denominator: float) -> float | None:
    return None if denominator == 0 else numerator / denominator


def order_economics(dataset: Dataset) -> pd.DataFrame:
    """One row per order with revenue, every variable cost and the contribution margin."""
    a = dataset.assumptions
    lines = dataset.orders.merge(dataset.products[["sku", "price", "unit_cost"]], on="sku")
    lines["gross"] = lines["price"] * lines["quantity"]
    lines["cogs"] = lines["unit_cost"] * lines["quantity"]

    orders = lines.groupby("order_id", as_index=False).agg(
        order_date=("order_date", "first"),
        customer_id=("customer_id", "first"),
        channel=("channel", "first"),
        items=("quantity", "sum"),
        gross=("gross", "sum"),
        cogs=("cogs", "sum"),
    )
    orders["subtotal"] = orders["gross"] * (1 - a.average_discount_rate)
    if a.free_shipping_threshold is None:
        orders["free_shipping"] = False
    else:
        orders["free_shipping"] = orders["subtotal"] >= a.free_shipping_threshold
    orders["shipping_charged"] = (~orders["free_shipping"]) * a.shipping_fee_charged
    orders["shipping_net_cost"] = a.shipping_cost_per_order - orders["shipping_charged"]
    orders["payment_fees"] = (orders["subtotal"] + orders["shipping_charged"]) * a.payment_fee_rate
    orders["taxes"] = orders["subtotal"] * a.tax_rate
    orders["packaging"] = a.packaging_cost_per_order
    orders["contribution"] = (
        orders["subtotal"]
        - orders["cogs"]
        - orders["payment_fees"]
        - orders["taxes"]
        - orders["shipping_net_cost"]
        - orders["packaging"]
    )
    return orders


def product_margins(dataset: Dataset) -> pd.DataFrame:
    """Contribution margin per unit for each SKU, before order-level costs.

    Order-level costs (shipping and packaging) are shared by the whole basket, so they are
    left out here and counted in :func:`order_economics`. Sorted from lowest margin.
    """
    a = dataset.assumptions
    products = dataset.products.copy()
    products["net_price"] = products["price"] * (1 - a.average_discount_rate)
    products["fees_and_taxes"] = products["net_price"] * (a.payment_fee_rate + a.tax_rate)
    products["contribution"] = (
        products["net_price"] - products["unit_cost"] - products["fees_and_taxes"]
    )
    products["margin"] = products["contribution"] / products["net_price"]

    units = dataset.orders.groupby("sku")["quantity"].sum()
    products["units_sold"] = products["sku"].map(units).fillna(0).astype(int)
    products["total_contribution"] = products["contribution"] * products["units_sold"]
    columns = [
        "sku",
        "name",
        "category",
        "price",
        "net_price",
        "unit_cost",
        "fees_and_taxes",
        "contribution",
        "margin",
        "units_sold",
        "total_contribution",
    ]
    return products[columns].sort_values("margin").reset_index(drop=True)


def _first_orders(orders: pd.DataFrame) -> pd.DataFrame:
    return orders.sort_values(["order_date", "order_id"]).drop_duplicates("customer_id")


def channel_cac(dataset: Dataset) -> pd.DataFrame:
    """Spend, new customers and CAC per channel.

    Every customer in the data is treated as new in the period and is credited to the channel
    of their first order. Channels with no spend have no CAC (shown as missing).
    """
    a = dataset.assumptions
    months = dataset.months
    first = _first_orders(dataset.orders.drop_duplicates("order_id"))
    new_customers = first.groupby("channel")["customer_id"].nunique()

    channels = sorted(set(new_customers.index) | set(a.monthly_marketing_spend))
    table = pd.DataFrame({"channel": channels})
    table["spend"] = table["channel"].map(a.monthly_marketing_spend).fillna(0.0) * months
    table["new_customers"] = table["channel"].map(new_customers).fillna(0).astype(int)
    paid = (table["spend"] > 0) & (table["new_customers"] > 0)
    table["cac"] = (table["spend"] / table["new_customers"]).where(paid)
    return table.sort_values("spend", ascending=False).reset_index(drop=True)


def _break_even_orders(assumptions: CostAssumptions, contribution_per_order: float) -> float | None:
    if contribution_per_order <= 0:
        return None
    monthly_costs = assumptions.monthly_fixed_costs + assumptions.total_monthly_marketing_spend
    return monthly_costs / contribution_per_order


def summarize(dataset: Dataset) -> UnitEconomics:
    """Compute every headline metric for the dataset."""
    a = dataset.assumptions
    orders = order_economics(dataset)
    months = dataset.months

    order_count = len(orders)
    customers = orders["customer_id"].nunique()
    net_revenue = float(orders["subtotal"].sum())
    aov = net_revenue / order_count
    contribution_per_order = float(orders["contribution"].mean())

    marketing = a.total_monthly_marketing_spend
    blended_cac = _safe_divide(marketing * months, customers) if marketing > 0 else None
    orders_per_customer = order_count / customers
    ltv = contribution_per_order * orders_per_customer
    ltv_to_cac = _safe_divide(ltv, blended_cac) if blended_cac else None
    payback = (
        blended_cac / contribution_per_order if blended_cac and contribution_per_order > 0 else None
    )

    orders_per_month = order_count / months
    monthly_contribution = contribution_per_order * orders_per_month
    break_even_orders = _break_even_orders(a, contribution_per_order)

    return UnitEconomics(
        months=months,
        orders=order_count,
        customers=customers,
        net_revenue=net_revenue,
        average_order_value=aov,
        items_per_order=float(orders["items"].mean()),
        contribution_per_order=contribution_per_order,
        contribution_margin=contribution_per_order / aov,
        free_shipping_share=float(orders["free_shipping"].mean()),
        orders_per_month=orders_per_month,
        new_customers_per_month=customers / months,
        blended_cac=blended_cac,
        orders_per_customer=orders_per_customer,
        ltv=ltv,
        ltv_to_cac=ltv_to_cac,
        payback_orders=payback,
        monthly_marketing_spend=marketing,
        monthly_fixed_costs=a.monthly_fixed_costs,
        monthly_contribution=monthly_contribution,
        monthly_operating_result=monthly_contribution - marketing - a.monthly_fixed_costs,
        break_even_orders_per_month=break_even_orders,
        break_even_revenue_per_month=break_even_orders * aov if break_even_orders else None,
    )


def break_even_curve(metrics: UnitEconomics, points: int = 25) -> pd.DataFrame:
    """Monthly operating result for a range of monthly order volumes (for charting)."""
    target = metrics.break_even_orders_per_month or metrics.orders_per_month
    top = max(target, metrics.orders_per_month) * 1.5
    volumes = [top * step / (points - 1) for step in range(points)]
    fixed = metrics.monthly_fixed_costs + metrics.monthly_marketing_spend
    return pd.DataFrame(
        {
            "orders_per_month": volumes,
            "operating_result": [metrics.contribution_per_order * v - fixed for v in volumes],
        }
    )
