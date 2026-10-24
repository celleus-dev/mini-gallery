"""Paint library helpers shared by process_mini.py and learn.py.

library/ranges/*.json     published reference colours for whole paint ranges
library/observed/<key>.json   how each paint has actually looked on Dan's minis
                              (colour clusters per mini, learned by learn.py)
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "library"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def load_ranges():
    """{(brand_alias_slug, name_slug): {"name", "hex", "brand", "range", "key", "source"}}"""
    index = {}
    for f in sorted((LIB / "ranges").glob("*.json")):
        doc = json.loads(f.read_text())
        aliases = {slug(a) for a in doc.get("aliases", [])} | {slug(doc["brand"])}
        for p in doc["paints"]:
            entry = {
                "name": p["name"],
                "hex": p["hex"],
                "brand": doc["brand"],
                "range": doc.get("range", ""),
                "key": f"{f.stem}/{slug(p['name'])}",
                "source": doc.get("source", ""),
            }
            for a in aliases:
                index[(a, slug(p["name"]))] = entry
            index.setdefault(("", slug(p["name"])), entry)
    return index


def lookup(name, brand="", ranges=None):
    """Find a paint by name (and brand if given). Returns None if not in the library."""
    ranges = ranges if ranges is not None else load_ranges()
    return ranges.get((slug(brand), slug(name))) or ranges.get(("", slug(name)))


def paint_key(p, ranges=None):
    hit = lookup(p["name"], p.get("brand", ""), ranges)
    return hit["key"] if hit else f"other/{slug(p.get('brand', ''))}-{slug(p['name'])}".replace("/-", "/")


def observed_path(key):
    return LIB / "observed" / (key.replace("/", "__") + ".json")


def load_observed(key):
    path = observed_path(key)
    return json.loads(path.read_text()) if path.exists() else None
