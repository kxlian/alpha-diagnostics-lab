# Alpha Diagnostics Summary

This report summarizes the output of the Alpha Diagnostics Lab workflow.

## Headline Results

| Metric | Value |
|---|---:|
| Mean Rank IC | 0.0413 |
| Rank IC IR | 0.3872 |
| Positive IC Share | 66.60% |
| Mean Long-Short Spread | 0.14% |
| Cumulative Long-Short Spread | 97.00% |
| Average Rank Turnover | 12.33% |

## Information Decay

|   horizon |   mean_rank_ic |   median_rank_ic |   ic_volatility |   ic_ir |   positive_ic_share |   observations |
|----------:|---------------:|-----------------:|----------------:|--------:|--------------------:|---------------:|
|    1.0000 |         0.0413 |           0.0408 |          0.1068 |  0.3872 |              0.6660 |       503.0000 |
|    2.0000 |         0.0334 |           0.0401 |          0.1111 |  0.3004 |              0.6135 |       502.0000 |
|    5.0000 |         0.0274 |           0.0311 |          0.1144 |  0.2397 |              0.6032 |       499.0000 |
|   10.0000 |         0.0102 |           0.0085 |          0.1123 |  0.0904 |              0.5243 |       494.0000 |
|   20.0000 |         0.0104 |           0.0047 |          0.1111 |  0.0940 |              0.5207 |       484.0000 |

## Interpretation

The synthetic alpha signal shows positive average Rank IC and a constructive long-short quantile spread. The information decay curve is used to check whether signal quality is strongest at shorter horizons and weakens as the forecast window extends.

This is a diagnostic framework, not a live trading strategy. The purpose is to show how alpha signals can be evaluated before being passed into portfolio construction.

## Suggested Extensions

- Sector-neutral Rank IC
- Bootstrap confidence intervals
- Transaction cost sensitivity
- Regime-level robustness diagnostics
- Factor exposure checks
