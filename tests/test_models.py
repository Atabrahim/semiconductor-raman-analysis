import numpy as np
import pytest
from scipy.integrate import quad

from raman_analysis import lorentzian, voigt, voigt_fwhm


@pytest.mark.parametrize("gamma", [0.2, 1.5, 8.0])
def test_lorentzian_area_and_half_height(gamma):
    integral = quad(lambda x: float(lorentzian(x, 4.3, 0, gamma)), -np.inf, np.inf)[0]
    assert integral == pytest.approx(4.3, rel=1e-9)
    assert lorentzian(gamma, 1, 0, gamma) == pytest.approx(lorentzian(0, 1, 0, gamma) / 2)
    assert voigt_fwhm(gamma, 0) == pytest.approx(2 * gamma)


def test_gaussian_limit():
    shift = np.linspace(-8, 8, 100)
    sigma = 1.4
    expected = np.exp(-(shift**2) / (2 * sigma**2)) / (sigma * np.sqrt(2 * np.pi))
    np.testing.assert_allclose(voigt(shift, 1, 0, 0, sigma), expected, rtol=1e-12)
    assert voigt_fwhm(0, sigma) == pytest.approx(2 * np.sqrt(2 * np.log(2)) * sigma)


@pytest.mark.parametrize("offset", [-3.0, 0.0, 4.0])
def test_voigt_against_independent_convolution_quadrature(offset):
    sigma, gamma = 0.7, 1.3

    def integrand(position):
        gaussian = np.exp(-(position**2) / (2 * sigma**2)) / (sigma * np.sqrt(2 * np.pi))
        cauchy = gamma / (np.pi * ((offset - position) ** 2 + gamma**2))
        return gaussian * cauchy

    reference, _ = quad(integrand, -np.inf, np.inf, epsabs=1e-11)
    assert voigt(offset, 1, 0, gamma, sigma) == pytest.approx(reference, rel=1e-9)


@pytest.mark.parametrize("gamma,sigma", [(1.2, 0.6), (0.1, 3), (5, 0.02)])
def test_voigt_fwhm_is_half_height(gamma, sigma):
    half_width = voigt_fwhm(gamma, sigma) / 2
    assert voigt(half_width, 1, 0, gamma, sigma) == pytest.approx(
        voigt(0, 1, 0, gamma, sigma) / 2
    )


@pytest.mark.parametrize("gamma,sigma", [(-1, 1), (1, -1), (0, 0), (np.nan, 1)])
def test_invalid_widths(gamma, sigma):
    with pytest.raises(ValueError):
        voigt([0, 1], 1, 0, gamma, sigma)
