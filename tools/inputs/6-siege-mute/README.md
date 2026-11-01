Inputs used to build Mute (kept so it can be re-run).

python3 tools/inputs/6-siege-mute/make_mask.py <padded photo> tools/inputs/6-siege-mute/fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/6-siege-mute/original.jpg \
  --paints tools/inputs/6-siege-mute/paints.json \
  --name "Mute" --game "6 Siege" --id 6-siege-mute --date 2026-11-01 \
  --crop 830,300,1530,1225 --pad 0.15 \
  --fg-mask tools/inputs/6-siege-mute/fg_mask.png

<padded photo> = original.jpg cropped to 725,161,1635,1364 (the crop above grown 15% per side).
Speckled black-velvet backdrop: outline polygons + GrabCut (make_mask.py), whole base ellipse and clip kept.
Dan's paints (Nov 1 2026): Tyrian Navy, Camo Cloak, Grim Black, Dark Wood, Gravelord Grey,
Vallejo Electric Blue (72.023, #3495b6, Scalemates). Hot Orange clip (72.009, #e64c2a) and
Black base added per the standing rules. Photo used: the black-backdrop shot (a grey-backdrop
shot was also sent).
