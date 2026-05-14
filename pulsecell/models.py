"""Typed configuration and result objects for the PulseCell suite."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class WaveformType(str, Enum):
    DC = "DC"
    SQUARE_PULSE = "Square Pulse"
    BURST_PULSE = "Burst Pulse"
    RAMPED_PULSE = "Ramped Pulse"
    SINUSOIDAL = "Sinusoidal"
    CUSTOM_CSV = "Custom CSV"


class ComparisonMode(str, Enum):
    SAME_PEAK_CURRENT = "Same peak current"
    SAME_AVERAGE_CURRENT = "Same average current"
    SAME_TOTAL_CHARGE = "Same total charge"
    SAME_ENERGY_INPUT = "Same energy input"
    USER_DEFINED = "User-defined"


class ThermalSafetyStatus(str, Enum):
    NORMAL = "Normal"
    ELEVATED = "Elevated simulated temperature"
    EXCEEDS_LIMIT = "Exceeds simulated temperature limit"
    INVALID = "Invalid scenario"


@dataclass
class ScenarioConfig:
    scenario_name: str = "Balanced Demo"
    total_time_s: float = 10.0
    dt_s: float = 0.005
    waveform_type: WaveformType = WaveformType.SQUARE_PULSE
    current_amplitude_A: float = 5.0
    frequency_hz: float = 20.0
    duty_cycle_percent: float = 50.0
    electrode_area_cm2: float = 25.0
    cell_voltage_V: float = 2.0
    bubble_generation_coeff: float = 0.035
    detach_on_coeff: float = 0.080
    detach_off_coeff: float = 0.600
    thermal_capacitance_J_per_C: float = 650.0
    thermal_resistance_C_per_W: float = 3.0
    ambient_temperature_C: float = 22.0
    max_allowable_temperature_C: float = 60.0
    thermal_loss_fraction: float = 0.25
    burst_on_cycles: int = 5
    burst_off_cycles: int = 5
    ramp_fraction: float = 0.25
    user_defined_dc_current_A: float | None = None
    notes: str = (
        "Software-only scenario for pulsed-current bubble coverage modelling."
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScenarioConfig":
        clean = dict(data)
        if "waveform_type" in clean and not isinstance(clean["waveform_type"], WaveformType):
            clean["waveform_type"] = WaveformType(clean["waveform_type"])
        return cls(**clean)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["waveform_type"] = self.waveform_type.value
        return data


@dataclass
class SimulationKPIs:
    average_current_A: float
    peak_current_A: float
    rms_current_A: float
    total_charge_C: float
    effective_charge_C: float
    average_power_W: float
    energy_input_J: float
    energy_input_Wh: float
    average_bubble_coverage_percent: float
    max_bubble_coverage_percent: float
    average_active_area_cm2: float
    minimum_active_area_cm2: float
    active_area_utilization_factor: float
    theoretical_h2_mol: float
    theoretical_h2_mol_per_Wh: float
    final_temperature_C: float
    max_temperature_C: float
    thermal_safety_status: ThermalSafetyStatus

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["thermal_safety_status"] = self.thermal_safety_status.value
        return data


@dataclass
class SimulationResult:
    scenario: ScenarioConfig
    dataframe: Any
    kpis: SimulationKPIs
    warnings: list[str] = field(default_factory=list)


@dataclass
class ComparisonResult:
    mode: ComparisonMode
    dc_scenario: ScenarioConfig
    test_scenario: ScenarioConfig
    dc_result: SimulationResult
    test_result: SimulationResult
    deltas: dict[str, float]
    warnings: list[str]
    normalization_description: str


@dataclass
class OptimizationResult:
    best_scenario: ScenarioConfig
    best_result: SimulationResult
    best_score: float
    ranked_table: Any
    constraint_status: str


@dataclass
class CalibrationResult:
    generation_coeff: float
    detach_on_coeff: float
    detach_off_coeff: float
    rmse: float
    mae: float
    fit_dataframe: Any
    success: bool
    message: str
