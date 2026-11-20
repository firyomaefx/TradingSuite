"""Volatility breakout: Donchian channel break with HTF bias (geraked LRCUTB analogue)."""

from __future__ import annotations

import pandas as pd
import numpy as np

from gate import EMA_SEED, TARGET_R, fold_index
from indicators import atr_series, ema_series, rolling_max, rolling_min, simulate_long_short
from strategies.trend_3maf import bias_at_entry, htf_bias_from_d1
from walkforward import Trade, spread_deduct

TIME_STOP = 20
CHANNEL = 20
COMPRESSION_BARS = 5


def run(entry: pd.DataFrame, d1: pd.DataFrame, sym: str, tf_sec: int, strategy: str) -> list[Trade]:
    trades: list[Trade] = []
    c = entry["close"].to_numpy(dtype=float)
    h = entry["high"].to_numpy(dtype=float)
    l = entry["low"].to_numpy(dtype=float)
    atr = atr_series(h, l, c)
    upper = rolling_max(h, CHANNEL)
    lower = rolling_min(l, CHANNEL)
    period = pd.Timedelta(seconds=tf_sec)
    index = entry.index
    biases = bias_at_entry(htf_bias_from_d1(d1), index, period)

    start_i = EMA_SEED + CHANNEL + COMPRESSION_BARS
    for i in range(start_i, len(c) - TIME_STOP - 1):
        if np.isnan(atr[i]) or atr[i] <= 0:
            continue
        width = (upper[i - 1] - lower[i - 1]) / atr[i] if not np.isnan(upper[i - 1]) else 99
        if width > 2.5:
            continue
        recent_width = [(upper[j] - lower[j]) / atr[j] for j in range(i - COMPRESSION_BARS, i) if atr[j] > 0]
        if not recent_width or min(recent_width) > 1.8:
            continue

        bias = int(biases[i])
        if bias > 0 and c[i] > upper[i - 1] and c[i - 1] <= upper[i - 2]:
            entry_px = c[i]
            sl = lower[i]
            risk = entry_px - sl
            if risk <= 0:
                continue
            tp = entry_px + TARGET_R * risk
            r_gross = simulate_long_short(h, l, c, i + 1, 1, entry_px, sl, tp, TIME_STOP, TARGET_R)
            r_net = spread_deduct(r_gross, atr[i], risk)
            tc = index[i] + period
            trades.append(Trade(tc.to_pydatetime(), sym, 1, r_gross, r_net, fold_index(tc.to_pydatetime()), strategy))

        elif bias < 0 and c[i] < lower[i - 1] and c[i - 1] >= lower[i - 2]:
            entry_px = c[i]
            sl = upper[i]
            risk = sl - entry_px
            if risk <= 0:
                continue
            tp = entry_px - TARGET_R * risk
            r_gross = simulate_long_short(h, l, c, i + 1, -1, entry_px, sl, tp, TIME_STOP, TARGET_R)
            r_net = spread_deduct(r_gross, atr[i], risk)
            tc = index[i] + period
            trades.append(Trade(tc.to_pydatetime(), sym, -1, r_gross, r_net, fold_index(tc.to_pydatetime()), strategy))

    return trades