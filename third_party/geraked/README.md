# geraked/metatrader5 (reference)

Upstream: https://github.com/geraked/metatrader5 (MIT).

TradingSuite **does not** vendor full Experts in v0.1.0. Strategy logic for `trend_3maf`, `breakout_donchian`, and `meanrev_bbrsi` is **reimplemented** in Python from published descriptions (3MAF, LRCUTB, BBRSI), then walk-forward tested.

To vendor a single MIT EA after a gate pass, copy the file here with `LICENSE` preserved and record the commit hash in [docs/STRATEGY_REGISTER.md](../../docs/STRATEGY_REGISTER.md).