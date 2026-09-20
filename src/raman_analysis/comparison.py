"""Same-observation line-shape rankings and explicit analysis-choice sensitivity."""

from itertools import product

import numpy as np
import pandas as pd

from .fitting import PeakFit, fit_peak
from .spectrum import Spectrum


def rank_fits(fits: list[PeakFit]) -> pd.DataFrame:
    """Rank AICc only when observations and their retained indices agree exactly.

    Values are descriptive when the working independent Gaussian noise model is
    contradicted by residual diagnostics. Do not compare across fit windows.
    """
    if len(fits) < 2:
        raise ValueError("Need at least two fits to compare")
    for fit in fits[1:]:
        for name in ("shift_cm1", "observed", "source_indices"):
            if not np.array_equal(getattr(fit, name), getattr(fits[0], name)):
                raise ValueError("AICc ranking requires exactly the same retained observations")
    rows = []
    best = min(fit.aicc for fit in fits)
    for fit in fits:
        rows.append(
            {
                "model": fit.model,
                "baseline_degree": fit.baseline_degree,
                "center_cm1": fit.center_cm1,
                "fwhm_cm1": fit.fwhm_cm1,
                "area_intensity_cm1": fit.parameters["area_intensity_cm1"],
                "height_intensity": fit.parameters["height_intensity"],
                "aicc": fit.aicc,
                "delta_aicc": fit.aicc - best,
                "residual_sd": fit.residual_sd,
                "lag1_correlation": fit.lag1_correlation,
                "flags": ";".join(fit.flags),
            }
        )
    return pd.DataFrame(rows).sort_values("aicc", ignore_index=True)


def sensitivity_study(
    spectrum: Spectrum,
    *,
    windows_cm1: tuple[tuple[float, float], ...] = ((495, 545), (500, 540), (490, 550)),
    models: tuple[str, ...] = ("lorentzian", "voigt"),
    baseline_degrees: tuple[int, ...] = (0, 1, 2),
    center_bounds_cm1: tuple[float, float] = (510, 530),
    exclude_spikes: bool = False,
) -> pd.DataFrame:
    """Report sensitivity; no AICc ranking across different windows is performed.

    Errors are explicit rows, never silently discarded. Choices are fixed before
    inspecting their fit results and are not tuned to match a desired peak centre.
    """
    if not windows_cm1 or not models or not baseline_degrees:
        raise ValueError("At least one window, model and baseline degree are required")
    rows = []
    for window, model, degree in product(windows_cm1, models, baseline_degrees):
        row = dict(
            window_low_cm1=window[0],
            window_high_cm1=window[1],
            model=model,
            baseline_degree=degree,
            status="ok",
        )
        try:
            fit = fit_peak(
                spectrum,
                model=model,
                baseline_degree=degree,
                window_cm1=window,
                center_bounds_cm1=center_bounds_cm1,
                exclude_spikes=exclude_spikes,
            )
            row.update(
                center_cm1=fit.center_cm1,
                fwhm_cm1=fit.fwhm_cm1,
                area_intensity_cm1=fit.parameters["area_intensity_cm1"],
                height_intensity=fit.parameters["height_intensity"],
                lag1_correlation=fit.lag1_correlation,
                flags=";".join(fit.flags),
            )
        except (ValueError, RuntimeError, np.linalg.LinAlgError) as error:
            row.update(status="failed", error=str(error))
        rows.append(row)
    return pd.DataFrame(rows)
