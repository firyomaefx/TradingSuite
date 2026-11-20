# Install (MTrading MT5)

1. Clone or copy this repository.
2. From PowerShell:

```powershell
.\scripts\install.ps1 -DataPath "$env:APPDATA\MetaQuotes\Terminal\<ID>"
.\scripts\build.ps1 -DataPath "$env:APPDATA\MetaQuotes\Terminal\<ID>"
```

3. Attach `TradingSuiteCore` to XAUUSD H4, GBPUSD M30, or EURUSD M30.
4. Logs: `Common\Files\ts_<login>_events_v1.csv`

## Research (Python)

```bash
cd research
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_screen.py --data dukascopy
```

On Windows with MTrading history exports in `research/data/mt5/`:

```powershell
$env:TS_MT5_DATA = ".\research\data\mt5"
python run_screen.py --data mt5
```