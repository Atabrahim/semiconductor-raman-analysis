# Experimental data provenance

`silicon_raw.txt` is an **unmodified experimental measurement**, renamed for portable paths. `SOURCE_README.txt` is the original measurement description. `provenance.json` records download URLs, original-file identifiers, checksums, acquisition settings and missing metadata.

**Citation:** Kauffmann, Thomas (2021), *Raman spectrum of silicon sample from 50 to 4000 cm-1*, Recherche Data Gouv, version 1.0, [doi:10.12763/VUVLSZ](https://doi.org/10.12763/VUVLSZ). Creator: LMOPS Spectroscopy Platform, Université de Lorraine. Licence: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Please cite the creator and dataset even though CC0 permits reuse without an attribution condition.

The measurement is a silicon calibration wafer supplied by HORIBA, recorded on 25 November 2021 at room temperature using a HORIBA HR Evolution, 532 nm excitation, 1800 gr/mm grating, 100x objective, 100 µm pinhole, one 1-second acquisition, and a CCD cooled to −70 °C. "No polarization" is the source's description. It does not establish a crystal-orientation selection rule.

The first column is Raman shift in cm⁻¹; the second is intensity in source instrument units. There are **10,166 points and one measured spectrum**. This is not a set of independent repeat measurements. No spatial coordinates are provided, so no map is created. Laser power at the sample, numerical sample temperature, calibration uncertainty, detector response, spectral resolution and an instrument line-shape calibration are not supplied. Grating density or sampling step alone does not determine spectral resolution.

The local analysis selects a window around the first-order Si peak. It does not normalize, smooth, interpolate or overwrite the source file. Baselines are fitted jointly with peak models. Candidate spikes are retained unless exclusion is explicitly requested. Every exported result records that decision. Resampling produces **synthetic bootstrap spectra**, not additional experimental observations.

## Original candidate rejected after byte-level inspection

The original roadmap nominated Sojo-Gordillo et al., Zenodo [10.5281/zenodo.5806684](https://doi.org/10.5281/zenodo.5806684), CC BY 4.0. Its description mentions Raman maps. On 20 September 2026, the 202,695,944-byte archive was downloaded and matched published MD5 `57bcb52f239d66334791d5f73a9e495b`. Inspection found 402 entries: 175 CSV, 123 TIFF, 66 TXT and 38 directories. The files and archive README concern I–V, Seebeck and SEM measurements; no Raman spectra are present. The companion record 7043726 also describes transport data. Neither is used as Raman evidence.

The replacement preserves the original semiconductor Raman-analysis problem, but changes the measured sample from nanowires to a wafer. The single-spectrum limitation is explicit; batch processing is verified with independent synthetic input files. No claimed nanowire, strain or doping result is carried over from the original proposal.
