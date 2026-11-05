"""Load and validate the input files (products CSV, orders CSV and assumptions JSON)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import IO

import pandas as pd

from unit_economics.models import CostAssumptions, Dataset

Source = str | Path | IO

PRODUCT_COLUMNS = ["sku", "name", "category", "price", "unit_cost"]
ORDER_COLUMNS = ["order_id", "order_date", "customer_id", "channel", "sku", "quantity"]
MAX_ROWS = 500_000


class DataError(ValueError):
    """Raised when an input file is missing, malformed or inconsistent."""


def _read_csv(source: Source, label: str, columns: list[str]) -> pd.DataFrame:
    try:
        frame = pd.read_csv(source, dtype={"sku": str, "order_id": str, "customer_id": str})
    except FileNotFoundError as error:
        raise DataError(f"{label} file not found: {source}") from error
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as error:
        raise DataError(f"{label} file could not be read as CSV: {error}") from error

    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise DataError(f"{label} file is missing column(s): {', '.join(missing)}.")
    if frame.empty:
        raise DataError(f"{label} file has no rows.")
    if len(frame) > MAX_ROWS:
        raise DataError(f"{label} file has more than {MAX_ROWS:,} rows.")
    return frame[columns].copy()


def _to_number(frame: pd.DataFrame, column: str, label: str) -> pd.Series:
    values = pd.to_numeric(frame[column], errors="coerce")
    if values.isna().any():
        row = int(values.isna().to_numpy().argmax()) + 2  # +2: header and 1-based rows
        raise DataError(f"{label}: '{column}' must be a number (check row {row}).")
    return values.astype(float)


def load_products(source: Source) -> pd.DataFrame:
    products = _read_csv(source, "Products", PRODUCT_COLUMNS)
    products["price"] = _to_number(products, "price", "Products")
    products["unit_cost"] = _to_number(products, "unit_cost", "Products")

    if products["sku"].duplicated().any():
        duplicated = products.loc[products["sku"].duplicated(), "sku"].iloc[0]
        raise DataError(f"Products: SKU '{duplicated}' appears more than once.")
    if (products["price"] <= 0).any():
        raise DataError("Products: every price must be greater than zero.")
    if (products["unit_cost"] < 0).any():
        raise DataError("Products: unit_cost cannot be negative.")
    return products.reset_index(drop=True)


def load_orders(source: Source, known_skus: set[str] | None = None) -> pd.DataFrame:
    orders = _read_csv(source, "Orders", ORDER_COLUMNS)
    orders["quantity"] = _to_number(orders, "quantity", "Orders")
    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
    orders["channel"] = orders["channel"].astype(str).str.strip()

    if orders["order_date"].isna().any():
        raise DataError("Orders: every order_date must be a valid date (YYYY-MM-DD).")
    if (orders["quantity"] <= 0).any():
        raise DataError("Orders: every quantity must be greater than zero.")
    if known_skus is not None:
        unknown = sorted(set(orders["sku"]) - known_skus)
        if unknown:
            preview = ", ".join(unknown[:5])
            raise DataError(f"Orders reference SKU(s) not in the product catalog: {preview}.")
    return orders.reset_index(drop=True)


def load_assumptions(source: Source) -> CostAssumptions:
    try:
        if hasattr(source, "read"):
            raw = json.load(source)  # type: ignore[arg-type]
        else:
            raw = json.loads(Path(source).read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise DataError(f"Assumptions file not found: {source}") from error
    except json.JSONDecodeError as error:
        raise DataError(f"Assumptions file is not valid JSON: {error}") from error

    try:
        return CostAssumptions.from_dict(raw)
    except (TypeError, ValueError) as error:
        raise DataError(f"Assumptions: {error}") from error


def load_dataset(
    products: Source, orders: Source, assumptions: CostAssumptions | Source
) -> Dataset:
    catalog = load_products(products)
    order_lines = load_orders(orders, known_skus=set(catalog["sku"]))
    if not isinstance(assumptions, CostAssumptions):
        assumptions = load_assumptions(assumptions)
    return Dataset(products=catalog, orders=order_lines, assumptions=assumptions)


def load_dataset_from_dir(directory: str | Path) -> Dataset:
    """Load ``products.csv``, ``orders.csv`` and ``assumptions.json`` from a folder."""
    folder = Path(directory)
    if not folder.is_dir():
        raise DataError(f"Data folder not found: {folder}")
    return load_dataset(folder / "products.csv", folder / "orders.csv", folder / "assumptions.json")
