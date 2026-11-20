# Pre-registered walk-forward gate

Registered **before** strategy screens on TradingSuite v0.1.0. Do not change pass rules after seeing fold results.

## Data

- **Primary:** MTrading terminal exported OHLC (bid), documented in result JSON as `data_source`.
- **Fallback:** Dukascopy BID UTC (bar open). Reports must state `broker_mismatch_risk: true`.

## Spread model

Each trade deducts **0.05 ATR in R units** from gross R (same assumption as JevScalper daily-trend walk-forward). Skip entries when spread / ATR > **0.15** when spread series is available; otherwise apply spread deduction only.

## Folds

Four expanding windows, trade `decision_time` assigned by fold end:

| Fold | End (UTC)   |
|------|-------------|
| 1    | 2021-08-15  |
| 2    | 2023-04-01  |
| 3    | 2024-11-15  |
| 4    | 2026-09-30  |

Sample start: **2020-01-01** UTC.

## Pass rule (per fold)

A fold **passes** iff:

- `n >= 100` resolved trades in that fold, and
- `mean(r_net) > 0` after spread deduction.

## Ship rule

A strategy **ships to MQL5** only if **≥ 3 of 4** folds pass.

Otherwise it is **killed** and listed in [STRATEGY_REGISTER.md](STRATEGY_REGISTER.md) with fold table. Display-only EAs may still log candidates for paper audit; they must not claim edge.

## MQL5 execution

- Default: **display-only** (no `OrderSend`).
- Live: separate input `InpAllowLive=false` default + second risk review doc (not in v0.1.0).