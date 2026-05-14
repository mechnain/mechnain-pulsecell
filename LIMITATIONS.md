# Limitations

Mechnain PulseCell V1.0 is a software-only early-stage modelling tool. It is built for visualization, comparison, and engineering communication, not physical design.

## Not Validated

The model has not been validated against real electrochemical hardware. Numeric results should be treated as simulation outputs from user-selected assumptions.

## Simplified Physics

The bubble model is first-order and coefficient-driven. It does not model detailed bubble nucleation, growth, coalescence, detachment mechanics, buoyancy, channel geometry, or multiphase flow.

## No Detailed Electrochemistry

The app does not include:

- Butler-Volmer kinetics
- overpotential models
- electrolyte concentration effects
- electrode material behavior
- surface roughness effects
- membrane transport
- gas crossover
- degradation or fouling

## No Detailed Thermal or Fluid Model

The thermal model is a lumped approximation. It does not represent distributed heating, coolant flow, enclosure effects, phase changes, pressure, or validated temperature limits.

## No Safety Certification

The software is not a safety-certified engineering model. It must not be used to certify, size, operate, or validate real hardware.

## No Hardware Guidance

This project intentionally avoids instructions for:

- real electrolysis construction
- wiring or power electronics
- electrode fabrication
- chemical preparation
- pressure vessels
- gas storage
- ignition, flames, burners, or combustion
- physical reactors or propulsion systems

## No Unusual Energy Claim

The app does not claim unusual energy production. Water is not treated as an energy source. Electricity is the input energy in the simulation.

## Appropriate Use

- Comparing simulated waveform strategies
- Teaching pulsed-current modelling concepts
- Exploring sensitivity to assumed coefficients
- Producing portfolio-grade software and engineering communication

## Inappropriate Use

- Designing real hydrogen hardware
- Predicting real production output
- Safety certification
- Gas storage sizing
- Combustion or propulsion design
- Making investment or operational decisions about physical systems
