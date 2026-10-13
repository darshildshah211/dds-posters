"""Publish due Instagram posts/stories/reels from instagram/queue/*.json using Meta's free
Instagram API (Instagram Login). Run by GitHub Actions every 15 minutes. Standard library only.

Queue file (instagram/queue/<name>.json):
  {"publish_at": "2026-10-14T09:00:00+05:30", "max_late_hours": 6,
   "type": "POST" | "STORY" | "REEL",
   "media": "instagram/media/2026-10-14-feed.jpg",   # JPEG for POST/STORY, MP4 for REEL; path in repo
   "caption": "text (POST/REEL only)"}
Done files move to instagram/queue/done/ (with the Instagram media id); too-late ones to skipped/.
Exit code 2 = login expired.
"""
import datetime as dt, glob, json, os, shutil, sys, time
import urllib.error, urllib.parse, urllib.request

G = "https://graph.instagram.com/v23.0"
QDIR = "instagram/queue"
RAW = "https://raw.githubusercontent.com/" + os.environ.get("GITHUB_REPOSITORY", "darshildshah211/dds-posters") + "/main/"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


class Expired(Exception):
    pass


def call(method, path, token, params=None):
    params = dict(params or {})
    params["access_token"] = token
    url = G + path
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=90) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        if e.code == 401 or '"code":190' in body.replace(" ", ""):
            raise Expired(body)
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {body}")


def publish(token, item):
    me = call("GET", "/me", token, {"fields": "user_id,username"})
    uid = me.get("user_id") or me["id"]
    kind = item["type"].upper()
    url = RAW + item["media"]
    p = {}
    if kind == "POST":
        p = {"image_url": url, "caption": item.get("caption", "")}
    elif kind == "STORY":
        p = {"image_url": url, "media_type": "STORIES"}
    elif kind == "REEL":
        p = {"video_url": url, "media_type": "REELS", "caption": item.get("caption", "")}
    else:
        raise RuntimeError("unknown type " + kind)
    cid = call("POST", f"/{uid}/media", token, p)["id"]
    for _ in range(40):  # wait for processing (videos take longer)
        st = call("GET", f"/{cid}", token, {"fields": "status_code"}).get("status_code")
        if st == "FINISHED":
            break
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError("container status " + st)
        time.sleep(5)
    else:
        raise RuntimeError("container not ready in time")
    return call("POST", f"/{uid}/media_publish", token, {"creation_id": cid})["id"]


def main():
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    if "--check" in sys.argv:
        if not token:
            print("No INSTAGRAM_ACCESS_TOKEN secret found.")
            return 1
        try:
            me = call("GET", "/me", token, {"fields": "user_id,username,account_type"})
        except Expired:
            print("Instagram login has expired. Please generate a new token.")
            return 2
        print("Instagram login works. Connected as:", me)
        return 0
    if not token:
        print("No INSTAGRAM_ACCESS_TOKEN secret yet; nothing to do.")
        return 0
    now = dt.datetime.now(dt.timezone.utc)
    rc = 0
    for f in sorted(glob.glob(f"{QDIR}/*.json")):
        item = json.load(open(f))
        when = dt.datetime.fromisoformat(item["publish_at"])
        if when.tzinfo is None:
            when = when.replace(tzinfo=IST)
        if when > now:
            continue
        late = (now - when).total_seconds() / 3600
        if late > item.get("max_late_hours", 6):
            item["skipped_reason"] = f"{late:.1f}h late"
            json.dump(item, open(f, "w"), ensure_ascii=False, indent=2)
            shutil.move(f, f"{QDIR}/skipped/" + os.path.basename(f))
            print("SKIPPED (too late):", f)
            continue
        try:
            mid = publish(token, item)
        except Expired as e:
            print("Login expired:", e)
            return 2
        except Exception as e:  # leave in queue, retry next run until too late
            print("FAILED:", f, e)
            rc = rc or 0
            continue
        item["posted_id"] = mid
        item["posted_at"] = now.isoformat()
        json.dump(item, open(f, "w"), ensure_ascii=False, indent=2)
        shutil.move(f, f"{QDIR}/done/" + os.path.basename(f))
        print("POSTED:", f, mid)
    return rc


sys.exit(main())
