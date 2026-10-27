Inputs used to build Ant-Man (kept so it can be re-run).

python3 tools/process_mini.py --photo <original photo> \
  --paints tools/inputs/marvel-united-ant-man/paints.json \
  --name "Ant-Man" --game "Marvel United" --crop 370,560,1340,1960 \
  --fg-mask tools/inputs/marvel-united-ant-man/fg_mask.png

Paint colours: Speedpaint 2.0 values from the library; Shining Silver #b5b5bd (MiniMatch).
fg_mask.png: hint-based GrabCut outline (busy dark fabric background), made with fg_hints.py.
