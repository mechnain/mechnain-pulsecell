"""Fit simplified bubble-model coefficients to observed or synthetic data."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from pulsecell.simulation import simulate_bubble_coverage


REQUIRED_CALIBRATION_COLUMNS = {
    "time_s",
    "current_A",
    "observed_bubble_coverage_fraction",
}


def validate_calibration_data(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_CALIBRATION_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Calibration CSV missing required columns: {sorted(missing)}")
    clean = df[list(REQUIRED_CALIBRATION_COLUMNS)].copy()
    clean = clean.sort_values("time_s").reset_index(drop=True)
    if (clean["time_s"] < 0).any():
        raise ValueError("Calibration time values cannot be negative.")
    if clean["time_s"].duplicated().any():
        raise ValueError("Calibration time values must be unique.")
    observed = clean["observed_bubble_coverage_fraction"]
    if ((observed < 0) | (observed > 0.95)).any():
        raise ValueError("Observed bubble coverage must be between 0 and 0.95.")
    return clean


def load_synthetic_calibration_data(base_dir: Path | None = None) -> pd.DataFrame:
    root = base_dir if base_dir is not None else Path(__file__).resolve().parents[1]
    path = root / "examples" / "synthetic_calibration_data.csv"
    return pd.read_csv(path)


def fit_bubble_coefficients(df: pd.DataFrame):
    clean = validate_calibration_data(df)
    t = clean["time_s"].to_numpy(dtype=float)
    current = clean["current_A"].to_numpy(dtype=float)
    observed = clean["observed_bubble_coverage_fraction"].to_numpy(dtype=float)

    def objective(params: np.ndarray) -> float:
        generation, detach_on, detach_off = params
        simulated = simulate_bubble_coverage(
            t,
            current,
            generation_coeff=generation,
            detach_on_coeff=detach_on,
            detach_off_coeff=detach_off,
        )
        return float(np.mean(np.square(simulated - observed)))

    fit = minimize(
        objective,
        x0=np.array([0.035, 0.08, 0.60]),
        bounds=[(0.0, 1.0), (0.0, 5.0), (0.0, 8.0)],
        method="L-BFGS-B",
    )
    generation, detach_on, detach_off = fit.x
    simulated = simulate_bubble_coverage(
        t,
        current,
        generation_coeff=float(generation),
        detach_on_coeff=float(detach_on),
        detach_off_coeff=float(detach_off),
    )
    residual = simulated - observed
    rmse = float(np.sqrt(np.mean(np.square(residual))))
    mae = float(np.mean(np.abs(residual)))
    fit_df = clean.copy()
    fit_df["simulated_bubble_coverage_fraction"] = simulated
    fit_df["residual_fraction"] = residual
    return {
        "generation_coeff": float(generation),
        "detach_on_coeff": float(detach_on),
        "detach_off_coeff": float(detach_off),
        "rmse": rmse,
        "mae": mae,
        "fit_dataframe": fit_df,
        "success": bool(fit.success),
        "message": str(fit.message),
    }
