"""Bounded single-peak fitting with joint background and interpretable diagnostics."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import least_squares
from scipy.special import voigt_profile

from .models import voigt_fwhm
from .spectrum import Spectrum, spike_candidates


@dataclass
class PeakFit:
    """Fit estimates are conditional on the window, line shape and observation model."""

    model: str
    baseline_degree: int
    parameters: dict[str, float]
    center_cm1: float
    fwhm_cm1: float
    center_se_cm1: float | None
    fwhm_se_cm1: float | None
    rss: float
    aicc: float
    residual_sd: float
    lag1_correlation: float
    snr: float
    flags: tuple[str, ...]
    shift_cm1: NDArray[np.float64]
    observed: NDArray[np.float64]
    predicted: NDArray[np.float64]
    baseline: NDArray[np.float64]
    residual: NDArray[np.float64]
    source_indices: NDArray[np.int64]
    spike_indices: NDArray[np.int64]
    excluded_indices: NDArray[np.int64]
    config: dict

    def summary(self) -> dict:
        """JSON-safe scalar summary; full fitted observations are exported separately."""
        keys = (
            "model",
            "baseline_degree",
            "parameters",
            "center_cm1",
            "fwhm_cm1",
            "center_se_cm1",
            "fwhm_se_cm1",
            "rss",
            "aicc",
            "residual_sd",
            "lag1_correlation",
            "snr",
            "flags",
            "config",
        )
        result = {key: getattr(self, key) for key in keys}
        result.update(
            n_points=len(self.shift_cm1),
            spike_indices=self.spike_indices.tolist(),
            excluded_indices=self.excluded_indices.tolist(),
        )
        return result


def fit_peak(
    spectrum: Spectrum,
    *,
    model: str = "voigt",
    baseline_degree: int = 1,
    window_cm1: tuple[float, float] = (495, 545),
    center_bounds_cm1: tuple[float, float] = (510, 530),
    exclude_spikes: bool = False,
    max_nfev: int = 2000,
) -> PeakFit:
    """Fit an isolated positive peak plus polynomial baseline, without smoothing.

    Independent equal-variance intensity errors are the working likelihood. Their
    unknown variance is estimated from residuals. Reported SEs exclude calibration,
    correlated noise and model discrepancy. AICc comparisons require the same data.
    """
    if model not in ("lorentzian", "voigt"):
        raise ValueError("model must be lorentzian or voigt")
    if type(baseline_degree) is not int or baseline_degree not in (0, 1, 2):
        raise ValueError("baseline_degree must be 0, 1 or 2")
    bounds_array = np.asarray([window_cm1, center_bounds_cm1], dtype=float)
    if bounds_array.shape != (2, 2) or not np.isfinite(bounds_array).all():
        raise ValueError("window and center bounds need two finite values each")
    lower_window, upper_window = bounds_array[0]
    lower_center, upper_center = bounds_array[1]
    if not lower_window < lower_center < upper_center < upper_window:
        raise ValueError("center bounds must be strictly inside an increasing fit window")
    if type(max_nfev) is not int or max_nfev < 1:
        raise ValueError("max_nfev must be a positive integer")
    if type(exclude_spikes) is not bool:
        raise ValueError("exclude_spikes must be boolean")
    mask = (spectrum.shift_cm1 >= lower_window) & (spectrum.shift_cm1 <= upper_window)
    indices = np.flatnonzero(mask)
    if len(indices) < 20:
        raise ValueError("Need at least 20 measured points in the fit window")
    candidates = spike_candidates(spectrum.intensity[mask])
    spike_indices = indices[candidates]
    excluded = spike_indices if exclude_spikes else np.array([], dtype=int)
    if exclude_spikes:
        indices = indices[~candidates]
    shift = spectrum.shift_cm1[indices]
    observed = spectrum.intensity[indices]
    if len(shift) < 20:
        raise ValueError("Fewer than 20 points remain after explicit spike exclusion")
    half_window = (upper_window - lower_window) / 2
    midpoint = (upper_window + lower_window) / 2
    coordinate = (shift - midpoint) / half_window
    scale = max(float(np.ptp(observed)), 1.0)
    normalized = observed / scale
    n_shape = 4 if model == "voigt" else 3
    n_parameters = n_shape + baseline_degree + 1
    spacing = float(np.median(np.diff(shift)))
    width_min = max(spacing / 100, 1e-4)
    width_max = half_window
    low = [-25, lower_center, np.log(width_min)]
    high = [np.log(1e5 * half_window), upper_center, np.log(width_max)]
    if model == "voigt":
        low.append(np.log(width_min))
        high.append(np.log(width_max))
    low.extend([-np.inf] * (baseline_degree + 1))
    high.extend([np.inf] * (baseline_degree + 1))

    def components(parameters):
        area, center, gamma = np.exp(parameters[0]), parameters[1], np.exp(parameters[2])
        sigma = np.exp(parameters[3]) if model == "voigt" else 0.0
        peak = area * voigt_profile(shift - center, sigma, gamma)
        background = np.polynomial.polynomial.polyval(coordinate, parameters[n_shape:])
        return peak, background

    edge = np.abs(coordinate) > 0.7
    if np.count_nonzero(edge) < baseline_degree + 2:
        raise ValueError("Insufficient observations in the outer fit-window wings")
    background_guess = np.polynomial.polynomial.polyfit(
        coordinate[edge], normalized[edge], baseline_degree
    )
    corrected = normalized - np.polynomial.polynomial.polyval(coordinate, background_guess)
    inside = (shift >= lower_center) & (shift <= upper_center)
    if not np.any(inside):
        raise ValueError("No observations inside the requested center bounds")
    center_guess = float(shift[np.flatnonzero(inside)[np.argmax(corrected[inside])]])
    center_guess = float(np.clip(center_guess, lower_center + 1e-6, upper_center - 1e-6))
    height = max(float(np.max(corrected[inside])), 1e-6)
    above_half = shift[corrected > height / 2]
    width_guess = (above_half[-1] - above_half[0]) / 2 if len(above_half) > 1 else spacing
    width_guess = np.clip(width_guess, spacing, width_max / 2)
    solutions = []
    for fraction in [0.25, 0.75] if model == "voigt" else [0]:
        gamma = width_guess * (1 - fraction)
        sigma = width_guess * fraction
        area_guess = height / voigt_profile(0, sigma, gamma)
        guess = [np.log(area_guess), center_guess, np.log(gamma)]
        if model == "voigt":
            guess.append(np.log(max(sigma, width_min * 2)))
        guess.extend(background_guess)
        solution = least_squares(
            lambda p: sum(components(p)) - normalized,
            guess,
            bounds=(low, high),
            jac="3-point",
            x_scale="jac",
            max_nfev=max_nfev,
            ftol=1e-10,
            xtol=1e-10,
            gtol=1e-10,
        )
        if solution.success and np.isfinite(solution.fun).all():
            solutions.append(solution)
    if not solutions:
        raise RuntimeError("Peak fit did not converge within max_nfev")
    solution = min(solutions, key=lambda result: result.cost)
    parameters = solution.x
    peak, background = components(parameters)
    predicted, background = (peak + background) * scale, background * scale
    residual = observed - predicted
    rss = float(residual @ residual)
    dof = len(shift) - n_parameters
    residual_sd = float(np.sqrt(rss / dof))
    gamma = float(np.exp(parameters[2]))
    sigma = float(np.exp(parameters[3])) if model == "voigt" else 0.0
    fwhm = voigt_fwhm(gamma, sigma)
    noise_floor = np.finfo(float).eps * scale
    snr = float(np.max(peak) * scale / max(residual_sd, noise_floor))
    lag1 = (
        float(np.corrcoef(residual[:-1], residual[1:])[0, 1])
        if min(np.std(residual[:-1]), np.std(residual[1:])) > noise_floor
        else 0.0
    )
    flags = []
    if len(spike_indices):
        flags.append("spikes_excluded" if exclude_spikes else "spike_candidates_retained")
    if snr < 5:
        flags.append("low_signal_to_residual_noise")
    if abs(lag1) > 0.35:
        flags.append("correlated_residuals_or_model_mismatch")
    if fwhm < 3 * spacing:
        flags.append("underresolved_peak")
    if np.any(solution.active_mask):
        flags.append("parameter_at_bound")
    if min(shift[-1] - parameters[1], parameters[1] - shift[0]) < 2 * fwhm:
        flags.append("insufficient_wings_in_window")
    _, singular, right = np.linalg.svd(solution.jac, full_matrices=False)
    center_se = fwhm_se = None
    if singular[-1] <= 1e-10 * singular[0]:
        flags.append("rank_deficient_fit")
    if "rank_deficient_fit" not in flags and "parameter_at_bound" not in flags:
        covariance = (right.T / singular**2) @ right * (rss / scale**2 / dof)
        center_se = float(np.sqrt(max(0, covariance[1, 1])))
        gradient = np.zeros(n_parameters)
        step = 1e-4
        gradient[2] = (
            voigt_fwhm(gamma * np.exp(step), sigma) - voigt_fwhm(gamma * np.exp(-step), sigma)
        ) / (2 * step)
        if model == "voigt":
            gradient[3] = (
                voigt_fwhm(gamma, sigma * np.exp(step))
                - voigt_fwhm(gamma, sigma * np.exp(-step))
            ) / (2 * step)
        fwhm_se = float(np.sqrt(max(0, gradient @ covariance @ gradient)))
    # Include the estimated noise variance as one fitted likelihood parameter.
    aic_parameters = n_parameters + 1
    aicc = (
        len(shift) * np.log(max(rss / len(shift), noise_floor**2))
        + 2 * aic_parameters
        + 2 * aic_parameters * (aic_parameters + 1) / (len(shift) - aic_parameters - 1)
    )
    reported = {
        "area_intensity_cm1": float(np.exp(parameters[0]) * scale),
        "center_cm1": float(parameters[1]),
        "gamma_cm1": gamma,
        "sigma_cm1": sigma,
        "height_intensity": float(
            np.exp(parameters[0]) * scale * voigt_profile(0, sigma, gamma)
        ),
        **{
            f"baseline_c{j}": float(coefficient * scale)
            for j, coefficient in enumerate(parameters[n_shape:])
        },
    }
    config = dict(
        model=model,
        baseline_degree=baseline_degree,
        window_cm1=list(window_cm1),
        center_bounds_cm1=list(center_bounds_cm1),
        exclude_spikes=exclude_spikes,
        max_nfev=max_nfev,
    )
    return PeakFit(
        model,
        baseline_degree,
        reported,
        float(parameters[1]),
        fwhm,
        center_se,
        fwhm_se,
        rss,
        float(aicc),
        residual_sd,
        lag1,
        snr,
        tuple(flags),
        shift,
        observed,
        predicted,
        background,
        residual,
        indices,
        spike_indices,
        excluded,
        config,
    )
