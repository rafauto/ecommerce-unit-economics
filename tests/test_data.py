import io
import json

import pytest

from unit_economics.data import (
    DataError,
    load_assumptions,
    load_dataset,
    load_dataset_from_dir,
    load_orders,
    load_products,
)
from unit_economics.models import CostAssumptions

PRODUCTS = "sku,name,category,price,unit_cost\nA,Item,Cat,10,4\n"
ORDERS = "order_id,order_date,customer_id,channel,sku,quantity\nO1,2026-07-01,C1,ads,A,1\n"


def test_loads_valid_files():
    dataset = load_dataset(io.StringIO(PRODUCTS), io.StringIO(ORDERS), CostAssumptions())

    assert list(dataset.products["sku"]) == ["A"]
    assert dataset.months == 1


def test_missing_column_has_clear_error():
    with pytest.raises(DataError, match="missing column\\(s\\): unit_cost"):
        load_products(io.StringIO("sku,name,category,price\nA,Item,Cat,10\n"))


def test_non_numeric_price_points_to_row():
    with pytest.raises(DataError, match="row 2"):
        load_products(io.StringIO("sku,name,category,price,unit_cost\nA,Item,Cat,ten,4\n"))


def test_duplicate_sku_rejected():
    with pytest.raises(DataError, match="more than once"):
        load_products(io.StringIO(PRODUCTS + "A,Other,Cat,12,5\n"))


def test_non_positive_price_rejected():
    with pytest.raises(DataError, match="greater than zero"):
        load_products(io.StringIO("sku,name,category,price,unit_cost\nA,Item,Cat,0,4\n"))


def test_unknown_sku_in_orders_rejected():
    with pytest.raises(DataError, match="not in the product catalog: Z"):
        load_orders(io.StringIO(ORDERS.replace(",A,", ",Z,")), known_skus={"A"})


def test_invalid_date_rejected():
    with pytest.raises(DataError, match="valid date"):
        load_orders(io.StringIO(ORDERS.replace("2026-07-01", "yesterday")))


def test_empty_file_rejected():
    with pytest.raises(DataError, match="could not be read"):
        load_products(io.StringIO(""))


def test_missing_folder_rejected(tmp_path):
    with pytest.raises(DataError, match="Data folder not found"):
        load_dataset_from_dir(tmp_path / "nope")


def test_assumptions_reject_unknown_field():
    with pytest.raises(DataError, match="Unknown assumption field"):
        load_assumptions(io.StringIO(json.dumps({"tax": 0.1})))


def test_assumptions_reject_invalid_rate():
    with pytest.raises(DataError, match="between 0 and 1"):
        load_assumptions(io.StringIO(json.dumps({"tax_rate": 6})))


def test_assumptions_reject_negative_spend():
    with pytest.raises(ValueError, match="cannot be negative"):
        CostAssumptions(monthly_marketing_spend={"ads": -1})
