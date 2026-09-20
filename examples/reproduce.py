"""Reproduce the measured case, synthetic batch and independent recovery checks."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from raman_analysis import (
    Spectrum,
    bootstrap_fit,
    fit_peak,
    rank_fits,
    read_spectrum,
    sensitivity_study,
)
from raman_analysis.plotting import plot_raw, plot_sensitivity
from raman_analysis.workflow import analyze_files

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("outputs/case-study"))
    parser.add_argument("--bootstrap", type=int, default=200)
    args = parser.parse_args()
    output = args.output
    if output.exists() and any(output.iterdir()):
        parser.error("Output directory is not empty; choose a fresh directory")
    output.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((ROOT / "data/provenance.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / "examples/silicon.json").read_text(encoding="utf-8"))
    path = ROOT / "data/silicon_raw.txt"
    spectrum = read_spectrum(path, metadata=metadata)
    measured = analyze_files(
        [path],
        output / "measured",
        config=config,
        metadata=metadata,
        block_size=5,
        n_resamples=args.bootstrap,
        make_plots=True,
    )
    assert (measured.status != "failed").all()
    fit = fit_peak(spectrum, **config)
    iid = bootstrap_fit(fit, n_resamples=args.bootstrap, block_size=1)
    (output / "independent_bootstrap.json").write_text(
        json.dumps(iid.summary(), indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    measured_report = json.loads((output / "measured/report.json").read_text(encoding="utf-8"))
    blocked = measured_report["files"][0]["uncertainty"]
    compare = rank_fits(
        [
            fit_peak(spectrum, model=model, baseline_degree=degree)
            for model in ("lorentzian", "voigt")
            for degree in (0, 1, 2)
        ]
    )
    compare.to_csv(output / "model_comparison.csv", index=False)
    sensitivity = sensitivity_study(spectrum)
    assert (sensitivity.status == "ok").all()
    sensitivity.to_csv(output / "sensitivity.csv", index=False)
    plot_raw(spectrum, output / "raw_measurement.png")
    plot_sensitivity(
        sensitivity,
        {
            "Independent": iid.intervals["center_cm1"],
            "5-channel blocks": blocked["intervals"]["center_cm1"],
        },
        output / "sensitivity.png",
    )

    # Independent analytical Lorentz formula supplies explicit synthetic truth.
    synthetic_dir = output / "synthetic_inputs"
    synthetic_dir.mkdir()
    shift = np.linspace(495, 545, 201)
    truth, paths = [], []
    for index, (center, gamma, label) in enumerate(
        [
            (519.9, 1.2, "clean"),
            (520.4, 1.5, "clean"),
            (521.0, 1.3, "spike"),
        ]
    ):
        signal = 1200 * gamma / (np.pi * ((shift - center) ** 2 + gamma**2)) + 12
        signal += np.random.default_rng(50 + index).normal(0, 1.5, len(shift))
        if label == "spike":
            signal[48] += 900
        filename = synthetic_dir / f"synthetic_{index}_{label}.txt"
        np.savetxt(filename, np.column_stack([shift, signal]), fmt="%.10g")
        paths.append(filename)
        truth.append(
            {
                "input": filename.name,
                "true_center_cm1": center,
                "true_fwhm_cm1": 2 * gamma,
                "true_area_intensity_cm1": 1200,
                "category": "SYNTHETIC DEMONSTRATION",
            }
        )
    pd.DataFrame(truth).to_csv(output / "synthetic_truth.csv", index=False)
    synthetic = analyze_files(
        paths,
        output / "synthetic_batch",
        config={"model": "lorentzian"},
        n_resamples=args.bootstrap,
        metadata={"category": "SYNTHETIC DEMONSTRATION", "noise_sd": 1.5},
    )
    assert (synthetic.status != "failed").all()
    excluded = fit_peak(read_spectrum(paths[-1]), model="lorentzian", exclude_spikes=True)
    assert excluded.excluded_indices.tolist() == [48]

    # Monte Carlo validation of the local covariance under its own noise assumptions.
    rng = np.random.default_rng(931)
    true_center, true_width, noise_sd = 520.4, 2.8, 1.5
    clean = 1200 * 1.4 / (np.pi * ((shift - true_center) ** 2 + 1.4**2)) + 12
    centers, widths, standard_errors = [], [], []
    for _ in range(100):
        replica = Spectrum(shift, clean + rng.normal(0, noise_sd, len(shift)))
        estimate = fit_peak(replica, model="lorentzian")
        centers.append(estimate.center_cm1)
        widths.append(estimate.fwhm_cm1)
        standard_errors.append(estimate.center_se_cm1)
    centers = np.asarray(centers)
    coverage = np.mean(abs(centers - true_center) <= 1.96 * np.asarray(standard_errors))
    validation = {
        "category": "SYNTHETIC VALIDATION; not experimental accuracy",
        "trials": 100,
        "seed": 931,
        "independent_gaussian_noise_sd": noise_sd,
        "center_bias_cm1": float(np.mean(centers - true_center)),
        "center_rmse_cm1": float(np.sqrt(np.mean((centers - true_center) ** 2))),
        "fwhm_bias_cm1": float(np.mean(np.asarray(widths) - true_width)),
        "local_95_percent_center_interval_coverage": float(coverage),
        "coverage_monte_carlo_se": float(np.sqrt(coverage * (1 - coverage) / 100)),
        "spike_excluded_center_cm1": excluded.center_cm1,
        "spike_excluded_indices": excluded.excluded_indices.tolist(),
    }
    assert abs(validation["center_bias_cm1"]) < 0.01
    assert abs(validation["fwhm_bias_cm1"]) < 0.02
    assert 0.85 <= coverage <= 1
    (output / "validation.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"output": str(output), "validation": validation}, indent=2))


if __name__ == "__main__":
    main()
