"""Simulation engine for charge, bubble coverage, Faraday estimate, and thermal state."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pulsecell.constants import FARADAY_CONSTANT_C_PER_MOL, MAX_BUBBLE_COVERAGE
from pulsecell.models import ScenarioConfig, SimulationKPIs, SimulationResult, ThermalSafetyStatus
from pulsecell.validation import scenario_warnings, validate_scenario
from pulsecell.waveforms import generate_current_waveform


def integrate_quantity(y: np.ndarray, t: np.ndarray) -> float:
    return float(np.trapezoid(y, t))


def faraday_h2_mol(effective_charge_C: float) -> float:
    return float(effective_charge_C / (2.0 * FARADAY_CONSTANT_C_PER_MOL))


def time_average(y: np.ndarray, t: np.ndarray) -> float:
    duration_s = float(t[-1] - t[0])
    if duration_s <= 0:
        return 0.0
    return integrate_quantity(y, t) / duration_s


def time_rms(y: np.ndarray, t: np.ndarray) -> float:
    duration_s = float(t[-1] - t[0])
    if duration_s <= 0:
        return 0.0
    return float(np.sqrt(integrate_quantity(np.square(y), t) / duration_s))


def simulate_bubble_coverage(
    t: np.ndarray,
    current_A: np.ndarray,
    generation_coeff: float,
    detach_on_coeff: float,
    detach_off_coeff: float,
    max_coverage: float = MAX_BUBBLE_COVERAGE,
) -> np.ndarray:
    if len(t) != len(current_A):
        raise ValueError("t and current_A must have the same length.")

    coverage = np.zeros_like(t, dtype=float)
    for i in range(1, len(t)):
        dt_s = t[i] - t[i - 1]
        previous = coverage[i - 1]
        current_now = max(float(current_A[i]), 0.0)
        generation = generation_coeff * current_now * (1.0 - previous / max_coverage)
        detachment_coeff = detach_on_coeff if current_now > 1e-9 else detach_off_coeff
        detachment = detachment_coeff * previous
        coverage[i] = np.clip(previous + (generation - detachment) * dt_s, 0.0, max_coverage)
    return coverage


def simulate_temperature(
    t: np.ndarray,
    power_W: np.ndarray,
    ambient_temperature_C: float,
    thermal_capacitance_J_per_C: float,
    thermal_resistance_C_per_W: float,
    thermal_loss_fraction: float,
) -> np.ndarray:
    temperature = np.zeros_like(t, dtype=float)
    temperature[0] = ambient_temperature_C
    for i in range(1, len(t)):
        dt_s = t[i] - t[i - 1]
        previous = temperature[i - 1]
        p_loss_W = thermal_loss_fraction * max(float(power_W[i]), 0.0)
        cooling_W = (previous - ambient_temperature_C) / thermal_resistance_C_per_W
        dtemp_dt = (p_loss_W - cooling_W) / thermal_capacitance_J_per_C
        temperature[i] = previous + dtemp_dt * dt_s
    return temperature


def classify_thermal_status(
    max_temperature_C: float,
    ambient_temperature_C: float,
    limit_C: float,
) -> ThermalSafetyStatus:
    if max_temperature_C >= limit_C:
        return ThermalSafetyStatus.EXCEEDS_LIMIT
    elevated_threshold = ambient_temperature_C + 0.6 * (limit_C - ambient_temperature_C)
    if max_temperature_C >= elevated_threshold:
        return ThermalSafetyStatus.ELEVATED
    return ThermalSafetyStatus.NORMAL


def run_simulation(
    scenario: ScenarioConfig,
    custom_waveform_df: pd.DataFrame | None = None,
) -> SimulationResult:
    validate_scenario(scenario)
    t, current_A, waveform_warnings = generate_current_waveform(scenario, custom_waveform_df)
    warnings = scenario_warnings(scenario) + waveform_warnings

    coverage = simulate_bubble_coverage(
        t,
        current_A,
        scenario.bubble_generation_coeff,
        scenario.detach_on_coeff,
        scenario.detach_off_coeff,
    )
    active_area_fraction = 1.0 - coverage
    active_area_cm2 = scenario.electrode_area_cm2 * active_area_fraction
    effective_current_A = current_A * active_area_fraction
    h2_rate_mol_s = effective_current_A / (2.0 * FARADAY_CONSTANT_C_PER_MOL)
    power_W = current_A * scenario.cell_voltage_V
    temperature_C = simulate_temperature(
        t,
        power_W,
        scenario.ambient_temperature_C,
        scenario.thermal_capacitance_J_per_C,
        scenario.thermal_resistance_C_per_W,
        scenario.thermal_loss_fraction,
    )

    total_charge_C = integrate_quantity(current_A, t)
    effective_charge_C = integrate_quantity(effective_current_A, t)
    energy_input_J = integrate_quantity(power_W, t)
    energy_input_Wh = energy_input_J / 3600.0
    theoretical_h2_mol = faraday_h2_mol(effective_charge_C)
    max_temperature_C = float(np.max(temperature_C))
    thermal_status = classify_thermal_status(
        max_temperature_C,
        scenario.ambient_temperature_C,
        scenario.max_allowable_temperature_C,
    )

    if thermal_status == ThermalSafetyStatus.EXCEEDS_LIMIT:
        warnings.append("Simulated temperature exceeds the configured limit.")

    df = pd.DataFrame(
        {
            "time_s": t,
            "current_A": current_A,
            "bubble_coverage_fraction": coverage,
            "bubble_coverage_percent": coverage * 100.0,
            "active_area_fraction": active_area_fraction,
            "effective_area_cm2": active_area_cm2,
            "effective_current_A": effective_current_A,
            "h2_rate_mol_s": h2_rate_mol_s,
            "power_W": power_W,
            "temperature_C": temperature_C,
        }
    )

    kpis = SimulationKPIs(
        average_current_A=time_average(current_A, t),
        peak_current_A=float(np.max(current_A)),
        rms_current_A=time_rms(current_A, t),
        total_charge_C=total_charge_C,
        effective_charge_C=effective_charge_C,
        average_power_W=time_average(power_W, t),
        energy_input_J=energy_input_J,
        energy_input_Wh=energy_input_Wh,
        average_bubble_coverage_percent=float(np.mean(coverage) * 100.0),
        max_bubble_coverage_percent=float(np.max(coverage) * 100.0),
        average_active_area_cm2=float(np.mean(active_area_cm2)),
        minimum_active_area_cm2=float(np.min(active_area_cm2)),
        active_area_utilization_factor=float(np.mean(active_area_fraction)),
        theoretical_h2_mol=theoretical_h2_mol,
        theoretical_h2_mol_per_Wh=float(theoretical_h2_mol / energy_input_Wh)
        if energy_input_Wh > 0
        else 0.0,
        final_temperature_C=float(temperature_C[-1]),
        max_temperature_C=max_temperature_C,
        thermal_safety_status=thermal_status,
    )

    return SimulationResult(
        scenario=scenario,
        dataframe=df,
        kpis=kpis,
        warnings=warnings,
    )
