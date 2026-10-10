"""Publish due LinkedIn posts from linkedin/queue/*.json using LinkedIn's official (free) API.

Run by GitHub Actions every 15 minutes. Uses only the Python standard library.

Queue file (linkedin/queue/<name>.json):
  {"publish_at": "2026-10-10T19:00:00+05:30",   # when to publish (ISO, with offset)
   "max_late_hours": 12,                          # skip instead of posting if later than this
   "image": "linkedin/2026-10-10-edu.png",        # path inside the repo (optional)
   "alt": "short description of the image",       # optional
   "text": "caption ..."}

After posting, the file moves to linkedin/queue/done/ (with the LinkedIn post id added).
Too-late files move to linkedin/queue/skipped/.
Exit code 2 = login expired (GitHub then emails the owner to re-login).
"""
import datetime as dt
import glob
import json
import mimetypes
import os
import shutil
import sys
import urllib.error
import urllib.request

API = "https://api.linkedin.com"
VERSION = os.environ.get("LINKEDIN_VERSION", "202604")
QDIR = "linkedin/queue"
RESERVED = set("\\|{}@[]()<>*_~")  # '#' left alone so hashtags work


class Expired(Exception):
    pass


def escape(text):
    """LinkedIn 'little text' format: reserved characters must be backslash-escaped,
    otherwise LinkedIn silently truncates the post at the first '(' etc."""
    return "".join("\\" + c if c in RESERVED else c for c in text)


def call(method, url, token, body=None, data=None, headers=None, want_headers=False):
    h = {"Authorization": "Bearer " + token}
    if url.startswith(API + "/rest/"):
        h["LinkedIn-Version"] = VERSION
        h["X-Restli-Protocol-Version"] = "2.0.0"
    if headers:
        h.update(headers)
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            js = json.loads(raw) if raw and raw[:1] in b"{[" else {}
            return (js, dict(r.headers)) if want_headers else js
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")[:500]
        if e.code == 401:
            raise Expired(msg)
        raise RuntimeError(f"{method} {url} -> HTTP {e.code}: {msg}")


def whoami(token):
    info = call("GET", API + "/v2/userinfo", token)
    return "urn:li:person:" + info["sub"], info.get("name", "")


def upload_image(token, owner, path):
    init = call("POST", API + "/rest/images?action=initializeUpload", token,
                body={"initializeUploadRequest": {"owner": owner}})["value"]
    ctype = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        call("PUT", init["uploadUrl"], token, data=f.read(), headers={"Content-Type": ctype})
    return init["image"]


def publish(token, author, item):
    post = {
        "author": author,
        "commentary": escape(item["text"]),
        "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [],
                         "thirdPartyDistributionChannels": []},
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    if item.get("image"):
        urn = upload_image(token, author, item["image"])
        post["content"] = {"media": {"id": urn, "altText": item.get("alt", "")[:300]}}
    _, hdr = call("POST", API + "/rest/posts", token, body=post, want_headers=True)
    return hdr.get("x-restli-id") or hdr.get("X-RestLi-Id", "")


def main():
    dry = "--dry-run" in sys.argv
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    if "--check" in sys.argv:
        if not token:
            print("No LINKEDIN_ACCESS_TOKEN secret found.")
            return 1
        try:
            urn, name = whoami(token)
        except Expired:
            print("LinkedIn login has expired. Please generate a new access token.")
            return 2
        print(f"LinkedIn login works. Connected as: {name} ({urn})")
        return 0

    now = dt.datetime.now(dt.timezone.utc)
    due = []
    for f in sorted(glob.glob(f"{QDIR}/*.json")):
        item = json.load(open(f))
        when = dt.datetime.fromisoformat(item["publish_at"])
        if when.tzinfo is None:
            when = when.replace(tzinfo=dt.timezone(dt.timedelta(hours=5, minutes=30)))
        if when > now:
            continue
        late = (now - when).total_seconds() / 3600
        if late > float(item.get("max_late_hours", 12)):
            print(f"SKIP (too late by {late:.1f}h): {f}")
            if not dry:
                shutil.move(f, f"{QDIR}/skipped/" + os.path.basename(f))
            continue
        due.append((f, item))

    if not due:
        print("Nothing due.")
        return 0

    if dry:
        for f, item in due:
            print(f"WOULD POST {f}\n--- escaped text ---\n{escape(item['text'])}\n--- image: {item.get('image')}")
        return 0

    if not token:
        print("No LINKEDIN_ACCESS_TOKEN secret set.")
        return 1
    try:
        author, name = whoami(token)
    except Expired:
        print("LinkedIn login has expired. Generate a new access token and update the secret.")
        return 2

    rc = 0
    for f, item in due:
        try:
            pid = publish(token, author, item)
        except Expired:
            print("LinkedIn login expired while posting.")
            return 2
        except Exception as e:  # keep going with the other posts
            print(f"FAILED {f}: {e}")
            rc = 1
            continue
        item["posted_id"] = pid
        item["posted_at"] = now.isoformat()
        json.dump(item, open(f, "w"), indent=2, ensure_ascii=False)
        shutil.move(f, f"{QDIR}/done/" + os.path.basename(f))
        print(f"POSTED {f} -> {pid}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
