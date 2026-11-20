#ifndef TS_LOG_MQH
#define TS_LOG_MQH

#define TS_SCHEMA_VER 1
#define TS_EVENTS_HEADER \
   "schema_ver,event_id,bar_open_msc,decision_msc,symbol,timeframe,signal,direction," \
   "entry,sl,tp,atr,spread_pts,taken,skip_reason,strategy_id,gate_status\n"

string g_tsPrefix = "";

string TsEventsFile() { return g_tsPrefix + "ts_events_v" + IntegerToString(TS_SCHEMA_VER) + ".csv"; }

void TsSetPrefix(const long login, const bool tester)
  {
   if(tester)
      g_tsPrefix = "ts_tester_";
   else
      g_tsPrefix = "ts_" + IntegerToString(login) + "_";
  }

bool TsAppendEvent(const string line, const bool useCommon)
  {
   int flags = FILE_READ | FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_SHARE_READ | FILE_SHARE_WRITE |
               (useCommon ? FILE_COMMON : 0);
   int h = FileOpen(TsEventsFile(), flags);
   if(h == INVALID_HANDLE)
      return false;
   if(FileSize(h) == 0)
      FileWriteString(h, TS_EVENTS_HEADER);
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, line + "\n");
   FileClose(h);
   return true;
  }

string TsNewEventId(const string sym, const datetime barOpen)
  {
   return sym + "_" + IntegerToString((long)barOpen) + "_" + IntegerToString(GetTickCount());
  }

#endif