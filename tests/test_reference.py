"""Regression against reviewed measured outputs, complementary to independent tests."""

import json
from pathlib import Path

import numpy as np

from raman_analysis import bootstrap_fit, fit_peak, read_spectrum

ROOT = Path(__file__).resolve().parents[1]


def test_measured_case_reproduces_reviewed_estimates_and_conditional_intervals():
    reference = json.loads((ROOT / "reports/measured_report.json").read_text(encoding="utf-8"))
    saved = reference["files"][0]
    spectrum = read_spectrum(ROOT / "data/silicon_raw.txt")
    fit = fit_peak(spectrum, **saved["fit"]["config"])
    np.testing.assert_allclose(fit.center_cm1, saved["fit"]["center_cm1"], rtol=0, atol=1e-5)
    np.testing.assert_allclose(fit.fwhm_cm1, saved["fit"]["fwhm_cm1"], rtol=1e-5)
    assert "correlated_residuals_or_model_mismatch" in fit.flags
    resampled = bootstrap_fit(fit, n_resamples=200, block_size=5, seed=2026)
    assert len(resampled.samples) == 200
    assert not resampled.failed_refits
    for quantity, bounds in saved["uncertainty"]["intervals"].items():
        if quantity == "center_cm1":
            np.testing.assert_allclose(resampled.intervals[quantity], bounds, rtol=0, atol=1e-5)
        else:
            np.testing.assert_allclose(
                resampled.intervals[quantity], bounds, rtol=2e-4, atol=1e-5
            )
