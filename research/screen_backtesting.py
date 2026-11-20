"""Optional fast OHLC screen with backtesting.py (research-only, AGPL)."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from data_loader import load_symbol_bars
from gate import SPECS


class EmaCross(Strategy):
    n1 = 20
    n2 = 50

    def init(self):
        close = self.data.Close
        self.ema1 = self.I(lambda x: pd.Series(x).ewm(span=self.n1).mean(), close)
        self.ema2 = self.I(lambda x: pd.Series(x).ewm(span=self.n2).mean(), close)

    def next(self):
        if crossover(self.ema1, self.ema2):
            self.buy()
        elif crossover(self.ema2, self.ema1):
            self.sell()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="GBPUSD")
    args = parser.parse_args()
    spec = next(s for s in SPECS if s.symbol == args.symbol)
    entry, _, src = load_symbol_bars(spec, "dukascopy")
    df = entry.rename(columns=str.title)[["Open", "High", "Low", "Close", "Volume"]]
    bt = Backtest(df, EmaCross, commission=0.0002, exclusive_orders=True)
    stats = bt.run()
    out = Path(__file__).resolve().parent / "results" / f"backtesting_{spec.symbol}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(str(stats))
    print(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())