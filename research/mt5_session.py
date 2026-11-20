"""Minimal MT5 Python bridge stub (recreate Joaopeuko/Mql5-Python-Integration patterns on laptop).

Set TS_MT5_DATA to a folder of CSV exports: SYMBOL_TF.csv with time, open, high, low, close.
Optional live: pip install MetaTrader5 and implement copy_rates below.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MT5_DATA = Path(os.environ.get("TS_MT5_DATA", ROOT / "data" / "mt5"))


def data_ready() -> bool:
    needed = ("XAUUSD_H4.csv", "GBPUSD_M30.csv", "EURUSD_M30.csv", "XAUUSD_D1.csv")
    return MT5_DATA.exists() and all((MT5_DATA / f).exists() for f in needed[:3])


def copy_rates_to_csv(symbol: str, timeframe: str, out_dir: Path | None = None) -> Path | None:
    """When MetaTrader5 is installed on Windows, export bars to CSV for walk-forward."""
    try:
        import MetaTrader5 as mt5  # type: ignore
    except ImportError:
        return None
    out_dir = out_dir or MT5_DATA
    out_dir.mkdir(parents=True, exist_ok=True)
    if not mt5.initialize():
        return None
    tf_map = {"M30": mt5.TIMEFRAME_M30, "H4": mt5.TIMEFRAME_H4, "D1": mt5.TIMEFRAME_D1}
    rates = mt5.copy_rates_from_pos(symbol, tf_map[timeframe], 0, 50000)
    mt5.shutdown()
    if rates is None:
        return None
    import pandas as pd

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    path = out_dir / f"{symbol}_{timeframe}.csv"
    df.to_csv(path, index=False)
    return path