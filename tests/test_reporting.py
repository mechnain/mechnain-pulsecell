from pulsecell.models import ScenarioConfig
from pulsecell.reporting import generate_markdown_report
from pulsecell.simulation import run_simulation


def test_report_generator_returns_non_empty_markdown():
    scenario = ScenarioConfig(total_time_s=1.0, dt_s=0.01)
    result = run_simulation(scenario)

    report = generate_markdown_report(scenario, result)

    assert "Simulation Study Report" in report
    assert "Inspiration and Engineering Context" in report
    assert "Alex Burkan" in report
    assert "does not validate Alex Burkan's system" in report
    assert "## Units" in report
    assert "Simulation only" in report
    assert len(report) > 500
