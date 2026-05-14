from pulsecell.models import ScenarioConfig
from pulsecell.optimizer import optimize_grid


def test_optimizer_returns_result_within_bounds():
    scenario = ScenarioConfig(total_time_s=1.0, dt_s=0.01)

    result = optimize_grid(
        scenario,
        frequency_bounds=(5.0, 15.0),
        duty_bounds=(20.0, 60.0),
        current_bounds=(2.0, 6.0),
        resolution="coarse",
    )

    assert 5.0 <= result.best_scenario.frequency_hz <= 15.0
    assert 20.0 <= result.best_scenario.duty_cycle_percent <= 60.0
    assert 2.0 <= result.best_scenario.current_amplitude_A <= 6.0
    assert result.best_score >= 0.0
