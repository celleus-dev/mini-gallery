Inputs used to build Blitz (kept so it can be re-run).

Photo replaced Oct 27 2026 with Dan's single front photo on a black backdrop (original.jpg).

python3 tools/inputs/6-siege-blitz/make_mask.py <padded photo> tools/inputs/6-siege-blitz/fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/6-siege-blitz/original.jpg \
  --paints tools/inputs/6-siege-blitz/paints.json \
  --name "Blitz" --game "6 Siege" --id 6-siege-blitz --date 2026-10-26 \
  --crop 690,890,1240,1750 --pad 0.15 \
  --fg-mask tools/inputs/6-siege-blitz/fg_mask.png

<padded photo> = original.jpg cropped to 608,761,1322,1879 (the crop above grown 15% per side).
fg_mask.png: outline polygons + GrabCut (make_mask.py); whole base ellipse and clip kept.

Paint colours: published Speedpaint 2.0 values (lexmechanic.com/paints/speedpaint-2);
Vallejo Electric Blue (72.023, #3495b6) and Magic Blue (72.021, #006eb5) from Scalemates.
Dan's corrections (Oct 26 2026): Broadsword Silver is just the gun; Tyrian Navy is the
blue-grey (helmet, sleeves); Occultist Cloak is the grey that isn't black.
Electric Blue = shield window, Magic Blue = base clip, Hardened Leather = gloves, Dark Wood = boots.

old/ holds the earlier front+back composite inputs (Oct 26 2026).
