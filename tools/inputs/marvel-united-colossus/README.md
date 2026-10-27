Inputs used to build Colossus (kept so it can be re-run).

python3 tools/process_mini.py --photo tools/inputs/marvel-united-colossus/original.jpg \
  --paints tools/inputs/marvel-united-colossus/paints.json \
  --name "Colossus" --game "Marvel United" --date 2026-10-27 --crop 300,430,1440,1980 --pad 0.15 \
  --fg-mask tools/inputs/marvel-united-colossus/fg_mask.png

Paint colours: Speedpaint 2.0 values from the library; Shining Silver #b5b5bd (MiniMatch);
Dead White #ffffff (Scalemates, Vallejo Model Color 70.951 White).
fg_mask.png: hint-based GrabCut outline (busy dark fabric background).

Re-cropped Oct 27 2026 with --pad 0.15 (Dan: photos looked too zoomed in); paint areas shifted with tools/recrop.py.
