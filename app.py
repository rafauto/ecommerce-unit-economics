"""Streamlit interface for the unit economics calculator.

Run with: streamlit run app.py
All calculations live in the ``unit_economics`` package; this file only handles the UI.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from unit_economics import (
    CostAssumptions,
    DataError,
    Dataset,
    Scenario,
    apply_scenario,
    break_even_curve,
    channel_cac,
    compare,
    lever_impact,
    load_dataset,
    product_margins,
    summarize,
)
from unit_economics.data import load_assumptions
from unit_economics.report import brl, number, pct, verdict

SAMPLE_DIR = Path(os.environ.get("UNIT_ECONOMICS_DATA_DIR", "examples/sample-store"))

st.set_page_config(page_title="E-commerce Unit Economics", page_icon="🧮", layout="wide")


@st.cache_data(show_spinner=False)
def _load(products, orders) -> tuple[pd.DataFrame, pd.DataFrame]:
    dataset = load_dataset(products, orders, CostAssumptions())
    return dataset.products, dataset.orders


def _sidebar_data() -> tuple[object, object, CostAssumptions]:
    st.sidebar.header("1. Data")
    use_own = st.sidebar.toggle("Upload my own CSVs", value=False)
    defaults = load_assumptions(SAMPLE_DIR / "assumptions.json")
    if not use_own:
        st.sidebar.caption("Using the fictional sample store *Lumi Custom*.")
        return SAMPLE_DIR / "products.csv", SAMPLE_DIR / "orders.csv", defaults

    st.sidebar.caption("Use anonymised data only. Files are processed in memory, never stored.")
    products = st.sidebar.file_uploader("products.csv", type="csv")
    orders = st.sidebar.file_uploader("orders.csv", type="csv")
    if products is None or orders is None:
        st.info("Upload both files to continue. See the README for the expected columns.")
        st.stop()
    return products, orders, defaults


def _sidebar_assumptions(defaults: CostAssumptions, channels: list[str]) -> CostAssumptions:
    st.sidebar.header("2. Cost assumptions")
    side = st.sidebar
    payment = side.number_input(
        "Payment fee (%)", 0.0, 99.0, value=float(defaults.payment_fee_rate * 100)
    )
    tax = side.number_input("Taxes on sales (%)", 0.0, 99.0, value=float(defaults.tax_rate * 100))
    discount = side.number_input(
        "Average discount (%)", 0.0, 99.0, value=float(defaults.average_discount_rate * 100)
    )
    shipping_cost = side.number_input(
        "Shipping cost per order (R$)", 0.0, value=float(defaults.shipping_cost_per_order)
    )
    shipping_fee = side.number_input(
        "Shipping fee charged to customer (R$)", 0.0, value=float(defaults.shipping_fee_charged)
    )
    threshold = side.number_input(
        "Free shipping above (R$, 0 = never)",
        0.0,
        value=float(defaults.free_shipping_threshold or 0.0),
    )
    packaging = side.number_input(
        "Packaging per order (R$)", 0.0, value=float(defaults.packaging_cost_per_order)
    )
    fixed = side.number_input(
        "Monthly fixed costs (R$)", 0.0, value=float(defaults.monthly_fixed_costs), step=1000.0
    )

    side.subheader("Monthly marketing spend (R$)")
    spend = {
        channel: side.number_input(
            channel,
            0.0,
            value=float(defaults.monthly_marketing_spend.get(channel, 0.0)),
            step=500.0,
            key=f"spend_{channel}",
        )
        for channel in channels
    }
    return CostAssumptions(
        payment_fee_rate=payment / 100,
        tax_rate=tax / 100,
        average_discount_rate=discount / 100,
        shipping_cost_per_order=shipping_cost,
        shipping_fee_charged=shipping_fee,
        free_shipping_threshold=threshold or None,
        packaging_cost_per_order=packaging,
        monthly_fixed_costs=fixed,
        monthly_marketing_spend=spend,
    )


def _sidebar_scenario(current_threshold: float | None) -> Scenario:
    st.sidebar.header("3. What-if scenario")
    price = st.sidebar.slider("Price change (%)", -30, 30, 0)
    cost = st.sidebar.slider("Product cost change (%)", -30, 30, 0)
    cac = st.sidebar.slider("CAC change (%)", -50, 50, 0)
    shipping = st.sidebar.slider("Shipping cost change (%)", -50, 50, 0)
    threshold = st.sidebar.number_input(
        "Scenario free-shipping threshold (R$)", 0.0, value=float(current_threshold or 0.0)
    )
    return Scenario(
        price_change=price / 100,
        unit_cost_change=cost / 100,
        cac_change=cac / 100,
        shipping_cost_change=shipping / 100,
        free_shipping_threshold=None if threshold == (current_threshold or 0.0) else threshold,
    )


def _delta(after: float | None, before: float | None, fmt) -> str | None:
    if after is None or before is None or after == before:
        return None
    return fmt(after - before)


def _kpis(base, result) -> None:
    rows = [
        ("Average order value", "average_order_value", brl, "normal"),
        ("Contribution / order", "contribution_per_order", brl, "normal"),
        ("Contribution margin", "contribution_margin", pct, "normal"),
        ("Blended CAC", "blended_cac", brl, "inverse"),
        ("LTV / CAC", "ltv_to_cac", lambda v: number(v, 2), "normal"),
        ("CAC payback (orders)", "payback_orders", number, "inverse"),
        (
            "Break-even orders / month",
            "break_even_orders_per_month",
            lambda v: number(v, 0),
            "inverse",
        ),
        ("Monthly operating result", "monthly_operating_result", brl, "normal"),
    ]
    for start in range(0, len(rows), 4):
        for column, (label, attr, fmt, color) in zip(
            st.columns(4), rows[start : start + 4], strict=False
        ):
            after, before = getattr(result, attr), getattr(base, attr)
            column.metric(label, fmt(after), _delta(after, before, fmt), delta_color=color)


def main() -> None:
    st.title("🧮 E-commerce Unit Economics Calculator")
    st.caption(
        "Average order value, margin per product, CAC, LTV/CAC and break-even, with what-if "
        "scenarios. Sample data is fictional."
    )

    products_src, orders_src, defaults = _sidebar_data()
    try:
        products, orders = _load(products_src, orders_src)
    except DataError as error:
        st.error(f"Could not load the data: {error}")
        st.stop()

    channels = sorted(set(orders["channel"]) | set(defaults.monthly_marketing_spend))
    try:
        assumptions = _sidebar_assumptions(defaults, channels)
        scenario = _sidebar_scenario(assumptions.free_shipping_threshold)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    dataset = Dataset(products, orders, assumptions)
    base = summarize(dataset)
    scenario_data = apply_scenario(dataset, scenario)
    result = summarize(scenario_data)

    if not scenario.is_baseline:
        st.info("Scenario active: values show the scenario, deltas compare with the baseline.")
    _kpis(base, result)
    (st.success if result.monthly_operating_result >= 0 else st.warning)(verdict(result))

    tab_be, tab_products, tab_cac, tab_levers, tab_compare = st.tabs(
        ["Break-even", "Products", "CAC by channel", "Lever impact", "Scenario vs baseline"]
    )

    with tab_be:
        if result.break_even_orders_per_month is None:
            st.error("Contribution per order is zero or negative, so there is no break-even.")
        else:
            curve = break_even_curve(result).set_index("orders_per_month")
            st.line_chart(curve, x_label="Orders per month", y_label="Monthly result (R$)")
            st.write(
                f"Break-even at **{number(result.break_even_orders_per_month, 0)} orders/month** "
                f"({brl(result.break_even_revenue_per_month)} revenue). "
                f"Current volume: **{number(result.orders_per_month, 0)} orders/month**."
            )

    with tab_products:
        margins = product_margins(scenario_data)
        shown = margins.assign(margin=margins["margin"] * 100)
        st.dataframe(
            shown,
            hide_index=True,
            column_config={
                "price": st.column_config.NumberColumn("Price", format="R$ %.2f"),
                "net_price": st.column_config.NumberColumn("Net price", format="R$ %.2f"),
                "unit_cost": st.column_config.NumberColumn("Unit cost", format="R$ %.2f"),
                "fees_and_taxes": st.column_config.NumberColumn("Fees + taxes", format="R$ %.2f"),
                "contribution": st.column_config.NumberColumn("Contribution", format="R$ %.2f"),
                "margin": st.column_config.NumberColumn("Margin", format="%.1f%%"),
                "total_contribution": st.column_config.NumberColumn(
                    "Total contribution", format="R$ %.0f"
                ),
            },
        )
        st.caption("Per unit, before shipping and packaging (those are shared by the order).")
        st.download_button(
            "Download product margins (CSV)",
            margins.to_csv(index=False).encode("utf-8"),
            "product_margins.csv",
            "text/csv",
        )

    with tab_cac:
        cac = channel_cac(scenario_data)
        st.dataframe(
            cac,
            hide_index=True,
            column_config={
                "spend": st.column_config.NumberColumn("Spend (period)", format="R$ %.0f"),
                "cac": st.column_config.NumberColumn("CAC", format="R$ %.2f"),
            },
        )
        st.caption("Each customer is credited to the channel of their first order.")

    with tab_levers:
        levers = lever_impact(dataset)
        chart = levers.set_index("lever")[["minus", "plus"]].rename(
            columns={"minus": "-10%", "plus": "+10%"}
        )
        st.bar_chart(chart, horizontal=True, stack=False, y_label="", x_label="R$ per month")
        top = levers.iloc[0]
        st.write(
            f"**{top['lever']}** is the strongest lever: a 10% change moves the monthly result "
            f"by up to {brl(top['impact'])}."
        )

    with tab_compare:
        table = compare(base, result)
        st.dataframe(table, hide_index=True)


main()
