# TradingSuite charter

## Product

MT5 expert advisors for **MTrading** account, symbols:

| Symbol   | Entry TF | HTF bias source |
|----------|----------|-----------------|
| XAUUSD   | H4       | D1              |
| GBPUSD   | M30      | H4              |
| EURUSD   | M30      | H4              |

## Mission

Find at least one **simple, slow** rule with positive **walk-forward expectancy after spread**, then port it to MQL5. No profitability claims until [GATE.md](GATE.md) close criteria are met.

## Non-goals

- Retail MT5 HFT or market making
- Grid / martingale EAs
- Forking unvetted “profitable” GitHub EAs without recreation and walk-forward
- Merging execution into JevScalperSuite without a separate charter amendment

## Relationship to JevScalperSuite

- **Guideline:** CSV audit (`event_id`), `Common\Files`, VERSION file, `build.ps1` / `install.ps1`, SAFETY tone
- **Not a fork:** SMC research stays in JevScalper; TradingSuite defaults to trend / breakout / mean-reversion candidates from the geraked survey
- JevScalper remains the signal lab; TradingSuite is the product line that **earns the right to trade**

## PMP phases

1. **Initiate** — this charter + pre-registered gate
2. **Plan** — repo layout, license audit ([internal/repo-survey.md](../internal/repo-survey.md))
3. **Execute** — Python research → walk-forward → optional MQL5 display-only → optional live layer
4. **Monitor** — paper trade, drift vs backtest
5. **Close** — ship tagged release or kill strategy in [STRATEGY_REGISTER.md](STRATEGY_REGISTER.md)

## Holdout

The **last calendar quarter** of the sample window is reserved for a one-time holdout after a gate pass. Do not tune on holdout.