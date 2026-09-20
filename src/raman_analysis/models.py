"""Area-normalized Raman line shapes and physical width conventions."""

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import brentq
from scipy.special import voigt_profile


def _validate(shift_cm1, area, center_cm1, gamma_cm1, sigma_cm1=0):
    shift = np.asarray(shift_cm1, dtype=float)
    scalars = [area, center_cm1, gamma_cm1, sigma_cm1]
    if not np.isfinite(shift).all() or not np.isfinite(scalars).all():
        raise ValueError("Line-shape inputs must be finite")
    if area < 0 or gamma_cm1 < 0 or sigma_cm1 < 0 or gamma_cm1 + sigma_cm1 <= 0:
        raise ValueError("Area must be nonnegative; widths nonnegative and not both zero")
    return shift


def lorentzian(
    shift_cm1: ArrayLike, area: float, center_cm1: float, gamma_cm1: float
) -> NDArray[np.float64]:
    """Area has units intensity*cm^-1; gamma is HWHM in cm^-1, FWHM=2*gamma."""
    shift = _validate(shift_cm1, area, center_cm1, gamma_cm1)
    return area * gamma_cm1 / (np.pi * ((shift - center_cm1) ** 2 + gamma_cm1**2))


def voigt(
    shift_cm1: ArrayLike, area: float, center_cm1: float, gamma_cm1: float, sigma_cm1: float
) -> NDArray[np.float64]:
    """Convolution of Lorentzian HWHM gamma and Gaussian standard deviation sigma.

    Both widths and shift are in cm^-1. Without an instrument response calibration,
    these components are descriptive fit parameters, not a lifetime measurement.
    """
    shift = _validate(shift_cm1, area, center_cm1, gamma_cm1, sigma_cm1)
    return area * voigt_profile(shift - center_cm1, sigma_cm1, gamma_cm1)


def voigt_fwhm(gamma_cm1: float, sigma_cm1: float) -> float:
    """Numerical half-height width; also supports exact Gaussian/Lorentzian limits."""
    _validate(0, 1, 0, gamma_cm1, sigma_cm1)
    half_height = voigt_profile(0, sigma_cm1, gamma_cm1) / 2
    half_width = brentq(
        lambda offset: voigt_profile(offset, sigma_cm1, gamma_cm1) - half_height,
        0,
        20 * (gamma_cm1 + sigma_cm1),
        xtol=1e-12,
    )
    return 2 * half_width
