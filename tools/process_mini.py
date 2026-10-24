#!/usr/bin/env python3
"""Add (or re-process) one painted miniature for the gallery.

Takes a photo and a list of paints, works out which parts of the mini match
each paint, and writes everything the website needs:

    minis/<id>/photo.jpg            resized photo
    minis/<id>/mask-<paint>.png     one transparency mask per highlighted paint
    data/minis.json                 entry added or replaced (matched by id)

It also writes a review image (original | paint map | unmatched areas) so the
result can be checked before it is committed.

Paints file (JSON list), one object per paint, in the order to display them:
    [
      {"name": "Mephiston Red", "brand": "Citadel", "role": "Base",
       "hex": "#9a1115", "source": "<where the colour value came from>"},
      {"name": "Nuln Oil", "brand": "Citadel", "role": "Wash",
       "hex": "#14100e", "highlight": false}
    ]
"hex" can be left out for any paint in library/ranges/ (looked up by name and
brand). Paints that have been on earlier minis also match using the shades
they showed there (library/observed/, built by tools/learn.py); turn that off
with --no-learned.

Optional per paint: "samples": [[x, y], ...] spots on the (cropped) photo
known to be that paint, so its shadow/recess tones match too;
"highlight": false (list it, but don't map it on the
photo -- useful for washes/glazes that only tint other colours) and
"threshold" (how loosely to match that paint; default from --threshold).

How matching works: colours are compared in CIELAB using the CIEDE2000
colour difference, with brightness weighted down (kL) so shadows and
highlights of the same paint still count as that paint. Each pixel on the
mini goes to its closest paint if it's within the threshold; anything else
stays unmatched rather than being forced onto a paint.

Example:
    python3 tools/process_mini.py --photo amy.jpg --paints amy_paints.json \
        --name "Amy" --game "Zombicide" --date 2026-10-24 \
        --preview /tmp/amy_review.png
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi
from skimage import color

import paintlib

ROOT = Path(__file__).resolve().parent.parent
MAX_SIDE = 1600


def slug(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"bad hex colour: {h!r}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_photo(path, crop=None):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img).convert("RGB")
    if crop:
        img = img.crop(crop)
    w, h = img.size
    scale = min(1.0, MAX_SIDE / max(w, h))
    if scale < 1.0:
        img = img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    return img


def largest_component(mask):
    lab, n = ndi.label(mask)
    if n == 0:
        return mask
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    return lab == (int(np.argmax(sizes)) + 1)


def foreground(img, lab_img, mode, bg_threshold):
    """True where the miniature is, False for the background."""
    if mode == "rembg":
        try:
            from rembg import remove  # optional dependency
        except ImportError:
            sys.exit("rembg isn't installed; run without --background rembg, or pip install rembg")
        cut = remove(img)  # RGBA
        fg = np.array(cut)[:, :, 3] > 128
    elif mode == "none":
        return np.ones(lab_img.shape[:2], bool)
    elif mode == "grabcut":
        # For busy backgrounds: crop tightly around the mini first (--crop), then
        # OpenCV's GrabCut separates the mini from whatever surrounds it.
        import cv2  # optional dependency (opencv-python-headless)
        bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        h, w = bgr.shape[:2]
        mx, my = max(2, w // 50), max(2, h // 50)
        gc = np.zeros((h, w), np.uint8)
        bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        cv2.grabCut(bgr, gc, (mx, my, w - 2 * mx, h - 2 * my), bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)
        fg = (gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)
    else:
        # "border": assume the photo's edges are background (plain backdrop).
        border = np.concatenate([
            lab_img[:4].reshape(-1, 3), lab_img[-4:].reshape(-1, 3),
            lab_img[:, :4].reshape(-1, 3), lab_img[:, -4:].reshape(-1, 3),
        ])
        bg_lab = np.median(border, axis=0)
        dist = color.deltaE_ciede2000(lab_img, bg_lab[None, None, :])
        fg = dist > bg_threshold
    fg = ndi.binary_opening(fg, iterations=2)
    fg = ndi.binary_closing(fg, iterations=4)
    fg = largest_component(fg)
    # Fill only small holes (specks inside the mini). Bigger enclosed areas are
    # real gaps -- e.g. between an arm and the body -- so they stay background.
    holes = ndi.binary_fill_holes(fg) & ~fg
    lab, n = ndi.label(holes)
    if n:
        sizes = ndi.sum(holes, lab, range(1, n + 1))
        small = np.zeros(n + 1, bool)
        small[1:] = sizes < fg.sum() * 0.002
        fg |= small[lab]
    return fg


def clean(mask, min_px):
    """Smooth a paint region and drop specks smaller than min_px."""
    mask = ndi.binary_opening(mask, iterations=1)
    lab, n = ndi.label(mask)
    if n:
        sizes = ndi.sum(mask, lab, range(1, n + 1))
        keep = np.zeros(n + 1, bool)
        keep[1:] = sizes >= min_px
        mask = keep[lab]
    return ndi.binary_closing(mask, iterations=2)


def match_paints(lab_img, fg, paints, default_thr, kL):
    h, w = fg.shape
    mapped = [p for p in paints if p.get("highlight", True)]
    if not mapped:
        return {}, np.zeros((h, w), bool)
    def reference_colours(p):
        # The paint's published colour, plus any "samples": [x, y] spots on this
        # photo known to be that paint (e.g. how it looks in shadow or pooled in
        # recesses). Coordinates are in the cropped photo.
        refs = [color.rgb2lab(np.array(hex_to_rgb(p["hex"]), float)[None, None, :] / 255.0)[0, 0]]
        for x, y in p.get("samples", []):
            patch = lab_img[max(0, y - 2):y + 3, max(0, x - 2):x + 3].reshape(-1, 3)
            refs.append(np.median(patch, axis=0))
        refs += [np.array(c, float) for c in p.get("_learned", [])]
        return refs

    dists = np.stack([
        np.min([color.deltaE_ciede2000(lab_img, r[None, None, :], kL=kL) for r in reference_colours(p)], axis=0)
        for p in mapped
    ])
    best = np.argmin(dists, axis=0)
    best_d = np.take_along_axis(dists, best[None], 0)[0]
    thr = np.array([p.get("threshold", default_thr) for p in mapped])[best]
    assigned = fg & (best_d <= thr)

    min_px = max(20, int(fg.sum() * 0.0008))
    masks, taken = {}, np.zeros((h, w), bool)
    for i, p in enumerate(mapped):
        raw = assigned & (best == i)
        m = clean(raw, min_px) & fg
        m &= ~taken  # smoothing may fill small gaps, but never take another paint's pixels
        taken |= m
        masks[p["name"]] = m
    return masks, fg & ~taken


def save_mask(mask, path):
    alpha = (mask.astype(np.uint8) * 255)
    alpha = np.array(Image.fromarray(alpha).filter(_soften()))
    rgba = np.zeros(mask.shape + (4,), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = alpha
    Image.fromarray(rgba, "RGBA").save(path, optimize=True)


def _soften():
    from PIL import ImageFilter
    return ImageFilter.GaussianBlur(0.8)


def review_image(img, fg, masks, unmatched, paints, path):
    base = np.array(img).astype(float)
    dim = (base.mean(axis=2, keepdims=True) * 0.35).repeat(3, axis=2)

    painted = dim.copy()
    for p in paints:
        m = masks.get(p["name"])
        if m is not None:
            painted[m] = np.array(hex_to_rgb(p["hex"]), float) * 0.85 + base[m] * 0.15

    miss = dim.copy()
    miss[fg & ~unmatched] = base[fg & ~unmatched] * 0.6
    miss[unmatched] = [255, 0, 200]
    miss[~fg] = [20, 60, 90]  # background shown as dark blue

    panel = np.concatenate([base, painted, miss], axis=1).clip(0, 255).astype(np.uint8)
    Image.fromarray(panel).save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--photo", required=True)
    ap.add_argument("--paints", required=True, help="JSON file with the paint list")
    ap.add_argument("--name", required=True, help="the mini's name")
    ap.add_argument("--game", required=True, help="board game it belongs to")
    ap.add_argument("--id", help="URL id (default: game-name)")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--notes", default="")
    ap.add_argument("--threshold", type=float, default=16.0,
                    help="max colour difference to count as a paint (higher = looser)")
    ap.add_argument("--kL", type=float, default=2.2,
                    help="brightness tolerance; higher ignores shading more")
    ap.add_argument("--background", choices=["border", "grabcut", "rembg", "none"], default="border",
                    help="border: plain backdrop; grabcut: busy backdrop (use with --crop)")
    ap.add_argument("--crop", help="left,top,right,bottom in photo pixels: crop to the mini first")
    ap.add_argument("--fg-mask", help="optional image the same size as the (cropped) photo; "
                                      "white = mini, black = background. Overrides --background.")
    ap.add_argument("--bg-threshold", type=float, default=12.0)
    ap.add_argument("--preview", help="where to write the review image")
    ap.add_argument("--no-learned", action="store_true",
                    help="match on published colours and samples only, ignoring shades learned from earlier minis")
    args = ap.parse_args()

    paints = json.loads(Path(args.paints).read_text())
    mini_id = args.id or slug(f"{args.game} {args.name}")
    ranges = paintlib.load_ranges()
    for p in paints:
        lib = paintlib.lookup(p["name"], p.get("brand", ""), ranges)
        if not p.get("hex"):
            if not lib:
                sys.exit(f"No colour for {p['name']!r}: not in library/ranges/, so give a \"hex\"")
            p["hex"] = lib["hex"]
        hex_to_rgb(p["hex"])  # validate early
        if not args.no_learned:
            obs = paintlib.load_observed(paintlib.paint_key(p, ranges))
            if obs:  # shades seen on *other* minis (never this one, to avoid learning from itself)
                p["_learned"] = [c["lab"] for m in obs["minis"] if m["mini"] != mini_id
                                 for c in m["clusters"] if c["weight"] >= 0.1]

    crop = tuple(int(v) for v in args.crop.split(",")) if args.crop else None
    img = load_photo(args.photo, crop)
    rgb = np.array(img).astype(float) / 255.0
    lab_img = color.rgb2lab(ndi.gaussian_filter(rgb, sigma=(1, 1, 0)))

    if args.fg_mask:
        fgm = Image.open(args.fg_mask).convert("L").resize(img.size, Image.NEAREST)
        fg = np.array(fgm) > 127
    else:
        fg = foreground(img, lab_img, args.background, args.bg_threshold)
    masks, unmatched = match_paints(lab_img, fg, paints, args.threshold, args.kL)

    out_dir = ROOT / "minis" / mini_id
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("mask-*.png"):
        old.unlink()
    img.save(out_dir / "photo.jpg", quality=88, optimize=True, progressive=True)
    # The mini's outline, kept for the training dataset (tools/learn.py)
    ds_dir = ROOT / "dataset" / mini_id
    ds_dir.mkdir(parents=True, exist_ok=True)
    Image.fromarray((fg * 255).astype(np.uint8)).save(ds_dir / "fg.png")

    fg_px = max(1, int(fg.sum()))
    entry_paints = []
    for p in paints:
        e = {k: p[k] for k in ("name", "brand", "role", "hex") if p.get(k)}
        m = masks.get(p["name"])
        if m is not None and m.any():
            fname = f"mask-{slug(p['name'])}.png"
            save_mask(m, out_dir / fname)
            e["mask"] = f"minis/{mini_id}/{fname}"
            e["coverage"] = round(100.0 * m.sum() / fg_px, 1)
        entry_paints.append(e)

    entry = {
        "id": mini_id,
        "name": args.name,
        "game": args.game,
        "date": args.date,
        "photo": f"minis/{mini_id}/photo.jpg",
        "width": img.size[0],
        "height": img.size[1],
        "paints": entry_paints,
    }
    if args.notes:
        entry["notes"] = args.notes

    data_path = ROOT / "data" / "minis.json"
    data = json.loads(data_path.read_text()) if data_path.exists() else {"minis": []}
    data["minis"] = [m for m in data.get("minis", []) if m.get("id") != mini_id] + [entry]
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    if args.preview:
        review_image(img, fg, masks, unmatched, paints, args.preview)

    # Summary for the review conversation
    print(f"id: {mini_id}  ({img.size[0]}x{img.size[1]}, mini = {100 * fg.mean():.0f}% of photo)")
    for e in entry_paints:
        cov = f"{e['coverage']:5.1f}%" if "coverage" in e else "  not mapped"
        print(f"  {cov}  {e['name']}")
    print(f"  {100.0 * unmatched.sum() / fg_px:5.1f}%  (unmatched)")


if __name__ == "__main__":
    main()
