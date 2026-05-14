import pytest

from pulsecell.constants import FARADAY_CONSTANT
from pulsecell.models import ScenarioConfig, WaveformType
from pulsecell.simulation import faraday_h2_mol, run_simulation


def test_faraday_calculation_is_dimensionally_correct():
    charge_c = 2.0 * FARADAY_CONSTANT

    mol_h2 = faraday_h2_mol(charge_c)

    assert mol_h2 == pytest.approx(1.0)


def test_average_current_uses_integrated_charge_over_duration():
    scenario = ScenarioConfig(
        total_time_s=1.0,
        dt_s=0.01,
        waveform_type=WaveformType.SQUARE_PULSE,
        current_amplitude_A=10.0,
        frequency_hz=10.0,
        duty_cycle_percent=25.0,
    )

    result = run_simulation(scenario)

    assert result.kpis.average_current_A == pytest.approx(
        result.kpis.total_charge_C / scenario.total_time_s,
        rel=1e-9,
    )
