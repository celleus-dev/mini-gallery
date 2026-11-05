Inputs used to build Ant-Man (kept so it can be re-run).

python3 tools/inputs/marvel-united-ant-man/make_mask.py <padded photo> tools/inputs/marvel-united-ant-man/fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/marvel-united-ant-man/original.jpg \
  --paints tools/inputs/marvel-united-ant-man/paints.json \
  --name "Ant-Man" --game "Marvel United" --id marvel-united-ant-man \
  --date 2026-10-27 --crop 840,610,1415,1455 --pad 0.15 \
  --fg-mask tools/inputs/marvel-united-ant-man/fg_mask.png

Photo replaced Nov 5 2026 (new black-backdrop photo set); paint areas redrawn for it.
Paint colours: Speedpaint 2.0 values from the library; Shining Silver #b5b5bd (MiniMatch).
The dark underside of the coin is unlisted and kept unmarked. Ashen Stone = rocks, Black = rest of the base.
