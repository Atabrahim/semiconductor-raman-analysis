# Figure captions

`raw_measurement.png`: experimental silicon wafer spectrum, full recorded range
and a zoom around the first-order optical phonon peak. Raman shift is in cm^-1;
intensity is in uncalibrated source instrument units (a.u.). No smoothing or
background subtraction has been applied. Source: Kauffmann (2021),
DOI 10.12763/VUVLSZ, CC0-1.0. The largest sampled value is not a fitted peak centre.

`silicon_fit.png`: the experimental band with the fitted Voigt + linear background
in 495–545 cm^-1. The lower panel is measured minus fitted intensity. SD uses the
residual degrees of freedom; the serial residual pattern is visibly inconsistent
with ideal independent noise. Neither curve is a measurement of strain or doping.

`sensitivity.png`: conditional estimates for both line shapes, polynomial degrees
0–2 and windows of width 40, 50 and 60 cm^-1, centred on 520 cm^-1. The enlarged
centre axis illustrates sensitivity, not absolute precision. The right panel
compares 200-refit percentile centre intervals under independent and five-channel
resampling. They exclude calibration, instrument-response and model-selection
uncertainty. See `examples/reproduce.py` and `reports/` for numerical values.
