#ifndef TS_TREND_MQH
#define TS_TREND_MQH

// Display-only 3MAF-style detector (matches research/strategies/trend_3maf.py intent).

input int    TsFastEma   = 20;
input int    TsMidEma    = 50;
input int    TsSlowEma   = 200;
input double TsTargetR   = 1.5;

int TsEmaHandle(const string sym, const ENUM_TIMEFRAMES tf, const int period)
  {
   return iMA(sym, tf, period, 0, MODE_EMA, PRICE_CLOSE);
  }

bool TsReadEma(const int h, const int shift, double &val)
  {
   double buf[];
   ArraySetAsSeries(buf, true);
   if(CopyBuffer(h, 0, shift, 1, buf) != 1)
      return false;
   val = buf[0];
   return true;
  }

bool TsTrend3MafSignal(const string sym, const ENUM_TIMEFRAMES tf, const int shift,
                       int &direction, double &entry, double &sl, double &tp)
  {
   direction = 0;
   int hFast = TsEmaHandle(sym, tf, TsFastEma);
   int hMid  = TsEmaHandle(sym, tf, TsMidEma);
   int hSlow = TsEmaHandle(sym, tf, TsSlowEma);
   int hAtr  = iATR(sym, tf, 14);
   if(hFast == INVALID_HANDLE || hMid == INVALID_HANDLE || hSlow == INVALID_HANDLE || hAtr == INVALID_HANDLE)
      return false;

   double c0 = iClose(sym, tf, shift);
   double c1 = iClose(sym, tf, shift + 1);
   double ef0, ef1, em0, em1, es0, atr0, l0, h0;
   if(!TsReadEma(hFast, shift, ef0) || !TsReadEma(hFast, shift + 1, ef1)) return false;
   double em1;
   if(!TsReadEma(hMid, shift, em0) || !TsReadEma(hMid, shift + 1, em1)) return false;
   if(!TsReadEma(hSlow, shift, es0)) return false;
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(hAtr, 0, shift, 1, atr) != 1) return false;
   atr0 = atr[0];
   l0 = iLow(sym, tf, shift);
   h0 = iHigh(sym, tf, shift);

   bool alignLong  = (c0 > ef0 && ef0 > em0 && em0 > es0);
   bool alignShort = (c0 < ef0 && ef0 < em0 && em0 < es0);

   if(alignLong && c1 <= ef1 && c0 > ef0)
     {
      direction = 1;
      entry = c0;
      sl = l0 - 0.5 * atr0;
      double risk = entry - sl;
      if(risk <= 0) return false;
      tp = entry + TsTargetR * risk;
      return true;
     }
   if(alignShort && c1 >= ef1 && c0 < ef0)
     {
      direction = -1;
      entry = c0;
      sl = h0 + 0.5 * atr0;
      double risk = sl - entry;
      if(risk <= 0) return false;
      tp = entry - TsTargetR * risk;
      return true;
     }
   return false;
  }

#endif