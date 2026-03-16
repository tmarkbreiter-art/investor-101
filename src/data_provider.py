"""
AXIOM US — vNext Data Provider
Finnhub: live quotes, news, fundamentals
yfinance: price history + 52wk high/low
"""
import time, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import yfinance as yf


class DataProvider:
    FINNHUB_BASE = "https://finnhub.io/api/v1"

    def __init__(self, config):
        self.config = config
        self.fk = config.FINNHUB_API_KEY

    def _fh_get(self, endpoint, params):
        params["token"] = self.fk
        try:
            r = requests.get(f"{self.FINNHUB_BASE}/{endpoint}", params=params, timeout=8)
            if r.ok:
                return r.json()
        except Exception as e:
            print(f"  Finnhub {endpoint}: {e}")
        return None

    def fetch_quote(self, symbol):
        d = self._fh_get("quote", {"symbol": symbol})
        if not d or not d.get("c"):
            return None
        return {"price": round(float(d["c"]), 2), "dp": round(float(d.get("dp", 0) or 0), 2)}

    def fetch_52wk(self, symbol, price):
        try:
            fi = yf.Ticker(symbol).fast_info
            h52 = round(float(fi.year_high), 2) if fi.year_high else round(price * 1.2, 2)
            l52 = round(float(fi.year_low),  2) if fi.year_low  else round(price * 0.8, 2)
            if h52 <= l52: h52 = l52 + 1
            return h52, l52
        except:
            return round(price * 1.2, 2), round(price * 0.8, 2)

    def fetch_news(self, symbol):
        today    = datetime.now()
        week_ago = today - timedelta(days=7)
        d = self._fh_get("company-news", {
            "symbol": symbol,
            "from": week_ago.strftime("%Y-%m-%d"),
            "to":   today.strftime("%Y-%m-%d"),
        })
        if not isinstance(d, list):
            return []
        return [{"headline": n.get("headline",""), "datetime": n.get("datetime",0)} for n in d[:5]]

    def fetch_metrics(self, symbol):
        d = self._fh_get("stock/metric", {"symbol": symbol, "metric": "all"})
        if not d or not d.get("metric"):
            return {}
        m = d["metric"]
        return {
            "pe":         m.get("peBasicExclExtraTTM"),
            "rev_growth": m.get("revenueGrowthTTMYoy"),
            "roe":        m.get("roeTTM"),
            "debt_eq":    m.get("totalDebt/totalEquityQuarterly"),
        }

    def fetch_history(self, symbol, days=60):
        try:
            hist = yf.Ticker(symbol).history(period=f"{days}d")
            if hist.empty: return []
            return [round(float(p), 4) for p in hist["Close"].tolist()]
        except Exception as e:
            print(f"  yfinance {symbol}: {e}")
            return []

    def fetch_stock(self, symbol):
        meta  = self.config.SYMBOL_MAP.get(symbol, {"name": symbol, "sector": "?"})
        quote = self.fetch_quote(symbol)
        if not quote:
            print(f"  No quote: {symbol}")
            return None
        price    = quote["price"]
        history  = self.fetch_history(symbol)
        h52, l52 = self.fetch_52wk(symbol, price)
        news     = self.fetch_news(symbol)
        metrics  = self.fetch_metrics(symbol)
        return {
            "symbol": symbol, "name": meta["name"], "sector": meta["sector"],
            "price": price, "dp": quote["dp"],
            "h52": h52, "l52": l52,
            "history": history, "news": news, "metrics": metrics,
        }

    def fetch_all_stocks(self, symbols):
        results = []
        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = {ex.submit(self._fetch_with_delay, sym, i): sym
                       for i, sym in enumerate(symbols)}
            for fut in as_completed(futures):
                data = fut.result()
                if data: results.append(data)
        results.sort(key=lambda x: symbols.index(x["symbol"]) if x["symbol"] in symbols else 99)
        print(f"  Fetched {len(results)}/{len(symbols)} stocks")
        return results

    def _fetch_with_delay(self, symbol, index):
        time.sleep(index * 0.25)
        return self.fetch_stock(symbol)

    def fetch_pulse(self):
        pulse = {}
        for sym in self.config.PULSE_SYMBOLS:
            q = self.fetch_quote(sym)
            if q:
                h52, l52 = self.fetch_52wk(sym, q["price"])
                pulse[sym] = {**q, "h52": h52, "l52": l52}
            time.sleep(0.15)

        vixy = pulse.get("VIXY", {})
        fear_level = "NEUTRAL"
        if vixy:
            rng = vixy["h52"] - vixy["l52"]
            pos = (vixy["price"] - vixy["l52"]) / rng if rng else 0.3
            if   pos > 0.78: fear_level = "EXTREME FEAR"
            elif pos > 0.58: fear_level = "HIGH FEAR"
            elif pos > 0.38: fear_level = "ELEVATED"
            elif pos > 0.18: fear_level = "NEUTRAL"
            else:            fear_level = "GREED"

        spy_dp  = pulse.get("SPY", {}).get("dp", 0)
        uso_dp  = pulse.get("USO", {}).get("dp", 0)
        geo_risk = fear_level in ("EXTREME FEAR", "HIGH FEAR") or uso_dp > 4

        return {"quotes": pulse, "fear_level": fear_level,
                "geo_risk": geo_risk, "spy_dp": spy_dp, "uso_dp": uso_dp}
