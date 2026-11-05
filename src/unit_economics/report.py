"""Formatting helpers and a plain-language summary shared by the CLI and the app."""

from __future__ import annotations

from unit_economics.metrics import UnitEconomics


def brl(value: float | None) -> str:
    """Format a value as Brazilian reais, e.g. ``R$ 1,234.56`` or ``-R$ 80.00``."""
    if value is None:
        return "n/a"
    sign = "-" if value < 0 else ""
    return f"{sign}R$ {abs(value):,.2f}"


def pct(value: float | None, decimals: int = 1) -> str:
    return "n/a" if value is None else f"{value * 100:.{decimals}f}%"


def number(value: float | None, decimals: int = 1) -> str:
    return "n/a" if value is None else f"{value:,.{decimals}f}"


def verdict(metrics: UnitEconomics) -> str:
    """One sentence a PM can say in a meeting."""
    if metrics.contribution_per_order <= 0:
        return (
            "Each order loses money before marketing and fixed costs: selling more makes the "
            "result worse. Fix price, product cost or shipping before scaling."
        )
    gap = metrics.break_even_orders_per_month - metrics.orders_per_month
    if gap <= 0:
        return (
            f"The store is above break-even: {number(metrics.orders_per_month, 0)} orders/month "
            f"against {number(metrics.break_even_orders_per_month, 0)} needed."
        )
    return (
        f"The store needs {number(gap, 0)} more orders per month "
        f"({pct(metrics.break_even_progress, 0)} of break-even today), "
        f"or a higher contribution per order, to cover fixed costs and marketing."
    )


def summary_lines(metrics: UnitEconomics) -> list[tuple[str, str]]:
    """Label/value pairs in reading order."""
    return [
        ("Period analysed", f"{metrics.months} month(s), {metrics.orders:,} orders"),
        ("Average order value (AOV)", brl(metrics.average_order_value)),
        ("Items per order", number(metrics.items_per_order, 2)),
        ("Orders with free shipping", pct(metrics.free_shipping_share)),
        ("Contribution per order", brl(metrics.contribution_per_order)),
        ("Contribution margin", pct(metrics.contribution_margin)),
        ("Blended CAC", brl(metrics.blended_cac)),
        ("Orders per customer (period)", number(metrics.orders_per_customer, 2)),
        ("Contribution LTV (period)", brl(metrics.ltv)),
        ("LTV / CAC", number(metrics.ltv_to_cac, 2)),
        ("CAC payback (orders)", number(metrics.payback_orders, 1)),
        ("Orders per month", number(metrics.orders_per_month, 0)),
        ("Break-even orders per month", number(metrics.break_even_orders_per_month, 0)),
        ("Break-even revenue per month", brl(metrics.break_even_revenue_per_month)),
        ("Monthly operating result", brl(metrics.monthly_operating_result)),
    ]


def format_summary(metrics: UnitEconomics) -> str:
    width = max(len(label) for label, _ in summary_lines(metrics))
    body = "\n".join(f"{label:<{width}}  {value}" for label, value in summary_lines(metrics))
    return f"{body}\n\n{verdict(metrics)}"
