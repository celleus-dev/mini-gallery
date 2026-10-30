#!/usr/bin/env python3
"""Keep the Supabase database in step with this repo.

    python3 tools/sync_supabase.py push
        -> uploads every mini's photo and masks to the "gallery" storage bucket
           (only minis whose "updated" stamp changed), writes data/minis.json and
           data/games.json into the minis/games tables, and removes minis that
           are no longer in the repo
    python3 tools/sync_supabase.py pull-edits
        -> applies lasso edits saved from the editor (edits table, status
           "pending") with tools/apply_edits.py, then marks them applied/skipped.
           Commit and push afterwards, then run "push".

Needs SUPABASE_SECRET_KEY in the environment (the project's secret key; never
commit it). The project URL is read from assets/config.js, or SUPABASE_URL.
Runs automatically from .github/workflows/supabase-sync.yml.
Uses only the standard library, so "push" needs no installs.
"""

import argparse
import datetime as dt
import json
import mimetypes
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUCKET = "gallery"


def config():
    url = os.environ.get("SUPABASE_URL", "").strip()
    if not url:
        m = re.search(r'supabaseUrl:\s*"([^"]*)"', (ROOT / "assets" / "config.js").read_text())
        url = m.group(1) if m else ""
    key = os.environ.get("SUPABASE_SECRET_KEY", "").strip()
    if not url or not key:
        sys.exit("Supabase isn't set up: need the URL in assets/config.js and SUPABASE_SECRET_KEY")
    return url.rstrip("/"), key


class Supabase:
    def __init__(self, url, key):
        self.url = url
        self.headers = {"apikey": key}
        if not key.startswith("sb_"):  # legacy service_role key (a JWT) also goes in Authorization
            self.headers["Authorization"] = f"Bearer {key}"

    def call(self, method, path, body=None, headers=None, raw=False):
        h = dict(self.headers, **(headers or {}))
        data = body
        if body is not None and not raw:
            data = json.dumps(body).encode()
            h.setdefault("Content-Type", "application/json")
        req = urllib.request.Request(self.url + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                text = r.read().decode() or "null"
                return json.loads(text) if "json" in r.headers.get("Content-Type", "") else text
        except urllib.error.HTTPError as e:
            sys.exit(f"Supabase {method} {path}: {e.code} {e.read().decode()[:300]}")

    def upload(self, path, file):
        ctype = mimetypes.guess_type(str(file))[0] or "application/octet-stream"
        self.call("POST", f"/storage/v1/object/{BUCKET}/{urllib.parse.quote(path)}", file.read_bytes(),
                  {"Content-Type": ctype, "x-upsert": "true", "cache-control": "3600"}, raw=True)


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def mini_files(mini):
    files = [mini["photo"]] + [p["mask"] for p in mini.get("paints", []) if p.get("mask")]
    return [f for f in files if f]


def push(sb):
    minis = json.loads((ROOT / "data" / "minis.json").read_text()).get("minis", [])
    games_path = ROOT / "data" / "games.json"
    games = json.loads(games_path.read_text()).get("games", []) if games_path.exists() else []

    existing = {r["id"]: r["data"].get("updated")
                for r in sb.call("GET", "/rest/v1/minis?select=id,data")}

    uploaded = 0
    for m in minis:
        if existing.get(m["id"]) == m.get("updated") and m.get("updated"):
            continue
        for rel in mini_files(m):
            f = ROOT / rel
            if not f.exists():
                sys.exit(f"{m['id']}: missing file {rel}")
            sb.upload(rel, f)
            uploaded += 1
        print(f"uploaded {m['id']}")

    rows = [{"id": m["id"], "name": m["name"], "game": m.get("game"), "date": m.get("date"),
             "data": m, "updated_at": now()} for m in minis]
    if rows:
        sb.call("POST", "/rest/v1/minis?on_conflict=id", rows,
                {"Prefer": "resolution=merge-duplicates,return=minimal"})
    gone = [i for i in existing if i not in {m["id"] for m in minis}]
    for i in gone:
        sb.call("DELETE", f"/rest/v1/minis?id=eq.{urllib.parse.quote(i)}", headers={"Prefer": "return=minimal"})
        print(f"removed {i}")

    if games:
        sb.call("POST", "/rest/v1/games?on_conflict=name", [{"name": g["name"], "data": g} for g in games],
                {"Prefer": "resolution=merge-duplicates,return=minimal"})
    names = [g["name"] for g in games]
    for r in sb.call("GET", "/rest/v1/games?select=name"):
        if r["name"] not in names:
            sb.call("DELETE", f"/rest/v1/games?name=eq.{urllib.parse.quote(r['name'])}",
                    headers={"Prefer": "return=minimal"})

    print(f"synced {len(minis)} minis, {len(games)} games, {uploaded} files uploaded")


def pull_edits(sb):
    pending = sb.call("GET", "/rest/v1/edits?status=eq.pending&select=id,mini_id,doc&order=id")
    if not pending:
        print("no pending edits")
        return
    tmp = Path(tempfile.mkdtemp())
    for e in pending:
        doc = e["doc"]
        doc["mini"] = e["mini_id"]
        f = tmp / f"{e['mini_id']}-edits-db{e['id']}.json"
        f.write_text(json.dumps(doc))
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "apply_edits.py"), str(f)],
                           cwd=ROOT, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip()
        status = "applied" if r.returncode == 0 else "skipped"
        print(f"edit {e['id']} ({e['mini_id']}): {status}\n{out}")
        sb.call("PATCH", f"/rest/v1/edits?id=eq.{e['id']}",
                {"status": status, "note": out[-1000:], "applied_at": now()},
                {"Prefer": "return=minimal"})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["push", "pull-edits"])
    args = ap.parse_args()
    sb = Supabase(*config())
    push(sb) if args.action == "push" else pull_edits(sb)


if __name__ == "__main__":
    main()
