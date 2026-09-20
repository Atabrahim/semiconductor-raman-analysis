# Validation and interpretation

## What was checked

| Evidence | Independent reference or check | Scope |
|---|---|---|
| Line shapes | Numerical convolution by quadrature; Gaussian/Lorentzian limits; Lorentzian area integral | Implementation and width conventions |
| Noiseless recovery | Independently written analytical Lorentz formula | Centre, width, area and background to tight tolerances |
| Noise and uncertainty | Known-noise synthetic experiments, covariance-scale check, fixed-seed residual resampling | Conditional statistical behaviour |
| Correlated residuals | Controlled AR(1)-type synthetic errors | Block intervals widen in a tested case; not universal coverage |
| Model comparison | Same-data AICc; different windows explicitly rejected | Valid likelihood comparison domain |
| Import/QC | Malformed, nonfinite, descending and duplicate axes; known injected spike | Audit, flags, explicit exclusions |
| Experimental file | Published checksums and untouched bytes | Authenticity and traceability, not certified peak accuracy |
| CLI/batch | Mixed valid/invalid inputs, duplicate names, protected outputs | Reusable reporting and explicit failures |

## Experimental case

Default Voigt + linear background, 495–545 cm^-1, centre bounds 510–530 cm^-1:
centre 520.515353 cm^-1; observed FWHM 3.540529 cm^-1; residual SD 45.944 source
units; lag-1 residual correlation 0.607. The raw sampled maximum is 520.694 cm^-1.
The distinction reflects sampling and model estimation; neither is a calibration standard.

200/200 bootstrap refits converged for both independent residuals and five-channel
blocks, seed 2026. No boundary-hit refits occurred. Conditional 95% centre intervals:
520.511710–520.519080 and 520.510522–520.520384 cm^-1 respectively.
The five-channel FWHM interval is 3.523089–3.558877 cm^-1. All other reported
quantities have intervals in `reports/measured_report.json`.

The 18-choice study spans windows 490–550, 495–545 and 500–540 cm^-1, both line
shapes and background degrees 0, 1 and 2. Centres span roughly 520.51463–520.51666
cm^-1. Lorentzian widths span 3.47954–3.51309 cm^-1; Voigt widths 3.53998–3.54085
cm^-1. The model-choice spread and bootstrap intervals answer different questions.
They must not be combined as independent error sources or called a complete
experimental uncertainty budget. Residual structure is visible and flagged in
all six equal-window model/background fits. AICc ranking is therefore descriptive.

## Synthetic batch and Monte Carlo check

Three independently generated Lorentzian spectra have centres 519.9, 520.4 and
521.0 cm^-1; FWHMs 2.4, 3.0 and 2.6 cm^-1; area 1200 intensity × cm^-1. Gaussian
noise SD is 1.5 intensity units. The third includes a +900 single-channel impulse.
Default retention flags it, and the low signal/residual ratio withholds bootstrap
uncertainty. Explicit exclusion identifies channel 48 and recovers centre
521.0024 cm^-1. This demonstrates the consequence of a preprocessing choice.

100 additional noisy Lorentzian spectra (centre 520.4, FWHM 2.8, area 1200;
201 samples, seed 931) yield centre bias 0.000183 cm^-1, centre RMSE 0.003965 cm^-1
and FWHM bias 0.000003 cm^-1. Local Gaussian 95% centre intervals cover truth in
92/100 trials. Estimated Monte Carlo SE is 0.027; this small study is consistent
with useful local errors but does not establish exact nominal coverage, nor
bootstrap coverage in misspecified experimental data.

## Reproducibility and limits

Run `python examples/reproduce.py --output outputs/case-study` after installing
`.[plots]`. Output folders must be empty/new. The bundled reports use 200 refits;
smaller counts are for smoke checks only. Results may differ in their last digits
with SciPy/BLAS/platform versions. Source data hashes must match exactly.

No experiment was performed by this project. One measured spectrum cannot test
repeatability or spatial variation. Calibration, instrument response, detector
noise, laser heating and sample heterogeneity remain unquantified. This is a
validated software workflow with an honestly limited measured case study, not
an independently calibrated material-property measurement.
