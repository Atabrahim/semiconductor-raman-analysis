# Learning and interview notes

## Explain the work in 30 seconds

“This portfolio project analyses a public silicon Raman spectrum. The Python
workflow fits a peak and its background together, compares Lorentzian and Voigt
models, and reports bootstrap uncertainty and residual diagnostics. Known-parameter
synthetic tests check numerical recovery. The measured residuals remain correlated,
so I present conditional peak estimates rather than claiming strain or doping.
The implementation and QA were AI-assisted; I am learning to explain and reproduce
each part.”

Use the last sentence honestly. Do not claim independent implementation or
validation unless you have actually repeated that work.

## Concepts to understand

| Term | Meaning and engineering use | Example here |
|---|---|---|
| Raman shift | Photon wavenumber change associated with inelastic scattering | Silicon optical-phonon band near 520 cm^-1 |
| Line shape | A model of intensity around a band | Lorentzian versus Gaussian-convolved Lorentzian (Voigt) |
| FWHM | Width at half the background-free peak height | Voigt width needs a root solve; it is not gamma or sigma |
| Baseline | Slowly varying intensity unrelated to the targeted peak | Polynomial fitted jointly so peak/background covariance remains visible |
| Residual | Measured minus fitted intensity | Structured residuals reveal inadequacy hidden by the tall peak |
| Identifiability | Whether observations distinguish model parameters | Gaussian and Lorentzian widths can trade off |
| Bootstrap | Refit artificial observations built from resampled residuals | Fixed seed and explicit refit failures make uncertainty auditable |
| Model discrepancy | Difference between the assumed mean model and reality | Block resampling does not repair a wrong line shape |
| AICc | Fit/complexity ranking under a common likelihood | Cannot compare different windows as if they used the same observations |
| Provenance | Evidence connecting outputs to original measurements and decisions | Hash, metadata, window, exclusions, seed and version |

## Technical explanation

Follow `read_spectrum` into `fit_peak`. Explain the normalized shift coordinate,
logarithmic positivity constraints, bounded trust-region method, SVD covariance
and independent half-height root. Explain why simultaneous fitting is preferable
to treating a previously estimated background as exact. Then follow
`bootstrap_fit`: the retained mask is fixed, block starts are sampled, residuals
are recentered/scaled, each replica is refitted and failures are counted.

`rank_fits` enforces common observations; `sensitivity_study` deliberately avoids
AICc rankings across windows. `analyze_files` converts results to auditable tables
and keeps failed files visible. The CLI is a thin argument parser. Plotting is
optional; tests import the same public package users install.

## Questions to practise

1. What makes a Voigt profile different from a Lorentzian, and what would justify
   interpreting its components physically?
2. Why can a fitted centre be more precise than the acquisition spacing yet still
   be inaccurate in absolute units?
3. What does the residual correlation say? What does it not identify?
4. Which uncertainty sources are missing from the reported intervals?
5. Why fit background and peak together? What happens with a narrow window?
6. Why is a five-channel block length a sensitivity choice rather than a known truth?
7. How do you prevent silent data cleaning and misleading model comparisons?
8. What would change if the spectrum were asymmetric, saturated or multi-peak?
9. How would you design repeated measurements and calibration checks to improve this study?
10. Which tests are independent of the fitted implementation, and why does that matter?

## Accurate portfolio wording

CV: “Created an AI-assisted Python Raman-analysis portfolio project with joint
peak/background fitting, residual-bootstrap uncertainty, traceable batch reports
and validation against analytical and synthetic reference cases.”

LinkedIn: “Raman spectroscopy analysis for a public silicon wafer measurement:
Lorentzian/Voigt fitting, residual diagnostics, uncertainty and model sensitivity,
with reproducible reports and scientific tests. AI-assisted development; experimental
data credited to the original researchers.”

New competencies relative to Projects 1 and 2: experimental provenance, inverse
parameter estimation, preprocessing audit, residual interpretation and uncertainty
under imperfect model assumptions. Relevant to materials characterization, lab
R&D, test/data analysis and scientific software roles; this is not instrument
operation experience or an industrial metrology qualification.
