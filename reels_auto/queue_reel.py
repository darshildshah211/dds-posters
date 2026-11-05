"""Queue the rendered reel for the existing Instagram publisher (scripts/ig_publish.py).
Usage: python3 reels_auto/queue_reel.py reels/auto/2026-11-05-decay.mp4"""
import datetime as dt, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
media = sys.argv[1]
d = json.load(open(os.path.join(HERE, "out", "data.json")))
c = d["nifty_chg"]
nifty = f"Nifty {'+' if c >= 0 else '−'}{abs(c):.2f}% on the day."
caption = f"""{d['weekday']}, {d['date_label']}: the Nifty {d['strike']} {d['side']} (weekly, {d['expiry_label'].title()} expiry) went from ₹{d['open']:.2f} to ₹{d['last']:.2f} in a single session. {d['drop_pct']}% of its premium, gone. {nifty}

Option premium is a melting asset. Time decay works every minute, whether the market moves or not.

Rules over emotions. Systematic, rule-based execution is how disciplined investors approach derivatives. Ask us how it works.

To know more, contact us.
.
Educational content, not investment advice or a recommendation. 9 out of 10 individual traders in equity F&O incurred net losses (SEBI study). Derivatives carry substantial risk of loss. AMFI-registered Mutual Fund Distributor, ARN-359084.

#Nifty #ThetaDecay #OptionsTrading #StockMarketIndia #NSE #FnO #RiskManagement #DDSCapital"""
item = {
    "publish_at": (dt.datetime.now(IST) + dt.timedelta(minutes=2)).isoformat(timespec="seconds"),
    "max_late_hours": 6,
    "type": "REEL",
    "media": media,
    "caption": caption,
    "source": "reels_auto/decay " + d["trigger"],
}
path = f"instagram/queue/{d['date_iso']}-decay-reel.json"
json.dump(item, open(path, "w"), ensure_ascii=False, indent=2)
print("QUEUED:", path)
