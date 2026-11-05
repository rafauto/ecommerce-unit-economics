"""E-commerce unit economics: AOV, product margin, CAC, LTV/CAC and break-even."""

from unit_economics.data import DataError, load_dataset, load_dataset_from_dir
from unit_economics.metrics import (
    UnitEconomics,
    break_even_curve,
    channel_cac,
    order_economics,
    product_margins,
    summarize,
)
from unit_economics.models import CostAssumptions, Dataset
from unit_economics.scenarios import Scenario, apply_scenario, compare, lever_impact

__version__ = "0.1.0"

__all__ = [
    "CostAssumptions",
    "DataError",
    "Dataset",
    "Scenario",
    "UnitEconomics",
    "apply_scenario",
    "break_even_curve",
    "channel_cac",
    "compare",
    "lever_impact",
    "load_dataset",
    "load_dataset_from_dir",
    "order_economics",
    "product_margins",
    "summarize",
]
