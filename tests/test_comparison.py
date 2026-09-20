import numpy as np
import pytest

from raman_analysis import Spectrum, fit_peak, rank_fits, sensitivity_study, voigt


def sample():
    shift = np.linspace(490, 550, 201)
    return Spectrum(shift, voigt(shift, 1000, 520.5, 0.7, 1.1) + 20)


def test_same_data_ranking_prefers_generating_shape():
    spectrum = sample()
    table = rank_fits([fit_peak(spectrum), fit_peak(spectrum, model="lorentzian")])
    assert table.iloc[0]["model"] == "voigt"
    assert table.iloc[0]["delta_aicc"] == 0


def test_different_windows_cannot_be_ranked_by_aicc():
    spectrum = sample()
    with pytest.raises(ValueError, match="same retained"):
        rank_fits([fit_peak(spectrum), fit_peak(spectrum, window_cm1=(500, 540))])


def test_sensitivity_preserves_failures_and_does_not_rank_different_data():
    table = sensitivity_study(sample(), models=("voigt", "bad"), baseline_degrees=(0, 1))
    assert len(table) == 12
    assert (table.status == "failed").sum() == 6
    assert "aicc" not in table
    assert max(abs(table.loc[table.status == "ok", "center_cm1"] - 520.5)) < 1e-5


def test_missing_window_wings_gives_clear_error():
    shift = np.linspace(510, 530, 80)
    with pytest.raises(ValueError, match="outer fit-window wings"):
        fit_peak(Spectrum(shift, voigt(shift, 1000, 520.4, 1, 1)))
