#!/usr/bin/env python3
"""Re-crop an existing mini with more space around it, keeping its paint areas.

Paint regions, samples and the fg mask were drawn on the old (tight) photo.
This works out where every point sits in the original photo(s), then where
that point lands in the new padded crop, and rewrites paints.json, fg_mask.png
and hints.json (if present) to match. Then run process_mini.py as usual.

Spec (JSON):
  {"id": "6-siege-flores",
   "old_size": [742, 1383],          # size of the current minis/<id>/photo.jpg
   "views": [{"photo": "a.jpg", "crop": [l, t, r, b]}, ...],  # left to right
   "pad": 0.15,
   "out_photo": "composite.jpg"}     # padded photo (side by side if several views)

Old layout: the views' crops pasted left to right, scaled to old_size.
New layout: the same, with each crop grown by `pad` of its size per side
(clamped to the photo), scaled so the longest side is at most 1600.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

MAX_SIDE = 1600


def padded(crop, size, pad):
    l, t, r, b = crop
    dx, dy = round((r - l) * pad), round((b - t) * pad)
    return [max(0, l - dx), max(0, t - dy), min(size[0], r + dx), min(size[1], b + dy)]


def layout(crops):
    offs, x = [], 0
    for c in crops:
        offs.append(x)
        x += c[2] - c[0]
    return offs, x, max(c[3] - c[1] for c in crops)


def main(spec_path):
    spec = json.load(open(spec_path))
    root = Path(__file__).resolve().parent.parent
    inp = root / "tools" / "inputs" / spec["id"]
    photos = [ImageOps.exif_transpose(Image.open(v["photo"])).convert("RGB") for v in spec["views"]]
    old = [v["crop"] for v in spec["views"]]
    new = [padded(c, p.size, spec["pad"]) for c, p in zip(old, photos)]
    o_off, o_w, o_h = layout(old)
    n_off, n_w, n_h = layout(new)
    s_old = spec["old_size"][0] / o_w
    s_new = min(1.0, MAX_SIDE / max(n_w, n_h))

    def view_of(x):
        X = x / s_old
        for i in range(len(old) - 1, -1, -1):
            if X >= o_off[i]:
                return i
        return 0

    def pt(x, y, i=None):
        i = view_of(x) if i is None else i
        ox = x / s_old - o_off[i] + old[i][0]
        oy = y / s_old + old[i][1]
        return [round((ox - new[i][0] + n_off[i]) * s_new), round((oy - new[i][1]) * s_new)]

    k = s_new / s_old

    def shape(r):
        if isinstance(r, dict) and "ellipse" in r:
            cx, cy, rx, ry = r["ellipse"]
            return {**r, "ellipse": pt(cx, cy) + [round(rx * k), round(ry * k)]}
        if isinstance(r, dict) and "polygon" in r:
            xs = [p[0] for p in r["polygon"]]
            i = view_of(sum(xs) / len(xs))
            return {**r, "polygon": [pt(x, y, i) for x, y in r["polygon"]]}
        x0, y0, x1, y1 = r
        i = view_of((x0 + x1) / 2)
        return pt(x0, y0, i) + pt(x1, y1, i)

    pj = inp / "paints.json"
    paints = json.load(open(pj))
    for p in paints:
        if "regions" in p:
            p["regions"] = [shape(r) for r in p["regions"]]
        if "exclude_regions" in p:
            p["exclude_regions"] = [shape(r) for r in p["exclude_regions"]]
        if "samples" in p:
            p["samples"] = [pt(x, y) for x, y in p["samples"]]
    pj.write_text(json.dumps(paints, indent=2) + "\n")

    # New padded photo
    canvas = Image.new("RGB", (n_w, n_h))
    for i, (p, c) in enumerate(zip(photos, new)):
        canvas.paste(p.crop(c), (n_off[i], 0))
    out_w, out_h = round(n_w * s_new), round(n_h * s_new)
    if len(new) > 1 or spec.get("out_photo"):
        canvas.resize((out_w, out_h), Image.LANCZOS).save(spec["out_photo"], quality=92)

    # Foreground mask: move each view's part of the old mask into place
    fm = inp / "fg_mask.png"
    if fm.exists():
        m = Image.open(fm).convert("L")
        nm = Image.new("L", (out_w, out_h), 0)
        for i in range(len(old)):
            x0, x1 = round(o_off[i] * s_old), round((o_off[i] + old[i][2] - old[i][0]) * s_old)
            part = m.crop((x0, 0, x1, m.height))
            part = part.resize((max(1, round(part.width * k)), max(1, round(part.height * k))), Image.NEAREST)
            nm.paste(part, tuple(pt(x0, 0, i)))
        nm.save(fm)

    # GrabCut hints (half-scale coordinates), so the mask can be remade
    hj = inp / "hints.json"
    if hj.exists():
        H = json.load(open(hj))
        h2 = lambda x, y: [round(v / 2) for v in pt(x * 2, y * 2)]
        if "rects" in H:
            R = []
            for x, y, w, h in H["rects"]:
                a = h2(x, y); b = h2(x + w, y + h)
                R.append([a[0], a[1], b[0] - a[0], b[1] - a[1]])
            H["rects"] = R
        for key in ("fg", "bg"):
            if key in H:
                H[key] = [[h2(x, y) for x, y in s] for s in H[key]]
        hj.write_text(json.dumps(H) + "\n")

    print(json.dumps({"new_crops": new, "new_size": [out_w, out_h], "scale": s_new}))


if __name__ == "__main__":
    main(sys.argv[1])
