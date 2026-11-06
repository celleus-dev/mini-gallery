Inputs used to build Captain Marvel (kept so it can be re-run).

python3 tools/inputs/marvel-united-captain-marvel/make_mask.py <padded photo> tools/inputs/marvel-united-captain-marvel/fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/marvel-united-captain-marvel/original.jpg \
  --paints tools/inputs/marvel-united-captain-marvel/paints.json \
  --name "Captain Marvel" --game "Marvel United" --id marvel-united-captain-marvel \
  --date 2026-10-27 --crop 900,405,1500,1505 --pad 0.35 \
  --fg-mask tools/inputs/marvel-united-captain-marvel/fg_mask.png

Photo replaced Nov 5 2026 (new black-backdrop photo set); paint areas redrawn for it.
Hint-based fg mask: saturated paint + face polygon + whole base ellipse.
Ashen Stone = base flooring (not priority, so the red sash lying on the base stays red),
Peachy Flesh = face (Dan, Oct 27 2026). Black on the rim.

Framing widened to --pad 0.35 on Nov 6 2026 (Dan: zoom out a bit). paints.json is in the
pad-0.35 frame. make_mask.py still works on the old pad-0.15 frame, so after running it, move
the mask over:
python3 tools/reframe_inputs.py --photo tools/inputs/marvel-united-captain-marvel/original.jpg \
  --fg-mask tools/inputs/marvel-united-captain-marvel/fg_mask.png --old-crop <crop above> --old-pad 0.15 \
  --new-crop <crop above> --new-pad 0.35
