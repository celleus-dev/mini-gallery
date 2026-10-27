Inputs used to build Tachanka (kept so it can be re-run).

python3 tools/inputs/6-siege-tachanka/make_mask.py <padded photo> tools/inputs/6-siege-tachanka/fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/6-siege-tachanka/original.jpg \
  --paints tools/inputs/6-siege-tachanka/paints.json \
  --name "Tachanka" --game "6 Siege" --id 6-siege-tachanka --date 2026-10-27 \
  --crop 480,490,1340,1540 --pad 0.15 \
  --fg-mask tools/inputs/6-siege-tachanka/fg_mask.png

Speckled black-velvet backdrop: outline polygons + GrabCut (make_mask.py), whole base ellipse kept.
Hot Orange = the clip (Vallejo Game Color 72.009, Scalemates #e64c2a).
Camo Cloak = helmet and vest (Dan calls it Camo Green). Burnt Moss = trousers. Drum, boots and gun stock left unmarked (Dan, Oct 27 2026).
