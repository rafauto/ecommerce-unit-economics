from pathlib import Path

import pytest

from unit_economics.data import load_dataset_from_dir
from unit_economics.models import Dataset

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SAMPLE_STORE = ROOT / "examples" / "sample-store"


@pytest.fixture
def tiny_store() -> Dataset:
    """Three hand-checked orders (expected values are worked out in test_metrics.py)."""
    return load_dataset_from_dir(FIXTURES / "tiny-store")


@pytest.fixture
def sample_store() -> Dataset:
    return load_dataset_from_dir(SAMPLE_STORE)
