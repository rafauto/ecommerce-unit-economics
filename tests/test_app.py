"""Smoke test for the Streamlit app: it must render with the sample data and no errors."""

import pytest
from conftest import ROOT

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402


@pytest.fixture
def app(monkeypatch) -> AppTest:
    monkeypatch.chdir(ROOT)
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)


def test_app_renders_sample_store(app):
    app.run()

    assert not app.exception
    assert not app.error
    labels = [metric.label for metric in app.metric]
    assert "Break-even orders / month" in labels


def test_app_scenario_slider_updates_result(app):
    app.run()
    app.sidebar.slider[0].set_value(5).run()  # price +5%

    assert not app.exception
    result = next(m for m in app.metric if m.label == "Monthly operating result")
    assert result.value == "R$ 4,096.58"
