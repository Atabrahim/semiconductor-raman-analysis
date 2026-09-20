# Project 3 progress

Updated: 2026-09-20. Read this record and compare the local working tree with GitHub before resuming. Do not recreate the repository or redesign the agreed scope.

## Original objectives and scope

Recovered from Semiconductor_Portfolio_Plan.md (18 September 2026): **Raman Spectroscopy Analysis with Uncertainty**, repository `semiconductor-raman-analysis`. Analyse one measured silicon-nanowire collection with traceable preprocessing, baseline/line-shape comparison, peak position and width uncertainty, and batch reporting. Include a spatial map only if acquisition metadata supports one. Do not infer unique strain, temperature or doping from peak shifts.

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

## Validation status

No scientific code or automated tests implemented yet. No fit, simulation or experimental-validation claim is made.

## Remaining milestones

1. Publish scaffold and this continuity record; inspect raw spectra and record licence/metadata/file checksums.
2. Implement import/QC and peak fitting with synthetic verification; publish.
3. Implement uncertainty, baseline/line-shape comparison and measured batch case; publish.
4. Generate and visually inspect figures; document results and limitations; publish.
5. Run full tests/lint, clean package installation, README commands and actual CI; publish release.

Latest verified GitHub commit: `9053e5258836440889624d4a3f270c30bed5ed8d` (repository creation). Later commits may contain this record; verify the current remote rather than treating this hash as HEAD.

Known issue: the original source archive contains no Raman spectra. Next action: finish scaffold backup and verify a replacement collection within the original Raman-analysis scope. GitHub write operations use the authorized browser; do not repeat unavailable repository-creation connector probes.

## Attribution

Software development, numerical checks and documentation are performed with AI assistance. Dataset authors performed the experiments. This record does not establish which technical work the owner can personally explain or has independently reproduced.
