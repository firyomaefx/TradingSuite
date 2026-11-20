//+------------------------------------------------------------------+
//| TradingSuiteCore.mq5  v0.1.0                                     |
//| Display-only: logs 3MAF-style trend signals to CSV. Never trades.|
//| Gate status is baked from research (see docs/STRATEGY_REGISTER).  |
//+------------------------------------------------------------------+
#property copyright "TradingSuite"
#property version   "0.10"
#property description "Display-only trend research EA. Research only. No proven edge."
#property description "Never places orders (InpAllowLive not implemented in v0.1.0)."

#define TS_VERSION "0.1.0"
#define TS_GATE_STATUS "PAPER_ONLY_GATE_NOT_PASSED"

input group "=== Logging ==="
input bool   InpLogEvents   = true;
input bool   InpUseCommon   = true;
input string InpStrategyId  = "trend_3maf";

input group "=== Safety ==="
input string InpFooter      = "Research only. No proven edge.";

#include <TradingSuite/TsLog.mqh>
#include <TradingSuite/TsTrend.mqh>

datetime g_lastBar = 0;

int OnInit()
  {
   TsSetPrefix(AccountInfoInteger(ACCOUNT_LOGIN), MQLInfoInteger(MQL_TESTER));
   Comment(InpFooter, "\n", TS_VERSION, " ", InpStrategyId, " ", TS_GATE_STATUS);
   return INIT_SUCCEEDED;
  }

void OnDeinit(const int reason)
  {
   Comment("");
  }

void OnTick()
  {
   datetime bar = iTime(_Symbol, PERIOD_CURRENT, 0);
   if(bar == 0 || bar == g_lastBar)
      return;
   g_lastBar = bar;

   int dir = 0;
   double entry = 0, sl = 0, tp = 0;
   if(!TsTrend3MafSignal(_Symbol, PERIOD_CURRENT, 1, dir, entry, sl, tp))
      return;

   string sig = (dir > 0) ? "BUY" : "SELL";
   string id = TsNewEventId(_Symbol, bar);
   long decision = (long)TimeCurrent() * 1000;
   long barOpen = (long)bar * 1000;
   double atr = 0;
   int hAtr = iATR(_Symbol, PERIOD_CURRENT, 14);
   double ab[];
   ArraySetAsSeries(ab, true);
   if(CopyBuffer(hAtr, 0, 1, 1, ab) == 1)
      atr = ab[0];
   double spread = (double)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);

   string skip = TS_GATE_STATUS;
   bool taken = false;

   if(InpLogEvents)
     {
      string line = StringFormat(
         "%d,%s,%I64d,%I64d,%s,%s,%s,%d,%.8f,%.8f,%.8f,%.8f,%.1f,%s,%s,%s,%s",
         TS_SCHEMA_VER, id, barOpen, decision, _Symbol, EnumToString(PERIOD_CURRENT), sig, dir,
         entry, sl, tp, atr, spread, (taken ? "true" : "false"), skip, InpStrategyId, TS_GATE_STATUS);
      TsAppendEvent(line, InpUseCommon);
     }

   string arrow = (dir > 0) ? "TradingSuiteUp" : "TradingSuiteDn";
   ObjectCreate(0, id, OBJ_ARROW, 0, bar, entry);
   ObjectSetInteger(0, id, OBJPROP_ARROWCODE, (dir > 0) ? 233 : 234);
   ObjectSetInteger(0, id, OBJPROP_COLOR, (dir > 0) ? clrLime : clrRed);
  }