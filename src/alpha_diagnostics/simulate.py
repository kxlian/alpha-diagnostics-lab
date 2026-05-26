"""Alpha Diagnostics Lab.

Utilities for simulating alpha scores and evaluating signal quality.
"""

from .simulate import simulate_alpha_dataset
from .diagnostics import (
    compute_rank_ic,
    compute_information_decay,
    compute_quantile_returns,
    compute_rank_turnover,
    summarize_diagnostics,
)
