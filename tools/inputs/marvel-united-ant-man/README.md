Inputs used to build Ant-Man (kept so it can be re-run).

python3 tools/process_mini.py --photo tools/inputs/marvel-united-ant-man/original.jpg \
  --paints tools/inputs/marvel-united-ant-man/paints.json \
  --name "Ant-Man" --game "Marvel United" --date 2026-10-27 --crop 370,560,1340,1960 --pad 0.15 \
  --fg-mask tools/inputs/marvel-united-ant-man/fg_mask.png

Paint colours: Speedpaint 2.0 values from the library; Shining Silver #b5b5bd (MiniMatch).
fg_mask.png: hint-based GrabCut outline (busy dark fabric background), made with fg_hints.py.

Re-cropped Oct 27 2026 with --pad 0.15 (Dan: photos looked too zoomed in); paint areas shifted with tools/recrop.py.
