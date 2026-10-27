Inputs used to build Captain Marvel (kept so it can be re-run).

python3 tools/inputs/marvel-united-captain-marvel/make_mask.py <padded photo> tools/inputs/marvel-united-captain-marvel/fg_mask.png
python3 tools/process_mini.py --photo <original photo> \
  --paints tools/inputs/marvel-united-captain-marvel/paints.json \
  --name "Captain Marvel" --game "Marvel United" --id marvel-united-captain-marvel \
  --date 2026-10-27 --crop 470,480,1440,2240 --pad 0.15 \
  --fg-mask tools/inputs/marvel-united-captain-marvel/fg_mask.png

Hint-based fg mask (busy speckled backdrop): saturated paint + face polygon + whole base ellipse.
Ashen Stone placed on the base's stone floor, Black on the rim — to confirm with Dan.
