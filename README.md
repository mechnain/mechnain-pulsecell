# Mechnain PulseCell V1.0

**One-line summary:** A software-only engineering suite for comparing pulsed-current electrochemical simulations, bubble coverage, active electrode area, energy input, thermal state, and theoretical Faraday estimates.

## Plain-English Summary

Mechnain PulseCell V1.0 is a software-only engineering suite inspired by the compact hydrogen-system challenges made visible by Alex Burkan's garage-scale suit project. It models pulsed-current effects on bubble coverage, effective active electrode area, charge, energy input, thermal risk, and theoretical Faraday-based hydrogen estimates.

Gas bubbles can cover part of an electrode surface in electrochemical systems. When that happens, less surface area is effectively available in the model. PulseCell is a passion project and engineering software tool that lets a user compare constant DC current against pulsed-current waveforms to see how modeled off-time may reduce bubble coverage.

This is a simulation and decision-support dashboard. It does not generate hydrogen, it does not explain how to build hardware, and it does not claim that water is an energy source. Electricity is the energy input in the model.

This project does not claim that water is an energy source. In electrolysis, water is the reactant/feedstock, and electricity is the energy input.

## Inspiration and Engineering Context

- Alex Burkan's public hydrogen suit work helped make compact hydrogen-system challenges visible to a broader audience.
- The real engineering interest is not the viral phrase "runs on water."
- The real engineering interest is compact electrochemical system control: current waveform, gas-bubble detachment, electrode active area, heat, energy accounting, and safety limits.
- PulseCell turns that public engineering problem into a safe software-only simulation workflow.
- The model is simplified and not a validation of any real hardware.

## Problem Statement

Gas bubbles generated during electrochemical reactions can cover electrode surfaces, reduce effective active area, affect resistance, and complicate energy-system control. Pulsed-current operation may create off-time that allows bubble detachment. PulseCell provides a simplified simulation environment for studying these effects before any physical testing.

Early-stage electrochemical concepts often need a safe way to reason about waveform choice before any physical work is considered. Useful engineering communication needs scenario definition, fair comparison, sensitivity analysis, calibration hooks, transparent equations, exports, and clear limitations.

## Solution Overview

Mechnain PulseCell Engineering Suite turns the original dashboard into a workflow:

1. Define a scenario.
2. Select a waveform.
3. Run a simulation.
4. Compare against a normalized DC reference.
5. Sweep design space.
6. Estimate sensitivity and uncertainty.
7. Fit simplified bubble coefficients to synthetic or uploaded data.
8. Export CSV and JSON.
9. Generate a simulation study report.
10. Document assumptions, exclusions, and safety boundaries.

## Why Pulsed Current Matters in the Model

The model assumes bubbles accumulate when current is on and detach over time. Off-time in a pulsed waveform can be assigned a higher detachment coefficient, which may reduce average bubble coverage compared with a continuously driven DC reference. Lower simulated bubble coverage can increase effective active area.

This is a control and modelling question, not a claim of improved real hardware performance.

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

## What the App Provides

- DC, square pulse, burst pulse, ramped pulse, sinusoidal, and custom CSV waveforms.
- Fair comparison modes: same peak current, same time-averaged current, same total charge, same energy input, and user-defined DC reference.
- Electrical, bubble, area, theoretical Faraday, and simplified thermal KPIs.
- Design-space sweeps across frequency, duty cycle, and current amplitude.
- Bounded grid-search optimization that reports the best simulated candidate found.
- One-at-a-time sensitivity and Monte Carlo uncertainty analysis.
- Simplified coefficient fitting against synthetic or uploaded calibration data.
- Combined simulation data, scenario JSON, Markdown reports, and HTML reports.
- CLI support for repeatable scenario runs.

## Engineering Methodology

The project follows a disciplined simulation workflow:

- **Scope control:** The tool is explicitly software-only and avoids physical build guidance.
- **Scenario definition:** All assumptions are stored in a structured scenario object.
- **Normalization:** Comparisons identify whether peak current, time-averaged current, charge, or energy is being held constant.
- **Conservation-style accounting:** Current, charge, power, and energy are integrated over time.
- **Model transparency:** Bubble and thermal models are simple first-order equations with visible coefficients.
- **Uncertainty:** Sensitivity and Monte Carlo runs show how assumed parameters influence conclusions.
- **Calibration readiness:** A fitting tool demonstrates how coefficients could be estimated from safe synthetic or observed software data.
- **Reporting:** Results are exported with assumptions, limitations, equations, and safety notes attached.

## Visual Design

The app uses a premium dark R&D dashboard style inspired by compact robotics, pulsed-power systems, and cinematic engineering interfaces. It avoids copyrighted references and remains a professional engineering visualization.

## Branding Note

The visual design is inspired by high-performance engineering dashboards. It does not use copyrighted characters, logos, names, fictional technologies, or direct visual references from entertainment properties.

## Screenshots

Add screenshots here after running the Streamlit app:

- Overview dashboard
- Fair comparison tab
- Design-space heatmaps
- Report generator

## Installation

```bash
cd C:\Users\hasna\OneDrive\Desktop\Projects\mechnain-pulsecell
python -m pip install -r requirements.txt
```

## Run the Streamlit App

```bash
streamlit run app.py
```

## Run the CLI

```bash
python pulsecell_cli.py --config examples/balanced_demo.json --output outputs/result.csv
```

The CLI loads a scenario JSON file, runs the software simulation, saves a CSV, and prints KPI summary values.

## Example Scenarios

- `examples/balanced_demo.json`
- `examples/high_bubble_formation.json`
- `examples/strong_detachment.json`
- `examples/same_energy_comparison.json`
- `examples/synthetic_calibration_data.csv`

## Core Equations

Charge:

```text
Q = integral(I dt)
```

Time-averaged current:

```text
I_avg = Q / duration
```

Effective current:

```text
I_effective = I * (1 - bubble_coverage)
```

Theoretical Faraday estimate:

```text
mol_H2 = Q_effective / (2F)
F = 96485.33212 C/mol
```

Effective active area:

```text
A_effective = A_total * (1 - bubble_coverage)
```

Power and energy:

```text
P = I * V
E = integral(P dt)
```

Simplified thermal model:

```text
dT/dt = (P_loss - (T - T_ambient) / R_th) / C_th
P_loss = thermal_loss_fraction * P
```

## What the Model Includes

- Waveform generation and custom CSV waveform interpolation.
- First-order bubble generation and detachment.
- Effective active area and effective current.
- Charge, RMS current, power, and energy accounting.
- Theoretical Faraday estimate.
- Lumped thermal-risk estimate.
- Design-space ranking and constrained grid-search optimization.
- Sensitivity, uncertainty, calibration, and report generation.

## What the Model Excludes

- Real electrochemical kinetics.
- Electrode material behavior.
- Electrolyte chemistry.
- Fluid dynamics or CFD.
- Membrane behavior.
- Pressure effects.
- Gas handling, storage, ignition, combustion, or propulsion design.
- Hardware design guidance.
- Safety certification.
- Validated real-system performance prediction.

## Safety Disclaimer

Simulation only. This project does not generate hydrogen and must not be used as hardware instructions.

This project intentionally avoids physical electrolysis or hydrogen-generation guidance. It must not be used to design, build, operate, or certify real electrochemical or gas-producing hardware.

## Limitations

This is a simplified early-stage software model. Results depend strongly on user-selected coefficients and scenario assumptions. The Faraday estimate is theoretical and uses effective current as a modelling convenience. The thermal model is lumped and not validated for hardware safety.

See `LIMITATIONS.md` for a fuller list.

## File Structure

```text
mechnain-pulsecell/
  app.py
  pulsecell_cli.py
  pulsecell/
    constants.py
    models.py
    waveforms.py
    simulation.py
    comparison.py
    optimizer.py
    sensitivity.py
    calibration.py
    reporting.py
    validation.py
    plotting.py
    utils.py
  examples/
  tests/
  outputs/
  README.md
  TECHNICAL_NOTES.md
  LIMITATIONS.md
  requirements.txt
```

## Testing

```bash
python -m py_compile app.py pulsecell_cli.py pulsecell/*.py
pytest
```

## Exported Data

Combined CSV exports use neutral `test_waveform_*` columns rather than assuming the selected waveform is always a square pulse. Key columns include:

- `time_s`
- `dc_current_A`
- `test_waveform_current_A`
- `dc_bubble_coverage_fraction`
- `test_waveform_bubble_coverage_fraction`
- `dc_active_area_cm2`
- `test_waveform_active_area_cm2`
- `dc_hydrogen_estimate_mol_s`
- `test_waveform_hydrogen_estimate_mol_s`
- `dc_power_W`
- `test_waveform_power_W`

## Future Roadmap

- Add richer model provenance tracking.
- Add saved study bundles.
- Add comparison overlays for multiple scenarios.
- Add validated benchmark datasets if safe and appropriate.
- Add more robust report plots.
- Add model version metadata to every export.
- Add additional waveform families and regression tests.

