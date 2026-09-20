"""Traceable analysis of isolated semiconductor Raman peaks."""

from .comparison import rank_fits, sensitivity_study
from .fitting import PeakFit, fit_peak
from .models import lorentzian, voigt, voigt_fwhm
from .spectrum import Spectrum, read_spectrum, spike_candidates
from .uncertainty import BootstrapResult, bootstrap_fit

__version__ = "0.1.0"
__all__ = [
    "PeakFit",
    "BootstrapResult",
    "Spectrum",
    "fit_peak",
    "bootstrap_fit",
    "rank_fits",
    "sensitivity_study",
    "lorentzian",
    "read_spectrum",
    "spike_candidates",
    "voigt",
    "voigt_fwhm",
]
