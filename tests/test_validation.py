import pytest

from pulsecell.models import ScenarioConfig
from pulsecell.validation import validate_scenario


def test_invalid_duty_cycle_raises_validation_error():
    scenario = ScenarioConfig(duty_cycle_percent=120.0)

    with pytest.raises(ValueError):
        validate_scenario(scenario)
