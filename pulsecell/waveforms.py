"""Current waveform generation and custom waveform handling."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pulsecell.models import ScenarioConfig, WaveformType
from pulsecell.validation import validate_scenario


def generate_time_array(total_time_s: float, dt_s: float) -> np.ndarray:
    if total_time_s <= 0:
        raise ValueError("total_time_s must be positive.")
    if dt_s <= 0:
        raise ValueError("dt_s must be positive.")
    if dt_s >= total_time_s:
        raise ValueError("dt_s must be smaller than total_time_s.")
    t = np.arange(0.0, total_time_s, dt_s)
    if len(t) == 0 or not np.isclose(t[-1], total_time_s):
        t = np.append(t, total_time_s)
    return t


def dc_waveform(t: np.ndarray, current_amplitude_A: float) -> np.ndarray:
    return np.full_like(t, current_amplitude_A, dtype=float)


def square_pulse_waveform(
    t: np.ndarray,
    current_amplitude_A: float,
    frequency_hz: float,
    duty_cycle_percent: float,
) -> np.ndarray:
    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive.")
    duty = np.clip(duty_cycle_percent / 100.0, 0.0, 1.0)
    period_s = 1.0 / frequency_hz
    phase = np.mod(t, period_s)
    return np.where(phase < duty * period_s, current_amplitude_A, 0.0)


def burst_pulse_waveform(
    t: np.ndarray,
    current_amplitude_A: float,
    frequency_hz: float,
    duty_cycle_percent: float,
    burst_on_cycles: int,
    burst_off_cycles: int,
) -> np.ndarray:
    base = square_pulse_waveform(
        t, current_amplitude_A, frequency_hz, duty_cycle_percent
    )
    cycle_period_s = 1.0 / frequency_hz
    burst_period_s = max(1, burst_on_cycles + burst_off_cycles) * cycle_period_s
    burst_phase = np.mod(t, burst_period_s)
    burst_on_time = max(1, burst_on_cycles) * cycle_period_s
    return np.where(burst_phase < burst_on_time, base, 0.0)


def ramped_pulse_waveform(
    t: np.ndarray,
    current_amplitude_A: float,
    frequency_hz: float,
    duty_cycle_percent: float,
    ramp_fraction: float,
) -> np.ndarray:
    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive.")
    duty = np.clip(duty_cycle_percent / 100.0, 0.0, 1.0)
    ramp_fraction = np.clip(ramp_fraction, 0.0, 0.9)
    period_s = 1.0 / frequency_hz
    on_time_s = duty * period_s
    phase = np.mod(t, period_s)
    current = np.zeros_like(t, dtype=float)
    if on_time_s <= 0:
        return current

    ramp_time_s = max(on_time_s * ramp_fraction, 1e-12)
    on_mask = phase < on_time_s
    ramp_mask = on_mask & (phase < ramp_time_s)
    plateau_mask = on_mask & ~ramp_mask
    current[ramp_mask] = current_amplitude_A * phase[ramp_mask] / ramp_time_s
    current[plateau_mask] = current_amplitude_A
    return current


def sinusoidal_current_waveform(
    t: np.ndarray,
    current_amplitude_A: float,
    frequency_hz: float,
    duty_cycle_percent: float | None = None,
) -> np.ndarray:
    del duty_cycle_percent
    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive.")
    return 0.5 * current_amplitude_A * (
        1.0 + np.sin(2.0 * np.pi * frequency_hz * t)
    )


def validate_custom_waveform_dataframe(df: pd.DataFrame) -> list[str]:
    required = {"time_s", "current_A"}
    if not required.issubset(df.columns):
        raise ValueError("Custom waveform CSV must include time_s and current_A columns.")
    if df["time_s"].isna().any() or df["current_A"].isna().any():
        raise ValueError("Custom waveform contains missing time or current values.")
    if (df["time_s"] < 0).any():
        raise ValueError("Custom waveform time values cannot be negative.")
    if df["time_s"].duplicated().any():
        raise ValueError("Custom waveform time values must be unique.")
    if not df["time_s"].is_monotonic_increasing:
        df.sort_values("time_s", inplace=True)
    warnings: list[str] = []
    if (df["current_A"] < 0).any():
        warnings.append(
            "Custom waveform includes negative current values. The simulator will "
            "keep them for electrical accounting but bubble generation uses the "
            "non-negative portion."
        )
    return warnings


def custom_csv_waveform(t: np.ndarray, waveform_df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    df = waveform_df[["time_s", "current_A"]].copy()
    warnings = validate_custom_waveform_dataframe(df)
    if t[-1] > float(df["time_s"].iloc[-1]):
        warnings.append(
            "Simulation time extends beyond the uploaded waveform duration; "
            "the final uploaded current value is held by interpolation."
        )
    current = np.interp(t, df["time_s"].to_numpy(), df["current_A"].to_numpy())
    return current.astype(float), warnings


def generate_current_waveform(
    scenario: ScenarioConfig,
    custom_waveform_df: pd.DataFrame | None = None,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    validate_scenario(scenario)
    t = generate_time_array(scenario.total_time_s, scenario.dt_s)
    warnings: list[str] = []

    if scenario.waveform_type == WaveformType.DC:
        current = dc_waveform(t, scenario.current_amplitude_A)
    elif scenario.waveform_type == WaveformType.SQUARE_PULSE:
        current = square_pulse_waveform(
            t,
            scenario.current_amplitude_A,
            scenario.frequency_hz,
            scenario.duty_cycle_percent,
        )
    elif scenario.waveform_type == WaveformType.BURST_PULSE:
        current = burst_pulse_waveform(
            t,
            scenario.current_amplitude_A,
            scenario.frequency_hz,
            scenario.duty_cycle_percent,
            scenario.burst_on_cycles,
            scenario.burst_off_cycles,
        )
    elif scenario.waveform_type == WaveformType.RAMPED_PULSE:
        current = ramped_pulse_waveform(
            t,
            scenario.current_amplitude_A,
            scenario.frequency_hz,
            scenario.duty_cycle_percent,
            scenario.ramp_fraction,
        )
    elif scenario.waveform_type == WaveformType.SINUSOIDAL:
        current = sinusoidal_current_waveform(
            t,
            scenario.current_amplitude_A,
            scenario.frequency_hz,
            scenario.duty_cycle_percent,
        )
    elif scenario.waveform_type == WaveformType.CUSTOM_CSV:
        if custom_waveform_df is None:
            raise ValueError("Custom CSV waveform selected but no CSV data was provided.")
        current, warnings = custom_csv_waveform(t, custom_waveform_df)
    else:
        raise ValueError(f"Unsupported waveform type: {scenario.waveform_type}")

    return t, current, warnings
