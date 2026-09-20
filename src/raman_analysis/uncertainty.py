"""Conditional residual resampling; systematic calibration and model bias are excluded."""

from collections import Counter
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .fitting import PeakFit, fit_peak
from .spectrum import Spectrum


@dataclass
class BootstrapResult:
    """Percentile intervals and successful refits, including boundary-hit refits."""

    quantities: tuple[str, ...]
    samples: NDArray[np.float64]
    intervals: dict[str, tuple[float, float] | None]
    n_requested: int
    block_size: int
    seed: int
    confidence: float
    failed_refits: dict[str, int]
    boundary_refits: int
    flags: tuple[str, ...]

    def summary(self) -> dict:
        """Return a JSON-safe audit without duplicating the sample table."""
        return {
            "method": "circular residual block bootstrap",
            "n_requested": self.n_requested,
            "n_successful": len(self.samples),
            "block_size_channels": self.block_size,
            "seed": self.seed,
            "confidence": self.confidence,
            "intervals": self.intervals,
            "failed_refits": self.failed_refits,
            "boundary_refits": self.boundary_refits,
            "flags": self.flags,
            "includes_calibration_uncertainty": False,
            "includes_model_selection_uncertainty": False,
            "mask": "held fixed from original fit; no new spike removal during resampling",
        }


def bootstrap_fit(
    fit: PeakFit,
    *,
    n_resamples: int = 200,
    block_size: int = 1,
    seed: int = 2026,
    confidence: float = 0.95,
) -> BootstrapResult:
    """Resample centred, degrees-of-freedom-adjusted residuals and refit.

    Block size 1 assumes independent errors. Larger circular blocks preserve local
    correlation in retained-channel order; they require approximately stationary
    residuals. This is a sensitivity calculation, not a remedy for model mismatch.
    Intervals are withheld if fewer than 80% of refits converge. All successful
    refits, including those hitting a bound, are retained and counted.
    """
    if type(n_resamples) is not int or n_resamples < 20:
        raise ValueError("n_resamples must be an integer >=20")
    if type(block_size) is not int or not 1 <= block_size <= len(fit.residual) // 4:
        raise ValueError("block_size must be an integer between 1 and one quarter of N")
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    if not np.isfinite(confidence) or not 0 < confidence < 1:
        raise ValueError("confidence must be between zero and one")
    if "low_signal_to_residual_noise" in fit.flags or "rank_deficient_fit" in fit.flags:
        raise ValueError("Unresolved or rank-deficient peak: uncertainty is not reportable")
    rng = np.random.default_rng(seed)
    count = len(fit.residual)
    n_parameters = 4 + fit.baseline_degree + int(fit.model == "voigt")
    residual = (fit.residual - np.mean(fit.residual)) * np.sqrt(count / (count - n_parameters))
    quantities = tuple(fit.parameters) + ("fwhm_cm1",)
    samples, failures, boundary_refits = [], Counter(), 0
    config = {**fit.config, "exclude_spikes": False}
    for _ in range(n_resamples):
        starts = rng.integers(0, count, size=int(np.ceil(count / block_size)))
        indices = ((starts[:, None] + np.arange(block_size)) % count).ravel()[:count]
        replica = Spectrum(fit.shift_cm1, fit.predicted + residual[indices])
        try:
            result = fit_peak(replica, **config)
        except (ValueError, RuntimeError, np.linalg.LinAlgError) as error:
            failures[f"{type(error).__name__}: {error}"] += 1
            continue
        values = {**result.parameters, "fwhm_cm1": result.fwhm_cm1}
        samples.append([values[name] for name in quantities])
        boundary_refits += int("parameter_at_bound" in result.flags)
    samples = np.asarray(samples, dtype=float).reshape((-1, len(quantities)))
    flags = []
    if len(samples) < 0.8 * n_resamples:
        flags.append("insufficient_successful_refits")
        intervals = dict.fromkeys(quantities)
    else:
        tails = [(1 - confidence) / 2, (1 + confidence) / 2]
        limits = np.quantile(samples, tails, axis=0)
        intervals = {name: tuple(map(float, limits[:, j])) for j, name in enumerate(quantities)}
    if boundary_refits:
        flags.append("boundary_refits_included")
    if abs(fit.lag1_correlation) > 0.35:
        flags.append("conditional_on_correlated_residuals_or_model_mismatch")
    if fit.excluded_indices.size:
        flags.append("conditional_on_fixed_spike_exclusion")
    return BootstrapResult(
        quantities,
        samples,
        intervals,
        n_resamples,
        block_size,
        seed,
        confidence,
        dict(failures),
        boundary_refits,
        tuple(flags),
    )
