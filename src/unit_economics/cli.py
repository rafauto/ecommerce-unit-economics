"""Command-line interface: ``unit-economics --data-dir examples/sample-store``."""

from __future__ import annotations

import argparse
import os
import sys

from unit_economics.data import DataError, load_dataset_from_dir
from unit_economics.metrics import product_margins, summarize
from unit_economics.report import brl, format_summary, pct
from unit_economics.scenarios import Scenario, apply_scenario, compare, lever_impact

DEFAULT_DATA_DIR = "examples/sample-store"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="unit-economics",
        description="Unit economics report for an e-commerce store (AOV, margin, CAC, break-even).",
    )
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("UNIT_ECONOMICS_DATA_DIR", DEFAULT_DATA_DIR),
        help="Folder with products.csv, orders.csv and assumptions.json "
        f"(default: $UNIT_ECONOMICS_DATA_DIR or {DEFAULT_DATA_DIR}).",
    )
    scenario = parser.add_argument_group("what-if scenario (values in percent, e.g. 5 = +5%%)")
    scenario.add_argument("--price-change", type=float, default=0.0)
    scenario.add_argument("--unit-cost-change", type=float, default=0.0)
    scenario.add_argument("--cac-change", type=float, default=0.0)
    scenario.add_argument("--shipping-cost-change", type=float, default=0.0)
    scenario.add_argument(
        "--free-shipping-threshold", type=float, default=None, help="New threshold in BRL."
    )
    return parser


def _print_section(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        dataset = load_dataset_from_dir(args.data_dir)
        scenario = Scenario(
            price_change=args.price_change / 100,
            unit_cost_change=args.unit_cost_change / 100,
            cac_change=args.cac_change / 100,
            shipping_cost_change=args.shipping_cost_change / 100,
            free_shipping_threshold=args.free_shipping_threshold,
        )
    except (DataError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    baseline = summarize(dataset)
    _print_section("Unit economics summary")
    print(format_summary(baseline))

    _print_section("Five lowest-margin products (per unit, before shipping)")
    for row in product_margins(dataset).head(5).itertuples():
        print(f"{row.sku:<8} {row.name:<28} {brl(row.contribution):>12}  {pct(row.margin):>6}")

    _print_section("Lever impact on monthly result (-10% / +10%)")
    for row in lever_impact(dataset).itertuples():
        print(f"{row.lever:<14} {brl(row.minus):>14}  {brl(row.plus):>14}")

    if not scenario.is_baseline:
        result = summarize(apply_scenario(dataset, scenario))
        _print_section("Scenario vs baseline")
        for row in compare(baseline, result).itertuples():
            print(
                f"{row.metric:<28} {_fmt(row.metric, row.baseline):>14}  ->  "
                f"{_fmt(row.metric, row.scenario):>14}"
            )
    return 0


def _fmt(metric: str, value: float | None) -> str:
    if metric == "Contribution margin":
        return pct(value)
    if metric in {"LTV / CAC", "Payback (orders)", "Break-even orders / month"}:
        return "n/a" if value is None else f"{value:,.1f}"
    return brl(value)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
