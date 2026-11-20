"""Walk-forward engine: summarize trades into gate folds."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

from gate import (
    FOLD_ENDS,
    MIN_FOLDS_TO_SHIP,
    MIN_TRADES_PER_FOLD,
    NUM_FOLDS,
    SPREAD_ATR,
)


@dataclass
class Trade:
    t: datetime
    sym: str
    side: int
    r_gross: float
    r_net: float
    fold: int
    strategy: str


def spread_deduct(r_gross: float, atr: float, risk: float) -> float:
    if risk <= 0:
        return r_gross
    spread_r = SPREAD_ATR * atr / risk
    return r_gross - spread_r


def summarize(trades: list[Trade]) -> dict:
    folds: dict[int, list[float]] = {i: [] for i in range(NUM_FOLDS)}
    for t in trades:
        folds[t.fold].append(t.r_net)

    rows = []
    pass_n = 0
    for i in range(NUM_FOLDS):
        rs = folds[i]
        n = len(rs)
        mean_r = float(np.mean(rs)) if n else float("nan")
        sum_r = float(np.sum(rs)) if n else 0.0
        ok = n >= MIN_TRADES_PER_FOLD and mean_r > 0
        if ok:
            pass_n += 1
        rows.append(
            {
                "fold": i + 1,
                "end": FOLD_ENDS[i].strftime("%Y-%m-%d"),
                "n": n,
                "mean_R": round(mean_r, 4) if n else None,
                "sum_R": round(sum_r, 2),
                "pass": ok,
            }
        )
    return {
        "folds": rows,
        "folds_passed": pass_n,
        "gate_pass": pass_n >= MIN_FOLDS_TO_SHIP,
        "total_trades": len(trades),
        "spread_assumption_atr": SPREAD_ATR,
    }


def write_result(result: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2))


def trades_to_json(trades: list[Trade], meta: dict) -> dict:
    body = summarize(trades)
    body.update(meta)
    body["trades_sample"] = [asdict(t) for t in trades[:5]]
    for row in body.get("trades_sample", []):
        row["t"] = row["t"].isoformat() if hasattr(row["t"], "isoformat") else str(row["t"])
    return body