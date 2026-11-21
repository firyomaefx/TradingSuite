# 📈 TradingSuite

**Research-first MT5 product line for MTrading — XAUUSD H4, GBPUSD M30, EURUSD M30.**

Strategies must pass a **pre-registered walk-forward gate** in Python before any MQL5 port or live `OrderSend`. [JevScalperSuite](https://github.com/ttrg/JevScalperSuite) is the guideline for logging and safety, not a fork.

- Version: **0.1.0** ([VERSION](VERSION))
- Status: **no proven edge** — display-only EA + Python screens

---

## 📑 Table of contents

1. [⏱️ 2-minute start](#️-2-minute-start)
2. [🧠 Mental model](#-mental-model)
3. [🗺️ Architecture](#️-architecture)
4. [🚀 Quick start](#-quick-start)
5. [📖 Usage](#-usage)
6. [🚫 What we will NOT do](#-what-we-will-not-do)
7. [📤 Sample output](#-sample-output)
8. [⚡ Power users](#-power-users)
9. [🔒 Privacy](#-privacy)
10. [⚙️ Config](#️-config)
11. [🛠️ Developers & license](#️-developers--license)

---

## ⏱️ 2-minute start

**Research (any OS, lazy data = Dukascopy):**

```bash
cd research
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_screen.py --data dukascopy
```

- Exit **0** if any strategy hits the ship gate; **2** if none pass (see `research/run_screen.py`).
- JSON land in `research/results/*_walkforward.json` and `research/results/_summary.json`.

**MT5 (Windows, display-only EA):**

```powershell
.\scripts\install.ps1 -DataPath "$env:APPDATA\MetaQuotes\Terminal\<ID>"
.\scripts\build.ps1   -DataPath "$env:APPDATA\MetaQuotes\Terminal\<ID>"
```

Attach `MQL5/Experts/TradingSuite/TradingSuiteCore.ex5` to the right symbol/TF. It **does not trade**.

---

## 🧠 Mental model

| Layer | Location | Role |
|-------|----------|------|
| **Gate contract** | `docs/GATE.md`, `research/gate.py` | Pre-registered folds, spread model, ship rule (≥3/4 folds) |
| **Research** | `research/` | Load bars → run `STRATEGIES` → write walk-forward JSON |
| **Data** | `research/data_loader.py` | `--data dukascopy` (default) or `--data mt5` + `TS_MT5_DATA` |
| **MQL5 (after gate)** | `MQL5/` | v0.1.0: **display-only** `TradingSuiteCore` logs CSV + chart arrows |
| **Ops scripts** | `scripts/install.ps1`, `scripts/build.ps1` | Copy tree to terminal `DataPath`, compile via MetaEditor |
| **Governance** | `docs/CHARTER.md`, `docs/STRATEGY_REGISTER.md`, `docs/SAFETY.md` | Kill/ship decisions, no edge claims |

---

## 🗺️ Architecture

```text
Dukascopy / MT5 CSV ──► research/run_screen.py ──► walkforward.py ──► gate.py
                              │
                              ├── strategies: trend_3maf | breakout_donchian | meanrev_bbrsi
                              └── research/results/*_walkforward.json
                                        │
                                        ▼ (only if gate_pass; v0.1.0: none shipped live)
MT5 bars ──► TradingSuiteCore.mq5 ──► TsTrend.mqh (signal) ──► TsLog.mqh ──► ts_*_events_v1.csv
                    │                      no OrderSend
                    └── chart arrows (display-only)
```

---

## 🚀 Quick start

### Python research

```bash
cd research
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_screen.py --data dukascopy
```

Single strategy:

```bash
python run_screen.py --data dukascopy --strategy trend_3maf
```

`--strategy` choices: `trend_3maf`, `breakout_donchian`, `meanrev_bbrsi` (from `research/strategies/__init__.py`).

### MTrading MT5 (Windows)

See [docs/INSTALL.md](docs/INSTALL.md).

```powershell
.\scripts\install.ps1 -DataPath "C:\Users\<you>\AppData\Roaming\MetaQuotes\Terminal\<ID>"
.\scripts\build.ps1   -DataPath "C:\Users\<you>\AppData\Roaming\MetaQuotes\Terminal\<ID>"
```

| Script | Parameters | Behavior |
|--------|------------|----------|
| `install.ps1` | **`-DataPath`** (required) | Copies `MQL5/Experts/TradingSuite` and `MQL5/Include/TradingSuite` into `<DataPath>\MQL5\` |
| `build.ps1` | **`-DataPath`** (required), **`-MetaEditor`** (optional) | Runs `install.ps1`, compiles `TradingSuiteCore.mq5`, writes `dist/TradingSuiteCore_<VERSION>.ex5` |

`build.ps1` searches `MetaEditor64.exe` under MTrading or generic MT5 paths unless `-MetaEditor` is set.

---

## 📖 Usage

### Walk-forward screen

| Flag | Values | Default |
|------|--------|---------|
| `--data` | `dukascopy`, `mt5` | `dukascopy` |
| `--strategy` | `trend_3maf`, `breakout_donchian`, `meanrev_bbrsi` | all keys in `STRATEGIES` |

**Gate (from [docs/GATE.md](docs/GATE.md) and `research/gate.py`):**

- Sample: **2020-01-01** → **2026-09-30** UTC
- Four fold ends: 2021-08-15, 2023-04-01, 2024-11-15, 2026-09-30
- Per fold **pass**: `n ≥ 100` and `mean(r_net) > 0` after **0.05 ATR** spread deduction (`SPREAD_ATR`)
- **Ship**: **≥ 3 of 4** folds (`MIN_FOLDS_TO_SHIP`)

Symbols in gate (`SPECS`): **XAUUSD H4**, **GBPUSD M30**, **EURUSD M30** (with D1 HTF).

### `TradingSuiteCore.mq5` inputs

| Input | Type | Default | Purpose |
|-------|------|---------|---------|
| `InpLogEvents` | bool | `true` | Append rows to CSV |
| `InpUseCommon` | bool | `true` | `FILE_COMMON` → `Common\Files` |
| `InpStrategyId` | string | `trend_3maf` | `strategy_id` column |
| `InpFooter` | string | `Research only. No proven edge.` | Chart comment |

Compiled constants: `TS_VERSION "0.1.0"`, `TS_GATE_STATUS "PAPER_ONLY_GATE_NOT_PASSED"`. **No `InpAllowLive` in v0.1.0** — display-only only.

### CSV event log (`TsLog.mqh`)

When `InpUseCommon=true`, files live under **`Common\Files`**:

```text
ts_<login>_events_v1.csv        # live chart
ts_tester_events_v1.csv         # Strategy Tester
```

Header (`TS_EVENTS_HEADER`):

```text
schema_ver,event_id,bar_open_msc,decision_msc,symbol,timeframe,signal,direction,entry,sl,tp,atr,spread_pts,taken,skip_reason,strategy_id,gate_status
```

Rows use `taken=false` and `skip_reason` / `gate_status` = `PAPER_ONLY_GATE_NOT_PASSED` until a strategy ships.

---

## 🚫 What we will NOT do

- Call `OrderSend` / `OrderModify` / `OrderClose` in v0.1.0 ([docs/SAFETY.md](docs/SAFETY.md))
- Ship MQL5 “live” logic before **≥3/4** gate folds on **MTrading-primary** data
- Claim profitability from Telegram, arrows, or CSV rows
- Embed AGPL `backtesting` code inside compiled EAs (research-only dependency)
- Commit tokens, `.set` files, or terminal CSV exports ([.gitignore](.gitignore))
- Grid / martingale / unvetted “profitable EA” forks without recreation + walk-forward ([docs/CHARTER.md](docs/CHARTER.md))

---

## 📤 Sample output

### `_summary.json` (screen aggregate)

```json
{
  "screen": {
    "trend_3maf": {
      "folds_passed": 0,
      "gate_pass": false,
      "total_trades": 4908,
      "path": "trend_3maf_walkforward.json"
    }
  },
  "any_gate_pass": false
}
```

### Per-strategy fold snippet (`trend_3maf_walkforward.json`)

```json
{
  "folds": [
    { "fold": 1, "end": "2021-08-15", "n": 804, "mean_R": -0.002, "pass": false }
  ],
  "folds_passed": 0,
  "gate_pass": false,
  "spread_assumption_atr": 0.05,
  "strategy_id": "trend_3maf",
  "data_source": "Dukascopy Bank SA, BID, UTC bar open (broker_mismatch_risk)",
  "broker_mismatch_risk": true
}
```

With `--data dukascopy`, JSON includes `broker_mismatch_risk: true`. Verdicts: [docs/STRATEGY_REGISTER.md](docs/STRATEGY_REGISTER.md).

### CSV row (illustrative)

```text
1,XAUUSD_1609459200_12345,1609459200000,1609462800000,XAUUSD,PERIOD_H4,BUY,1,1900.50000000,1890.00000000,1915.00000000,8.50000000,25.0,false,PAPER_ONLY_GATE_NOT_PASSED,trend_3maf,PAPER_ONLY_GATE_NOT_PASSED
```

---

## ⚡ Power users

- **One strategy only:** `python run_screen.py --data dukascopy --strategy meanrev_bbrsi`
- **MTrading CSV path:** set `TS_MT5_DATA` (see [Config](#️-config)) then `python run_screen.py --data mt5`
- Expected MT5 filenames: `{SYMBOL}_{TF}.csv` e.g. `XAUUSD_H4.csv`, plus `*_D1.csv` for HTF (`load_mt5_csv` in `research/data_loader.py`)
- **Dukascopy cache:** `research/.walkforward_cache/*.parquet` — delete to refetch
- **AGPL screen:** `research/screen_backtesting.py` (optional fast checks; ship rule still uses `run_screen.py` / `walkforward.py`)
- **Recompile only:** `build.ps1 -MetaEditor "C:\Path\MetaEditor64.exe" -DataPath "<terminal data>"`

---

## 🔒 Privacy

- CSV names include **account login** (`ts_<login>_…`); treat `Common\Files` as private ([docs/SAFETY.md](docs/SAFETY.md))
- No account credentials in git; credentials only on the terminal
- Dukascopy downloads are BID bars — not your broker’s exact fills

---

## ⚙️ Config

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `TS_MT5_DATA` | No | `research/data/mt5` | Directory of MT5-exported OHLC CSVs for `--data mt5` |

**Lazy mode (recommended for CI/cloud):** no `.env` — `run_screen.py --data dukascopy` pulls Dukascopy BID data.

Copy [`.env.example`](.env.example) to `.env` only when you use MTrading exports locally:

```bash
# .env (optional)
TS_MT5_DATA=/path/to/your/mt5/csv
```

---

## 🛠️ Developers & license

### Repository map

```text
docs/              CHARTER, GATE, SAFETY, STRATEGY_REGISTER, INSTALL
research/          run_screen.py, gate.py, walkforward.py, strategies/
MQL5/              TradingSuiteCore.mq5, Include/TradingSuite/*.mqh
scripts/           install.ps1, build.ps1
third_party/       vendor notes (e.g. geraked survey)
dist/              TradingSuiteCore_<VERSION>.ex5 from build.ps1
```

### Python pins (`research/requirements.txt`)

```text
numpy>=1.24
pandas>=2.0
pyarrow>=14.0
dukascopy-python>=4.0
backtesting>=0.3.3
```

### Development rules

- Pre-register gate changes in `docs/GATE.md` **before** re-running screens
- Bump `VERSION`, `#property version`, and `TS_VERSION` together on release
- Update [docs/CHANGELOG.md](docs/CHANGELOG.md) and [docs/STRATEGY_REGISTER.md](docs/STRATEGY_REGISTER.md) when verdicts change
- Display-only MQL5 unless gate + safety review ([docs/GATE.md](docs/GATE.md) live section)

### License

- **Original TradingSuite code:** MIT (see repository license file when published)
- **Third-party:** [third_party/](third_party/) and [internal/repo-survey.md](internal/repo-survey.md) — respect AGPL for `backtesting` in `research/` only

### Links

- GitHub: <https://github.com/firyomaefx/TradingSuite>