# Project 3 progress

Updated: 2026-09-20. Read this record and compare the local working tree with GitHub before resuming. Do not recreate the repository or redesign the agreed scope.

## Original objectives and scope

Recovered from Semiconductor_Portfolio_Plan.md (18 September 2026): **Raman Spectroscopy Analysis with Uncertainty**, repository `semiconductor-raman-analysis`. Analyse one measured silicon Raman dataset (original nanowire candidate proved unsuitable) with traceable preprocessing, baseline/line-shape comparison, peak position and width uncertainty, and batch reporting. Include a spatial map only if acquisition metadata supports one. Do not infer unique strain, temperature or doping from peak shifts.

## Architecture

Small `src/raman_analysis` package: data validation/import, peak model/fitting, uncertainty/batch workflow, optional plotting, thin CLI. Tests accompany each scientific component. A reproducible example supplies figures/reports. JSON configuration and provenance record explicit units and choices. No dependency on the first two portfolio repositories is necessary.

## Completed and verified

- Original roadmap recovered, including the exact project title and repository name.
- Projects 1 and 2 inspected: reuse explicit units, numerical safeguards, independent checks, thin CLI, `src` packaging, clean wheel verification and actual CI validation. New competencies are experimental preprocessing, line-shape comparison and resampling uncertainty.
- Workspace and authenticated GitHub profile inspected: no existing Project 3 implementation or duplicate repository.
- Public repository created under Atabrahim; initial README verified in browser.
- Zenodo metadata retrieved: version 1.0, DOI `10.5281/zenodo.5806684`, licence `cc-by-4.0`.

## Dataset investigation

Sojo-Gordillo et al., *Dataset for "Tuning the thermoelectric properties of boron-doped silicon nanowires integrated in a micro-harvester"*.

Archive: `Tuning_the_TE_props_of_Si_NW_integrated_in_a_uTEG-Raw_Data.zip`; 202695944 bytes; published MD5 `57bcb52f239d66334791d5f73a9e495b`. The source describes tip-enhanced Raman maps as tabulated text. The downloaded archive matches the published MD5. Its 402 entries contain 175 CSV, 123 TIFF and 66 TXT files, all under transport/SEM folders; there are no Raman/TERS spectra. The archive README likewise describes only I-V and Seebeck data. This source is unsuitable for the measured Raman case despite its record description. Preserve this discrepancy; inspect a replacement measured silicon collection before implementing a dataset-specific importer. Do not invent measurement conditions.

## Current verified dataset and implementation

The selected replacement is Thomas H. Kauffmann's silicon wafer Raman spectrum,
Recherche Data Gouv DOI **10.12763/VUVLSZ**, version 1.0, CC0-1.0.
`data/provenance.json` records conditions, original URLs and verified hashes.
There is one experimental spectrum (10,166 finite, ordered points); no spatial
coordinates, calibration uncertainty or measured instrument response are supplied.
No spatial map or unique strain/doping/temperature inference is supported.
Batch processing will be verified separately on labelled synthetic files.

Task 1 (recovery and feasibility) and Task 2 (repository scaffold) are complete.
Task 3 is implemented and verified: strict import/audit, spike candidates retained
by default, Lorentzian/Voigt joint background fitting, SVD covariance, AICc with
same-data enforcement, residual/QC flags, fixed-mask residual/block bootstrap for
all reported parameters, and declared background/line-shape/window sensitivity.

**54 tests passed** (Python 3.12). Ruff lint and formatting pass. Tests include
independent convolution, analytic limits, known-parameter recovery, input checks,
scale invariance, bootstrap reproducibility, covariance-scale agreement under
independent Gaussian noise, wider intervals for a controlled correlated-noise
case, counted refit failures and prevention of invalid cross-window AICc ranking.
Real-data bootstrap and the 18-choice sensitivity study were also executed.

The measured Voigt/linear fit has centre near 520.515 cm^-1 and observed FWHM
near 3.541 cm^-1. Residual correlation is flagged. Conditional intervals exclude
axis calibration, instrumental response and model bias; no material-property
inversion is claimed. Local recovery checkpoint `1cf0046` preserved all work
before development resumed. All recovered files were verified byte-identical
against GitHub checkpoint `def2a2ac880e47232a30beb742ce336be74e1f7a`.

## Remaining milestones

1. Publish the verified Task 3 workflow and this record.
2. Task 4: CLI, batch reports, reproducible measured case, figures and documentation.
3. Task 5: full tests/lint, clean wheel/sdist installation, documented commands,
   actual GitHub Actions verification and v0.1.0 release.

Latest verified GitHub checkpoint: `def2a2ac880e47232a30beb742ce336be74e1f7a`
(recovered core/data/tests backup). Task 3 additions are being published; verify
remote HEAD before resuming. This field intentionally
records an already verified predecessor, not a self-referential commit hash.

Known scientific issue: serial residual structure/model mismatch in the measured
spectrum. Quantify its effect without claiming bootstrap removes model bias.
Next action: publish Task 3, then complete Task 4 batch/CLI/case-study outputs.
GitHub write operations use the authorized browser; do not repeat unavailable
repository-creation connector probes.

## Attribution

Software development, numerical checks and documentation are performed with AI assistance. Dataset authors performed the experiments. This record does not establish which technical work the owner can personally explain or has independently reproduced.
