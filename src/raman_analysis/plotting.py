"""Scientific figures; plotting is optional and never changes observations."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter, MaxNLocator

from .fitting import PeakFit
from .spectrum import Spectrum

STYLE = {
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 110,
    "savefig.dpi": 180,
}


def plot_fit(
    spectrum: Spectrum, fit: PeakFit, path: str | Path, *, title: str = "Raman peak fit"
):
    """Save measured/fitted intensity, background and residuals; mark candidate spikes."""
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(
            2,
            1,
            figsize=(8.2, 6.5),
            sharex=True,
            gridspec_kw={"height_ratios": [2.4, 1]},
            layout="constrained",
        )
        axes[0].plot(fit.shift_cm1, fit.observed, ".", ms=4, color="#263c54", label="Measured")
        axes[0].plot(
            fit.shift_cm1,
            fit.predicted,
            color="#cf4c25",
            label=f"{fit.model.title()} + background",
        )
        axes[0].plot(
            fit.shift_cm1, fit.baseline, "--", color="#148479", label="Fitted background"
        )
        if fit.spike_indices.size:
            idx = fit.spike_indices
            axes[0].plot(
                spectrum.shift_cm1[idx],
                spectrum.intensity[idx],
                "x",
                color="#a52656",
                label="Spike candidates (see report)",
            )
        axes[0].set(ylabel="Intensity (source units, a.u.)", title=title)
        axes[0].legend(frameon=False)
        axes[1].axhline(0, color="0.5", lw=0.8)
        axes[1].plot(fit.shift_cm1, fit.residual, ".-", ms=3, lw=0.8, color="#263c54")
        axes[1].set(
            xlabel=r"Raman shift (cm$^{-1}$)",
            ylabel="Measured − fit (a.u.)",
            title=(
                f"Residuals: SD = {fit.residual_sd:.2f} a.u.; "
                f"lag-1 correlation = {fit.lag1_correlation:.2f}"
            ),
        )
        fig.savefig(path)
        plt.close(fig)


def plot_raw(spectrum: Spectrum, path: str | Path):
    """Show original measurement and targeted band without subtracting a baseline."""
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.9), layout="constrained")
        for axis in axes:
            axis.plot(spectrum.shift_cm1, spectrum.intensity, color="#263c54", lw=1)
            axis.set(xlabel=r"Raman shift (cm$^{-1}$)", ylabel="Intensity (source units, a.u.)")
        axes[0].set(title="Experimental silicon wafer spectrum", xlim=(50, 4000))
        axes[1].set(title="First-order band: unprocessed", xlim=(490, 550))
        fig.savefig(path)
        plt.close(fig)


def plot_sensitivity(table, intervals: dict, path: str | Path):
    """Window/model/background estimates with conditional bootstrap shown separately."""
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 3, figsize=(12, 4.4), layout="constrained")
        colors = {"voigt": "#148479", "lorentzian": "#cf4c25"}
        for model, group in table[table.status == "ok"].groupby("model"):
            for degree in sorted(group.baseline_degree.unique()):
                selected = group[group.baseline_degree == degree].sort_values("window_low_cm1")
                width = selected.window_high_cm1 - selected.window_low_cm1
                for axis, quantity in zip(axes[:2], ("center_cm1", "fwhm_cm1"), strict=True):
                    axis.plot(
                        width,
                        selected[quantity],
                        marker=["o", "s", "^"][degree],
                        color=colors[model],
                        lw=0.8,
                        label=f"{model.title()}, bg {degree}",
                    )
        axes[0].set(
            xlabel=r"Fit-window width (cm$^{-1}$)",
            ylabel=r"Fitted centre (cm$^{-1}$)",
            title="Window and background sensitivity",
        )
        axes[0].ticklabel_format(useOffset=False)
        axes[1].set(
            xlabel=r"Fit-window width (cm$^{-1}$)",
            ylabel=r"Observed FWHM (cm$^{-1}$)",
            title="Line shape affects observed width",
        )
        axes[1].legend(frameon=False, fontsize=8)
        for index, (_label, bounds) in enumerate(intervals.items()):
            low, high = bounds
            axes[2].plot([low, high], [index, index], "o-", color="#263c54", ms=4)
        axes[2].set(
            yticks=np.arange(len(intervals)),
            yticklabels=list(intervals),
            xlabel=r"Fitted centre (cm$^{-1}$)",
            title="95% conditional bootstrap intervals",
            ylim=(-0.6, len(intervals) - 0.4),
        )
        axes[2].xaxis.set_major_locator(MaxNLocator(nbins=3))
        axes[2].xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
        fig.savefig(path)
        plt.close(fig)
