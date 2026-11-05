import pytest

from unit_economics.metrics import summarize
from unit_economics.scenarios import Scenario, apply_scenario, compare, lever_impact


def test_baseline_scenario_changes_nothing(tiny_store):
    assert summarize(apply_scenario(tiny_store, Scenario())) == summarize(tiny_store)


def test_scenario_does_not_modify_input(tiny_store):
    apply_scenario(tiny_store, Scenario(price_change=0.5))

    assert tiny_store.products["price"].tolist() == [100.0, 50.0]


def test_cac_change_scales_spend(tiny_store):
    result = summarize(apply_scenario(tiny_store, Scenario(cac_change=0.2)))

    assert result.blended_cac == pytest.approx(180.0)


def test_lower_threshold_gives_more_free_shipping(tiny_store):
    result = summarize(apply_scenario(tiny_store, Scenario(free_shipping_threshold=50.0)))

    assert result.free_shipping_share == pytest.approx(1.0)
    assert result.contribution_per_order < summarize(tiny_store).contribution_per_order


def test_unit_cost_change_moves_contribution_by_cost(tiny_store):
    base = summarize(tiny_store)
    result = summarize(apply_scenario(tiny_store, Scenario(unit_cost_change=0.10)))

    # Total product cost is 140 across 3 orders, so +10% costs 14 / 3 per order.
    assert base.contribution_per_order - result.contribution_per_order == pytest.approx(14 / 3)


def test_invalid_scenario_rejected():
    with pytest.raises(ValueError, match="greater than -100%"):
        Scenario(price_change=-1.0)


def test_compare_reports_change(tiny_store):
    base = summarize(tiny_store)
    table = compare(base, summarize(apply_scenario(tiny_store, Scenario(cac_change=0.2))))
    row = table.set_index("metric").loc["Blended CAC"]

    assert row["change"] == pytest.approx(30.0)


def test_lever_impact_sorted_by_impact(tiny_store):
    table = lever_impact(tiny_store)

    assert set(table["lever"]) == {"Price", "Product cost", "CAC", "Shipping cost"}
    assert table["impact"].is_monotonic_decreasing
    cac = table.set_index("lever").loc["CAC"]
    assert cac["plus"] == pytest.approx(-30.0)  # +10% of R$300 spend
