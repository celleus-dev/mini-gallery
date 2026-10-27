Inputs used to build Black Widow (kept so it can be re-run).

python3 tools/process_mini.py --photo <original photo> \
  --paints tools/inputs/marvel-united-black-widow/paints.json \
  --name "Black Widow" --game "Marvel United" --date 2026-10-27 \
  --crop 380,760,1380,2000 \
  --fg-mask tools/inputs/marvel-united-black-widow/fg_mask.png --no-house

Paint colours: all Speedpaint 2.0 values from the library.
--no-house: painted light stone base (like Wasp), not the usual black.
fg_mask.png: hint-based GrabCut outline (busy dark fabric background), made with fg_hints.py.
Grey paints are kept off the brown cloth and the blue weapons (not on the paint list).
