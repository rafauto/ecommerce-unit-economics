"""Generate the fictional "Lumi Custom" sample store used by the demo and the tests.

Every product, customer and order here is invented. The generator is deterministic (fixed
seed), so running it again produces exactly the same files.

Usage:
    python examples/generate_sample_data.py
"""

from __future__ import annotations

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
OUTPUT_DIR = Path(__file__).parent / "sample-store"
START_DATE = date(2026, 7, 1)
DAYS = 92  # July, August and September 2026
NEW_CUSTOMERS = 2_600

# sku, name, category, price (BRL), unit cost (BRL), popularity weight
# Unit cost = blank item + personalisation (printing or engraving).
PRODUCTS = [
    ("MUG-001", "Custom ceramic mug 325 ml", "Mugs", 49.90, 18.50, 10),
    ("MUG-002", "Magic colour-changing mug", "Mugs", 69.90, 28.00, 6),
    ("MUG-003", "Enamel camping mug", "Mugs", 79.90, 36.00, 3),
    ("BTL-001", "Engraved steel bottle 500 ml", "Bottles", 119.90, 52.00, 6),
    ("BTL-002", "Thermal tumbler 600 ml", "Bottles", 139.90, 63.00, 4),
    ("BTL-003", "Aluminium squeeze 500 ml", "Bottles", 44.90, 19.50, 7),
    ("NTB-001", "Custom cover notebook A5", "Notebooks", 54.90, 21.00, 8),
    ("NTB-002", "Personalised planner 2027", "Notebooks", 89.90, 41.00, 4),
    ("NTB-003", "Kraft pocket notebook", "Notebooks", 24.90, 11.80, 6),
    ("PEN-001", "Engraved metal pen", "Pens", 29.90, 13.40, 7),
    ("PEN-002", "Pen and gift box kit", "Pens", 64.90, 33.00, 4),
    ("GFT-001", "Gift wrapping", "Services", 9.90, 6.50, 4),
]

# channel, share of new customers, monthly spend (BRL)
CHANNELS = [
    ("paid_social", 0.36, 12_000),
    ("google_ads", 0.24, 7_500),
    ("influencers", 0.10, 5_000),
    ("organic", 0.22, 0),
    ("email", 0.08, 0),
]

ASSUMPTIONS = {
    "payment_fee_rate": 0.039,
    "tax_rate": 0.06,
    "average_discount_rate": 0.05,
    "shipping_cost_per_order": 19.0,
    "shipping_fee_charged": 12.9,
    "free_shipping_threshold": 149.0,
    "packaging_cost_per_order": 4.5,
    "monthly_fixed_costs": 17_000,
    "monthly_marketing_spend": {name: spend for name, _, spend in CHANNELS},
}


def _pick_basket(rng: random.Random) -> list[tuple[str, int]]:
    """Return a list of (sku, quantity) for one order."""
    skus = [p[0] for p in PRODUCTS]
    weights = [p[5] for p in PRODUCTS]
    item_count = rng.choices([1, 2, 3, 4], weights=[45, 33, 15, 7])[0]
    chosen = set()
    while len(chosen) < item_count:
        chosen.add(rng.choices(skus, weights=weights)[0])
    return [(sku, rng.choices([1, 2], weights=[85, 15])[0]) for sku in sorted(chosen)]


def generate() -> None:
    rng = random.Random(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    orders: list[tuple[date, str, str]] = []  # (date, customer_id, channel)
    channel_names = [c[0] for c in CHANNELS]
    channel_shares = [c[1] for c in CHANNELS]

    for index in range(1, NEW_CUSTOMERS + 1):
        customer_id = f"C{index:05d}"
        first_day = START_DATE + timedelta(days=rng.randrange(DAYS))
        orders.append((first_day, customer_id, rng.choices(channel_names, channel_shares)[0]))
        # Some customers come back during the period, mostly through email or organic.
        next_day = first_day
        while rng.random() < 0.24:
            next_day = next_day + timedelta(days=rng.randint(10, 45))
            if next_day >= START_DATE + timedelta(days=DAYS):
                break
            orders.append((next_day, customer_id, rng.choice(["email", "organic", "paid_social"])))

    orders.sort()

    with (OUTPUT_DIR / "orders.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["order_id", "order_date", "customer_id", "channel", "sku", "quantity"])
        for number, (order_day, customer_id, channel) in enumerate(orders, start=1):
            for sku, quantity in _pick_basket(rng):
                writer.writerow(
                    [f"O{number:06d}", order_day.isoformat(), customer_id, channel, sku, quantity]
                )

    with (OUTPUT_DIR / "products.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["sku", "name", "category", "price", "unit_cost"])
        for sku, name, category, price, cost, _ in PRODUCTS:
            writer.writerow([sku, name, category, f"{price:.2f}", f"{cost:.2f}"])

    (OUTPUT_DIR / "assumptions.json").write_text(
        json.dumps(ASSUMPTIONS, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(orders)} orders to {OUTPUT_DIR}")


if __name__ == "__main__":
    generate()
