"""Scenario validation and engineering warnings."""

from __future__ import annotations

from pulsecell.models import ComparisonMode, ScenarioConfig, WaveformType


def validate_scenario(scenario: ScenarioConfig) -> None:
    """Raise ValueError when a scenario is numerically invalid."""

    if scenario.dt_s <= 0:
        raise ValueError("Time step must be greater than zero.")
    if scenario.total_time_s <= scenario.dt_s:
        raise ValueError("Total simulation time must be greater than time step.")
    if not 0.0 <= scenario.duty_cycle_percent <= 100.0:
        raise ValueError("Duty cycle must be between 0 and 100 percent.")
    if scenario.waveform_type != WaveformType.DC and scenario.frequency_hz <= 0:
        raise ValueError("Frequency must be positive for time-varying waveforms.")
    if scenario.current_amplitude_A < 0:
        raise ValueError("Current amplitude must be non-negative.")
    if scenario.electrode_area_cm2 <= 0:
        raise ValueError("Electrode area must be greater than zero.")
    if scenario.cell_voltage_V <= 0:
        raise ValueError("Cell voltage must be greater than zero.")
    if scenario.thermal_capacitance_J_per_C <= 0:
        raise ValueError("Thermal capacitance must be greater than zero.")
    if scenario.thermal_resistance_C_per_W <= 0:
        raise ValueError("Thermal resistance must be greater than zero.")
    if not 0.0 <= scenario.thermal_loss_fraction <= 1.0:
        raise ValueError("Thermal loss fraction must be between 0 and 1.")
    coeffs = [
        scenario.bubble_generation_coeff,
        scenario.detach_on_coeff,
        scenario.detach_off_coeff,
    ]
    if any(coeff < 0 for coeff in coeffs):
        raise ValueError("Bubble model coefficients must be non-negative.")


def scenario_warnings(scenario: ScenarioConfig) -> list[str]:
    warnings: list[str] = []
    if scenario.waveform_type != WaveformType.DC and scenario.frequency_hz > 0:
        samples_per_period = 1.0 / (scenario.frequency_hz * scenario.dt_s)
        if samples_per_period < 20:
            warnings.append(
                "Time step is coarse for the selected pulse frequency; waveform "
                "and bubble dynamics may be under-sampled."
            )
    if scenario.duty_cycle_percent < 5 or scenario.duty_cycle_percent > 95:
        warnings.append(
            "Duty cycle is near an extreme; comparison results may be sensitive "
            "to small parameter changes."
        )
    if scenario.current_amplitude_A > 20:
        warnings.append(
            "Current amplitude is high for this simplified model. Treat results "
            "as numerical exploration only."
        )
    if scenario.max_allowable_temperature_C <= scenario.ambient_temperature_C:
        warnings.append(
            "Temperature limit is at or below ambient temperature; thermal status "
            "will likely exceed the simulated limit."
        )
    return warnings


def comparison_warning(mode: ComparisonMode) -> str:
    if mode == ComparisonMode.SAME_PEAK_CURRENT:
        return (
            "Same-peak comparisons do not necessarily preserve average current, "
            "total charge, or energy input."
        )
    if mode == ComparisonMode.USER_DEFINED:
        return (
            "User-defined comparisons depend on the selected DC reference and "
            "may not be normalized."
        )
    return (
        "Comparison mode strongly affects interpretation. Do not claim pulsed "
        "operation is better unless the comparison basis is fair."
    )
