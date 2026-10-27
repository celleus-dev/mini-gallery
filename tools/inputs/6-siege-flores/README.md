Inputs used to build Flores (kept so it can be re-run).

python3 tools/process_mini.py --photo tools/inputs/6-siege-flores/original.jpg \
  --paints tools/inputs/6-siege-flores/paints.json \
  --name "Flores" --game "6 Siege" --date 2026-10-26 --crop 538,486,1280,1869 --pad 0.15 \
  --fg-mask tools/inputs/6-siege-flores/fg_mask.png

Paint colours: published Speedpaint 2.0 values (lexmechanic.com/paints/speedpaint-2).
fg_mask.png: hint-based GrabCut outline (busy dark fabric background).

Re-cropped Oct 27 2026 with --pad 0.15 (Dan: photos looked too zoomed in); paint areas shifted with tools/recrop.py.
