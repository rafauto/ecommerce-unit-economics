"""Unit tests for the calculations, using the hand-checked tiny store.

Tiny store (one month, July 2026):
- O1, customer C1 via "paid": 1x A (R$100). Below the R$150 threshold, so the customer pays
  R$10 shipping. Contribution = 100 - 40 cost - 5.50 fee - 10 tax - 10 net shipping - 5 pack = 29.50
- O2, customer C1 via "organic": 1x A + 2x B (R$200). Free shipping.
  Contribution = 200 - 80 - 10 - 20 - 20 - 5 = 65.00
- O3, customer C2 via "organic": 1x B (R$50).
  Contribution = 50 - 20 - 3 - 5 - 10 - 5 = 7.00
"""

import math

import pytest

from unit_economics.metrics import (
    break_even_curve,
    channel_cac,
    order_economics,
    product_margins,
    summarize,
)


def test_order_contribution_includes_every_variable_cost(tiny_store):
    orders = order_economics(tiny_store).set_index("order_id")

    assert orders.loc["O1", "contribution"] == pytest.approx(29.5)
    assert orders.loc["O2", "contribution"] == pytest.approx(65.0)
    assert orders.loc["O3", "contribution"] == pytest.approx(7.0)


def test_free_shipping_applies_only_above_threshold(tiny_store):
    orders = order_economics(tiny_store).set_index("order_id")

    assert orders["free_shipping"].to_dict() == {"O1": False, "O2": True, "O3": False}
    assert orders.loc["O2", "shipping_net_cost"] == pytest.approx(20.0)
    assert orders.loc["O1", "shipping_net_cost"] == pytest.approx(10.0)


def test_summary_headline_metrics(tiny_store):
    m = summarize(tiny_store)

    assert m.orders == 3
    assert m.customers == 2
    assert m.average_order_value == pytest.approx(350 / 3)
    assert m.contribution_per_order == pytest.approx(101.5 / 3)
    assert m.blended_cac == pytest.approx(150.0)
    assert m.orders_per_customer == pytest.approx(1.5)
    assert m.ltv == pytest.approx(50.75)
    assert m.ltv_to_cac == pytest.approx(50.75 / 150)
    assert m.payback_orders == pytest.approx(150 / (101.5 / 3))
    assert m.monthly_operating_result == pytest.approx(101.5 - 300 - 1000)
    assert m.break_even_orders_per_month == pytest.approx(1300 / (101.5 / 3))
    assert m.break_even_revenue_per_month == pytest.approx(1300 / (101.5 / 3) * 350 / 3)


def test_product_margins_sorted_and_counted(tiny_store):
    table = product_margins(tiny_store).set_index("sku")

    assert table.loc["A", "contribution"] == pytest.approx(45.0)
    assert table.loc["B", "contribution"] == pytest.approx(22.5)
    assert table.loc["A", "margin"] == pytest.approx(0.45)
    assert table.loc["A", "units_sold"] == 2
    assert table.loc["B", "units_sold"] == 3


def test_cac_credits_channel_of_first_order(tiny_store):
    table = channel_cac(tiny_store).set_index("channel")

    assert table.loc["paid", "new_customers"] == 1
    assert table.loc["paid", "cac"] == pytest.approx(300.0)
    assert table.loc["organic", "new_customers"] == 1
    assert math.isnan(table.loc["organic", "cac"])


def test_no_break_even_when_orders_lose_money(tiny_store):
    losing = tiny_store.assumptions.with_changes(shipping_cost_per_order=500.0)
    m = summarize(type(tiny_store)(tiny_store.products, tiny_store.orders, losing))

    assert m.contribution_per_order < 0
    assert m.break_even_orders_per_month is None
    assert m.break_even_progress is None
    assert m.payback_orders is None


def test_no_cac_without_marketing_spend(tiny_store):
    free = tiny_store.assumptions.with_changes(monthly_marketing_spend={})
    m = summarize(type(tiny_store)(tiny_store.products, tiny_store.orders, free))

    assert m.blended_cac is None
    assert m.ltv_to_cac is None


def test_break_even_curve_crosses_zero_at_break_even(tiny_store):
    m = summarize(tiny_store)
    curve = break_even_curve(m)

    assert curve["operating_result"].iloc[0] == pytest.approx(-1300.0)
    assert curve["operating_result"].iloc[-1] > 0
