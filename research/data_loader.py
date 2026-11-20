"""Load OHLC for walk-forward: Dukascopy (default) or MT5 CSV export."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from gate import END, START, SymbolSpec

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / ".walkforward_cache"
MT5_DATA = Path(os.environ.get("TS_MT5_DATA", ROOT / "data" / "mt5"))


def _chunk_ranges(start: datetime, end: datetime, months: int = 3):
    cur = start
    while cur < end:
        nxt = min(end, (pd.Timestamp(cur) + pd.DateOffset(months=months)).to_pydatetime().replace(tzinfo=timezone.utc))
        yield cur, nxt
        cur = nxt


def load_dukascopy(spec: SymbolSpec, timeframe_label: str, interval_hours_or_min: int, is_daily: bool) -> pd.DataFrame:
    from dukascopy_python import OfferSide, TimeUnit, fetch_candles, to_dataframe

    CACHE.mkdir(parents=True, exist_ok=True)
    key = f"{spec.dukascopy_code}_{timeframe_label}".replace("-", "_")
    path = CACHE / f"{key}.parquet"
    if path.exists():
        return pd.read_parquet(path)

    unit = TimeUnit.DAY if is_daily else (TimeUnit.HOUR if spec.tf_seconds >= 3600 else TimeUnit.MINUTE)
    interval = 1 if is_daily else interval_hours_or_min

    parts: list[pd.DataFrame] = []
    for a, b in _chunk_ranges(START, END):
        raw = fetch_candles(spec.dukascopy_code, interval, unit, OfferSide.BID, a, b)
        df = to_dataframe(raw)
        if len(df):
            parts.append(df)
    if not parts:
        raise RuntimeError(f"no Dukascopy data for {spec.symbol} {timeframe_label}")

    out = pd.concat(parts).sort_index()
    out = out[~out.index.duplicated(keep="last")]
    cols = [c for c in ("open", "high", "low", "close", "volume") if c in out.columns]
    out = out[cols].astype(float)
    out.to_parquet(path)
    return out


def load_mt5_csv(spec: SymbolSpec, timeframe_label: str) -> pd.DataFrame | None:
    """Expect files like mt5/XAUUSD_H4.csv with datetime index or 'time' column."""
    fname = MT5_DATA / f"{spec.symbol}_{timeframe_label}.csv"
    if not fname.exists():
        return None
    df = pd.read_csv(fname)
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], utc=True)
        df = df.set_index("time")
    df = df.sort_index()
    for c in ("open", "high", "low", "close"):
        df[c] = df[c].astype(float)
    return df


def load_symbol_bars(spec: SymbolSpec, data_mode: str) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Returns (entry_tf, d1_or_htf_daily, data_source_label)."""
    if data_mode == "mt5":
        entry = load_mt5_csv(spec, spec.entry_label)
        htf = load_mt5_csv(spec, "D1")
        if entry is not None and htf is not None:
            entry = entry.loc[(entry.index >= START) & (entry.index <= END)]
            htf = htf.loc[(htf.index >= START) & (htf.index <= END)]
            return entry, htf, f"MTrading export, {spec.symbol}"
        # fall through

    if spec.entry_label == "H4":
        entry = load_dukascopy(spec, "H4", 4, is_daily=False)
    else:
        entry = load_dukascopy(spec, spec.entry_label, 30, is_daily=False)
    d1 = load_dukascopy(spec, "D1", 1, is_daily=True)
    entry = entry.loc[(entry.index >= START) & (entry.index <= END)]
    d1 = d1.loc[(d1.index >= START) & (d1.index <= END)]
    return entry, d1, "Dukascopy Bank SA, BID, UTC bar open (broker_mismatch_risk)"