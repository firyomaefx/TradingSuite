#!/usr/bin/env python3
"""Run all registered strategies through the walk-forward gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from data_loader import load_symbol_bars
from gate import SPECS
from strategies import STRATEGIES
from walkforward import trades_to_json, write_result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", choices=("dukascopy", "mt5"), default="dukascopy")
    parser.add_argument("--strategy", choices=tuple(STRATEGIES.keys()), default=None)
    args = parser.parse_args()

    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    broker_mismatch = args.data == "dukascopy"

    strategies = [args.strategy] if args.strategy else list(STRATEGIES.keys())
    any_pass = False
    summary: dict[str, dict] = {}

    for key in strategies:
        name, runner = STRATEGIES[key]
        all_trades = []
        data_sources: set[str] = set()
        for spec in SPECS:
            sys.stderr.write(f"[{key}] loading {spec.symbol} ({args.data})...\n")
            entry, d1, src = load_symbol_bars(spec, args.data)
            data_sources.add(src)
            all_trades.extend(runner(entry, d1, spec.symbol, spec.tf_seconds, key))

        meta = {
            "strategy_id": key,
            "strategy_name": name,
            "data_source": "; ".join(sorted(data_sources)),
            "broker_mismatch_risk": broker_mismatch,
        }
        body = trades_to_json(all_trades, meta)
        out_path = results_dir / f"{key}_walkforward.json"
        write_result(body, out_path)
        summary[key] = {
            "folds_passed": body["folds_passed"],
            "gate_pass": body["gate_pass"],
            "total_trades": body["total_trades"],
            "path": str(out_path.name),
        }
        if body["gate_pass"]:
            any_pass = True
        print(json.dumps({key: body}, indent=2))

    write_result({"screen": summary, "any_gate_pass": any_pass}, results_dir / "_summary.json")
    return 0 if any_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())