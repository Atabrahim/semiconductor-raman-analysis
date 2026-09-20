"""Auditable single-file and batch reports; invalid files remain visible as failures."""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from . import __version__
from .fitting import fit_peak
from .spectrum import read_spectrum
from .uncertainty import bootstrap_fit

FIT_KEYS = {
    "model",
    "baseline_degree",
    "window_cm1",
    "center_bounds_cm1",
    "exclude_spikes",
    "max_nfev",
}


def analyze_files(
    paths: list[str | Path],
    output_dir: str | Path,
    *,
    config: dict | None = None,
    n_resamples: int = 200,
    block_size: int = 1,
    seed: int = 2026,
    skiprows: int = 0,
    allow_invalid: bool = False,
    metadata: dict | None = None,
    make_plots: bool = False,
) -> pd.DataFrame:
    """Write summary.csv, report.json and per-file fit/bootstrap tables.

    Every input gets a row. A bad file does not prevent processing the others.
    Existing output files are refused; select a fresh directory for each analysis.
    File seeds are seed + input index, recorded with the input order. Caller-supplied
    metadata applies to all input files; do not mix acquisition conditions that way.
    """
    if not paths:
        raise ValueError("Need at least one input file")
    config = dict(config or {})
    if unknown := set(config) - FIT_KEYS:
        raise ValueError(f"Unknown fit configuration keys: {sorted(unknown)}")
    if type(n_resamples) is not int or n_resamples < 20:
        raise ValueError("n_resamples must be an integer >=20")
    if type(block_size) is not int or block_size < 1:
        raise ValueError("block_size must be a positive integer")
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    output = Path(output_dir)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("Output directory is not empty; use a new directory")
    output.mkdir(parents=True, exist_ok=True)
    reports, rows = [], []
    for index, path in enumerate(map(Path, paths)):
        label = f"{index:03d}_{re.sub(r'[^a-zA-Z0-9_-]', '_', path.stem)}"
        report = {"input": path.name, "id": label, "status": "ok"}
        row = {"input": path.name, "id": label, "status": "ok"}
        try:
            spectrum = read_spectrum(
                path, skiprows=skiprows, allow_invalid=allow_invalid, metadata=metadata
            )
            fit = fit_peak(spectrum, **config)
            report.update(audit=spectrum.audit, metadata=spectrum.metadata, fit=fit.summary())
            row.update(
                model=fit.model,
                baseline_degree=fit.baseline_degree,
                **fit.parameters,
                fwhm_cm1=fit.fwhm_cm1,
                residual_sd=fit.residual_sd,
                lag1_correlation=fit.lag1_correlation,
                flags=";".join(fit.flags),
            )
            if fit.flags:
                row["status"] = report["status"] = "warning"
            try:
                bootstrap = bootstrap_fit(
                    fit, n_resamples=n_resamples, block_size=block_size, seed=seed + index
                )
                report["uncertainty"] = bootstrap.summary()
                pd.DataFrame(bootstrap.samples, columns=bootstrap.quantities).to_csv(
                    output / f"{label}_bootstrap.csv", index=False
                )
                for quantity, interval in bootstrap.intervals.items():
                    row[f"{quantity}_low"] = interval[0] if interval else None
                    row[f"{quantity}_high"] = interval[1] if interval else None
                if bootstrap.flags or bootstrap.failed_refits:
                    row["status"] = report["status"] = "warning"
            except (ValueError, RuntimeError, np.linalg.LinAlgError) as error:
                report["uncertainty_error"] = str(error)
                row["uncertainty_error"] = str(error)
                row["status"] = report["status"] = "warning"
            pd.DataFrame(
                {
                    "spectrum_index": fit.source_indices,
                    "shift_cm1": fit.shift_cm1,
                    "measured_intensity": fit.observed,
                    "fitted_intensity": fit.predicted,
                    "fitted_background": fit.baseline,
                    "residual_measured_minus_fit": fit.residual,
                }
            ).to_csv(output / f"{label}_fit.csv", index=False)
            if make_plots:
                from .plotting import plot_fit

                plot_fit(spectrum, fit, output / f"{label}_fit.png", title=path.name)
        except (OSError, ValueError, RuntimeError, np.linalg.LinAlgError) as error:
            row.update(status="failed", error=f"{type(error).__name__}: {error}")
            report.update(status="failed", error=row["error"])
        rows.append(row)
        reports.append(report)
    table = pd.DataFrame(rows)
    table.to_csv(output / "summary.csv", index=False)
    payload = {
        "software_version": __version__,
        "fit_configuration": config,
        "n_resamples": n_resamples,
        "block_size": block_size,
        "seed": seed,
        "interpretation": "Conditional model estimates; no strain/doping inversion",
        "files": reports,
    }
    (output / "report.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    return table
