Inputs used to build Colossus (kept so it can be re-run).

python3 tools/process_mini.py --photo <original photo> \
  --paints tools/inputs/marvel-united-colossus/paints.json \
  --name "Colossus" --game "Marvel United" --crop 300,430,1440,1980 \
  --fg-mask tools/inputs/marvel-united-colossus/fg_mask.png

Paint colours: Speedpaint 2.0 values from the library; Shining Silver #b5b5bd (MiniMatch);
Dead White #ffffff (Scalemates, Vallejo Model Color 70.951 White).
fg_mask.png: hint-based GrabCut outline (busy dark fabric background).
