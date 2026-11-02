#!/usr/bin/env python3
"""Turn a side-by-side two-view mini into a single view, keeping its paint areas.

Takes one panel of tools/inputs/<id>/composite.jpg (x0..x1 in composite pixels),
re-cuts that panel from the original photo at full resolution, and rewrites the
mask and paints so they line up with it. Shapes and samples that belong to the
other panel are dropped. Then run process_mini.py as usual on the new files.

    python3 tools/single_view.py <id> <x0> <x1> <photo> <l,t,r,b> <out_prefix>

<photo> and <l,t,r,b>: the original photo and the crop of it that the panel shows
(the panel is that crop, scaled to the panel's size in the composite).
Writes <out_prefix>.jpg, <out_prefix>_fg_mask.png and <out_prefix>_paints.json
in tools/inputs/<id>/.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

MAX_SIDE = 1600


def main(mid, x0, x1, photo, box, prefix):
    root = Path(__file__).resolve().parent.parent
    inp = root / "tools" / "inputs" / mid
    comp = Image.open(inp / "composite.jpg")
    H = comp.height
    l, t, r, b = box
    src = ImageOps.exif_transpose(Image.open(inp / photo)).convert("RGB").crop((l, t, r, b))
    k = src.width / (x1 - x0)                       # composite px -> new photo px
    s = min(1.0, MAX_SIDE / max(src.size))
    if s < 1:
        src = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
    k *= s
    src.save(inp / f"{prefix}.jpg", quality=95)

    mask = Image.open(inp / "fg_mask.png").convert("L").crop((x0, 0, x1, H))
    mask.resize(src.size, Image.NEAREST).save(inp / f"{prefix}_fg_mask.png")

    inside = lambda x: x0 <= x < x1
    P = lambda x, y: [round((x - x0) * k), round(y * k)]

    def region(rg):
        if isinstance(rg, dict) and "ellipse" in rg:
            cx, cy, rx, ry = rg["ellipse"]
            return {"ellipse": P(cx, cy) + [round(rx * k), round(ry * k)]} if inside(cx) else None
        if isinstance(rg, dict) and "polygon" in rg:
            pts = rg["polygon"]
            cx = sum(p[0] for p in pts) / len(pts)
            return {"polygon": [P(*p) for p in pts]} if inside(cx) else None
        L, T, R, B = rg
        return P(L, T) + P(R, B) if inside((L + R) / 2) else None

    paints = json.load(open(inp / "paints.json"))
    for p in paints:
        if "samples" in p:
            p["samples"] = [P(x, y) for x, y in p["samples"] if inside(x)]
        for key in ("regions", "exclude_regions"):
            if key in p:
                p[key] = [q for q in (region(rg) for rg in p[key]) if q is not None]
                if key == "regions" and not p[key]:
                    raise SystemExit(f"{p['name']}: no area left in this panel")
    json.dump(paints, open(inp / f"{prefix}_paints.json", "w"), indent=1)
    print(f"{mid}: {src.size[0]}x{src.size[1]}, scale {k:.3f}")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], int(a[1]), int(a[2]), a[3], [int(v) for v in a[4].split(",")], a[5])
