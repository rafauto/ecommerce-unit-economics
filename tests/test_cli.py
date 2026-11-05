from conftest import FIXTURES, SAMPLE_STORE

from unit_economics.cli import main


def test_cli_prints_report_end_to_end(capsys):
    assert main(["--data-dir", str(SAMPLE_STORE)]) == 0

    output = capsys.readouterr().out
    assert "Break-even orders per month" in output
    assert "Lever impact" in output
    assert "Scenario vs baseline" not in output


def test_cli_scenario_section(capsys):
    assert main(["--data-dir", str(FIXTURES / "tiny-store"), "--price-change", "5"]) == 0

    assert "Scenario vs baseline" in capsys.readouterr().out


def test_cli_reads_data_dir_from_environment(monkeypatch, capsys):
    monkeypatch.setenv("UNIT_ECONOMICS_DATA_DIR", str(FIXTURES / "tiny-store"))

    assert main([]) == 0
    assert "3 orders" in capsys.readouterr().out


def test_cli_invalid_folder_returns_error(tmp_path, capsys):
    assert main(["--data-dir", str(tmp_path / "missing")]) == 1
    assert "Data folder not found" in capsys.readouterr().err
