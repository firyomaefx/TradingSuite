"""Mean reversion: Bollinger + RSI with HTF trend filter (geraked BBRSI analogue)."""

from __future__ import annotations

import pandas as pd
import numpy as np

from gate import EMA_SEED, TARGET_R, fold_index
from indicators import atr_series, rsi_series, sma_series, simulate_long_short
from strategies.trend_3maf import bias_at_entry, htf_bias_from_d1
from walkforward import Trade, spread_deduct

TIME_STOP = 16
BB_PERIOD = 20
BB_STD = 2.0
RSI_PERIOD = 14
RSI_OS = 30
RSI_OB = 70


def run(entry: pd.DataFrame, d1: pd.DataFrame, sym: str, tf_sec: int, strategy: str) -> list[Trade]:
    trades: list[Trade] = []
    c = entry["close"].to_numpy(dtype=float)
    h = entry["high"].to_numpy(dtype=float)
    l = entry["low"].to_numpy(dtype=float)
    mid = sma_series(c, BB_PERIOD)
    std = np.full(len(c), np.nan)
    for i in range(BB_PERIOD - 1, len(c)):
        std[i] = float(np.std(c[i - BB_PERIOD + 1 : i + 1]))
    upper = mid + BB_STD * std
    lower = mid - BB_STD * std
    rsi = rsi_series(c, RSI_PERIOD)
    atr = atr_series(h, l, c)
    period = pd.Timedelta(seconds=tf_sec)
    index = entry.index
    biases = bias_at_entry(htf_bias_from_d1(d1), index, period)

    start_i = EMA_SEED + BB_PERIOD + RSI_PERIOD
    for i in range(start_i, len(c) - TIME_STOP - 1):
        if np.isnan(atr[i]) or atr[i] <= 0:
            continue
        bias = int(biases[i])

        if bias >= 0 and l[i] <= lower[i] and rsi[i] < RSI_OS and c[i] > c[i - 1]:
            entry_px = c[i]
            sl = l[i] - 0.25 * atr[i]
            risk = entry_px - sl
            if risk <= 0:
                continue
            tp = min(mid[i], entry_px + TARGET_R * risk)
            r_gross = simulate_long_short(h, l, c, i + 1, 1, entry_px, sl, tp, TIME_STOP, TARGET_R)
            r_net = spread_deduct(r_gross, atr[i], risk)
            tc = index[i] + period
            trades.append(Trade(tc.to_pydatetime(), sym, 1, r_gross, r_net, fold_index(tc.to_pydatetime()), strategy))

        elif bias <= 0 and h[i] >= upper[i] and rsi[i] > RSI_OB and c[i] < c[i - 1]:
            entry_px = c[i]
            sl = h[i] + 0.25 * atr[i]
            risk = sl - entry_px
            if risk <= 0:
                continue
            tp = max(mid[i], entry_px - TARGET_R * risk)
            r_gross = simulate_long_short(h, l, c, i + 1, -1, entry_px, sl, tp, TIME_STOP, TARGET_R)
            r_net = spread_deduct(r_gross, atr[i], risk)
            tc = index[i] + period
            trades.append(Trade(tc.to_pydatetime(), sym, -1, r_gross, r_net, fold_index(tc.to_pydatetime()), strategy))

    return trades