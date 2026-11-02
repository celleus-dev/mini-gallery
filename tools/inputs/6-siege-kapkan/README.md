Inputs used to build Kapkan (front views on two backdrops, side by side; kept so it can be re-run).

composite.jpg = original-1.jpg (black velvet) cropped 670,328,1540,1278 and original-2.jpg (grey)
cropped 708,295,1502,1245 (each ~15% margin around the mini), pasted left/right, scaled to 1600 wide.

python3 tools/inputs/6-siege-kapkan/make_mask.py composite.jpg fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/6-siege-kapkan/composite.jpg \
  --paints tools/inputs/6-siege-kapkan/paints.json \
  --name "Kapkan" --game "6 Siege" --id 6-siege-kapkan --date 2026-11-01 \
  --fg-mask tools/inputs/6-siege-kapkan/fg_mask.png

Hot Orange = the clip (Vallejo Game Color 72.009, Scalemates #e64c2a). Base: Black, whole circle.
Camo Cloak = what Dan calls Camo Green. Gravelord Grey confirmed by Dan. Algae Green = the yellow-green netting (Dan, Nov 1 2026).

Nov 2 2026 (Dan): grey-backdrop view removed; the site now shows only the black-backdrop photo.
Current build: black.jpg + black_paints.json + black_fg_mask.png (made from the composite with
tools/single_view.py). The composite files above are kept for reference only.
