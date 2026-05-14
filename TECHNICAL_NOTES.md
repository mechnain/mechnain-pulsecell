# Technical Notes

## Model Scope

Mechnain PulseCell V1.0 is a simplified software model for pulsed-current electrochemical system visualization. It is not a validated physical model and does not provide hardware guidance.

## Waveforms

Supported waveform families:

- DC
- Square pulse
- Burst pulse
- Ramped pulse
- Sinusoidal current
- Custom CSV waveform with `time_s` and `current_A`

Custom waveform data is interpolated onto the simulation time grid. Negative time values are rejected. Negative current values are preserved for electrical accounting, while bubble generation uses the non-negative current portion.

## Comparison Modes

Same peak current:

- DC and test waveform use the same maximum current.
- Average current, charge, and energy may differ.

Same average current:

- The DC reference current is set to the test waveform time-averaged current.
- Time-averaged current is computed from integrated charge divided by simulated duration, not from a raw sample mean.

Same total charge:

- The DC reference current is set so integrated charge matches the test waveform.

Same energy input:

- The DC reference current is set so integrated energy approximately matches the test waveform.

User-defined:

- The DC reference current is set by the user.
- This mode may not be normalized.

## Bubble Model

Coverage is constrained between `0` and `0.95`.

```text
dcoverage/dt = generation - detachment
generation = k_generation * max(I, 0) * (1 - coverage / coverage_max)
detachment = k_detach * coverage
```

The model uses `detach_on_coeff` while current is flowing and `detach_off_coeff` while current is off. This lets the simulation represent stronger off-time bubble detachment without modelling detailed fluid dynamics.

## Active Area and Effective Current

```text
active_area_fraction = 1 - bubble_coverage
A_effective = A_total * active_area_fraction
I_effective = I * active_area_fraction
```

## Charge, Power, and Energy

```text
Q = integral(I dt)
I_avg = Q / duration
P = I * V
E = integral(P dt)
```

## Theoretical Faraday Estimate

```text
mol_H2 = Q_effective / (2F)
F = 96485.33212 C/mol
```

This is a theoretical accounting estimate. It is not a prediction of real equipment output.

## Thermal Model

The app uses a first-order lumped thermal approximation:

```text
dT/dt = (P_loss - (T - T_ambient) / R_th) / C_th
P_loss = thermal_loss_fraction * P
```

Thermal states:

- Normal
- Elevated simulated temperature
- Exceeds simulated temperature limit
- Invalid scenario

This model is not validated for safety decisions.

## Optimizer Objective

Design-space ranking uses normalized KPI values:

```text
score =
  w_bubble * normalized_average_bubble_coverage
  + w_area * (1 - normalized_average_active_area)
  + w_energy * normalized_energy_input
  + w_temp * normalized_max_temperature
```

Lower score is better. The app reports the "best simulated candidate found" from the evaluated grid rather than an absolute optimum or a hardware recommendation.

## Sensitivity Method

One-at-a-time sensitivity varies each uncertain parameter around its baseline value and measures KPI changes.

Monte Carlo uncertainty randomly samples uncertain parameters within a user-selected fractional range and reports summary percentiles.

## Calibration Method

Calibration fits the simplified bubble coefficients:

- bubble generation coefficient
- on-time detachment coefficient
- off-time detachment coefficient

The fitting target is observed bubble coverage over time. The built-in dataset is synthetic and intended only to demonstrate the workflow.

## Units Table

| Variable | Meaning | Unit |
|---|---|---|
| `t` | Time | s |
| `I` | Current | A |
| `V` | Cell voltage assumption | V |
| `Q` | Charge | C |
| `P` | Power | W |
| `E` | Energy | J or Wh |
| `A_total` | Total electrode area assumption | cm2 |
| `A_effective` | Modeled active area | cm2 |
| `coverage` | Bubble coverage fraction | dimensionless |
| `T` | Simulated lumped temperature | C |
| `C_th` | Thermal capacitance assumption | J/C |
| `R_th` | Thermal resistance assumption | C/W |
| `F` | Faraday constant | C/mol |
