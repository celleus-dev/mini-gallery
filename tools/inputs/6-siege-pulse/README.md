Inputs used to build Pulse (kept so it can be re-run).

python3 tools/inputs/6-siege-pulse/make_mask.py <padded photo> tools/inputs/6-siege-pulse/fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/6-siege-pulse/original.jpg \
  --paints tools/inputs/6-siege-pulse/paints.json \
  --name "Pulse" --game "6 Siege" --id 6-siege-pulse --date 2026-11-01 \
  --crop 920,540,1500,1400 --pad 0.15 \
  --fg-mask tools/inputs/6-siege-pulse/fg_mask.png

Speckled black-velvet backdrop: outline polygons + GrabCut (make_mask.py), whole base ellipse kept.
Dan's paints: Peachy Flesh (head), Grim Black (vest, gear, gun), Gravelord Grey (uniform; he wrote "Gray"), Cloudburst Blue (boots).
Hot Orange = the clip (Vallejo Game Color 72.009, Scalemates #e64c2a). Base = regular Army Painter Black.
