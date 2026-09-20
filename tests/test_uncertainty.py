import numpy as np
import pytest

from raman_analysis import Spectrum, bootstrap_fit, fit_peak
from raman_analysis import uncertainty as module


@pytest.fixture
def fitted():
    shift = np.linspace(495, 545, 151)
    clean = 1500 * 1.2 / (np.pi * ((shift - 520.4) ** 2 + 1.2**2)) + 15
    data = clean + np.random.default_rng(74).normal(0, 1.5, len(shift))
    return fit_peak(Spectrum(shift, data), model="lorentzian")


def test_seed_reproducibility_and_all_reported_quantities(fitted):
    first = bootstrap_fit(fitted, n_resamples=24, seed=6)
    second = bootstrap_fit(fitted, n_resamples=24, seed=6)
    np.testing.assert_array_equal(first.samples, second.samples)
    assert not first.failed_refits
    assert set(first.intervals) == set(fitted.parameters) | {"fwhm_cm1"}
    for name in ("center_cm1", "fwhm_cm1", "area_intensity_cm1", "height_intensity"):
        low, high = first.intervals[name]
        assert low < high
    assert first.summary()["includes_calibration_uncertainty"] is False
    assert first.intervals["sigma_cm1"] == (0, 0)  # fixed, not an estimated error bar


def test_gaussian_residual_bootstrap_matches_local_covariance_scale(fitted):
    result = bootstrap_fit(fitted, n_resamples=100, seed=42)
    spread = np.std(result.samples[:, result.quantities.index("center_cm1")], ddof=1)
    assert 0.7 < spread / fitted.center_se_cm1 < 1.4


def test_correlated_noise_block_sensitivity():
    shift = np.linspace(495, 545, 251)
    noise = np.random.default_rng(91).normal(0, 0.9, len(shift))
    for index in range(1, len(noise)):
        noise[index] += 0.85 * noise[index - 1]
    data = 1500 * 1.2 / (np.pi * ((shift - 520.4) ** 2 + 1.2**2)) + 15 + noise
    fitted = fit_peak(Spectrum(shift, data), model="lorentzian")
    independent = bootstrap_fit(fitted, n_resamples=80, seed=13)
    blocked = bootstrap_fit(fitted, n_resamples=80, block_size=6, seed=13)

    def width(result):
        return np.ptp(result.intervals["center_cm1"])

    assert width(blocked) > 1.3 * width(independent)
    assert "conditional_on_correlated_residuals_or_model_mismatch" in blocked.flags


def test_refit_failures_are_counted_and_intervals_withheld(fitted, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("deliberate nonconvergence")

    monkeypatch.setattr(module, "fit_peak", fail)
    result = bootstrap_fit(fitted, n_resamples=20)
    assert sum(result.failed_refits.values()) == 20
    assert all(value is None for value in result.intervals.values())
    assert "insufficient_successful_refits" in result.flags


def test_bootstrap_holds_exclusion_mask_fixed(fitted, monkeypatch):
    calls = []
    original = module.fit_peak
    fitted.excluded_indices = np.array([50])

    def record(spectrum, **kwargs):
        calls.append((len(spectrum.shift_cm1), kwargs["exclude_spikes"]))
        return original(spectrum, **kwargs)

    monkeypatch.setattr(module, "fit_peak", record)
    result = bootstrap_fit(fitted, n_resamples=20)
    assert calls == [(len(fitted.shift_cm1), False)] * 20
    assert "conditional_on_fixed_spike_exclusion" in result.flags


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n_resamples": 10},
        {"n_resamples": True},
        {"block_size": 0},
        {"block_size": 100},
        {"seed": -1},
        {"confidence": 1},
        {"confidence": np.nan},
    ],
)
def test_invalid_settings(fitted, kwargs):
    with pytest.raises(ValueError):
        bootstrap_fit(fitted, **kwargs)
