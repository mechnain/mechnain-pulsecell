"""Sensitivity and uncertainty analysis utilities."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from pulsecell.models import ScenarioConfig
from pulsecell.simulation import run_simulation


PARAMETER_LABELS = {
    "bubble_generation_coeff": "Bubble generation coefficient",
    "detach_on_coeff": "On-time detachment coefficient",
    "detach_off_coeff": "Off-time detachment coefficient",
    "thermal_resistance_C_per_W": "Thermal resistance",
    "thermal_capacitance_J_per_C": "Thermal capacitance",
    "cell_voltage_V": "Cell voltage",
}


def one_at_a_time_sensitivity(
    scenario: ScenarioConfig,
    fractional_span: float = 0.25,
) -> pd.DataFrame:
    rows = []
    for field_name, label in PARAMETER_LABELS.items():
        base_value = float(getattr(scenario, field_name))
        for multiplier in (1.0 - fractional_span, 1.0, 1.0 + fractional_span):
            value = max(base_value * multiplier, 1e-9)
            candidate = replace(scenario, **{field_name: value})
            result = run_simulation(candidate)
            rows.append(
                {
                    "parameter": label,
                    "field": field_name,
                    "value": value,
                    "relative_to_base": multiplier,
                    "average_bubble_coverage_percent": result.kpis.average_bubble_coverage_percent,
                    "average_active_area_cm2": result.kpis.average_active_area_cm2,
                    "energy_input_Wh": result.kpis.energy_input_Wh,
                    "max_temperature_C": result.kpis.max_temperature_C,
                    "theoretical_h2_mol": result.kpis.theoretical_h2_mol,
                }
            )
    return pd.DataFrame(rows)


def monte_carlo_uncertainty(
    scenario: ScenarioConfig,
    sample_count: int = 100,
    seed: int = 7,
    fractional_span: float = 0.20,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    rows = []
    fields = list(PARAMETER_LABELS)
    for index in range(sample_count):
        updates = {}
        for field_name in fields:
            base_value = float(getattr(scenario, field_name))
            multiplier = rng.uniform(1.0 - fractional_span, 1.0 + fractional_span)
            updates[field_name] = max(base_value * multiplier, 1e-9)
        candidate = replace(scenario, scenario_name=f"Monte Carlo Sample {index + 1}", **updates)
        result = run_simulation(candidate)
        row = {
            "sample": index + 1,
            **updates,
            "average_bubble_coverage_percent": result.kpis.average_bubble_coverage_percent,
            "average_active_area_cm2": result.kpis.average_active_area_cm2,
            "energy_input_Wh": result.kpis.energy_input_Wh,
            "max_temperature_C": result.kpis.max_temperature_C,
            "theoretical_h2_mol": result.kpis.theoretical_h2_mol,
        }
        rows.append(row)

    samples = pd.DataFrame(rows)
    ci_rows = []
    for metric in [
        "average_bubble_coverage_percent",
        "average_active_area_cm2",
        "energy_input_Wh",
        "max_temperature_C",
        "theoretical_h2_mol",
    ]:
        ci_rows.append(
            {
                "metric": metric,
                "mean": float(samples[metric].mean()),
                "p05": float(samples[metric].quantile(0.05)),
                "p50": float(samples[metric].quantile(0.50)),
                "p95": float(samples[metric].quantile(0.95)),
            }
        )
    return samples, pd.DataFrame(ci_rows)
