"""Pre-registered walk-forward gate constants (see docs/GATE.md)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

SPREAD_ATR = 0.05
MAX_SPREAD_ATR = 0.15
MIN_TRADES_PER_FOLD = 100
MIN_FOLDS_TO_SHIP = 3
NUM_FOLDS = 4
TARGET_R = 1.5

START = datetime(2020, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

FOLD_ENDS = [
    datetime(2021, 8, 15, tzinfo=timezone.utc),
    datetime(2023, 4, 1, tzinfo=timezone.utc),
    datetime(2024, 11, 15, tzinfo=timezone.utc),
    END,
]

EMA_SEED = 200
ATR_PERIOD = 14


@dataclass(frozen=True)
class SymbolSpec:
    dukascopy_code: str
    symbol: str
    entry_label: str
    interval: int
    tf_seconds: int


SPECS = (
    SymbolSpec("XAU-USD", "XAUUSD", "H4", 4, 4 * 3600),
    SymbolSpec("GBP-USD", "GBPUSD", "M30", 30, 30 * 60),
    SymbolSpec("EUR-USD", "EURUSD", "M30", 30, 30 * 60),
)


def fold_index(t: datetime) -> int:
    for i, fe in enumerate(FOLD_ENDS):
        if t <= fe:
            return i
    return NUM_FOLDS - 1