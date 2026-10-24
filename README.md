# mini-gallery

A gallery of painted miniatures, sorted by board game. Each mini has a photo
and its paint list; tapping a paint lights up where it was used on the mini.

It's a plain static site (no build step), made to run on GitHub Pages.

## Pages

| Page | What it shows |
|---|---|
| `index.html` | Every board game as a shelf of minis, plus search (`?q=` searches mini names, games and paints) |
| `game.html?g=<game>` | All minis for one board game, and the paints used across that game |
| `mini.html?id=<id>` | The photo with paint highlights, the paint list, and notes |

## Where things live

```
data/minis.json        one entry per mini (name, game, date, photo, paints, notes)
data/games.json        optional extra details per game, e.g. {"name": "...", "description": "..."}
minis/<id>/photo.jpg   the photo
minis/<id>/mask-*.png  one mask per paint (where that paint is on the photo)
tools/process_mini.py  turns a photo + paint list into the files above
```

## Adding a mini

1. Write the paint list as JSON (see the top of `tools/process_mini.py` for the format).
   Each paint needs a colour value (`hex`). Washes and glazes can be listed with
   `"highlight": false` so they appear in the list but aren't mapped on the photo.
2. Run:
   ```
   pip install -r tools/requirements.txt
   python3 tools/process_mini.py --photo photo.jpg --paints paints.json \
       --name "Mini name" --game "Board game" --preview review.png
   ```
3. Check `review.png`: original | paint map | unmatched areas (pink) with the
   background in blue. Adjust a paint's `hex` or `threshold`, or the global
   `--threshold`, and re-run until it looks right. Re-running with the same name
   and game replaces the entry.
4. Commit and push.

5. Once Dan has checked the labels, run `python3 tools/learn.py --verify <mini-id>`
   to add it to the paint library and training dataset (below), then commit.
   Re-processing a mini clears its verified mark.

## Paint library and training data

```
library/ranges/            published colours for whole paint ranges (Speedpaint 2.0 so far)
library/observed/          the shades each paint has actually shown on approved minis
library/swatches/          one image per paint: published colour + how it looked on each mini
library/index.json         every paint used so far, and on which minis
dataset/<mini-id>/         training data: image.jpg + labels.png (per-pixel paint labels)
                           + labels.json (label number -> paint) + fg.png (mini outline)
```

- Paints in `library/ranges/` don't need a `hex` in the paint list; it's looked up by name.
- Each new mini is matched using the paint's published colour **plus** the shades it
  showed on earlier minis, so matching improves as the library grows.
- `dataset/` is what a future automatic model trains on. Only verified minis are
  included, and label edges are marked 255 = ignore, since that's where labels
  are least reliable.
- Paint `regions` in a mini's paint list record Dan's corrections (where each
  paint is allowed to appear); see tools/inputs/<mini-id>/paints.json.

## Photo tips

Plain white or grey background, even daylight-type lighting, no coloured light,
and the whole mini in frame. The background is detected from the photo's edges,
so keep the edges clear of the mini.

## Limitations

Matching is by colour, so it's approximate: washes and glazes blend into the
paint underneath, metallics reflect their surroundings, and very similar paints
can be confused. Anything that doesn't clearly match a paint is left unmatched
rather than guessed.

## Publishing

GitHub Pages is off while the site is private. To go public: make the repository
public (or use a paid plan), then Settings → Pages → deploy from the `main`
branch, root folder.
