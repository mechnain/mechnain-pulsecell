"""Generate downloadable simulation study reports."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

from pulsecell.constants import SAFETY_WARNING, SOFTWARE_ONLY_NOTE
from pulsecell.models import ScenarioConfig, SimulationResult


def _markdown_table(mapping: dict[str, Any]) -> str:
    rows = ["| Metric | Value |", "|---|---|"]
    for key, value in mapping.items():
        rows.append(f"| {key} | {_format_value(value)} |")
    return "\n".join(rows)


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _dataframe_markdown_table(df) -> str:
    if df is None or df.empty:
        return "No rows available."
    columns = list(df.columns)
    rows = ["| " + " | ".join(columns) + " |"]
    rows.append("| " + " | ".join("---" for _ in columns) + " |")
    for _, row in df.iterrows():
        values = [str(row[column]) for column in columns]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def generate_markdown_report(
    scenario: ScenarioConfig,
    result: SimulationResult,
    comparison=None,
    design_space=None,
    optimizer=None,
    sensitivity=None,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    kpis = result.kpis.to_dict()
    scenario_items = scenario.to_dict()

    report = f"""# Simulation Study Report

Generated: {now}

## Project

Mechnain PulseCell Engineering Suite

{SAFETY_WARNING}

{SOFTWARE_ONLY_NOTE}

## Summary

Mechnain PulseCell V1.0 is a software-only engineering suite inspired by the
compact hydrogen-system challenges made visible by Alex Burkan's garage-scale
suit project. It models pulsed-current effects on bubble coverage, effective
active electrode area, charge, energy input, thermal risk, and theoretical
Faraday-based hydrogen estimates.

This report documents a software-only simulation study for pulsed-current
electrochemical system modelling. It compares waveform behavior, bubble
coverage, effective active area, electrical input, a theoretical Faraday
estimate, and a simplified thermal state. It is not a certification report,
does not validate any real hardware, and must not be interpreted as hardware
guidance.

This project does not claim that water is an energy source. In electrolysis,
water is the reactant/feedstock, and electricity is the energy input.

## Inspiration and Engineering Context

- Alex Burkan's public hydrogen suit work helped make compact hydrogen-system challenges visible to a broader audience.
- The real engineering interest is not the viral phrase "runs on water."
- The real engineering interest is compact electrochemical system control: current waveform, gas-bubble detachment, electrode active area, heat, energy accounting, and safety limits.
- PulseCell turns that public engineering problem into a safe software-only simulation workflow.
- The model is simplified and not a validation of any real hardware.

## Problem Statement

Gas bubbles generated during electrochemical reactions can cover electrode
surfaces, reduce effective active area, affect resistance, and complicate
energy-system control. Pulsed-current operation may create off-time that allows
bubble detachment. PulseCell provides a simplified simulation environment for
studying these effects before any physical testing.

## What This Tool Helps Study

- DC vs pulsed-current comparison
- bubble coverage
- effective active electrode area
- charge and energy input
- theoretical Faraday-based output
- simplified thermal risk
- design-space exploration
- sensitivity and uncertainty
- calibration against synthetic or observed data
- simulation report generation

## What This Tool Does Not Do

- does not generate hydrogen
- does not provide hardware instructions
- does not design reactors
- does not certify safety
- does not validate Alex Burkan's system
- does not claim free energy
- does not treat water as fuel

## Scenario Settings

{_markdown_table(scenario_items)}

## Key Performance Indicators

{_markdown_table(kpis)}

## Units

| Quantity | Unit |
|---|---|
| Current | A |
| Charge | C |
| Voltage | V |
| Power | W |
| Energy | J and Wh |
| Active area | cm2 |
| Bubble coverage | percent or fraction |
| Temperature | C |
| Theoretical Faraday estimate | mol |

## Equations

- Charge: `Q = integral(I dt)`
- Effective current: `I_effective = I * (1 - bubble_coverage)`
- Faraday estimate: `mol_H2 = Q_effective / (2F)`
- Effective area: `A_effective = A_total * (1 - bubble_coverage)`
- Power: `P = I * V`
- Energy: `E = integral(P dt)`
- Thermal model: `dT/dt = (P_loss - (T - T_ambient) / R_th) / C_th`

## Assumptions

- Bubble generation and detachment are represented by adjustable first-order coefficients.
- Off-time detachment can be higher than on-time detachment.
- Faraday output is a theoretical accounting estimate using effective current.
- The thermal model is a lumped approximation and is not validated for hardware use.
- The model excludes detailed electrochemical kinetics, materials, pressure, membranes, fluid dynamics, and safety systems.

## Comparison Mode

"""
    if comparison is not None:
        report += (
            f"{comparison.mode.value}: {comparison.normalization_description}\n\n"
            f"{_markdown_table(comparison.deltas)}\n\n"
        )
    else:
        report += "No comparison result was attached to this report.\n\n"

    if design_space is not None:
        report += "## Design-Space Summary\n\n"
        report += "Simulation-ranked candidates only. Not hardware recommendations.\n\n"
        report += _dataframe_markdown_table(design_space.head(10))
        report += "\n\n"

    if optimizer is not None:
        report += "## Best Simulated Candidate Found\n\n"
        report += f"Constraint status: {optimizer.constraint_status}\n\n"
        report += _markdown_table(optimizer.best_scenario.to_dict())
        report += "\n\n"

    if sensitivity is not None:
        report += "## Sensitivity Summary\n\n"
        report += "Sensitivity results quantify model response to assumed parameter uncertainty.\n\n"

    report += f"""## Limitations

- This is a simplified software model, not a validated electrochemical design.
- Results depend strongly on user-selected coefficients.
- The Faraday estimate is theoretical and does not predict real equipment output.
- The software intentionally avoids physical electrolysis or hydrogen-generation guidance.
- Do not use this report for safety certification, gas storage sizing, combustion design, or hardware construction.

## Recommended Next Software Improvements

- Add validated experimental data only from safe, qualified sources.
- Improve uncertainty bounds and scenario provenance tracking.
- Add richer report plots and versioned model settings.
- Add regression tests for additional waveform families.

## Safety Disclaimer

{SAFETY_WARNING}

{SOFTWARE_ONLY_NOTE}
"""
    return report


def generate_html_report(markdown_report: str) -> str:
    escaped = escape(markdown_report)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Simulation Study Report</title>
  <style>
    body {{
      background: #080808;
      color: #f5f5f5;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
      padding: 32px;
    }}
    pre {{
      white-space: pre-wrap;
      background: #111111;
      border: 1px solid #2a2a2a;
      border-left: 4px solid #c47a3a;
      padding: 24px;
    }}
  </style>
</head>
<body>
<pre>{escaped}</pre>
</body>
</html>"""
