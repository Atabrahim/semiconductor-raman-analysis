"""Two-column import and explicit quality-control decisions; no silent smoothing."""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class Spectrum:
    """Increasing Raman shift in cm^-1 and intensity in source instrument units."""

    shift_cm1: ArrayLike
    intensity: ArrayLike
    metadata: dict = field(default_factory=dict)
    audit: tuple[str, ...] = ()

    def __post_init__(self):
        shift = np.array(self.shift_cm1, dtype=float, copy=True)
        intensity = np.array(self.intensity, dtype=float, copy=True)
        if shift.ndim != 1 or intensity.shape != shift.shape or shift.size < 9:
            raise ValueError("Spectrum needs matching one-dimensional arrays with >=9 points")
        if not np.isfinite(shift).all() or not np.isfinite(intensity).all():
            raise ValueError("Spectrum contains nonfinite values")
        if np.any(np.diff(shift) <= 0):
            raise ValueError("Raman shift must be strictly increasing, without duplicates")
        shift.setflags(write=False)
        intensity.setflags(write=False)
        object.__setattr__(self, "shift_cm1", shift)
        object.__setattr__(self, "intensity", intensity)


def read_spectrum(
    path: str | Path,
    *,
    skiprows: int = 0,
    allow_invalid: bool = False,
    metadata: dict | None = None,
) -> Spectrum:
    """Read two whitespace/comma-separated columns, optionally with explicit header skip.

    Invalid rows raise by default. Opt-in removal records source row numbers.
    Descending acquisition axes are reversed together with intensity and audited.
    """
    path = Path(path)
    if isinstance(skiprows, bool) or not isinstance(skiprows, int) or skiprows < 0:
        raise ValueError("skiprows must be a nonnegative integer")
    values, invalid_rows = [], []
    for row_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if row_number <= skiprows:
            continue
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        columns = line.split(",") if "," in line else line.split()
        if len(columns) != 2:
            raise ValueError(f"Expected exactly two columns at source row {row_number}")
        try:
            row = [float(column) for column in columns]
        except ValueError:
            row = [np.nan, np.nan]
        if not np.isfinite(row).all():
            invalid_rows.append(row_number)
        else:
            values.append(row)
    audit = [
        f"source_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}",
        f"explicit_header_rows_skipped={skiprows}",
    ]
    if invalid_rows:
        if not allow_invalid:
            raise ValueError(f"Invalid/nonfinite source rows: {invalid_rows}")
        audit.append(f"removed_invalid_source_rows={invalid_rows}")
    if len(values) < 9:
        raise ValueError("Need at least nine valid measured points")
    values = np.asarray(values)
    if len(values) >= 2 and np.all(np.diff(values[:, 0]) < 0):
        values = values[::-1]
        audit.append("reversed_descending_axis_and_intensity")
    return Spectrum(values[:, 0], values[:, 1], dict(metadata or {}), tuple(audit))


def spike_candidates(intensity: ArrayLike, threshold: float = 8.0) -> NDArray[np.bool_]:
    """Flag isolated positive one-channel impulses, not a definitive cosmic-ray detector.

    Both jumps must exceed threshold times the local outside slope and a robust
    noise floor. Endpoints are not assessed. Flags never modify observations.
    """
    signal = np.asarray(intensity, dtype=float)
    if signal.ndim != 1 or len(signal) < 5 or not np.isfinite(signal).all():
        raise ValueError("Need at least five finite intensities")
    if not np.isfinite(threshold) or threshold <= 1:
        raise ValueError("spike threshold must be finite and >1")
    difference = np.diff(signal)
    noise = np.median(np.abs(difference - np.median(difference))) / (0.67449 * np.sqrt(2))
    floor = max(noise, np.finfo(float).eps * max(1, np.max(np.abs(signal))))
    outside = np.maximum(np.abs(difference[:-3]), np.abs(difference[3:]))
    jump = np.minimum(difference[1:-2], -difference[2:-1])
    flags = np.zeros(len(signal), dtype=bool)
    flags[2:-2] = jump > threshold * np.maximum(outside, floor)
    return flags
