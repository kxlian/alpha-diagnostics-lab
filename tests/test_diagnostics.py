import numpy as np
import pandas as pd

from alpha_diagnostics.diagnostics import (
    compute_information_decay,
    compute_quantile_returns,
    compute_quantile_spread,
    compute_rank_ic,
    compute_rank_turnover,
)
from alpha_diagnostics.simulate import simulate_alpha_dataset


def test_rank_ic_has_observations():
    dataset = simulate_alpha_dataset(n_days=120, n_assets=30, seed=7)
    rank_ic = compute_rank_ic(dataset.alpha_scores, dataset.returns, horizon=1)

    assert len(rank_ic) > 80
    assert rank_ic.notna().all()
    assert rank_ic.mean() > 0


def test_information_decay_outputs_requested_horizons():
    dataset = simulate_alpha_dataset(n_days=160, n_assets=35, seed=11)
    decay = compute_information_decay(dataset.alpha_scores, dataset.returns, horizons=(1, 5, 10))

    assert decay["horizon"].tolist() == [1, 5, 10]
    assert set(["mean_rank_ic", "positive_ic_share", "observations"]).issubset(decay.columns)
    assert (decay["observations"] > 0).all()


def test_quantile_spread_and_turnover_are_valid():
    dataset = simulate_alpha_dataset(n_days=140, n_assets=40, seed=21)
    quantile_returns = compute_quantile_returns(dataset.alpha_scores, dataset.returns, n_quantiles=5)
    spread = compute_quantile_spread(quantile_returns)
    turnover = compute_rank_turnover(dataset.alpha_scores)

    assert not quantile_returns.empty
    assert "cumulative_spread_return" in spread.columns
    assert turnover.mean() > 0
    assert np.isfinite(spread["cumulative_spread_return"].iloc[-1])
