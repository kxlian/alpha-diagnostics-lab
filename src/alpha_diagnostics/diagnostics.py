from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SimulatedAlphaDataset:
    """Container for synthetic alpha research data."""

    returns: pd.DataFrame
    alpha_scores: pd.DataFrame
    sectors: pd.Series


def _zscore_cross_section(frame: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectionally z-score each row."""
    mean = frame.mean(axis=1)
    std = frame.std(axis=1).replace(0.0, np.nan)
    return frame.sub(mean, axis=0).div(std, axis=0).fillna(0.0)


def simulate_alpha_dataset(
    n_days: int = 504,
    n_assets: int = 80,
    n_sectors: int = 8,
    seed: int = 42,
    signal_strength: float = 0.00055,
) -> SimulatedAlphaDataset:
    """Simulate a cross-sectional alpha dataset.

    The simulation creates a signal with modest predictive information for next-day
    asset returns. The returns include a market component, sector component,
    idiosyncratic noise, and an alpha-linked component based on the lagged signal.

    Parameters
    ----------
    n_days:
        Number of trading days.
    n_assets:
        Number of assets in the synthetic universe.
    n_sectors:
        Number of synthetic sectors.
    seed:
        Random seed for reproducibility.
    signal_strength:
        Strength of the relationship between lagged alpha scores and next-day returns.
    """
    if n_days < 60:
        raise ValueError("n_days must be at least 60 for rolling diagnostics.")
    if n_assets < 10:
        raise ValueError("n_assets must be at least 10 for cross-sectional diagnostics.")

    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2023-01-02", periods=n_days)
    assets = [f"Asset_{i:03d}" for i in range(n_assets)]
    sectors = pd.Series(
        [f"Sector_{i % n_sectors}" for i in range(n_assets)],
        index=assets,
        name="sector",
    )

    # Persistent latent signal with asset-level structure and daily shocks.
    latent = rng.normal(size=(n_days, n_assets))
    for t in range(1, n_days):
        latent[t] = 0.86 * latent[t - 1] + 0.55 * rng.normal(size=n_assets)

    # Add a slow-moving cross-sectional component so rank stability is realistic.
    asset_quality = rng.normal(size=n_assets)
    signal = latent + 0.35 * asset_quality + 0.15 * rng.normal(size=(n_days, n_assets))
    alpha_scores = pd.DataFrame(signal, index=dates, columns=assets)
    alpha_scores = _zscore_cross_section(alpha_scores)

    # Market and sector components.
    market = rng.normal(loc=0.00025, scale=0.0085, size=n_days)
    sector_shocks = rng.normal(loc=0.0, scale=0.0040, size=(n_days, n_sectors))
    market_beta = rng.normal(loc=1.0, scale=0.15, size=n_assets)
    sector_index = np.array([i % n_sectors for i in range(n_assets)])

    noise = rng.normal(loc=0.0, scale=0.012, size=(n_days, n_assets))
    returns = np.zeros((n_days, n_assets))
    for t in range(n_days):
        alpha_component = np.zeros(n_assets)
        if t > 0:
            alpha_component = signal_strength * alpha_scores.iloc[t - 1].to_numpy()
        returns[t] = (
            market[t] * market_beta
            + sector_shocks[t, sector_index]
            + alpha_component
            + noise[t]
        )

    returns_df = pd.DataFrame(returns, index=dates, columns=assets)
    return SimulatedAlphaDataset(
        returns=returns_df,
        alpha_scores=alpha_scores,
        sectors=sectors,
    )
