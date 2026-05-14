from pulsecell.comparison import build_combined_export_dataframe, compare_baseline_to_waveform
from pulsecell.models import ComparisonMode, ScenarioConfig


def test_csv_export_contains_required_columns():
    scenario = ScenarioConfig(total_time_s=1.0, dt_s=0.01)
    comparison = compare_baseline_to_waveform(scenario, ComparisonMode.SAME_PEAK_CURRENT)

    export_df = build_combined_export_dataframe(comparison.dc_result, comparison.test_result)

    assert {
        "time_s",
        "dc_current_A",
        "test_waveform_current_A",
        "dc_bubble_coverage_fraction",
        "test_waveform_bubble_coverage_fraction",
        "dc_active_area_cm2",
        "test_waveform_active_area_cm2",
        "dc_power_W",
        "test_waveform_power_W",
    }.issubset(export_df.columns)

    assert not any(column.startswith("pulsed_") for column in export_df.columns)
