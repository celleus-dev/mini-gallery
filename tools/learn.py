#!/usr/bin/env python3
"""Learn what each paint looks like from the minis already on the site.

Run after a mini has been reviewed and approved. Rebuilds everything below
from data/minis.json, so it's safe to run any number of times:

  dataset/<mini-id>/image.jpg     the photo
  dataset/<mini-id>/labels.png    per-pixel labels: 0 = background,
                                  1 = on the mini but not matched to a paint,
                                  2+ = a paint (see labels.json)
  dataset/<mini-id>/labels.json   label number -> paint
  library/observed/<paint>.json   colour clusters this paint showed on each mini
  library/swatches/<paint>.png    published colour + what it looked like on each mini
  library/index.json              every paint used so far, and on which minis

The dataset/ folder is the training data for a future automatic model: photo
+ per-pixel answer, for paints Dan has confirmed.

Only minis marked verified are used -- being good enough for the website is
not the same as being trustworthy enough to learn from. Mark one with:

  python3 tools/learn.py --verify <mini-id>

Re-processing a mini with process_mini.py clears its verified mark, so it has
to be reviewed again. Label edges (where two paints meet, or the mini meets
the background) are set to 255 = "ignore", since that's where labels are
least reliable.
"""

import argparse
import json
import shutil

from scipy import ndimage as ndi

import numpy as np
from PIL import Image, ImageDraw
from scipy.cluster.vq import kmeans2
from skimage import color

import paintlib as pl

ROOT = pl.ROOT
MAX_CLUSTERS = 4
TILE_H = 160
EDGE = 2  # pixels on each side of a boundary that are left out of training


def load_mask(path):
    a = np.array(Image.open(ROOT / path).convert("RGBA"))[..., 3]
    return a > 127


def clusters(lab_pixels, rng):
    """A few representative colours (Lab) with their share of the pixels."""
    if len(lab_pixels) > 20000:
        lab_pixels = lab_pixels[rng.choice(len(lab_pixels), 20000, replace=False)]
    k = int(min(MAX_CLUSTERS, max(1, len(lab_pixels) // 200)))
    cent, lbl = kmeans2(lab_pixels, k, seed=1, minit="++")
    out = []
    for i, c in enumerate(cent):
        w = float((lbl == i).mean())
        if w < 0.03:
            continue
        rgb = (color.lab2rgb(c[None, None, :])[0, 0] * 255).round().astype(int)
        out.append({"lab": [round(float(v), 2) for v in c], "hex": "#%02x%02x%02x" % tuple(rgb), "weight": round(w, 3)})
    return sorted(out, key=lambda c: -c["weight"])


def tile(photo, mask):
    """Crop around the paint, with everything that isn't this paint darkened."""
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = photo[y0:y1, x0:x1].astype(float)
    m = mask[y0:y1, x0:x1]
    crop[~m] = crop[~m] * 0.15 + 20
    im = Image.fromarray(crop.clip(0, 255).astype(np.uint8))
    scale = TILE_H / im.height
    return im.resize((max(1, round(im.width * scale)), TILE_H), Image.LANCZOS)


def swatch_sheet(info, per_mini, path):
    pad, chip = 10, 28
    tiles = [(m, tile(ph, mk), cl) for m, ph, mk, cl in per_mini]
    width = max([340] + [t.width + 2 * pad for _, t, _ in tiles])
    height = 70 + sum(TILE_H + chip + 3 * pad + 14 for _ in tiles)
    sheet = Image.new("RGB", (width, height), (24, 22, 20))
    d = ImageDraw.Draw(sheet)
    d.rectangle([pad, pad, pad + 50, pad + 50], fill=info["hex"], outline=(90, 90, 90))
    d.text((pad + 62, pad + 6), info["name"], fill=(236, 228, 216))
    d.text((pad + 62, pad + 24), f"{info.get('brand', '')}  published {info['hex']}", fill=(168, 156, 139))
    y = 70
    for mini_id, t, cl in tiles:
        d.text((pad, y), f"on {mini_id}", fill=(168, 156, 139))
        y += 14
        sheet.paste(t, (pad, y))
        y += TILE_H + pad
        x = pad
        for c in cl:
            w = max(chip, int(c["weight"] * (width - 2 * pad)))
            d.rectangle([x, y, x + w - 2, y + chip], fill=c["hex"])
            x += w
        y += chip + 2 * pad
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", metavar="MINI_ID", help="mark a mini as verified for training, then rebuild")
    ap.add_argument("--unverify", metavar="MINI_ID", help="take a mini back out of the training data, then rebuild")
    args = ap.parse_args()

    ranges = pl.load_ranges()
    data_path = ROOT / "data" / "minis.json"
    data = json.loads(data_path.read_text())
    rng = np.random.default_rng(0)

    for mid, value in ((args.verify, True), (args.unverify, False)):
        if mid:
            hit = [m for m in data["minis"] if m["id"] == mid]
            if not hit:
                raise SystemExit(f"no mini with id {mid!r}")
            if value:
                hit[0]["verified"] = True
            else:
                hit[0].pop("verified", None)
            data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    observed = {}   # key -> {"info":..., "minis": [...]}
    swatch_src = {}  # key -> [(mini_id, photo, mask, clusters)]

    ds_root = ROOT / "dataset"
    verified = [m for m in data.get("minis", []) if m.get("verified")]
    for stale in (ds_root.iterdir() if ds_root.exists() else []):
        if stale.is_dir() and stale.name not in {m["id"] for m in verified}:
            for f in ("image.jpg", "labels.png", "labels.json"):
                (stale / f).unlink(missing_ok=True)  # keep fg.png: it's an input, not output

    for mini in verified:
        mid = mini["id"]
        photo = np.array(Image.open(ROOT / mini["photo"]).convert("RGB"))
        lab = color.rgb2lab(photo / 255.0)
        mapped = [p for p in mini.get("paints", []) if p.get("mask")]
        masks = {p["name"]: load_mask(p["mask"]) for p in mapped}

        ds = ROOT / "dataset" / mid
        ds.mkdir(parents=True, exist_ok=True)
        fg_path = ds / "fg.png"
        if fg_path.exists():
            fg = np.array(Image.open(fg_path).convert("L").resize(photo.shape[1::-1], Image.NEAREST)) > 127
        else:
            fg = np.any(list(masks.values()), axis=0) if masks else np.zeros(photo.shape[:2], bool)

        # Per-pixel labels for training
        labels = np.zeros(photo.shape[:2], np.uint8)
        labels[fg] = 1
        legend = {"0": "background", "1": "mini, unmatched"}
        palette = [0, 0, 0, 128, 128, 128]
        for i, p in enumerate(mapped, start=2):
            labels[masks[p["name"]] & fg] = i
            key = pl.paint_key(p, ranges)
            legend[str(i)] = {"key": key, "name": p["name"], "brand": p.get("brand", ""), "hex": p["hex"]}
            palette += list(int(p["hex"][j:j + 2], 16) for j in (1, 3, 5))
        # Ignore a thin band wherever the label changes
        size = 2 * EDGE + 1
        edge = ndi.maximum_filter(labels, size) != ndi.minimum_filter(labels, size)
        labels[edge] = 255
        legend["255"] = "ignore (edge between labels)"
        palette += [0] * (3 * 255 - len(palette)) + [255, 0, 255]
        lab_img = Image.fromarray(labels, "P")
        lab_img.putpalette(palette + [0] * (768 - len(palette)))
        lab_img.save(ds / "labels.png")
        shutil.copyfile(ROOT / mini["photo"], ds / "image.jpg")
        (ds / "labels.json").write_text(json.dumps({
            "mini": mid, "name": mini["name"], "game": mini.get("game", ""),
            "status": "verified",  # Dan reviewed and confirmed these labels
            "labels": legend,
        }, indent=2) + "\n")

        # What each paint looked like on this mini
        for i, p in enumerate(mapped, start=2):
            m = labels == i  # paint area with edges already trimmed
            if m.sum() < 50:
                continue
            key = pl.paint_key(p, ranges)
            lib = pl.lookup(p["name"], p.get("brand", ""), ranges)
            info = {"key": key, "name": p["name"], "brand": p.get("brand", ""),
                    "hex": lib["hex"] if lib else p["hex"],
                    "in_reference_library": bool(lib)}
            cl = clusters(lab[m], rng)
            entry = observed.setdefault(key, {"info": info, "minis": []})
            entry["minis"].append({"mini": mid, "pixels": int(m.sum()), "clusters": cl})
            swatch_src.setdefault(key, []).append((mid, photo, m, cl))

    out_dir = ROOT / "library" / "observed"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    sw_dir = ROOT / "library" / "swatches"
    if sw_dir.exists():
        shutil.rmtree(sw_dir)

    index = {}
    for key, entry in sorted(observed.items()):
        pl.observed_path(key).write_text(json.dumps({**entry["info"], "minis": entry["minis"]}, indent=1) + "\n")
        sw = sw_dir / (key.replace("/", "__") + ".png")
        swatch_sheet(entry["info"], swatch_src[key], sw)
        index[key] = {**entry["info"], "minis": [m["mini"] for m in entry["minis"]],
                      "swatch": str(sw.relative_to(ROOT))}
    (ROOT / "library" / "index.json").write_text(json.dumps(index, indent=1) + "\n")

    print(f"{len(verified)} of {len(data.get('minis', []))} minis verified for training, {len(index)} paints learned")
    for key, v in index.items():
        print(f"  {v['name']:20s} on {len(v['minis'])} mini(s)" + ("" if v["in_reference_library"] else "  (not in reference library)"))


if __name__ == "__main__":
    main()
