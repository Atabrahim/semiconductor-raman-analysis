import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from raman_analysis import Spectrum, read_spectrum, spike_candidates


def test_import_reverses_both_arrays_and_records_hash(tmp_path):
    path = tmp_path / "descending.txt"
    np.savetxt(path, np.column_stack([np.arange(12)[::-1], np.arange(12)[::-1] ** 2]))
    spectrum = read_spectrum(path)
    np.testing.assert_array_equal(spectrum.intensity, spectrum.shift_cm1**2)
    assert "reversed_descending_axis_and_intensity" in spectrum.audit
    assert any(hashlib.sha256(path.read_bytes()).hexdigest() in item for item in spectrum.audit)


def test_invalid_row_removal_is_opt_in_and_traceable(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "shift,intensity\n# comment\n"
        + "".join(f"{i},{i * i}\n" for i in range(10))
        + "11,nan\n"
    )
    with pytest.raises(ValueError, match="13"):
        read_spectrum(path, skiprows=1)
    spectrum = read_spectrum(path, skiprows=1, allow_invalid=True)
    assert "removed_invalid_source_rows=[13]" in spectrum.audit


@pytest.mark.parametrize(
    "shift,intensity",
    [
        ([0] * 10, list(range(10))),
        (list(range(10)), [np.nan] * 10),
        (list(range(3)), list(range(3))),
        (list(range(10)), list(range(9))),
        (list(range(9)) + [7], list(range(10))),
    ],
)
def test_invalid_spectrum(shift, intensity):
    with pytest.raises(ValueError):
        Spectrum(shift, intensity)


def test_spike_flag_does_not_modify_real_peak():
    shift = np.linspace(495, 545, 501)
    signal = 100 / (1 + ((shift - 520) / 1.5) ** 2)
    assert not spike_candidates(signal).any()
    signal[40] += 500
    saved = signal.copy()
    assert np.flatnonzero(spike_candidates(signal)).tolist() == [40]
    np.testing.assert_array_equal(signal, saved)


def test_published_measurement_bytes_and_axis_are_preserved():
    data = Path(__file__).resolve().parents[1] / "data"
    manifest = json.loads((data / "provenance.json").read_text())
    for item in manifest["files"]:
        assert hashlib.sha256((data / item["path"]).read_bytes()).hexdigest() == item["sha256"]
    spectrum = read_spectrum(data / "silicon_raw.txt")
    assert len(spectrum.shift_cm1) == 10166
    assert spectrum.shift_cm1[np.argmax(spectrum.intensity)] == pytest.approx(520.694)
