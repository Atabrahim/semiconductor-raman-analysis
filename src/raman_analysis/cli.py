"""Command-line interface for reproducible Raman analysis."""

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .workflow import analyze_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fit isolated Raman peaks with audited uncertainty."
    )
    parser.add_argument(
        "inputs", nargs="+", type=Path, help="Two-column shift (cm^-1), intensity files"
    )
    parser.add_argument("--output", required=True, type=Path, help="New/empty report directory")
    parser.add_argument("--config", type=Path, help="JSON fit_peak keyword configuration")
    parser.add_argument("--metadata", type=Path, help="JSON metadata common to all inputs")
    parser.add_argument(
        "--bootstrap", type=int, default=200, help="Residual refits, >=20 (default: 200)"
    )
    parser.add_argument(
        "--block-size", type=int, default=1, help="Residual block size in channels"
    )
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--skiprows", type=int, default=0, help="Explicit number of header rows"
    )
    parser.add_argument(
        "--allow-invalid", action="store_true", help="Audit and remove nonfinite rows"
    )
    parser.add_argument(
        "--plots", action="store_true", help="Save fit/residual plots (plots extra)"
    )
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.config.read_text(encoding="utf-8")) if args.config else {}
        metadata = (
            json.loads(args.metadata.read_text(encoding="utf-8")) if args.metadata else {}
        )
        if not isinstance(config, dict) or not isinstance(metadata, dict):
            raise ValueError("Configuration and metadata must be JSON objects")
        if args.plots:
            try:
                import matplotlib  # noqa: F401
            except ImportError as error:
                raise ValueError(
                    "Install semiconductor-raman-analysis[plots] to use --plots"
                ) from error
        table = analyze_files(
            args.inputs,
            args.output,
            config=config,
            metadata=metadata,
            n_resamples=args.bootstrap,
            block_size=args.block_size,
            seed=args.seed,
            skiprows=args.skiprows,
            allow_invalid=args.allow_invalid,
            make_plots=args.plots,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    failures = int((table.status == "failed").sum())
    warnings = int((table.status == "warning").sum())
    print(
        f"Wrote {len(table)} report rows to {args.output}; "
        f"{failures} failed, {warnings} with warnings."
    )
    if failures or warnings:
        print(
            "Inspect summary.csv and report.json before interpreting estimates.",
            file=sys.stderr,
        )
    return 1 if failures else 0
