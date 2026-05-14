import pytest

from pulsecell.comparison import compare_baseline_to_waveform
from pulsecell.models import ComparisonMode, ScenarioConfig, WaveformType


def test_same_average_current_comparison_preserves_average_current():
    scenario = ScenarioConfig(waveform_type=WaveformType.SQUARE_PULSE, current_amplitude_A=8.0, duty_cycle_percent=25.0)

    result = compare_baseline_to_waveform(scenario, ComparisonMode.SAME_AVERAGE_CURRENT)

    assert result.dc_result.kpis.average_current_A == pytest.approx(result.test_result.kpis.average_current_A, abs=0.05)


def test_same_charge_comparison_preserves_integrated_charge():
    scenario = ScenarioConfig(waveform_type=WaveformType.SQUARE_PULSE, current_amplitude_A=8.0, duty_cycle_percent=35.0)

    result = compare_baseline_to_waveform(scenario, ComparisonMode.SAME_TOTAL_CHARGE)

    assert result.dc_result.kpis.total_charge_C == pytest.approx(result.test_result.kpis.total_charge_C, rel=0.01)


def test_same_energy_comparison_preserves_integrated_energy():
    scenario = ScenarioConfig(
        waveform_type=WaveformType.RAMPED_PULSE,
        current_amplitude_A=8.0,
        duty_cycle_percent=45.0,
        cell_voltage_V=2.1,
    )

    result = compare_baseline_to_waveform(scenario, ComparisonMode.SAME_ENERGY_INPUT)

    assert result.dc_result.kpis.energy_input_Wh == pytest.approx(
        result.test_result.kpis.energy_input_Wh,
        rel=0.01,
    )
