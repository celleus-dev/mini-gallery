Inputs used to build Black Widow (kept so it can be re-run).

python3 tools/inputs/marvel-united-black-widow/make_mask.py <padded photo> tools/inputs/marvel-united-black-widow/fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/marvel-united-black-widow/original.jpg \
  --paints tools/inputs/marvel-united-black-widow/paints.json \
  --name "Black Widow" --game "Marvel United" --id marvel-united-black-widow \
  --date 2026-10-27 --crop 815,600,1495,1510 --pad 0.15 \
  --fg-mask tools/inputs/marvel-united-black-widow/fg_mask.png --no-house

Photo replaced Nov 5 2026 (new black-backdrop photo set); paint areas redrawn for it.
Nuclear Sunrise = hair, Peachy Flesh = face, Gravelord Grey = suit, Ashen Stone = base stone.
--no-house: painted light stone base, not the usual black. Brown cloth and blue weapons are unlisted, kept unmarked.
