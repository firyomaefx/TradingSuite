# Strategy register

Pre-registered gate: [GATE.md](GATE.md). **No strategy passed ship rule (≥3/4 folds)** on first Dukascopy screen (2026-11-20). Raw JSON: `research/results/*_walkforward.json`.

**Data:** Dukascopy BID UTC; `broker_mismatch_risk: true`. Re-run with `--data mt5` on MTrading exports before any ship decision.

## trend_3maf

**geraked upstream:** `2MOMEMA` / `3MAF` family (EMA stack + momentum; v0.1.0 Python uses simplified 3-EMA pullback, not a line port).

| Fold | End | n | mean R | Pass |
|------|-----|---|--------|------|
| 1 | 2021-08-15 | 804 | −0.0020 | no |
| 2 | 2023-04-01 | 1342 | −0.0724 | no |
| 3 | 2024-11-15 | 1292 | −0.0822 | no |
| 4 | 2026-09-30 | 1470 | −0.0600 | no |

**Verdict:** KILLED (`folds_passed` 0/4). MQL5 `TradingSuiteCore` logs this rule **display-only** with `skip_reason=PAPER_ONLY_GATE_NOT_PASSED`.

## breakout_donchian

**geraked upstream:** `DHLAOS` (daily high/low pierce + oscillator). v0.1.0 Python used Donchian compression instead; filters produced **n=0** (revisit DHLAOS logic, `Grid=false`, before next screen).

| Fold | End | n | mean R | Pass |
|------|-----|-----|--------|------|
| 1–4 | — | 0 | — | no |

**Verdict:** KILLED (no signals under v0.1.0 compression filters; revisit logic in Python before next screen, do not tune on folds).

## meanrev_bbrsi

**geraked upstream:** `BBRSI.mq5` (RSI + Bollinger reclaim; use `Grid=false`).

| Fold | End | n | mean R | Pass |
|------|-----|---|--------|------|
| 1 | 2021-08-15 | 284 | −0.1909 | no |
| 2 | 2023-04-01 | 156 | −0.1403 | no |
| 3 | 2024-11-15 | 190 | −0.0207 | no |
| 4 | 2026-09-30 | 162 | +0.1834 | **yes** |

**Verdict:** KILLED (`folds_passed` 1/4). One passing fold is not ship-worthy.

## Next candidate

Simple trend / session / volatility rules only. No MQL5 `OrderSend` until ≥3/4 folds pass on **MTrading-primary** data.