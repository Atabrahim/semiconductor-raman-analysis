import json

import numpy as np
import pytest

from raman_analysis.cli import main
from raman_analysis.workflow import analyze_files


@pytest.fixture
def spectrum_file(tmp_path):
    shift = np.linspace(495, 545, 151)
    signal = 1000 * 1.3 / (np.pi * ((shift - 520.4) ** 2 + 1.3**2)) + 20
    signal += np.random.default_rng(51).normal(0, 1, len(shift))
    path = tmp_path / "test.txt"
    np.savetxt(path, np.column_stack([shift, signal]))
    return path


def test_batch_retains_failure_row_and_full_audit(spectrum_file, tmp_path):
    output = tmp_path / "reports"
    table = analyze_files(
        [spectrum_file, tmp_path / "missing.txt"],
        output,
        config={"model": "lorentzian"},
        n_resamples=20,
    )
    assert list(table.status) == ["ok", "failed"]
    payload = json.loads((output / "report.json").read_text())
    assert payload["files"][0]["audit"][0].startswith("source_sha256=")
    assert payload["files"][0]["uncertainty"]["n_successful"] == 20
    assert len(list(output.glob("*_fit.csv"))) == 1
    with pytest.raises(FileExistsError, match="not empty"):
        analyze_files([spectrum_file], output, n_resamples=20)


def test_cli_writes_successful_report_and_has_failure_exit(spectrum_file, tmp_path):
    config = tmp_path / "config.json"
    config.write_text('{"model": "lorentzian"}')
    options = ["--config", str(config), "--bootstrap", "20"]
    assert main([str(spectrum_file), "--output", str(tmp_path / "ok"), *options]) == 0
    assert main([str(tmp_path / "missing"), "--output", str(tmp_path / "bad"), *options]) == 1


def test_duplicate_basenames_get_distinct_output_ids(spectrum_file, tmp_path):
    result = analyze_files(
        [spectrum_file, spectrum_file],
        tmp_path / "duplicates",
        config={"model": "lorentzian"},
        n_resamples=20,
    )
    assert result.id.nunique() == 2


def test_plot_optional_path_executes(spectrum_file, tmp_path):
    output = tmp_path / "plots"
    analyze_files(
        [spectrum_file], output, config={"model": "lorentzian"}, n_resamples=20, make_plots=True
    )
    assert (output / "000_test_fit.png").stat().st_size > 10000


@pytest.mark.parametrize("config", [{"typo": 1}, {"window": [500, 540]}])
def test_unknown_configuration_is_rejected(spectrum_file, tmp_path, config):
    with pytest.raises(ValueError, match="Unknown fit"):
        analyze_files([spectrum_file], tmp_path / "bad", config=config)


def test_cli_rejects_invalid_json_schema(tmp_path):
    config = tmp_path / "bad.json"
    config.write_text("[]")
    with pytest.raises(SystemExit) as error:
        main(["unused.txt", "--output", str(tmp_path / "out"), "--config", str(config)])
    assert error.value.code == 2
