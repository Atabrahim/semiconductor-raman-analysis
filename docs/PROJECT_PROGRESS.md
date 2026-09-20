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
Task 3 is in progress: strict import/audit, spike candidates retained by default,
positive Lorentzian/Voigt models, bounded joint peak/background fitting,
SVD covariance, AICc and residual/quality diagnostics are implemented.
**38 tests passed** on recovery (Python 3.12); independent numerical convolution,
analytic limits, known-parameter recovery, input validation and scale invariance
are covered. Local checkpoint `1cf0046` preserves the complete recovered work.

Initial measured fits yield centres near 520.515 cm^-1 and observed widths around
3.48--3.54 cm^-1, depending on line shape. Residual correlation is flagged; the
working independent-noise likelihood does not capture all observed structure.
These are conditional fit results, not independently calibrated material properties.

## Remaining milestones

1. Finish Task 3: bootstrap uncertainty for all reported peak/background quantities,
   same-data model comparison, window/background sensitivity and scientific tests.
2. Task 4: CLI, batch reports, reproducible measured case, figures and documentation.
3. Task 5: full tests/lint, clean wheel/sdist installation, documented commands,
   actual GitHub Actions verification and v0.1.0 release.

Latest verified GitHub checkpoint: `b453812ef18413b9d5ae63f6d378c10a2d6e981f`
(scaffold/package initializer). Core code, tests and dataset are being published in
recovery commits; verify remote HEAD before resuming. This field intentionally
records an already verified predecessor, not a self-referential commit hash.

Known scientific issue: serial residual structure/model mismatch in the measured
spectrum. Quantify its effect without claiming bootstrap removes model bias.
Next action: finish publishing the recovered checkpoint, then implement uncertainty.
GitHub write operations use the authorized browser; do not repeat unavailable
repository-creation connector probes.

## Attribution

Software development, numerical checks and documentation are performed with AI assistance. Dataset authors performed the experiments. This record does not establish which technical work the owner can personally explain or has independently reproduced.
