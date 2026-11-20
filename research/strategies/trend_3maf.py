"""Trend: three-EMA alignment + pullback (recreates geraked 3MAF idea, not a line-for-line port)."""

from __future__ import annotations

import pandas as pd

import numpy as np

from gate import EMA_SEED, TARGET_R, fold_index
from indicators import atr_series, ema_series, simulate_long_short
from walkforward import Trade, spread_deduct

TIME_STOP = 24
FAST = 20
MID = 50
SLOW = 200


def htf_bias_from_d1(d1: pd.DataFrame) -> pd.Series:
    c = d1["close"].to_numpy(dtype=float)
    ema50 = ema_series(c, MID)
    close_times = d1.index + pd.Timedelta(days=1)
    bias = np.zeros(len(c), dtype=np.int8)
    for j in range(EMA_SEED, len(c)):
        if np.isnan(ema50[j]):
            continue
        bias[j] = 1 if c[j] > ema50[j] else -1
    return pd.Series(bias, index=close_times)


def bias_at_entry(d1_bias: pd.Series, entry_index: pd.DatetimeIndex, period: pd.Timedelta) -> np.ndarray:
    decisions = entry_index + period
    tmp = pd.DataFrame({"tc": decisions}).sort_values("tc")
    bias_tbl = d1_bias.sort_index().rename("bias").reset_index()
    bias_tbl.columns = ["tc", "bias"]
    merged = pd.merge_asof(tmp, bias_tbl, on="tc", direction="backward")
    return merged["bias"].fillna(0).to_numpy(dtype=np.int8)


def run(entry: pd.DataFrame, d1: pd.DataFrame, sym: str, tf_sec: int, strategy: str) -> list[Trade]:
    trades: list[Trade] = []
    c = entry["close"].to_numpy(dtype=float)
    h = entry["high"].to_numpy(dtype=float)
    l = entry["low"].to_numpy(dtype=float)
    ema_f = ema_series(c, FAST)
    ema_m = ema_series(c, MID)
    ema_s = ema_series(c, SLOW)
    atr = atr_series(h, l, c)
    period = pd.Timedelta(seconds=tf_sec)
    index = entry.index
    biases = bias_at_entry(htf_bias_from_d1(d1), index, period)

    start_i = EMA_SEED + 5
    for i in range(start_i, len(c) - TIME_STOP - 1):
        if np.isnan(atr[i]) or atr[i] <= 0:
            continue
        bias = int(biases[i])
        if bias == 0:
            continue

        align_long = c[i] > ema_f[i] > ema_m[i] > ema_s[i]
        align_short = c[i] < ema_f[i] < ema_m[i] < ema_s[i]

        if bias > 0 and align_long and c[i - 1] <= ema_f[i - 1] and c[i] > ema_f[i]:
            entry_px = c[i]
            sl = l[i] - 0.5 * atr[i]
            risk = entry_px - sl
            if risk <= 0:
                continue
            tp = entry_px + TARGET_R * risk
            r_gross = simulate_long_short(h, l, c, i + 1, 1, entry_px, sl, tp, TIME_STOP, TARGET_R)
            r_net = spread_deduct(r_gross, atr[i], risk)
            tc = index[i] + period
            trades.append(Trade(tc.to_pydatetime(), sym, 1, r_gross, r_net, fold_index(tc.to_pydatetime()), strategy))

        elif bias < 0 and align_short and c[i - 1] >= ema_f[i - 1] and c[i] < ema_f[i]:
            entry_px = c[i]
            sl = h[i] + 0.5 * atr[i]
            risk = sl - entry_px
            if risk <= 0:
                continue
            tp = entry_px - TARGET_R * risk
            r_gross = simulate_long_short(h, l, c, i + 1, -1, entry_px, sl, tp, TIME_STOP, TARGET_R)
            r_net = spread_deduct(r_gross, atr[i], risk)
            tc = index[i] + period
            trades.append(Trade(tc.to_pydatetime(), sym, -1, r_gross, r_net, fold_index(tc.to_pydatetime()), strategy))

    return trades