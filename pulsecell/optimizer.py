"""Design-space exploration and bounded grid-search optimization."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from pulsecell.models import OptimizationResult, ScenarioConfig, WaveformType
from pulsecell.simulation import run_simulation


RESOLUTION_POINTS = {
    "coarse": 4,
    "medium": 7,
    "fine": 11,
}


def _linspace(bounds: tuple[float, float], count: int) -> np.ndarray:
    low, high = bounds
    if high < low:
        low, high = high, low
    return np.linspace(low, high, count)


def _normalize(series: pd.Series) -> pd.Series:
    span = float(series.max() - series.min())
    if span <= 1e-12:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - series.min()) / span


def rank_candidates(
    df: pd.DataFrame,
    w_bubble: float = 1.0,
    w_area: float = 1.0,
    w_energy: float = 0.4,
    w_temp: float = 0.4,
) -> pd.DataFrame:
    ranked = df.copy()
    bubble = _normalize(ranked["average_bubble_coverage_percent"])
    area = _normalize(ranked["average_active_area_cm2"])
    energy = _normalize(ranked["energy_input_Wh"])
    temp = _normalize(ranked["max_temperature_C"])
    ranked["objective_score"] = (
        w_bubble * bubble
        + w_area * (1.0 - area)
        + w_energy * energy
        + w_temp * temp
    )
    return ranked.sort_values("objective_score", ascending=True).reset_index(drop=True)


def evaluate_candidate(scenario: ScenarioConfig) -> dict[str, float | str]:
    result = run_simulation(scenario)
    return {
        "scenario_name": scenario.scenario_name,
        "frequency_hz": scenario.frequency_hz,
        "duty_cycle_percent": scenario.duty_cycle_percent,
        "current_amplitude_A": scenario.current_amplitude_A,
        "average_bubble_coverage_percent": result.kpis.average_bubble_coverage_percent,
        "average_active_area_cm2": result.kpis.average_active_area_cm2,
        "minimum_active_area_cm2": result.kpis.minimum_active_area_cm2,
        "energy_input_Wh": result.kpis.energy_input_Wh,
        "total_charge_C": result.kpis.total_charge_C,
        "theoretical_h2_mol": result.kpis.theoretical_h2_mol,
        "max_temperature_C": result.kpis.max_temperature_C,
        "thermal_status": result.kpis.thermal_safety_status.value,
    }


def design_space_sweep(
    scenario: ScenarioConfig,
    frequency_bounds: tuple[float, float],
    duty_bounds: tuple[float, float],
    current_bounds: tuple[float, float],
    resolution: str = "coarse",
    w_bubble: float = 1.0,
    w_area: float = 1.0,
    w_energy: float = 0.4,
    w_temp: float = 0.4,
) -> pd.DataFrame:
    count = RESOLUTION_POINTS.get(resolution, RESOLUTION_POINTS["coarse"])
    rows: list[dict[str, float | str]] = []
    for frequency in _linspace(frequency_bounds, count):
        for duty in _linspace(duty_bounds, count):
            for current in _linspace(current_bounds, count):
                candidate = replace(
                    scenario,
                    waveform_type=WaveformType.SQUARE_PULSE,
                    frequency_hz=float(frequency),
                    duty_cycle_percent=float(duty),
                    current_amplitude_A=float(current),
                )
                rows.append(evaluate_candidate(candidate))
    return rank_candidates(
        pd.DataFrame(rows),
        w_bubble=w_bubble,
        w_area=w_area,
        w_energy=w_energy,
        w_temp=w_temp,
    )


def optimize_grid(
    scenario: ScenarioConfig,
    frequency_bounds: tuple[float, float],
    duty_bounds: tuple[float, float],
    current_bounds: tuple[float, float],
    resolution: str = "coarse",
    max_energy_input_Wh: float | None = None,
    max_simulated_temperature_C: float | None = None,
    minimum_active_area_cm2: float | None = None,
) -> OptimizationResult:
    ranked = design_space_sweep(
        scenario,
        frequency_bounds=frequency_bounds,
        duty_bounds=duty_bounds,
        current_bounds=current_bounds,
        resolution=resolution,
    )

    feasible = ranked.copy()
    if max_energy_input_Wh is not None:
        feasible = feasible[feasible["energy_input_Wh"] <= max_energy_input_Wh]
    if max_simulated_temperature_C is not None:
        feasible = feasible[feasible["max_temperature_C"] <= max_simulated_temperature_C]
    if minimum_active_area_cm2 is not None:
        feasible = feasible[feasible["minimum_active_area_cm2"] >= minimum_active_area_cm2]

    if feasible.empty:
        selected = ranked.iloc[0]
        constraint_status = (
            "No candidate met every configured constraint. Best simulated "
            "unconstrained candidate returned; this is not a physical recommendation."
        )
    else:
        selected = feasible.iloc[0]
        constraint_status = (
            "Returned row satisfies the configured simulation constraints; this "
            "is not a physical recommendation."
        )

    best_scenario = replace(
        scenario,
        scenario_name="Best Simulated Candidate Found",
        waveform_type=WaveformType.SQUARE_PULSE,
        frequency_hz=float(selected["frequency_hz"]),
        duty_cycle_percent=float(selected["duty_cycle_percent"]),
        current_amplitude_A=float(selected["current_amplitude_A"]),
    )
    best_result = run_simulation(best_scenario)
    return OptimizationResult(
        best_scenario=best_scenario,
        best_result=best_result,
        best_score=float(selected["objective_score"]),
        ranked_table=ranked,
        constraint_status=constraint_status,
    )
