import numpy as np
import pandas as pd
import pytest

from pulsecell.models import ScenarioConfig, WaveformType
from pulsecell.waveforms import (
    custom_csv_waveform,
    dc_waveform,
    generate_time_array,
    square_pulse_waveform,
)


def test_dc_waveform_returns_constant_current():
    t = generate_time_array(total_time_s=1.0, dt_s=0.1)
    current = dc_waveform(t, current_amplitude_A=4.2)

    assert np.allclose(current, 4.2)


def test_pulsed_waveform_has_correct_approximate_duty_cycle():
    t = generate_time_array(total_time_s=2.0, dt_s=0.001)
    current = square_pulse_waveform(t, current_amplitude_A=5.0, frequency_hz=10.0, duty_cycle_percent=30.0)

    duty_fraction = np.mean(current > 0)

    assert duty_fraction == pytest.approx(0.30, abs=0.02)


def test_scenario_can_generate_time_array():
    scenario = ScenarioConfig(waveform_type=WaveformType.SQUARE_PULSE)

    t = generate_time_array(scenario.total_time_s, scenario.dt_s)

    assert t[0] == 0
    assert t[-1] == pytest.approx(scenario.total_time_s)


def test_custom_waveform_rejects_duplicate_time_values():
    t = generate_time_array(total_time_s=1.0, dt_s=0.1)
    waveform_df = pd.DataFrame(
        {
            "time_s": [0.0, 0.5, 0.5, 1.0],
            "current_A": [0.0, 1.0, 2.0, 0.0],
        }
    )

    with pytest.raises(ValueError):
        custom_csv_waveform(t, waveform_df)
