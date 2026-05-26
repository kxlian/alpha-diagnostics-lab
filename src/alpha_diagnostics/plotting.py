from __future__ import annotations

import numpy as np
import pandas as pd


def _validate_aligned_frames(alpha_scores: pd.DataFrame, returns: pd.DataFrame) -> None:
    if not alpha_scores.index.equals(returns.index):
        raise ValueError("alpha_scores and returns must share the same index.")
    if not alpha_scores.columns.equals(returns.columns):
        raise ValueError("alpha_scores and returns must share the same columns.")


def forward_returns(returns: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    """Compute point-in-time forward returns for each asset.

    A horizon of 1 compares signal_t with return_{t+1}. A horizon of 5
    compares signal_t with return_{t+5}. This makes the decay diagnostic
    easier to interpret because each horizon measures signal relevance at a
    specific future point rather than a cumulative multi-day window.
    """
    if horizon < 1:
        raise ValueError("horizon must be at least 1.")
    return returns.shift(-horizon)


def compute_rank_ic(
    alpha_scores: pd.DataFrame,
    returns: pd.DataFrame,
    horizon: int = 1,
) -> pd.Series:
    """Compute daily cross-sectional Spearman Rank IC.

    The alpha score at day t is compared with forward returns after day t.
    """
    _validate_aligned_frames(alpha_scores, returns)
    fwd = forward_returns(returns, horizon=horizon)
    rank_ic = []
    dates = []
    for date in alpha_scores.index[:-horizon]:
        signal = alpha_scores.loc[date]
        future_ret = fwd.loc[date]
        valid = signal.notna() & future_ret.notna()
        if valid.sum() < 5:
            continue
        rank_ic.append(signal[valid].rank().corr(future_ret[valid].rank()))
        dates.append(date)
    return pd.Series(rank_ic, index=pd.Index(dates, name="date"), name=f"rank_ic_{horizon}d")


def compute_information_decay(
    alpha_scores: pd.DataFrame,
    returns: pd.DataFrame,
    horizons: tuple[int, ...] = (1, 2, 5, 10, 20),
) -> pd.DataFrame:
    """Calculate Rank IC summary statistics across forward horizons."""
    rows = []
    for horizon in horizons:
        ic = compute_rank_ic(alpha_scores, returns, horizon=horizon)
        rows.append(
            {
                "horizon": horizon,
                "mean_rank_ic": ic.mean(),
                "median_rank_ic": ic.median(),
                "ic_volatility": ic.std(ddof=1),
                "ic_ir": ic.mean() / ic.std(ddof=1) if ic.std(ddof=1) != 0 else np.nan,
                "positive_ic_share": (ic > 0).mean(),
                "observations": ic.count(),
            }
        )
    return pd.DataFrame(rows)


def compute_quantile_returns(
    alpha_scores: pd.DataFrame,
    returns: pd.DataFrame,
    n_quantiles: int = 5,
    horizon: int = 1,
) -> pd.DataFrame:
    """Sort assets into signal quantiles and compute next-period returns."""
    _validate_aligned_frames(alpha_scores, returns)
    if n_quantiles < 2:
        raise ValueError("n_quantiles must be at least 2.")
    fwd = forward_returns(returns, horizon=horizon)
    records = []
    for date in alpha_scores.index[:-horizon]:
        signal = alpha_scores.loc[date]
        future_ret = fwd.loc[date]
        valid = signal.notna() & future_ret.notna()
        if valid.sum() < n_quantiles * 2:
            continue
        ranks = signal[valid].rank(method="first")
        buckets = pd.qcut(ranks, q=n_quantiles, labels=False) + 1
        for quantile in range(1, n_quantiles + 1):
            mask = buckets == quantile
            records.append(
                {
                    "date": date,
                    "quantile": quantile,
                    "return": future_ret[valid][mask].mean(),
                }
            )
    return pd.DataFrame(records)


def compute_quantile_spread(quantile_returns: pd.DataFrame) -> pd.DataFrame:
    """Compute high-minus-low quantile spread returns."""
    if quantile_returns.empty:
        raise ValueError("quantile_returns is empty.")
    pivot = quantile_returns.pivot(index="date", columns="quantile", values="return")
    low = pivot.columns.min()
    high = pivot.columns.max()
    spread = pivot[high] - pivot[low]
    return pd.DataFrame(
        {
            "spread_return": spread,
            "cumulative_spread_return": (1.0 + spread.fillna(0.0)).cumprod() - 1.0,
        }
    )


def compute_rank_turnover(alpha_scores: pd.DataFrame) -> pd.Series:
    """Estimate daily signal turnover based on rank changes."""
    ranks = alpha_scores.rank(axis=1, pct=True)
    turnover = ranks.diff().abs().mean(axis=1).dropna()
    turnover.name = "rank_turnover"
    return turnover


def summarize_diagnostics(
    rank_ic: pd.Series,
    information_decay: pd.DataFrame,
    quantile_spread: pd.DataFrame,
    turnover: pd.Series,
) -> pd.DataFrame:
    """Create a compact table of headline diagnostics."""
    spread = quantile_spread["spread_return"]
    rows = [
        ("Mean Rank IC", rank_ic.mean()),
        ("Rank IC Volatility", rank_ic.std(ddof=1)),
        ("Rank IC IR", rank_ic.mean() / rank_ic.std(ddof=1)),
        ("Positive IC Share", (rank_ic > 0).mean()),
        ("1D Mean IC", information_decay.loc[information_decay["horizon"] == 1, "mean_rank_ic"].iloc[0]),
        ("5D Mean IC", information_decay.loc[information_decay["horizon"] == 5, "mean_rank_ic"].iloc[0]),
        ("20D Mean IC", information_decay.loc[information_decay["horizon"] == 20, "mean_rank_ic"].iloc[0]),
        ("Mean Long-Short Spread", spread.mean()),
        ("Spread Volatility", spread.std(ddof=1)),
        ("Cumulative Long-Short Spread", quantile_spread["cumulative_spread_return"].iloc[-1]),
        ("Average Rank Turnover", turnover.mean()),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])
