# Raman Spectroscopy Analysis with Uncertainty

Reproducible analysis of measured silicon-nanowire Raman spectra, with traceable preprocessing, competing line shapes and uncertainty diagnostics.

**Status: in development.** No fitted scientific results are claimed yet. The original scope and next action are recorded in [the project progress file](docs/PROJECT_PROGRESS.md).

## Scientific question

Which spectral differences survive changes in baseline treatment, noise and line-shape assumptions? A precise fitted Raman shift alone does not establish strain, temperature or dopant concentration.

## Fixed first-release scope

- Import and validate one public measured silicon-nanowire collection with provenance.
- Flag invalid points and isolated spikes without silently changing observations.
- Compare baseline treatments and symmetric/asymmetric peak shapes.
- Estimate peak location and width with conditional uncertainty and fit-quality flags.
- Produce a reproducible batch report and scientific figures; map only if spatial metadata supports it.
- Provide an installable Python API, CLI, meaningful tests and working GitHub Actions.

No universal classifier, instrument control, strain/doping calibration or dashboard is planned.

## Data and licensing

The selected source is Sojo-Gordillo et al., *Dataset for "Tuning the thermoelectric properties of boron-doped silicon nanowires integrated in a micro-harvester"*, Zenodo version 1.0, [doi:10.5281/zenodo.5806684](https://doi.org/10.5281/zenodo.5806684). The record identifies tip-enhanced Raman maps and a **CC BY 4.0** data licence. Archive structure and measurement metadata are being inspected before selecting a subset.

Original software is MIT licensed. External experimental data retain their own licence and attribution. Development is AI-assisted; experimental collection and technical validation are not attributed to the repository owner unless independently performed by them.
