Inputs used to build Mute (front photo on two backdrops, side by side; kept so it can be re-run).

original-1.jpg = grey backdrop (left), original-2.jpg = black velvet (right).
make_composite.py builds composite.jpg, fg_mask.png and paints.json:
  left  = original-1 crop 815,320,1470,1320 grown 15% per side, scaled to the right panel's height;
  right = original-2 crop 830,300,1530,1225 grown 15% per side;
  then the whole composite is scaled to 1600 px wide (the site's limit) with all coordinates.
The right panel's mask/paints live in fg_mask-black.png and paints-black.json (its own padded-crop
coordinates); grey-panel shapes are in make_composite.py (original-1 pixels).

cd tools/inputs/6-siege-mute && python3 make_composite.py && cd ../../..
python3 tools/process_mini.py --photo tools/inputs/6-siege-mute/composite.jpg \
  --paints tools/inputs/6-siege-mute/paints.json \
  --name "Mute" --game "6 Siege" --id 6-siege-mute --date 2026-11-01 \
  --fg-mask tools/inputs/6-siege-mute/fg_mask.png

Dan's paints (Nov 1 2026): Tyrian Navy, Camo Cloak, Grim Black, Dark Wood, Gravelord Grey,
Vallejo Electric Blue (72.023, #3495b6, Scalemates). Hot Orange clip (72.009, #e64c2a) and
Black base added per the standing rules. First pass: Tyrian Navy uniform, Camo Cloak harness,
Gravelord Grey vest/pouches, Grim Black gun/boots/mask, Dark Wood hip pouch, Electric Blue goggles.
Red armband (grey photo) left unmarked: no paint listed for it.

Nov 2 2026 (Dan): grey-backdrop view removed; the site now shows only the black-backdrop photo.
Current build: black.jpg + black_paints.json + black_fg_mask.png (made from the composite with
tools/single_view.py). The composite files above are kept for reference only.
For Mute specifically: black.jpg = original-2.jpg cropped 725,161,1635,1364, with paints-black.json and fg_mask-black.png.
