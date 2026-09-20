# Scientific model and interpretation

## Measurement and question

Raman scattering exchanges photon energy with a material excitation. For Stokes scattering, the reported wavenumber shift is Δν = 1/λ_laser − 1/λ_scattered, using wavelengths in centimetres to obtain cm⁻¹. The corresponding phonon energy is h c Δν, where h is Planck's constant and c is the speed of light expressed in cm/s. This release reads the calibrated shift axis supplied by the experiment; it does not recalibrate a spectrometer.

The measured case is the first-order silicon optical-phonon band near 520 cm⁻¹. The question is how peak position and observed width change when the baseline and line shape are changed, and how conditional noise uncertainty compares with that sensitivity. The data do not supply an independent true peak position or width.

## Forward models

Let s be Raman shift (cm⁻¹), s₀ the fitted centre (cm⁻¹), A the positive integrated area (intensity × cm⁻¹), and γ the positive Lorentzian half width at half maximum (cm⁻¹). The symmetric Lorentzian is

$$L(s)=\frac{A\gamma}{\pi[(s-s_0)^2+\gamma^2]}.$$

Its FWHM is 2γ. The normalized Gaussian with standard deviation σ (cm⁻¹) is G(s) = exp[−s²/(2σ²)]/(σ√(2π)). The Voigt line is the convolution of a unit-area Lorentzian and Gaussian, multiplied by A and centred at s₀. SciPy evaluates it using the Faddeeva function. The observed Voigt FWHM is obtained by bracketing its half-height crossing, not by calling γ or σ the FWHM.

Lorentzian broadening is compatible with a damped mode; Gaussian broadening can represent an instrument response or inhomogeneity. **Fitting these functions does not identify the broadening mechanism.** Without a measured instrument response, fitted γ and σ are descriptive and must not be reported as an independently measured phonon lifetime or strain distribution.

The measured intensity is modelled as yᵢ = P(sᵢ) + Σⱼ bⱼ tᵢʲ + εᵢ, with P = L or Voigt, t = (s − window midpoint)/(window half-width), and baseline degree 0, 1 or 2. Each bⱼ has the same units as intensity because t is dimensionless. The baseline is estimated jointly; baseline-subtracted curves are model-derived outputs, not raw measurements.

## Numerical method and likelihood

Bounded trust-region least squares minimizes the intensity residual sum of squares. Equal, independent Gaussian intensity noise with unknown common variance is a **working assumption**, not a detector calibration. Log area/width parameters enforce positivity; intensity normalization and Jacobian scaling improve conditioning. Voigt fitting uses two starting width partitions and keeps the converged fit with lower objective. Failure to converge raises an error.

The local parameter covariance is residual variance × (JᵀJ)⁻¹, computed through SVD. Centre and FWHM standard errors are propagated from the transformed parameters. Rank deficiency or active bounds prevents a usual Gaussian covariance report. These errors are conditional on the model, baseline, fixed shift axis, fit window and noise assumptions.

AICc uses N ln(RSS/N) + 2K + 2K(K+1)/(N−K−1), up to a model-independent constant. N is the number of retained observations; K includes peak/background parameters **and the estimated noise variance**. Compare only the same observations and likelihood. AICc is a conditional ranking, not a probability that the physical model is true. Correlated residuals invalidate the independent-noise interpretation.

## Quality control and limits

Imports reject nonfinite points, duplicate/nonmonotonic axes and malformed columns. Explicit invalid-row removal is logged with original line numbers. Descending axes are reversed together with intensities and audited. One-channel positive spikes are only candidates; the detector cannot reliably distinguish every real narrow peak or multi-channel cosmic ray. Exclusion is opt-in and retains original indices.

Fit flags indicate low signal relative to residual noise, active bounds, deficient rank, insufficient wings, coarse sampling, candidate spikes and strong residual correlation. Thresholds are declared screening heuristics, not calibrated hypothesis tests. No automatic smoothing is applied.

Models cover a single, isolated, approximately symmetric band within a specified window. Multi-peak overlap, Fano asymmetry, confinement line shapes, heating, wavelength calibration error and detector saturation require additional evidence or models. The original doped-nanowire dataset might have required Fano physics; it contained no Raman files. The replacement wafer does not justify claiming Fano interference. A poor symmetric fit must be flagged rather than interpreted as a unique doping or strain measurement.

## Sources

- [HORIBA: Raman spectroscopy](https://www.horiba.com/int/scientific/technologies/raman-imaging-and-spectroscopy/raman-spectroscopy/): instrument manufacturer's description of inelastic scattering.
- [Kauffmann experimental record](https://doi.org/10.12763/VUVLSZ): raw data, conditions and licence.
- [SciPy Voigt profile](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.voigt_profile.html): convolution, width conventions and limiting cases.
- [SciPy least_squares](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html): bounded trust-region method and Jacobian.
- [Burke et al., Raman study of Fano interference in p-type doped silicon](https://arxiv.org/abs/0910.5244): why a symmetric line shape is not universally appropriate. Not a dataset validation for this release.

Equations and code are independently implemented; no external repository code is copied.

## Uncertainty and sensitivity

`bootstrap_fit` subtracts the mean residual and multiplies by sqrt(N/(N-p)),
where p is the number of free peak/background coefficients. It samples random
starting channels with replacement, concatenates circular blocks of length l,
and truncates to N channels. l=1 is independent residual resampling; l>1 retains
short-range correlation in channel order. Each artificial spectrum is the fitted
curve plus resampled residuals, and is refitted with the original configuration
and retained-observation mask. No new spike exclusion occurs during resampling.
Percentile endpoints use the requested confidence (default 95%). The same refits
provide intervals for centre, observed FWHM, integrated area, peak height, shape
widths and baseline coefficients. Lorentzian sigma=0 is fixed; its zero-width
interval is not a measured Gaussian-width precision.

Failures and boundary hits are counted; boundary-hit solutions are included.
Intervals are withheld if fewer than 80% of requested refits converge. A fixed
seed reproduces the random resamples within a supported numerical environment;
small floating-point differences across library/platform versions are expected.
200 resamples are a demonstrator budget, not high-precision tail estimation.

Residual bootstrap assumes a sufficiently correct mean model. Circular blocks
add a local stationarity assumption and an arbitrary end-to-start join. They do
not correct model bias, heteroscedastic detector noise, calibration, missing
instrument response or selection bias. Block length is in retained channels,
not cm^-1; irregular axes or excluded channels require particular care. The
measured case compares lengths 1 and 5 as a **sensitivity study**, not a uniquely
optimal error model. General block-resampling background: H. R. Künsch (1989),
*The jackknife and the bootstrap for general stationary observations*, Annals of
Statistics 17, 1217–1241; see the [author's publication record](https://people.math.ethz.ch/~kuensch/papers/).

The default 495–545 cm^-1 window isolates the observed first-order silicon band
and includes both wings. Centre bounds 510–530 cm^-1 define the targeted band;
they are not a calibration reference. Windows 490–550 and 500–540 cm^-1, background
degrees 0–2 and both symmetric line shapes are declared sensitivity choices.
Only equal-data fits can be ranked by AICc. Window sensitivity is reported as
estimates/ranges without cross-window AICc ranking. Choices are not optimized to
force a literature peak position. These ranges are not probability intervals.

All reported widths include instrumental broadening. Integrated area is the
model's entire positive peak area extrapolated beyond the fitted window;
height is the background-free model value at its centre. Neither is an absolute
Raman cross section. Spike indices refer to the validated ascending `Spectrum`
arrays (zero-based); source text row removal/reversal is separately audited.
