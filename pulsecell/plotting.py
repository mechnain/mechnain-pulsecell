"""Matplotlib plotting helpers for Streamlit and reports."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def apply_dark_axis_style(ax) -> None:
    ax.set_facecolor("#111111")
    ax.figure.set_facecolor("#080808")
    ax.tick_params(colors="#d8d8d8")
    ax.xaxis.label.set_color("#f5f5f5")
    ax.yaxis.label.set_color("#f5f5f5")
    ax.title.set_color("#f5f5f5")
    for spine in ax.spines.values():
        spine.set_color("#2a2a2a")
    ax.grid(True, alpha=0.22, color="#6a6a6a")


def comparison_line_plot(
    dc_df: pd.DataFrame,
    test_df: pd.DataFrame,
    y_col: str,
    title: str,
    ylabel: str,
):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(dc_df["time_s"], dc_df[y_col], label="DC reference", color="#b8b8b8", linewidth=1.8)
    ax.plot(test_df["time_s"], test_df[y_col], label="Test waveform", color="#f2b84b", linewidth=1.8)
    ax.set_title(title, pad=12)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel(ylabel)
    ax.legend(facecolor="#151515", edgecolor="#2a2a2a", labelcolor="#f5f5f5")
    apply_dark_axis_style(ax)
    fig.tight_layout()
    return fig


def heatmap_plot(
    df: pd.DataFrame,
    value_col: str,
    title: str,
    cbar_label: str,
):
    pivot = df.pivot_table(
        index="duty_cycle_percent",
        columns="frequency_hz",
        values=value_col,
        aggfunc="mean",
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    image = ax.imshow(pivot.values, aspect="auto", origin="lower", cmap="inferno")
    ax.set_title(title, pad=12)
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Duty cycle [%]")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"{value:.0f}" for value in pivot.columns], rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([f"{value:.0f}" for value in pivot.index])
    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label(cbar_label)
    cbar.ax.yaxis.label.set_color("#f5f5f5")
    cbar.ax.tick_params(colors="#d8d8d8")
    apply_dark_axis_style(ax)
    fig.tight_layout()
    return fig


def histogram_plot(df: pd.DataFrame, value_col: str, title: str, xlabel: str):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(df[value_col], bins=20, color="#c47a3a", edgecolor="#050505", alpha=0.9)
    ax.set_title(title, pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Sample count")
    apply_dark_axis_style(ax)
    fig.tight_layout()
    return fig


def calibration_fit_plot(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(
        df["time_s"],
        df["observed_bubble_coverage_fraction"] * 100.0,
        label="Observed",
        color="#b8b8b8",
    )
    ax.plot(
        df["time_s"],
        df["simulated_bubble_coverage_fraction"] * 100.0,
        label="Fitted model",
        color="#f2b84b",
    )
    ax.set_title("Measured vs Simulated Bubble Coverage", pad=12)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Bubble coverage [%]")
    ax.legend(facecolor="#151515", edgecolor="#2a2a2a", labelcolor="#f5f5f5")
    apply_dark_axis_style(ax)
    fig.tight_layout()
    return fig


def residual_plot(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 3))
    ax.axhline(0.0, color="#b8b8b8", linewidth=1.0)
    ax.plot(df["time_s"], df["residual_fraction"] * 100.0, color="#b33a3a")
    ax.set_title("Calibration Residual", pad=12)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Residual [percentage points]")
    apply_dark_axis_style(ax)
    fig.tight_layout()
    return fig
