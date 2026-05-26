from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DARK_BACKGROUND = "#050505"
AXIS_TEXT = "#f2f2f2"
GRID = "#323232"
BLUE = "#00A3FF"
ORANGE = "#FF8A00"
GREEN = "#37D627"
MUTED = "#A6A6A6"


def _apply_dark_style(ax: plt.Axes) -> None:
    ax.set_facecolor(DARK_BACKGROUND)
    ax.figure.set_facecolor(DARK_BACKGROUND)
    ax.tick_params(colors=AXIS_TEXT, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color(MUTED)
        spine.set_linewidth(0.9)
    ax.grid(True, color=GRID, linestyle="--", linewidth=0.7, alpha=0.65)
    ax.xaxis.label.set_color(AXIS_TEXT)
    ax.yaxis.label.set_color(AXIS_TEXT)
    ax.title.set_color(AXIS_TEXT)


def plot_rolling_rank_ic(rank_ic: pd.Series, output_path: str | Path, window: int = 63) -> None:
    output_path = Path(output_path)
    rolling = rank_ic.rolling(window=window).mean()
    fig, ax = plt.subplots(figsize=(12.8, 6.4), dpi=150)
    ax.plot(rank_ic.index, rank_ic.values, color=MUTED, alpha=0.25, linewidth=0.8, label="Daily Rank IC")
    ax.plot(rolling.index, rolling.values, color=BLUE, linewidth=2.2, label=f"{window}D Rolling Mean")
    ax.axhline(0.0, color=AXIS_TEXT, linewidth=0.8, alpha=0.7)
    ax.set_title("Rolling Rank IC", fontsize=18, weight="bold", pad=14)
    ax.set_ylabel("Rank IC", fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    _apply_dark_style(ax)
    legend = ax.legend(facecolor=DARK_BACKGROUND, edgecolor=MUTED, labelcolor=AXIS_TEXT, framealpha=0.9)
    for text in legend.get_texts():
        text.set_color(AXIS_TEXT)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def plot_information_decay(information_decay: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    fig, ax = plt.subplots(figsize=(12.8, 6.4), dpi=150)
    ax.plot(
        information_decay["horizon"],
        information_decay["mean_rank_ic"],
        color=GREEN,
        marker="o",
        linewidth=2.4,
    )
    ax.axhline(0.0, color=AXIS_TEXT, linewidth=0.8, alpha=0.7)
    ax.set_title("Information Decay Curve", fontsize=18, weight="bold", pad=14)
    ax.set_ylabel("Mean Rank IC", fontsize=12)
    ax.set_xlabel("Forward Return Horizon", fontsize=12)
    ax.set_xticks(information_decay["horizon"].tolist())
    _apply_dark_style(ax)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def plot_quantile_spread(quantile_spread: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    fig, ax = plt.subplots(figsize=(12.8, 6.4), dpi=150)
    ax.plot(
        quantile_spread.index,
        quantile_spread["cumulative_spread_return"],
        color=ORANGE,
        linewidth=2.2,
        label="Top-minus-bottom quantile spread",
    )
    ax.axhline(0.0, color=AXIS_TEXT, linewidth=0.8, alpha=0.7)
    ax.set_title("Long-Short Quantile Spread", fontsize=18, weight="bold", pad=14)
    ax.set_ylabel("Cumulative spread return", fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    _apply_dark_style(ax)
    legend = ax.legend(facecolor=DARK_BACKGROUND, edgecolor=MUTED, labelcolor=AXIS_TEXT, framealpha=0.9)
    for text in legend.get_texts():
        text.set_color(AXIS_TEXT)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def plot_signal_diagnostics_dashboard(
    rank_ic: pd.Series,
    information_decay: pd.DataFrame,
    quantile_spread: pd.DataFrame,
    turnover: pd.Series,
    output_path: str | Path,
) -> None:
    """Create a compact multi-panel diagnostic dashboard."""
    output_path = Path(output_path)
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor(DARK_BACKGROUND)

    # Panel 1: rolling IC
    ax = axes[0, 0]
    rolling = rank_ic.rolling(window=63).mean()
    ax.plot(rank_ic.index, rank_ic.values, color=MUTED, alpha=0.25, linewidth=0.7)
    ax.plot(rolling.index, rolling.values, color=BLUE, linewidth=1.8)
    ax.axhline(0.0, color=AXIS_TEXT, linewidth=0.7, alpha=0.7)
    ax.set_title("Rolling Rank IC", fontsize=12, weight="bold")
    ax.set_ylabel("Rank IC")
    _apply_dark_style(ax)

    # Panel 2: decay
    ax = axes[0, 1]
    ax.plot(information_decay["horizon"], information_decay["mean_rank_ic"], color=GREEN, marker="o", linewidth=2.0)
    ax.axhline(0.0, color=AXIS_TEXT, linewidth=0.7, alpha=0.7)
    ax.set_title("Information Decay", fontsize=12, weight="bold")
    ax.set_xlabel("Horizon")
    ax.set_ylabel("Mean Rank IC")
    ax.set_xticks(information_decay["horizon"].tolist())
    _apply_dark_style(ax)

    # Panel 3: quantile spread
    ax = axes[1, 0]
    ax.plot(quantile_spread.index, quantile_spread["cumulative_spread_return"], color=ORANGE, linewidth=1.9)
    ax.axhline(0.0, color=AXIS_TEXT, linewidth=0.7, alpha=0.7)
    ax.set_title("Long-Short Quantile Spread", fontsize=12, weight="bold")
    ax.set_ylabel("Cumulative return")
    _apply_dark_style(ax)

    # Panel 4: turnover
    ax = axes[1, 1]
    ax.plot(turnover.index, turnover.values, color="#C084FC", linewidth=1.4)
    ax.set_title("Rank Turnover", fontsize=12, weight="bold")
    ax.set_ylabel("Average rank change")
    _apply_dark_style(ax)

    fig.suptitle("Alpha Signal Diagnostics", color=AXIS_TEXT, fontsize=18, weight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def create_social_preview(rank_ic: pd.Series, output_path: str | Path, window: int = 63) -> None:
    """Create a simple dark chart suitable for repository social preview."""
    output_path = Path(output_path)
    rolling = rank_ic.rolling(window=window).mean()
    fig, ax = plt.subplots(figsize=(12.8, 6.4), dpi=150)
    ax.plot(rank_ic.index, rank_ic.values, color=MUTED, alpha=0.20, linewidth=0.8, label="Daily Rank IC")
    ax.plot(rolling.index, rolling.values, color=BLUE, linewidth=2.5, label=f"{window}D Rolling Mean")
    ax.axhline(0.0, color=AXIS_TEXT, linewidth=0.8, alpha=0.7)
    ax.set_title("Rolling Rank IC", fontsize=20, weight="bold", pad=16)
    ax.set_ylabel("Rank IC", fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    _apply_dark_style(ax)
    legend = ax.legend(facecolor=DARK_BACKGROUND, edgecolor=MUTED, labelcolor=AXIS_TEXT, framealpha=0.9)
    for text in legend.get_texts():
        text.set_color(AXIS_TEXT)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
