# Safety and scope

## Display-only default

`TradingSuiteCore` must not call `OrderSend`, `OrderModify`, `OrderClose`, or `OrderCloseBy` unless `InpAllowLive=true` **and** a strategy has passed the walk-forward gate documented in [STRATEGY_REGISTER.md](STRATEGY_REGISTER.md).

v0.1.0 ships **display-only only** (`InpAllowLive` is not offered).

## No proven edge

Until the gate and holdout are satisfied, footer text stays:

```text
Research only. No proven edge.
```

Do not market Telegram, arrows, or CSV rows as trade advice.

## Credentials

- No tokens, logins, or `.set` files in git
- Credentials live under `Common\Files` on the terminal only

## Data privacy

CSV logs may include account login in filenames. Treat `Common\Files` as private.

## AGPL

`backtesting.py` is used **only** in `research/`. Do not embed AGPL code inside compiled EAs.