"""Shared OHLC indicators for walk-forward replay."""

from __future__ import annotations

import numpy as np

from gate import ATR_PERIOD, EMA_SEED


def ema_series(close: np.ndarray, period: int) -> np.ndarray:
    out = np.full(len(close), np.nan)
    if len(close) < EMA_SEED:
        return out
    alpha = 2.0 / (period + 1.0)
    ema = float(close[EMA_SEED - 1])
    out[EMA_SEED - 1] = ema
    for i in range(EMA_SEED, len(close)):
        ema += alpha * (close[i] - ema)
        out[i] = ema
    return out


def sma_series(close: np.ndarray, period: int) -> np.ndarray:
    out = np.full(len(close), np.nan)
    if len(close) < period:
        return out
    for i in range(period - 1, len(close)):
        out[i] = float(np.mean(close[i - period + 1 : i + 1]))
    return out


def atr_series(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = ATR_PERIOD) -> np.ndarray:
    n = len(close)
    out = np.full(n, np.nan)
    for i in range(period, n):
        tr_sum = 0.0
        for j in range(i - period + 1, i + 1):
            tr = max(high[j] - low[j], abs(high[j] - close[j - 1]), abs(low[j] - close[j - 1]))
            tr_sum += tr
        out[i] = tr_sum / period
    return out


def rsi_series(close: np.ndarray, period: int = 14) -> np.ndarray:
    out = np.full(len(close), np.nan)
    if len(close) <= period:
        return out
    deltas = np.diff(close)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = float(np.mean(gains[:period]))
    avg_loss = float(np.mean(losses[:period]))
    if avg_loss == 0:
        out[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        out[period] = 100.0 - 100.0 / (1.0 + rs)
    for i in range(period + 1, len(close)):
        g = gains[i - 1]
        lo = losses[i - 1]
        avg_gain = (avg_gain * (period - 1) + g) / period
        avg_loss = (avg_loss * (period - 1) + lo) / period
        if avg_loss == 0:
            out[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            out[i] = 100.0 - 100.0 / (1.0 + rs)
    return out


def rolling_max(high: np.ndarray, period: int) -> np.ndarray:
    out = np.full(len(high), np.nan)
    for i in range(period - 1, len(high)):
        out[i] = float(np.max(high[i - period + 1 : i + 1]))
    return out


def rolling_min(low: np.ndarray, period: int) -> np.ndarray:
    out = np.full(len(low), np.nan)
    for i in range(period - 1, len(low)):
        out[i] = float(np.min(low[i - period + 1 : i + 1]))
    return out


def simulate_long_short(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    start: int,
    side: int,
    entry: float,
    sl: float,
    tp: float,
    max_bars: int,
    target_r: float,
) -> float:
    risk = (entry - sl) * side
    if risk <= 0:
        return 0.0
    for k in range(start, min(start + max_bars, len(close))):
        if side > 0:
            if low[k] <= sl:
                return -1.0
            if high[k] >= tp:
                return target_r
        else:
            if high[k] >= sl:
                return -1.0
            if low[k] <= tp:
                return target_r
    last = min(start + max_bars - 1, len(close) - 1)
    return side * (close[last] - entry) / risk