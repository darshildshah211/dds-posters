"""Decide whether today deserves a decay reel, and write reels_auto/out/data.json for the template.

Trigger (either):
  A) heavy decay: the ATM call or put of the nearest Nifty weekly expiry falls >= DECAY_PCT from its 9:15 open
  B) one-sided day: Nifty moves >= ONESIDED_PCT vs previous close AND closes in the outer 20% of its day range

ATM = strike nearest to Nifty's 9:15 open. On expiry day itself the next weekly expiry is used,
so ordinary expiry-day collapse does not fire a reel every week.

Env: UPSTOX_TOKEN (Upstox Analytics Token, read-only).  --demo uses built-in sample data (no API).
Prints TRIGGERED / NOT_TRIGGERED; exit 0 either way, exit 1 on error.
"""
import datetime as dt, json, os, sys, urllib.parse, urllib.request

DECAY_PCT = 40.0
ONESIDED_PCT = 1.0
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
API = "https://api.upstox.com"
NIFTY = "NSE_INDEX|Nifty 50"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def get(path, params=None):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "Authorization": "Bearer " + os.environ["UPSTOX_TOKEN"]})
    with urllib.request.urlopen(req, timeout=60) as r:
        j = json.loads(r.read())
    if j.get("status") != "success":
        raise RuntimeError(f"{path}: {j}")
    return j["data"]


def q(key):
    return urllib.parse.quote(key, safe="")


def intraday(key):
    """1-min candles for today, oldest first: [{t,o,h,l,c}]"""
    d = get(f"/v3/historical-candle/intraday/{q(key)}/minutes/1")
    rows = sorted(d.get("candles", []), key=lambda c: c[0])
    return [{"t": c[0][11:16], "o": c[1], "h": c[2], "l": c[3], "c": c[4]} for c in rows]


def prev_close(key, today):
    frm = (today - dt.timedelta(days=12)).isoformat()
    d = get(f"/v3/historical-candle/{q(key)}/days/1/{(today - dt.timedelta(days=1)).isoformat()}/{frm}")
    rows = sorted(d.get("candles", []), key=lambda c: c[0])
    return rows[-1][4]


def live_data():
    today = dt.datetime.now(IST).date()
    spot = intraday(NIFTY)
    if len(spot) < 300:
        print("NOT_TRIGGERED: market closed or incomplete data", len(spot)); return None
    pc = prev_close(NIFTY, today)
    contracts = get("/v2/option/contract", {"instrument_key": NIFTY})
    expiries = sorted({c["expiry"] for c in contracts if c["expiry"] > today.isoformat()})
    exp = expiries[0]
    opn = spot[0]["o"]
    chain = [c for c in contracts if c["expiry"] == exp]
    strike = min({c["strike_price"] for c in chain}, key=lambda s: abs(s - opn))
    legs = {}
    for c in chain:
        if c["strike_price"] == strike:
            legs[c["instrument_type"]] = intraday(c["instrument_key"])
    return {"date": today.isoformat(), "expiry": exp, "strike": strike, "spot": spot, "prev_close": pc,
            "CE": legs["CE"], "PE": legs["PE"]}


def demo_data():
    """Sample shaped like 5 Nov 2026's 24300 PE (approximate) for local testing only."""
    import math, random
    random.seed(7)
    anchors = [(0, 147), (2, 137.2), (17, 153), (40, 103), (57, 125), (130, 116), (140, 101), (205, 87),
               (250, 72), (286, 62.8), (330, 52), (374, 44)]
    def at(m):
        for (a, pa), (b, pb) in zip(anchors, anchors[1:]):
            if a <= m <= b: return pa + (pb - pa) * (m - a) / (b - a)
    pe, prev, dev = [], 147.0, 0
    for i in range(375):
        dev = dev * .7 + random.gauss(0, 1.1); c = at(i) + dev
        pe.append({"t": f"{9 + (15 + i) // 60:02d}:{(15 + i) % 60:02d}", "o": prev, "h": max(prev, c) + abs(random.gauss(0, .8)),
                   "l": min(prev, c) - abs(random.gauss(0, .8)), "c": c}); prev = c
    ce = [dict(k, o=150 - (k["o"] - 100) * .8, h=150 - (k["l"] - 100) * .8, l=150 - (k["h"] - 100) * .8, c=150 - (k["c"] - 100) * .8) for k in pe]
    spot = [dict(k, o=24300 + (147 - k["o"]) * 2.1, h=24300 + (147 - k["l"]) * 2.1, l=24300 + (147 - k["h"]) * 2.1, c=24300 + (147 - k["c"]) * 2.1) for k in pe]
    return {"date": "2026-11-05", "expiry": "2026-11-09", "strike": 24300, "spot": spot, "prev_close": 24170.0,
            "CE": ce, "PE": pe, "demo": True}


def decide(d):
    def drop(leg): return (leg[0]["o"] - leg[-1]["c"]) / leg[0]["o"] * 100
    dce, dpe = drop(d["CE"]), drop(d["PE"])
    side = "PE" if dpe >= dce else "CE"
    spot = d["spot"]
    close, hi, lo = spot[-1]["c"], max(k["h"] for k in spot), min(k["l"] for k in spot)
    chg = (close - d["prev_close"]) / d["prev_close"] * 100
    pos = (close - lo) / (hi - lo) if hi > lo else .5
    onesided = abs(chg) >= ONESIDED_PCT and ((chg > 0 and pos >= .8) or (chg < 0 and pos <= .2))
    heavy = max(dce, dpe) >= DECAY_PCT
    leg = d[side]
    day = dt.date.fromisoformat(d["date"])
    exp = dt.date.fromisoformat(d["expiry"])
    data = {
        "weekday": day.strftime("%A"), "date_label": f"{day.day} {day.strftime('%B')}",
        "date_iso": d["date"], "strike": int(d["strike"]), "side": side,
        "kind": "put" if side == "PE" else "call",
        "expiry_label": exp.strftime("%d %b %Y").upper(),
        "minutes": [[k["o"], k["h"], k["l"], k["c"]] for k in leg],
        "first_time": leg[0]["t"], "last_time": leg[-1]["t"],
        "open": round(leg[0]["o"], 2), "last": round(leg[-1]["c"], 2),
        "drop_pct": round(max(dce, dpe)), "nifty_close": round(close, 2), "nifty_chg": round(chg, 2),
        "trigger": "heavy_decay" if heavy else ("one_sided" if onesided else None),
        "demo": d.get("demo", False),
    }
    return data, (heavy or onesided)


def main():
    os.makedirs(OUT, exist_ok=True)
    try:
        d = demo_data() if "--demo" in sys.argv else live_data()
    except Exception as e:
        print("ERROR fetching data:", e); return 1
    if d is None:
        return 0
    data, fire = decide(d)
    print(json.dumps({k: v for k, v in data.items() if k != "minutes"}, indent=1))
    if fire or "--force" in sys.argv:
        json.dump(data, open(os.path.join(OUT, "data.json"), "w"))
        print("TRIGGERED")
        gh = os.environ.get("GITHUB_OUTPUT")
        if gh:
            open(gh, "a").write("triggered=true\n")
    else:
        print("NOT_TRIGGERED")
    return 0


sys.exit(main())
