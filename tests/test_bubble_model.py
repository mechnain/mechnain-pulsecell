import numpy as np

from pulsecell.simulation import simulate_bubble_coverage
from pulsecell.waveforms import generate_time_array


def test_bubble_coverage_remains_between_zero_and_maximum():
    t = generate_time_array(total_time_s=2.0, dt_s=0.01)
    current = np.full_like(t, 20.0)

    coverage = simulate_bubble_coverage(
        t=t,
        current_A=current,
        generation_coeff=0.4,
        detach_on_coeff=0.01,
        detach_off_coeff=0.5,
    )

    assert coverage.min() >= 0.0
    assert coverage.max() <= 0.95
