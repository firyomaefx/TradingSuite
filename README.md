# TradingSuite

Research-first MT5 EA program for **MTrading** (XAUUSD H4, GBPUSD M30, EURUSD M30).

Strategies must pass a **pre-registered walk-forward gate** in Python before any MQL5 port or live `OrderSend`. [JevScalperSuite](https://github.com/ttrg/JevScalperSuite) is the guideline for logging and safety, not a fork.

## Layout

```text
docs/           CHARTER, GATE, SAFETY, STRATEGY_REGISTER
research/       walk-forward, strategy screens (Python only)
MQL5/           EAs after a strategy earns the gate (display-only first)
scripts/        install.ps1, build.ps1
internal/       repo survey (not for publication)
```

## Quick start (research)

```bash
cd research
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_screen.py --data dukascopy
```

Prefer **MTrading terminal history** on your laptop when available (`--data mt5`). Cloud runs default to Dukascopy with a broker mismatch disclaimer in JSON output.

## Gate (pre-registered)

See [docs/GATE.md](docs/GATE.md). Ship MQL5 only when **≥3 of 4** walk-forward folds pass: **mean R after spread > 0** and **n ≥ 100** per fold.

## License

Original TradingSuite code: MIT. Third-party see `third_party/` and [internal/repo-survey.md](internal/repo-survey.md).