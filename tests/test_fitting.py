import numpy as np
import pytest

from raman_analysis import Spectrum, fit_peak, voigt


@pytest.fixture
def measured():
    shift = np.linspace(495, 545, 201)
    signal = 1200 * 1.4 / (np.pi * ((shift - 520.4) ** 2 + 1.4**2)) + 12 + 0.25 * (shift - 520)
    return Spectrum(shift, signal)


def test_noiseless_recovery_from_independent_analytical_formula(measured):
    result = fit_peak(measured, model="lorentzian")
    assert result.center_cm1 == pytest.approx(520.4, abs=1e-6)
    assert result.fwhm_cm1 == pytest.approx(2.8, abs=1e-6)
    assert result.parameters["area_intensity_cm1"] == pytest.approx(1200, rel=1e-7)
    assert result.rss < 1e-12


def test_noisy_voigt_recovery_and_model_comparison():
    shift = np.linspace(495, 545, 251)
    signal = (
        voigt(shift, 1500, 521.2, 0.7, 1.3)
        + 20
        + np.random.default_rng(71).normal(0, 1, len(shift))
    )
    spectrum = Spectrum(shift, signal)
    result = fit_peak(spectrum)
    assert abs(result.center_cm1 - 521.2) < 0.05
    assert result.parameters["gamma_cm1"] == pytest.approx(0.7, abs=0.07)
    assert result.parameters["sigma_cm1"] == pytest.approx(1.3, abs=0.07)
    assert result.aicc < fit_peak(spectrum, model="lorentzian").aicc - 10
    assert result.center_se_cm1 > 0


def test_intensity_scaling_preserves_spectral_estimates(measured):
    first = fit_peak(measured, model="lorentzian")
    second = fit_peak(
        Spectrum(measured.shift_cm1, measured.intensity * 1e4), model="lorentzian"
    )
    assert second.center_cm1 == pytest.approx(first.center_cm1, abs=1e-7)
    assert second.fwhm_cm1 == pytest.approx(first.fwhm_cm1, rel=1e-6)
    assert second.parameters["area_intensity_cm1"] == pytest.approx(
        1e4 * first.parameters["area_intensity_cm1"]
    )


def test_joint_quadratic_baseline_recovers_peak(measured):
    curved = Spectrum(
        measured.shift_cm1, measured.intensity + 0.08 * (measured.shift_cm1 - 520) ** 2
    )
    result = fit_peak(curved, model="lorentzian", baseline_degree=2)
    assert result.center_cm1 == pytest.approx(520.4, abs=1e-6)
    assert result.fwhm_cm1 == pytest.approx(2.8, abs=1e-6)


def test_spike_exclusion_is_explicit_and_preserves_indices(measured):
    intensity = measured.intensity.copy()
    intensity[60] += 2000
    spectrum = Spectrum(measured.shift_cm1, intensity)
    retained = fit_peak(spectrum, model="lorentzian")
    excluded = fit_peak(spectrum, model="lorentzian", exclude_spikes=True)
    assert "spike_candidates_retained" in retained.flags
    assert excluded.excluded_indices.tolist() == [60]
    assert excluded.center_cm1 == pytest.approx(520.4, abs=1e-6)
    assert 60 not in excluded.source_indices
    assert len(retained.observed) == len(measured.intensity)


def test_flat_data_is_not_accepted_as_a_resolved_peak(measured):
    result = fit_peak(
        Spectrum(measured.shift_cm1, np.ones(len(measured.shift_cm1))), model="lorentzian"
    )
    assert result.flags


def test_solver_failure_is_exposed(measured):
    with pytest.raises(RuntimeError, match="converge"):
        fit_peak(measured, max_nfev=1)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"model": "unknown"},
        {"baseline_degree": 3},
        {"baseline_degree": True},
        {"window_cm1": (545, 495)},
        {"center_bounds_cm1": (490, 520)},
        {"window_cm1": (np.nan, 545)},
        {"max_nfev": 0},
        {"window_cm1": (500, 501), "center_bounds_cm1": (500.1, 500.9)},
    ],
)
def test_invalid_fit_settings(measured, kwargs):
    with pytest.raises(ValueError):
        fit_peak(measured, **kwargs)
