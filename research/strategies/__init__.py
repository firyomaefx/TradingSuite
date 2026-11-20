from strategies.trend_3maf import run as run_trend_3maf
from strategies.breakout_donchian import run as run_breakout_donchian
from strategies.meanrev_bbrsi import run as run_meanrev_bbrsi

STRATEGIES = {
    "trend_3maf": ("Trend 3MAF (geraked-inspired)", run_trend_3maf),
    "breakout_donchian": ("LRC/Donchian breakout", run_breakout_donchian),
    "meanrev_bbrsi": ("BBRSI mean reversion", run_meanrev_bbrsi),
}