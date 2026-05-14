from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from pulsecell.calibration import fit_bubble_coefficients, load_synthetic_calibration_data
from pulsecell.comparison import (
    build_combined_export_dataframe,
    compare_baseline_to_waveform,
)
from pulsecell.constants import SAFETY_WARNING, SOFTWARE_ONLY_NOTE
from pulsecell.models import ComparisonMode, ScenarioConfig, WaveformType
from pulsecell.optimizer import design_space_sweep, optimize_grid
from pulsecell.plotting import (
    calibration_fit_plot,
    comparison_line_plot,
    heatmap_plot,
    histogram_plot,
    residual_plot,
)
from pulsecell.reporting import generate_html_report, generate_markdown_report
from pulsecell.sensitivity import monte_carlo_uncertainty, one_at_a_time_sensitivity
from pulsecell.utils import dataframe_to_csv_bytes, load_example_scenarios, scenario_to_json


st.set_page_config(
    page_title="Mechnain PulseCell V1.0",
    page_icon="PC",
    layout="wide",
)


def inject_theme() -> None:
    st.markdown(
        """
<style>
:root {
  --bg: #050505;
  --panel: #111111;
  --panel-2: #151515;
  --border: #2a2a2a;
  --text: #f5f5f5;
  --muted: #b8b8b8;
  --copper: #c47a3a;
  --gold: #f2b84b;
  --red: #b33a3a;
  --amber-muted: #8f5f24;
}

.stApp {
  background:
    radial-gradient(circle at top left, rgba(196, 122, 58, 0.10), transparent 28rem),
    linear-gradient(180deg, #080808 0%, #050505 100%);
  color: var(--text);
}

section[data-testid="stSidebar"] {
  background: #0b0b0b;
  border-right: 1px solid var(--border);
}

.block-container {
  padding-top: 1.4rem;
  padding-bottom: 2.5rem;
  max-width: 1450px;
}

h1, h2, h3 {
  letter-spacing: 0;
}

.pc-hero {
  border: 1px solid var(--border);
  border-left: 5px solid var(--copper);
  background: linear-gradient(135deg, rgba(21,21,21,0.98), rgba(8,8,8,0.98));
  box-shadow: 0 20px 55px rgba(0,0,0,0.36);
  padding: 1.35rem 1.5rem;
  margin-bottom: 0.85rem;
}

.pc-hero-kicker {
  color: var(--gold);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.pc-hero-title {
  color: var(--text);
  font-size: 2.05rem;
  font-weight: 760;
  margin-top: 0.25rem;
  margin-bottom: 0.25rem;
}

.pc-hero-subtitle {
  color: var(--muted);
  font-size: 1.02rem;
  margin-bottom: 0.9rem;
}

.pc-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.pc-tag {
  border: 1px solid #3a2a1d;
  background: #140f0a;
  color: #f4d79a;
  padding: 0.28rem 0.55rem;
  font-size: 0.78rem;
  font-weight: 650;
}

.pc-safety {
  border: 1px solid var(--red);
  border-left: 5px solid var(--red);
  background: rgba(179, 58, 58, 0.12);
  color: #ffe7e7;
  padding: 0.9rem 1rem;
  margin-bottom: 0.85rem;
  font-weight: 650;
}

.pc-status-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
  margin: 0.85rem 0 1.2rem;
}

.pc-status-card,
.pc-metric-card,
.pc-panel {
  border: 1px solid var(--border);
  background: rgba(17, 17, 17, 0.96);
  box-shadow: 0 14px 34px rgba(0,0,0,0.28);
}

.pc-status-card {
  padding: 0.85rem;
  border-top: 3px solid var(--copper);
}

.pc-status-label,
.pc-metric-label {
  color: var(--muted);
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.055em;
  margin-bottom: 0.28rem;
}

.pc-status-value {
  color: var(--text);
  font-size: 0.95rem;
  font-weight: 720;
}

.pc-metric-card {
  padding: 1rem;
  border-top: 3px solid var(--gold);
  min-height: 124px;
}

.pc-metric-value {
  color: var(--text);
  font-size: 1.55rem;
  font-weight: 780;
  margin: 0.25rem 0;
}

.pc-metric-detail {
  color: var(--muted);
  font-size: 0.82rem;
}

.pc-panel {
  padding: 1rem;
  margin: 0.65rem 0;
}

.pc-section-title {
  color: var(--gold);
  font-size: 0.84rem;
  font-weight: 760;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin: 0.5rem 0 0.4rem;
}

div[data-testid="stAlert"] {
  border-radius: 0;
}

button, .stDownloadButton button {
  border-radius: 2px !important;
}

@media (max-width: 900px) {
  .pc-status-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
<div class="pc-hero">
  <div class="pc-hero-kicker">Mechnain PulseCell Engineering Suite</div>
  <div class="pc-hero-title">Mechnain PulseCell V1.0</div>
  <div class="pc-hero-subtitle">Pulsed-current electrochemical system modelling, optimization, and reporting suite.</div>
  <div class="pc-tags">
    <span class="pc-tag">Digital Twin</span>
    <span class="pc-tag">Pulsed Current</span>
    <span class="pc-tag">Bubble Coverage Model</span>
    <span class="pc-tag">Engineering Reports</span>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="pc-safety">{SAFETY_WARNING}<br>{SOFTWARE_ONLY_NOTE}</div>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="pc-status-grid">
  <div class="pc-status-card"><div class="pc-status-label">Simulation Mode</div><div class="pc-status-value">Active</div></div>
  <div class="pc-status-card"><div class="pc-status-label">Hardware Output</div><div class="pc-status-value">Disabled</div></div>
  <div class="pc-status-card"><div class="pc-status-label">Hydrogen Generation</div><div class="pc-status-value">Not Performed</div></div>
  <div class="pc-status-card"><div class="pc-status-label">Safety State</div><div class="pc-status-value">Software-Only Model</div></div>
</div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, detail: str) -> str:
    return f"""
<div class="pc-metric-card">
  <div class="pc-metric-label">{label}</div>
  <div class="pc-metric-value">{value}</div>
  <div class="pc-metric-detail">{detail}</div>
</div>
"""


def scenario_from_sidebar() -> tuple[ScenarioConfig, ComparisonMode, pd.DataFrame | None]:
    examples = load_example_scenarios()
    example_names = list(examples) if examples else ["Balanced Demo"]

    st.sidebar.header("Scenario Manager")
    selected_example = st.sidebar.selectbox("Example scenario", example_names)
    base = examples.get(selected_example, ScenarioConfig())

    uploaded_scenario = st.sidebar.file_uploader(
        "Load scenario JSON",
        type=["json"],
        help="Optional. Basic usage works with built-in examples and sidebar controls.",
    )
    if uploaded_scenario is not None:
        try:
            loaded = ScenarioConfig.from_dict(json.load(uploaded_scenario))
            base = loaded
            st.sidebar.success("Scenario JSON loaded.")
        except Exception as exc:
            st.sidebar.error(f"Could not load scenario JSON: {exc}")

    comparison_mode = ComparisonMode(
        st.sidebar.selectbox(
            "Comparison Mode",
            [mode.value for mode in ComparisonMode],
            index=list(ComparisonMode).index(ComparisonMode.SAME_AVERAGE_CURRENT),
            help="Select how the DC reference is normalized against the test waveform.",
        )
    )

    st.sidebar.caption(
        "Comparison basis matters. Same-average, same-charge, or same-energy modes are usually more defensible than same-peak comparisons."
    )

    waveform_type = WaveformType(
        st.sidebar.selectbox(
            "Waveform type",
            [waveform.value for waveform in WaveformType],
            index=[waveform.value for waveform in WaveformType].index(base.waveform_type.value),
        )
    )

    st.sidebar.header("Simulation")
    scenario_name = st.sidebar.text_input("Scenario name", value=base.scenario_name)
    total_time_s = st.sidebar.slider("Total simulation time [s]", 1.0, 120.0, float(base.total_time_s), 1.0)
    dt_s = st.sidebar.select_slider(
        "Time step [s]",
        options=[0.001, 0.002, 0.005, 0.01, 0.02, 0.05],
        value=float(base.dt_s) if base.dt_s in [0.001, 0.002, 0.005, 0.01, 0.02, 0.05] else 0.005,
    )

    st.sidebar.header("Electrical")
    current_amplitude_A = st.sidebar.slider("Current amplitude [A]", 0.0, 40.0, float(base.current_amplitude_A), 0.1)
    cell_voltage_V = st.sidebar.slider("Cell voltage [V]", 0.5, 10.0, float(base.cell_voltage_V), 0.1)

    st.sidebar.header("Waveform")
    frequency_hz = st.sidebar.slider("Frequency [Hz]", 0.5, 500.0, float(base.frequency_hz), 0.5)
    duty_cycle_percent = st.sidebar.slider("Duty cycle [%]", 0.0, 100.0, float(base.duty_cycle_percent), 1.0)
    burst_on_cycles = st.sidebar.slider("Burst on cycles", 1, 20, int(base.burst_on_cycles), 1)
    burst_off_cycles = st.sidebar.slider("Burst off cycles", 1, 20, int(base.burst_off_cycles), 1)
    ramp_fraction = st.sidebar.slider("Ramp fraction", 0.0, 0.9, float(base.ramp_fraction), 0.05)

    st.sidebar.header("Bubble Model")
    electrode_area_cm2 = st.sidebar.slider("Electrode area [cm2]", 1.0, 500.0, float(base.electrode_area_cm2), 1.0)
    bubble_generation_coeff = st.sidebar.slider(
        "Bubble generation coefficient",
        0.0,
        1.0,
        float(base.bubble_generation_coeff),
        0.001,
    )
    detach_on_coeff = st.sidebar.slider("On-time detachment coefficient", 0.0, 5.0, float(base.detach_on_coeff), 0.001)
    detach_off_coeff = st.sidebar.slider("Off-time detachment coefficient", 0.0, 8.0, float(base.detach_off_coeff), 0.001)

    st.sidebar.header("Thermal Assumptions")
    thermal_loss_fraction = st.sidebar.slider("Thermal loss fraction", 0.0, 1.0, float(base.thermal_loss_fraction), 0.01)
    thermal_capacitance_J_per_C = st.sidebar.slider(
        "Thermal capacitance [J/C]",
        50.0,
        5000.0,
        float(base.thermal_capacitance_J_per_C),
        50.0,
    )
    thermal_resistance_C_per_W = st.sidebar.slider(
        "Thermal resistance [C/W]",
        0.1,
        20.0,
        float(base.thermal_resistance_C_per_W),
        0.1,
    )
    ambient_temperature_C = st.sidebar.slider("Ambient temperature [C]", 0.0, 60.0, float(base.ambient_temperature_C), 0.5)
    max_allowable_temperature_C = st.sidebar.slider(
        "Simulated temperature limit [C]",
        20.0,
        120.0,
        float(base.max_allowable_temperature_C),
        1.0,
    )
    user_defined_dc_current_A = st.sidebar.number_input(
        "User-defined DC current [A]",
        min_value=0.0,
        max_value=100.0,
        value=float(base.user_defined_dc_current_A or base.current_amplitude_A),
        step=0.1,
        help="Used only when Comparison Mode is User-defined.",
    )
    notes = st.sidebar.text_area("Scenario notes", value=base.notes, height=90)

    custom_waveform_df = None
    if waveform_type == WaveformType.CUSTOM_CSV:
        st.sidebar.header("Custom Waveform")
        uploaded_waveform = st.sidebar.file_uploader(
            "Custom waveform CSV",
            type=["csv"],
            help="Required columns: time_s, current_A. Data is used only for simulation.",
        )
        if uploaded_waveform is not None:
            custom_waveform_df = pd.read_csv(uploaded_waveform)

    scenario = ScenarioConfig(
        scenario_name=scenario_name,
        total_time_s=total_time_s,
        dt_s=dt_s,
        waveform_type=waveform_type,
        current_amplitude_A=current_amplitude_A,
        frequency_hz=frequency_hz,
        duty_cycle_percent=duty_cycle_percent,
        electrode_area_cm2=electrode_area_cm2,
        cell_voltage_V=cell_voltage_V,
        bubble_generation_coeff=bubble_generation_coeff,
        detach_on_coeff=detach_on_coeff,
        detach_off_coeff=detach_off_coeff,
        thermal_capacitance_J_per_C=thermal_capacitance_J_per_C,
        thermal_resistance_C_per_W=thermal_resistance_C_per_W,
        ambient_temperature_C=ambient_temperature_C,
        max_allowable_temperature_C=max_allowable_temperature_C,
        thermal_loss_fraction=thermal_loss_fraction,
        burst_on_cycles=burst_on_cycles,
        burst_off_cycles=burst_off_cycles,
        ramp_fraction=ramp_fraction,
        user_defined_dc_current_A=user_defined_dc_current_A,
        notes=notes,
    )
    return scenario, comparison_mode, custom_waveform_df


@st.cache_data(show_spinner=False)
def cached_sweep(
    scenario_dict: dict,
    frequency_bounds: tuple[float, float],
    duty_bounds: tuple[float, float],
    current_bounds: tuple[float, float],
    resolution: str,
    weights: tuple[float, float, float, float],
) -> pd.DataFrame:
    scenario = ScenarioConfig.from_dict(scenario_dict)
    return design_space_sweep(
        scenario,
        frequency_bounds,
        duty_bounds,
        current_bounds,
        resolution=resolution,
        w_bubble=weights[0],
        w_area=weights[1],
        w_energy=weights[2],
        w_temp=weights[3],
    )


@st.cache_data(show_spinner=False)
def cached_monte_carlo(
    scenario_dict: dict,
    sample_count: int,
    seed: int,
    fractional_span: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    return monte_carlo_uncertainty(
        ScenarioConfig.from_dict(scenario_dict),
        sample_count=sample_count,
        seed=seed,
        fractional_span=fractional_span,
    )


def render_kpi_table(result) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"KPI": key, "Value": str(value)}
            for key, value in result.kpis.to_dict().items()
        ]
    )


def show_warnings(warnings: list[str]) -> None:
    for warning in warnings:
        st.warning(warning)


def main() -> None:
    inject_theme()
    render_hero()

    scenario, comparison_mode, custom_waveform_df = scenario_from_sidebar()

    try:
        comparison = compare_baseline_to_waveform(
            scenario,
            mode=comparison_mode,
            custom_waveform_df=custom_waveform_df,
        )
    except Exception as exc:
        st.error(f"Scenario could not be simulated: {exc}")
        st.stop()

    combined_export_df = build_combined_export_dataframe(
        comparison.dc_result,
        comparison.test_result,
    )
    cards = [
        metric_card(
            "Average Bubble Coverage Reduction",
            f"{comparison.deltas['bubble_coverage_reduction_points']:.2f} pts",
            "DC reference minus test waveform average coverage.",
        ),
        metric_card(
            "Average Active Area Gain",
            f"{comparison.deltas['active_area_gain_cm2']:.2f} cm2",
            "Test waveform minus DC reference average active area.",
        ),
        metric_card(
            "DC Reference Energy Input",
            f"{comparison.dc_result.kpis.energy_input_Wh:.5f} Wh",
            "Electrical input in the normalized DC reference.",
        ),
        metric_card(
            "Test Waveform Energy Input",
            f"{comparison.test_result.kpis.energy_input_Wh:.5f} Wh",
            "Electrical input in the selected waveform.",
        ),
    ]

    tabs = st.tabs(
        [
            "Overview",
            "Scenario",
            "Compare",
            "Waveforms",
            "Design Space",
            "Optimizer",
            "Sensitivity",
            "Calibration",
            "Report",
            "Assumptions",
            "Raw Data",
        ]
    )

    with tabs[0]:
        st.markdown('<div class="pc-section-title">Inspiration and Engineering Context</div>', unsafe_allow_html=True)
        st.markdown(
            """
Mechnain PulseCell V1.0 is a software-only engineering suite inspired by the
compact hydrogen-system challenges made visible by Alex Burkan's garage-scale
suit project. It models pulsed-current effects on bubble coverage, effective
active electrode area, charge, energy input, thermal risk, and theoretical
Faraday-based hydrogen estimates.

The real engineering interest is compact electrochemical system control:
current waveform, gas-bubble detachment, electrode active area, heat, energy
accounting, and safety limits. This model is simplified and does not validate
any real hardware.
            """
        )
        st.warning(
            "This project does not claim that water is an energy source. In electrolysis, water is the reactant/feedstock, and electricity is the energy input."
        )
        st.markdown('<div class="pc-section-title">Problem Statement</div>', unsafe_allow_html=True)
        st.markdown(
            """
Gas bubbles generated during electrochemical reactions can cover electrode
surfaces, reduce effective active area, affect resistance, and complicate
energy-system control. Pulsed-current operation may create off-time that allows
bubble detachment. PulseCell provides a simplified simulation environment for
studying these effects before any physical testing.
            """
        )
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(
                '<div class="pc-panel"><b>Problem</b><br>Bubble coverage can block modeled active surface area and change apparent performance.</div>',
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                '<div class="pc-panel"><b>Control Lever</b><br>Pulsed current creates off-time in the simulation, allowing stronger modeled bubble detachment.</div>',
                unsafe_allow_html=True,
            )
        with col_c:
            st.markdown(
                '<div class="pc-panel"><b>Boundary</b><br>This is a software-only decision-support tool, not a hardware design or validation package.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="pc-section-title">Current Comparison Basis</div>', unsafe_allow_html=True)
        st.info(comparison.normalization_description)
        show_warnings(comparison.warnings[:3])

        metric_cols = st.columns(4)
        for column, card in zip(metric_cols, cards):
            column.markdown(card, unsafe_allow_html=True)

    with tabs[1]:
        st.markdown('<div class="pc-section-title">Scenario Definition</div>', unsafe_allow_html=True)
        st.write("Use the sidebar to select an example, edit assumptions, and export the resulting scenario.")
        col_json, col_notes = st.columns([1.2, 1])
        with col_json:
            st.json(scenario.to_dict())
            st.download_button(
                "Download scenario JSON",
                data=scenario_to_json(scenario),
                file_name="pulsecell_scenario.json",
                mime="application/json",
                key="scenario_tab_download_scenario_json",
            )
        with col_notes:
            st.markdown("**Scenario notes**")
            st.write(scenario.notes)
            st.markdown("**Comparison mode**")
            st.info(comparison.normalization_description)
            st.markdown("**Validation and interpretation warnings**")
            show_warnings(comparison.warnings)

    with tabs[2]:
        st.markdown('<div class="pc-section-title">Fair Comparison Summary</div>', unsafe_allow_html=True)
        st.warning(
            "Comparison mode strongly affects interpretation. Results should be read against the selected normalization basis."
        )
        metric_cols = st.columns(4)
        for column, card in zip(metric_cols, cards):
            column.markdown(card, unsafe_allow_html=True)

        left, right = st.columns(2)
        with left:
            st.subheader("DC Reference KPIs")
            st.dataframe(render_kpi_table(comparison.dc_result), width="stretch", hide_index=True)
        with right:
            st.subheader("Test Waveform KPIs")
            st.dataframe(render_kpi_table(comparison.test_result), width="stretch", hide_index=True)

        st.subheader("Comparison Deltas")
        st.dataframe(
            pd.DataFrame(
                [{"Metric": key, "Value": value} for key, value in comparison.deltas.items()]
            ),
            width="stretch",
            hide_index=True,
        )

    with tabs[3]:
        st.markdown('<div class="pc-section-title">Waveform and State Plots</div>', unsafe_allow_html=True)
        plot_specs = [
            ("current_A", "Current Waveform", "Current [A]"),
            ("bubble_coverage_percent", "Bubble Coverage", "Coverage [%]"),
            ("effective_area_cm2", "Effective Active Electrode Area", "Area [cm2]"),
            ("h2_rate_mol_s", "Theoretical Faraday Rate", "mol/s"),
            ("power_W", "Power Input", "Power [W]"),
            ("temperature_C", "Simulated Lumped Temperature", "Temperature [C]"),
        ]
        for y_col, title, ylabel in plot_specs:
            st.pyplot(
                comparison_line_plot(
                    comparison.dc_result.dataframe,
                    comparison.test_result.dataframe,
                    y_col,
                    title,
                    ylabel,
                ),
                clear_figure=True,
            )

    with tabs[4]:
        st.markdown('<div class="pc-section-title">Design Space Explorer</div>', unsafe_allow_html=True)
        st.caption("Simulation-ranked candidates only. Not hardware recommendations.")
        col1, col2, col3 = st.columns(3)
        with col1:
            f_min = st.number_input("Frequency min [Hz]", 0.5, 500.0, 5.0, 1.0)
            f_max = st.number_input("Frequency max [Hz]", 0.5, 500.0, 80.0, 1.0)
        with col2:
            d_min = st.number_input("Duty min [%]", 1.0, 99.0, 20.0, 1.0)
            d_max = st.number_input("Duty max [%]", 1.0, 99.0, 80.0, 1.0)
        with col3:
            i_min = st.number_input("Current min [A]", 0.0, 40.0, 2.0, 0.5)
            i_max = st.number_input("Current max [A]", 0.0, 40.0, max(6.0, scenario.current_amplitude_A), 0.5)

        col_res, col_w1, col_w2, col_w3, col_w4 = st.columns(5)
        resolution = col_res.selectbox("Sweep resolution", ["coarse", "medium", "fine"], index=0)
        w_bubble = col_w1.number_input("w bubble", 0.0, 5.0, 1.0, 0.1)
        w_area = col_w2.number_input("w area", 0.0, 5.0, 1.0, 0.1)
        w_energy = col_w3.number_input("w energy", 0.0, 5.0, 0.4, 0.1)
        w_temp = col_w4.number_input("w temp", 0.0, 5.0, 0.4, 0.1)

        if resolution == "fine":
            st.warning("Fine sweeps run more simulations and may take longer.")

        if st.button("Run design-space sweep", key="run_design_space_sweep"):
            with st.spinner("Evaluating simulated design space..."):
                st.session_state["design_space_df"] = cached_sweep(
                    scenario.to_dict(),
                    (f_min, f_max),
                    (d_min, d_max),
                    (i_min, i_max),
                    resolution,
                    (w_bubble, w_area, w_energy, w_temp),
                )

        design_space_df = st.session_state.get("design_space_df")
        if design_space_df is not None:
            st.subheader("Top 10 Simulation-Ranked Candidates")
            st.dataframe(design_space_df.head(10), width="stretch", hide_index=True)
            h1, h2, h3 = st.columns(3)
            h1.pyplot(heatmap_plot(design_space_df, "average_bubble_coverage_percent", "Average Bubble Coverage", "Coverage [%]"), clear_figure=True)
            h2.pyplot(heatmap_plot(design_space_df, "average_active_area_cm2", "Average Active Area", "Area [cm2]"), clear_figure=True)
            h3.pyplot(heatmap_plot(design_space_df, "energy_input_Wh", "Energy Input", "Wh"), clear_figure=True)
            st.download_button(
                "Download design-space CSV",
                data=dataframe_to_csv_bytes(design_space_df),
                file_name="pulsecell_design_space.csv",
                mime="text/csv",
                key="download_design_space_csv",
            )

    with tabs[5]:
        st.markdown('<div class="pc-section-title">Constrained Search</div>', unsafe_allow_html=True)
        st.caption("The result is the best simulated candidate found by bounded grid search, not a hardware recommendation.")
        o1, o2, o3 = st.columns(3)
        with o1:
            of_min = st.number_input("Optimizer frequency min [Hz]", 0.5, 500.0, 5.0, 1.0)
            of_max = st.number_input("Optimizer frequency max [Hz]", 0.5, 500.0, 100.0, 1.0)
        with o2:
            od_min = st.number_input("Optimizer duty min [%]", 1.0, 99.0, 15.0, 1.0)
            od_max = st.number_input("Optimizer duty max [%]", 1.0, 99.0, 75.0, 1.0)
        with o3:
            oi_min = st.number_input("Optimizer current min [A]", 0.0, 40.0, 1.0, 0.5)
            oi_max = st.number_input("Optimizer current max [A]", 0.0, 40.0, max(8.0, scenario.current_amplitude_A), 0.5)

        c1, c2, c3, c4 = st.columns(4)
        opt_resolution = c1.selectbox("Optimizer resolution", ["coarse", "medium", "fine"], index=0)
        max_energy = c2.number_input("Max energy [Wh]", 0.0, 100.0, 0.0, 0.01, help="0 disables this constraint.")
        max_temp = c3.number_input("Max simulated temp [C]", 0.0, 150.0, 0.0, 1.0, help="0 uses the scenario limit.")
        min_area = c4.number_input("Minimum active area [cm2]", 0.0, 500.0, 0.0, 1.0, help="0 disables this constraint.")

        if st.button("Find best simulated candidate", key="run_optimizer_grid_search"):
            with st.spinner("Searching bounded simulation grid..."):
                st.session_state["optimizer_result"] = optimize_grid(
                    scenario,
                    frequency_bounds=(of_min, of_max),
                    duty_bounds=(od_min, od_max),
                    current_bounds=(oi_min, oi_max),
                    resolution=opt_resolution,
                    max_energy_input_Wh=max_energy if max_energy > 0 else None,
                    max_simulated_temperature_C=max_temp if max_temp > 0 else scenario.max_allowable_temperature_C,
                    minimum_active_area_cm2=min_area if min_area > 0 else None,
                )

        optimizer_result = st.session_state.get("optimizer_result")
        if optimizer_result is not None:
            st.info(optimizer_result.constraint_status)
            st.write(f"Objective score: **{optimizer_result.best_score:.4f}**")
            st.json(optimizer_result.best_scenario.to_dict())
            optimized_comparison = compare_baseline_to_waveform(
                optimizer_result.best_scenario,
                mode=comparison_mode,
            )
            st.pyplot(
                comparison_line_plot(
                    comparison.test_result.dataframe,
                    optimized_comparison.test_result.dataframe,
                    "bubble_coverage_percent",
                    "Baseline vs Best Simulated Candidate Bubble Coverage",
                    "Coverage [%]",
                ),
                clear_figure=True,
            )
            st.dataframe(optimizer_result.ranked_table.head(10), width="stretch", hide_index=True)

    with tabs[6]:
        st.markdown('<div class="pc-section-title">Sensitivity and Uncertainty</div>', unsafe_allow_html=True)
        st.caption("Parameter uncertainty changes the simulated result. These ranges are assumptions, not measured bounds.")
        span = st.slider("One-at-a-time fractional span", 0.05, 0.75, 0.25, 0.05)
        oat_df = one_at_a_time_sensitivity(scenario, fractional_span=span)
        st.subheader("One-at-a-Time Sensitivity")
        st.dataframe(oat_df, width="stretch", hide_index=True)

        m1, m2, m3 = st.columns(3)
        sample_count = m1.selectbox("Monte Carlo samples", [50, 100, 250, 500], index=1)
        seed = m2.number_input("Random seed", 1, 99999, 7, 1)
        mc_span = m3.slider("Monte Carlo fractional span", 0.05, 0.75, 0.20, 0.05)
        if st.button("Run Monte Carlo uncertainty", key="run_monte_carlo_uncertainty"):
            with st.spinner("Sampling uncertainty space..."):
                st.session_state["mc_samples"], st.session_state["mc_ci"] = cached_monte_carlo(
                    scenario.to_dict(),
                    sample_count,
                    seed,
                    mc_span,
                )

        mc_samples = st.session_state.get("mc_samples")
        mc_ci = st.session_state.get("mc_ci")
        if mc_samples is not None and mc_ci is not None:
            st.subheader("Confidence Interval Table")
            st.dataframe(mc_ci, width="stretch", hide_index=True)
            p1, p2, p3 = st.columns(3)
            p1.pyplot(histogram_plot(mc_samples, "average_bubble_coverage_percent", "Average Bubble Coverage Distribution", "Coverage [%]"), clear_figure=True)
            p2.pyplot(histogram_plot(mc_samples, "max_temperature_C", "Max Temperature Distribution", "Temperature [C]"), clear_figure=True)
            p3.pyplot(histogram_plot(mc_samples, "theoretical_h2_mol", "Theoretical Faraday Estimate Distribution", "mol"), clear_figure=True)

    with tabs[7]:
        st.markdown('<div class="pc-section-title">Calibration Tool</div>', unsafe_allow_html=True)
        st.caption("Fits simplified bubble coefficients to observed or synthetic data. This does not validate real equipment.")
        calibration_source = st.radio("Calibration data source", ["Synthetic demo data", "Upload CSV"], horizontal=True)
        calibration_df = None
        if calibration_source == "Synthetic demo data":
            calibration_df = load_synthetic_calibration_data()
        else:
            calibration_upload = st.file_uploader(
                "Calibration CSV",
                type=["csv"],
                help="Required columns: time_s, current_A, observed_bubble_coverage_fraction.",
            )
            if calibration_upload is not None:
                calibration_df = pd.read_csv(calibration_upload)

        if calibration_df is not None:
            st.dataframe(calibration_df.head(50), width="stretch", hide_index=True)
            if st.button("Fit bubble coefficients", key="fit_bubble_coefficients"):
                try:
                    st.session_state["calibration_result"] = fit_bubble_coefficients(calibration_df)
                except Exception as exc:
                    st.error(f"Calibration failed: {exc}")

        calibration_result = st.session_state.get("calibration_result")
        if calibration_result is not None:
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Generation coeff", f"{calibration_result['generation_coeff']:.4f}")
            c2.metric("On detach coeff", f"{calibration_result['detach_on_coeff']:.4f}")
            c3.metric("Off detach coeff", f"{calibration_result['detach_off_coeff']:.4f}")
            c4.metric("RMSE", f"{calibration_result['rmse']:.4f}")
            c5.metric("MAE", f"{calibration_result['mae']:.4f}")
            fit_df = calibration_result["fit_dataframe"]
            st.pyplot(calibration_fit_plot(fit_df), clear_figure=True)
            st.pyplot(residual_plot(fit_df), clear_figure=True)

    with tabs[8]:
        st.markdown('<div class="pc-section-title">Simulation Study Report</div>', unsafe_allow_html=True)
        design_space_df = st.session_state.get("design_space_df")
        optimizer_result = st.session_state.get("optimizer_result")
        markdown_report = generate_markdown_report(
            scenario,
            comparison.test_result,
            comparison=comparison,
            design_space=design_space_df,
            optimizer=optimizer_result,
            sensitivity=st.session_state.get("mc_ci"),
        )
        html_report = generate_html_report(markdown_report)
        st.download_button(
            "Download Markdown report",
            data=markdown_report,
            file_name="pulsecell_simulation_study_report.md",
            mime="text/markdown",
            key="download_markdown_report",
        )
        st.download_button(
            "Download HTML report",
            data=html_report,
            file_name="pulsecell_simulation_study_report.html",
            mime="text/html",
            key="download_html_report",
        )
        st.download_button(
            "Download combined simulation CSV",
            data=dataframe_to_csv_bytes(combined_export_df),
            file_name="pulsecell_combined_simulation.csv",
            mime="text/csv",
            key="download_combined_simulation_csv",
        )
        st.download_button(
            "Download scenario JSON",
            data=scenario_to_json(scenario),
            file_name="pulsecell_scenario.json",
            mime="application/json",
            key="report_tab_download_scenario_json",
        )
        with st.expander("Preview Markdown report"):
            st.markdown(markdown_report)

    with tabs[9]:
        st.markdown('<div class="pc-section-title">Engineering Assumptions Library</div>', unsafe_allow_html=True)
        st.markdown(
            """
**Model confidence rating:** conceptual / early-stage simulation.

**Included**

- DC, square pulse, burst pulse, ramped pulse, sinusoidal, and uploaded CSV current waveforms
- Charge accounting, power, energy, and RMS current
- First-order bubble coverage and detachment dynamics
- Effective active area and effective current
- Theoretical Faraday estimate using effective charge
- Lumped first-order thermal-risk estimate
- Scenario export, CSV export, sensitivity, calibration, and report generation

**Excluded**

- Detailed electrochemical kinetics, electrode material behavior, electrolyte chemistry, membranes, pressure, gas handling, fluid dynamics, and validated safety systems
- Any real hardware construction, wiring, chemical preparation, pressure vessel design, gas storage, ignition, or combustion guidance

**Appropriate use cases**

- Comparing simulated waveform strategies
- Teaching pulsed-current control effects
- Exploring parameter sensitivity and uncertainty
- Generating early-stage software hypotheses and portfolio-grade engineering communication

**Inappropriate use cases**

- Designing real hydrogen hardware
- Predicting real reactor output
- Safety certification
- Claiming unusual energy production
- Sizing gas storage, combustion systems, or propulsion systems
            """
        )

    with tabs[10]:
        st.markdown('<div class="pc-section-title">Raw Simulation Data</div>', unsafe_allow_html=True)
        st.subheader("Combined Export")
        st.dataframe(combined_export_df, width="stretch", hide_index=True)
        st.subheader("DC Reference")
        st.dataframe(comparison.dc_result.dataframe, width="stretch", hide_index=True)
        st.subheader("Test Waveform")
        st.dataframe(comparison.test_result.dataframe, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
