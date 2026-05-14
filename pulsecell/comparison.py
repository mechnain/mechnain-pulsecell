"""Fair comparison modes and combined export helpers."""

from __future__ import annotations

from dataclasses import replace

import pandas as pd

from pulsecell.models import ComparisonMode, ComparisonResult, ScenarioConfig, WaveformType
from pulsecell.simulation import run_simulation
from pulsecell.validation import comparison_warning


MODE_DESCRIPTIONS = {
    ComparisonMode.SAME_PEAK_CURRENT: (
        "DC and the test waveform use the same maximum current. Average current, "
        "charge, and energy can differ."
    ),
    ComparisonMode.SAME_AVERAGE_CURRENT: (
        "The DC reference current is adjusted to match the time-averaged "
        "current of the test waveform, computed as integrated charge divided "
        "by simulated duration."
    ),
    ComparisonMode.SAME_TOTAL_CHARGE: (
        "The DC reference current is adjusted so integrated charge over the "
        "simulation matches the test waveform."
    ),
    ComparisonMode.SAME_ENERGY_INPUT: (
        "The DC reference current is adjusted so total electrical energy input "
        "approximately matches the test waveform."
    ),
    ComparisonMode.USER_DEFINED: (
        "The DC reference current uses the user-defined value. This may or may "
        "not be normalized."
    ),
}


def _duration_s(result_df: pd.DataFrame) -> float:
    return float(result_df["time_s"].iloc[-1] - result_df["time_s"].iloc[0])


def build_dc_reference_scenario(
    scenario: ScenarioConfig,
    mode: ComparisonMode,
    test_result=None,
) -> ScenarioConfig:
    dc_current = scenario.current_amplitude_A

    if mode == ComparisonMode.SAME_PEAK_CURRENT:
        dc_current = scenario.current_amplitude_A
    elif mode == ComparisonMode.SAME_AVERAGE_CURRENT:
        if test_result is None:
            raise ValueError("test_result is required for same-average-current mode.")
        dc_current = test_result.kpis.average_current_A
    elif mode == ComparisonMode.SAME_TOTAL_CHARGE:
        if test_result is None:
            raise ValueError("test_result is required for same-total-charge mode.")
        duration_s = _duration_s(test_result.dataframe)
        dc_current = test_result.kpis.total_charge_C / duration_s if duration_s > 0 else 0.0
    elif mode == ComparisonMode.SAME_ENERGY_INPUT:
        if test_result is None:
            raise ValueError("test_result is required for same-energy-input mode.")
        duration_s = _duration_s(test_result.dataframe)
        denominator = scenario.cell_voltage_V * duration_s
        dc_current = test_result.kpis.energy_input_J / denominator if denominator > 0 else 0.0
    elif mode == ComparisonMode.USER_DEFINED:
        dc_current = (
            scenario.user_defined_dc_current_A
            if scenario.user_defined_dc_current_A is not None
            else scenario.current_amplitude_A
        )

    return replace(
        scenario,
        scenario_name=f"{scenario.scenario_name} DC Reference",
        waveform_type=WaveformType.DC,
        current_amplitude_A=max(float(dc_current), 0.0),
    )


def compare_baseline_to_waveform(
    scenario: ScenarioConfig,
    mode: ComparisonMode = ComparisonMode.SAME_AVERAGE_CURRENT,
    custom_waveform_df: pd.DataFrame | None = None,
) -> ComparisonResult:
    test_result = run_simulation(scenario, custom_waveform_df=custom_waveform_df)
    dc_scenario = build_dc_reference_scenario(scenario, mode, test_result)
    dc_result = run_simulation(dc_scenario)

    deltas = {
        "bubble_coverage_reduction_points": (
            dc_result.kpis.average_bubble_coverage_percent
            - test_result.kpis.average_bubble_coverage_percent
        ),
        "active_area_gain_cm2": (
            test_result.kpis.average_active_area_cm2
            - dc_result.kpis.average_active_area_cm2
        ),
        "energy_difference_Wh": (
            test_result.kpis.energy_input_Wh - dc_result.kpis.energy_input_Wh
        ),
        "charge_difference_C": (
            test_result.kpis.total_charge_C - dc_result.kpis.total_charge_C
        ),
        "theoretical_h2_difference_mol": (
            test_result.kpis.theoretical_h2_mol - dc_result.kpis.theoretical_h2_mol
        ),
    }

    warnings = test_result.warnings + dc_result.warnings + [comparison_warning(mode)]
    if mode in {ComparisonMode.SAME_TOTAL_CHARGE, ComparisonMode.SAME_AVERAGE_CURRENT}:
        denom = max(abs(test_result.kpis.total_charge_C), 1e-9)
        if abs(deltas["charge_difference_C"]) / denom > 0.05:
            warnings.append("Charge differs by more than 5% despite normalization intent.")
    if mode == ComparisonMode.SAME_ENERGY_INPUT:
        denom = max(abs(test_result.kpis.energy_input_Wh), 1e-9)
        if abs(deltas["energy_difference_Wh"]) / denom > 0.05:
            warnings.append("Energy differs by more than 5% despite normalization intent.")

    return ComparisonResult(
        mode=mode,
        dc_scenario=dc_scenario,
        test_scenario=scenario,
        dc_result=dc_result,
        test_result=test_result,
        deltas=deltas,
        warnings=list(dict.fromkeys(warnings)),
        normalization_description=MODE_DESCRIPTIONS[mode],
    )


def build_combined_export_dataframe(
    dc_result,
    test_result,
) -> pd.DataFrame:
    dc = dc_result.dataframe
    test = test_result.dataframe
    return pd.DataFrame(
        {
            "time_s": test["time_s"],
            "dc_current_A": dc["current_A"],
            "test_waveform_current_A": test["current_A"],
            "dc_bubble_coverage_fraction": dc["bubble_coverage_fraction"],
            "test_waveform_bubble_coverage_fraction": test["bubble_coverage_fraction"],
            "dc_active_area_cm2": dc["effective_area_cm2"],
            "test_waveform_active_area_cm2": test["effective_area_cm2"],
            "dc_hydrogen_estimate_mol_s": dc["h2_rate_mol_s"],
            "test_waveform_hydrogen_estimate_mol_s": test["h2_rate_mol_s"],
            "dc_power_W": dc["power_W"],
            "test_waveform_power_W": test["power_W"],
            "dc_temperature_C": dc["temperature_C"],
            "test_waveform_temperature_C": test["temperature_C"],
        }
    )
