Inputs used to build Doc (kept so it can be re-run).

python3 tools/inputs/6-siege-doc/make_mask.py <padded photo> tools/inputs/6-siege-doc/fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/6-siege-doc/original.jpg \
  --paints tools/inputs/6-siege-doc/paints.json \
  --name "Doc" --game "6 Siege" --id 6-siege-doc --date 2026-11-01 \
  --crop 750,525,1280,1310 --pad 0.15 \
  --fg-mask tools/inputs/6-siege-doc/fg_mask.png

Speckled black-velvet backdrop: outline polygons + GrabCut (make_mask.py), whole base ellipse kept.
Paints from Dan: Blinding Light, Magic Blue (Speedpaint), Pastel Indigo, Occultist Cloak, Grim Black.
Hot Orange = the clip (Vallejo Game Color 72.009). Black = base (house paint).
