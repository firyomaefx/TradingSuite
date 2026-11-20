# GitHub reference survey (TradingSuite Plan)

One-page audit per reference: license, what we import, what we reject.

## 1. QuantConnect/Lean (~22k ★)

- **License:** Apache-2.0
- **Import:** Walk-forward discipline, algorithm lifecycle (research vs live), gate-before-ship mindset
- **Reject:** Embedding Lean runtime in MT5; too heavy for MTrading retail stack
- **Action:** Recreate gate rules in [docs/GATE.md](../docs/GATE.md) and [research/walkforward.py](../research/walkforward.py)

## 2. kernc/backtesting.py (~9k ★)

- **License:** AGPL-3.0 (research)
- **Import:** Fast OHLC screens in `research/screen_backtesting.py`
- **Reject:** Shipping AGPL code inside `.ex5`; any live path
- **Action:** Dependency only under `research/requirements.txt`

## 3. geraked/metatrader5 (~700 ★)

- **License:** MIT
- **Import:** EA structure, input groups, tester hygiene; strategy **ideas** for 3MAF, LRCUTB, BBRSI
- **Reject:** Blind fork of all Experts; grid-style EAs
- **Action:** Python recreation in [research/strategies/](../research/strategies/); optional vendor note in [third_party/geraked/README.md](../third_party/geraked/README.md)

## 4. Joaopeuko/Mql5-Python-Integration (~220 ★)

- **License:** MIT
- **Import:** CSV export + optional `MetaTrader5` copy_rates pattern
- **Reject:** Full bridge before any gate pass
- **Action:** [research/mt5_session.py](../research/mt5_session.py)

## 5. francomascareloai/EA_SCALPER_XAUUSD (~300 ★)

- **License:** Check per file (study only)
- **Import:** README tone: no profit claims without evidence
- **Reject:** Strategy copy without walk-forward
- **Action:** [docs/SAFETY.md](../docs/SAFETY.md)

## 6. nkaz001/hftbacktest (~5k ★)

- **License:** Apache-2.0
- **Import:** Spread and fill honesty; deduct spread in R (see GATE)
- **Reject:** Crypto LOB HFT on MT5 retail
- **Action:** `SPREAD_ATR` in [research/gate.py](../research/gate.py)

## 7. TheSnowGuru/PyTrader MT5 connector (~1k ★)

- **License:** Check repo (Phase 4)
- **Import:** Thin MQL5 gateway + Python brain **only after** gate + paper match
- **Reject:** Phase 1 scope
- **Action:** Documented in [docs/CHARTER.md](../docs/CHARTER.md) Phase D

## Explicit exclusions

- **freqtrade / vnpy:** crypto or non-MT5 stack; optional Phase 5
- **grid-master-pro-mt5-ea:** grid / ruin risk; not screened