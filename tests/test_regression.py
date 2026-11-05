"""Regression tests: lock the sample-store results shown in the README.

If you change the calculations on purpose, update these numbers and the README together.
"""

import pytest

from unit_economics.metrics import product_margins, summarize
from unit_economics.scenarios import Scenario, apply_scenario


def test_sample_store_headline_numbers(sample_store):
    m = summarize(sample_store)

    assert m.orders == 3065
    assert m.average_order_value == pytest.approx(121.74, abs=0.01)
    assert m.contribution_per_order == pytest.approx(39.44, abs=0.01)
    assert m.blended_cac == pytest.approx(28.27, abs=0.01)
    assert m.break_even_orders_per_month == pytest.approx(1052.1, abs=0.1)
    assert m.monthly_operating_result == pytest.approx(-1201.04, abs=0.01)


def test_sample_store_lowest_margin_product(sample_store):
    assert product_margins(sample_store).iloc[0]["sku"] == "GFT-001"


def test_sample_store_price_scenario_turns_positive(sample_store):
    result = summarize(apply_scenario(sample_store, Scenario(price_change=0.05)))

    assert result.monthly_operating_result == pytest.approx(4096.58, abs=0.01)
