from __future__ import annotations

import argparse
from pathlib import Path

from pulsecell.simulation import run_simulation
from pulsecell.utils import load_scenario_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a PulseCell software-only simulation from a scenario JSON file."
    )
    parser.add_argument("--config", required=True, help="Path to scenario JSON.")
    parser.add_argument("--output", required=True, help="Path for output CSV.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    scenario = load_scenario_json(args.config)
    result = run_simulation(scenario)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.dataframe.to_csv(output_path, index=False)

    print("Mechnain PulseCell Engineering Suite")
    print("Software-only simulation complete.")
    print(f"Scenario: {scenario.scenario_name}")
    print(f"Rows written: {len(result.dataframe)}")
    print(f"Output CSV: {output_path}")
    print(f"Average current [A]: {result.kpis.average_current_A:.4f}")
    print(f"Average bubble coverage [%]: {result.kpis.average_bubble_coverage_percent:.4f}")
    print(f"Average active area [cm2]: {result.kpis.average_active_area_cm2:.4f}")
    print(f"Energy input [Wh]: {result.kpis.energy_input_Wh:.6f}")
    print(f"Max simulated temperature [C]: {result.kpis.max_temperature_C:.3f}")
    print(f"Thermal status: {result.kpis.thermal_safety_status.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
