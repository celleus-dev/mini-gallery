"""Lasso edits from the site's editor (edit.html).

An edits file is JSON downloaded from the editor:

    {
      "mini": "crisis-protocol-bishop",
      "size": [420, 660],                 # photo width, height the edits were drawn on
      "created": "2026-10-26T22:10:00Z",
      "edits": [
        {"paint": "Familiar Pink", "op": "add",    "points": [[x, y], ...]},
        {"paint": "Familiar Pink", "op": "remove", "points": [[x, y], ...]}
      ]
    }

Edits are applied in order on top of the automatic matching:
  add    -- every pixel inside the lasso becomes this paint (taken from any other paint)
  remove -- pixels inside the lasso that are this paint become unmatched

Saved edits live in tools/inputs/<mini-id>/edits/ and are re-applied every
time process_mini.py re-runs that mini, so hand fixes are never lost.
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def load(path):
    doc = json.loads(Path(path).read_text())
    if not isinstance(doc.get("edits"), list) or "mini" not in doc:
        raise ValueError(f"{path}: not an edits file from the editor")
    for e in doc["edits"]:
        if e.get("op") not in ("add", "remove") or not e.get("paint") or len(e.get("points", [])) < 3:
            raise ValueError(f"{path}: bad edit {e!r}")
    return doc


def polygon_mask(points, w, h):
    im = Image.new("1", (w, h), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in points], fill=1, outline=1)
    return np.array(im, bool)


def apply(masks, paint_names, docs, w, h):
    """Apply edits docs (in order) to masks {paint name: bool array}. Returns
    (masks, notes). Paints in edits that aren't on this mini are skipped."""
    masks = {n: (masks.get(n).copy() if masks.get(n) is not None else np.zeros((h, w), bool))
             for n in paint_names}
    notes = []
    for doc in docs:
        dw, dh = doc.get("size", [w, h])
        if (dw, dh) != (w, h):
            notes.append(f"skipped {doc.get('_file', 'edits')}: drawn on a {dw}x{dh} photo, this one is {w}x{h}")
            continue
        for e in doc["edits"]:
            if e["paint"] not in masks:
                notes.append(f"skipped an edit for {e['paint']!r}: not in this mini's paint list")
                continue
            area = polygon_mask(e["points"], w, h)
            if e["op"] == "add":
                for n in masks:
                    masks[n] &= ~area
                masks[e["paint"]] |= area
            else:
                masks[e["paint"]] &= ~area
    return masks, notes


def saved_docs(inputs_dir):
    d = Path(inputs_dir) / "edits"
    docs = []
    for f in sorted(d.glob("*.json")) if d.exists() else []:
        doc = load(f)
        doc["_file"] = f.name
        docs.append(doc)
    return docs
