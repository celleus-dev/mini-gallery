#!/usr/bin/env python3
"""Apply an edits file downloaded from the site's lasso editor (edit.html).

    python3 tools/apply_edits.py <edits.json> --preview review.png --dry-run
        -> only writes the review image, changes nothing
    python3 tools/apply_edits.py <edits.json> --preview review.png
        -> applies it: updates the mini's masks and data/minis.json, and saves
           the edits file in tools/inputs/<mini-id>/edits/ so process_mini.py
           re-applies it on any future re-run

Works on the masks already on the site, so the original photo isn't needed.
Applying edits clears the mini's "verified for training" mark: the labels
changed, so Dan confirms them again before tools/learn.py --verify.
"""

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

import edits
import paintlib
from process_mini import review_image, save_mask, slug

ROOT = paintlib.ROOT


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edits_file")
    ap.add_argument("--preview", help="where to write the review image (original | paint map | unmatched)")
    ap.add_argument("--dry-run", action="store_true", help="only write the review image")
    args = ap.parse_args()

    doc = edits.load(args.edits_file)
    data_path = ROOT / "data" / "minis.json"
    data = json.loads(data_path.read_text())
    mini = next((m for m in data["minis"] if m["id"] == doc["mini"]), None)
    if not mini:
        sys.exit(f"no mini with id {doc['mini']!r} on the site")

    img = Image.open(ROOT / mini["photo"]).convert("RGB")
    w, h = img.size
    names = [p["name"] for p in mini["paints"]]
    masks = {p["name"]: np.array(Image.open(ROOT / p["mask"]).convert("RGBA"))[..., 3] > 127
             for p in mini["paints"] if p.get("mask")}
    before = {n: int(m.sum()) for n, m in masks.items()}
    original = {n: m.copy() for n, m in masks.items()}

    masks, notes = edits.apply(masks, names, [doc], w, h)
    for n in notes:
        print("note:", n)
    if any(n.startswith("skipped edits") for n in notes):
        sys.exit("nothing applied")

    fg_path = ROOT / "dataset" / mini["id"] / "fg.png"
    fg = (np.array(Image.open(fg_path).convert("L").resize((w, h), Image.NEAREST)) > 127) if fg_path.exists() \
        else np.zeros((h, w), bool)
    painted = np.any(list(masks.values()), axis=0)
    fg |= painted
    unmatched = fg & ~painted

    print(f"{mini['id']}: {len(doc['edits'])} lasso edit(s)")
    for n in names:
        b, a = before.get(n, 0), int(masks[n].sum())
        if a != b:
            print(f"  {n:22s} {b:7d} -> {a:7d} px")

    if args.preview:
        review_image(img, fg, masks, unmatched, mini["paints"], args.preview)
    if args.dry_run:
        print("dry run: nothing changed")
        return

    out_dir = ROOT / "minis" / mini["id"]
    fg_px = max(1, int(fg.sum()))
    for p in mini["paints"]:
        m = masks[p["name"]]
        fname = f"mask-{slug(p['name'])}.png"
        if p["name"] in original and np.array_equal(m, original[p["name"]]):
            p["coverage"] = round(100.0 * m.sum() / fg_px, 1)
            continue  # untouched paint: leave its mask file exactly as it was
        if m.any():
            save_mask(m, out_dir / fname)
            p["mask"] = f"minis/{mini['id']}/{fname}"
            p["coverage"] = round(100.0 * m.sum() / fg_px, 1)
        else:
            (out_dir / fname).unlink(missing_ok=True)
            p.pop("mask", None)
            p.pop("coverage", None)
    mini["updated"] = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
    was_verified = bool(mini.pop("verified", None))
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    if was_verified:
        # take it out of the training data until Dan confirms the new labels
        subprocess.run([sys.executable, str(ROOT / "tools" / "learn.py")], check=True, stdout=subprocess.DEVNULL)
        print("cleared 'verified for training' and rebuilt the training data without it --",
              "once Dan confirms: python3 tools/learn.py --verify", mini["id"])

    fg_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((fg * 255).astype(np.uint8)).save(fg_path)
    keep = ROOT / "tools" / "inputs" / mini["id"] / "edits"
    keep.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    shutil.copyfile(args.edits_file, keep / f"{stamp}.json")
    print(f"saved edits to {keep.relative_to(ROOT)}/{stamp}.json")


if __name__ == "__main__":
    main()
