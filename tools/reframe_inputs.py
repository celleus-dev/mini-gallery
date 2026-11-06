"""Move a mini's hand-placed paint areas (paints.json) and fg mask to a new framing
(different --pad and/or --crop), so they still line up with the photo.

Coordinates in paints.json are on the framed photo that process_mini.py makes
(crop + pad, then shrunk so the long side is at most 1600px). This converts them.

python3 tools/reframe_inputs.py --photo P [--paints J] [--fg-mask M] \
    --old-crop l,t,r,b --old-pad 0.15 --new-crop l,t,r,b --new-pad 0.35
Writes the files in place.
"""
import argparse, json
from PIL import Image, ImageOps

MAX_SIDE = 1600  # same as process_mini.py


def frame(size, crop, pad):
    W, H = size
    l, t, r, b = crop
    dx, dy = round((r - l) * pad), round((b - t) * pad)
    box = (max(0, l - dx), max(0, t - dy), min(W, r + dx), min(H, b + dy))
    w, h = box[2] - box[0], box[3] - box[1]
    s = min(1.0, MAX_SIDE / max(w, h))
    return box, s, (round(w * s), round(h * s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", required=True)
    ap.add_argument("--paints", help="omit to move only the fg mask")
    ap.add_argument("--fg-mask")
    ap.add_argument("--old-crop", required=True)
    ap.add_argument("--old-pad", type=float, required=True)
    ap.add_argument("--new-crop", required=True)
    ap.add_argument("--new-pad", type=float, required=True)
    a = ap.parse_args()
    size = ImageOps.exif_transpose(Image.open(a.photo)).size
    ob, os_, osz = frame(size, [int(v) for v in a.old_crop.split(",")], a.old_pad)
    nb, ns, nsz = frame(size, [int(v) for v in a.new_crop.split(",")], a.new_pad)

    def pt(x, y):  # old framed photo -> original photo -> new framed photo
        X, Y = x / os_ + ob[0], y / os_ + ob[1]
        return [round((X - nb[0]) * ns), round((Y - nb[1]) * ns)]

    k = ns / os_

    def region(r):
        if isinstance(r, dict) and "ellipse" in r:
            cx, cy, rx, ry = r["ellipse"]
            return {**r, "ellipse": pt(cx, cy) + [round(rx * k), round(ry * k)]}
        if isinstance(r, dict) and "polygon" in r:
            return {**r, "polygon": [pt(x, y) for x, y in r["polygon"]]}
        x0, y0, x1, y1 = r
        return pt(x0, y0) + pt(x1, y1)

    paints = json.load(open(a.paints)) if a.paints else []
    for p in paints:
        if "samples" in p:
            p["samples"] = [pt(x, y) for x, y in p["samples"]]
        for key in ("regions", "exclude_regions"):
            if key in p:
                p[key] = [region(r) for r in p[key]]
    if a.paints:
        json.dump(paints, open(a.paints, "w"), indent=1)

    if a.fg_mask:
        m = Image.open(a.fg_mask).convert("L").resize(osz, Image.NEAREST)
        full = Image.new("L", size, 0)
        full.paste(m.resize((ob[2] - ob[0], ob[3] - ob[1]), Image.NEAREST), ob[:2])
        full.crop(nb).resize(nsz, Image.NEAREST).save(a.fg_mask)
    print(f"old frame {ob} x{os_:.3f} -> new frame {nb} x{ns:.3f} {nsz}")


if __name__ == "__main__":
    main()
