"""Shared constants for the PulseCell simulation suite."""

FARADAY_CONSTANT_C_PER_MOL = 96485.33212
FARADAY_CONSTANT = FARADAY_CONSTANT_C_PER_MOL
MAX_BUBBLE_COVERAGE = 0.95

SAFETY_WARNING = (
    "Simulation only. This project does not generate hydrogen and must not be "
    "used as hardware instructions."
)

SOFTWARE_ONLY_NOTE = (
    "This project intentionally avoids physical electrolysis or "
    "hydrogen-generation guidance."
)
