from __future__ import annotations

from pathlib import Path

from alpha_diagnostics.diagnostics import (
    compute_information_decay,
    compute_quantile_returns,
    compute_quantile_spread,
    compute_rank_ic,
    compute_rank_turnover,
    summarize_diagnostics,
)
from alpha_diagnostics.plotting import (
    create_social_preview,
    plot_information_decay,
    plot_quantile_spread,
    plot_rolling_rank_ic,
    plot_signal_diagnostics_dashboard,
)
from alpha_diagnostics.report import write_summary_report
from alpha_diagnostics.simulate import simulate_alpha_dataset


def main() -> None:
    root = Path(__file__).resolve().parent
    data_dir = root / "data"
    figures_dir = root / "figures"
    reports_dir = root / "reports"
    assets_dir = root / "assets"

    for directory in (data_dir, figures_dir, reports_dir, assets_dir):
        directory.mkdir(parents=True, exist_ok=True)

    dataset = simulate_alpha_dataset()
    returns = dataset.returns
    alpha_scores = dataset.alpha_scores

    rank_ic = compute_rank_ic(alpha_scores, returns, horizon=1)
    information_decay = compute_information_decay(alpha_scores, returns)
    quantile_returns = compute_quantile_returns(alpha_scores, returns, n_quantiles=5, horizon=1)
    quantile_spread = compute_quantile_spread(quantile_returns)
    turnover = compute_rank_turnover(alpha_scores)
    summary_metrics = summarize_diagnostics(rank_ic, information_decay, quantile_spread, turnover)

    # Persist datasets and diagnostics.
    returns.to_csv(data_dir / "simulated_returns.csv")
    alpha_scores.to_csv(data_dir / "alpha_scores.csv")
    rank_ic.to_frame().to_csv(data_dir / "rank_ic.csv")
    information_decay.to_csv(data_dir / "information_decay.csv", index=False)
    quantile_returns.to_csv(data_dir / "quantile_returns.csv", index=False)
    quantile_spread.to_csv(data_dir / "quantile_spread.csv")
    turnover.to_frame().to_csv(data_dir / "turnover.csv")
    summary_metrics.to_csv(data_dir / "summary_metrics.csv", index=False)

    # Create figures.
    plot_rolling_rank_ic(rank_ic, figures_dir / "rolling_rank_ic.png")
    plot_information_decay(information_decay, figures_dir / "information_decay.png")
    plot_quantile_spread(quantile_spread, figures_dir / "quantile_spread.png")
    plot_signal_diagnostics_dashboard(
        rank_ic,
        information_decay,
        quantile_spread,
        turnover,
        figures_dir / "signal_diagnostics_dashboard.png",
    )
    create_social_preview(rank_ic, assets_dir / "social_preview.png")

    # Write report.
    write_summary_report(
        summary_metrics,
        information_decay,
        reports_dir / "alpha_diagnostics_summary.md",
    )

    print("Alpha diagnostics analysis complete.")
    print(summary_metrics.to_string(index=False))


if __name__ == "__main__":
    main()
