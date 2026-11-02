Inputs used to build Thunderbird (front photo on two backdrops, side by side; kept so it can be re-run).

composite.jpg (1456x1158) = original-1.jpg (grey backdrop) cropped 786,251,1514,1409 | original-2.jpg (black velvet)
cropped 796,156,1524,1314, pasted left/right. Those are the crops 870,385,1430,1275 and 880,290,1440,1180
grown 15% per side.

python3 tools/inputs/6-siege-thunderbird/make_mask.py tools/inputs/6-siege-thunderbird/composite.jpg tools/inputs/6-siege-thunderbird/fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/6-siege-thunderbird/composite.jpg \
  --paints tools/inputs/6-siege-thunderbird/paints.json \
  --name "Thunderbird" --game "6 Siege" --id 6-siege-thunderbird --date 2026-11-01 \
  --fg-mask tools/inputs/6-siege-thunderbird/fg_mask.png

Dan's paints (Oct 24 2026): Hardened Leather, Grim Black, Graveyard Grey (taken as Speedpaint Gravelord Grey),
Peachy Flesh, Noble Skin, Satchel Brown, Poppy Red. Clip = Vallejo Hot Orange; base = Black (house).
First-pass placement (awaiting Dan's corrections): Satchel Brown jacket+trousers, Hardened Leather pouches,
Grim Black gun/goggles, Gravelord Grey helmet+boots, both skin paints on face/hands, Poppy Red collar+sash.
White patches and the grey pouch left unmarked.

Nov 2 2026 (Dan): grey-backdrop view removed; the site now shows only the black-backdrop photo.
Current build: black.jpg + black_paints.json + black_fg_mask.png (made from the composite with
tools/single_view.py). The composite files above are kept for reference only.
