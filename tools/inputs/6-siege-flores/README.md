Inputs used to build Flores (kept so it can be re-run).

python3 tools/process_mini.py --photo <original photo> \
  --paints tools/inputs/6-siege-flores/paints.json \
  --name "Flores" --game "6 Siege" --crop 416,57,1620,2152 \
  --fg-mask tools/inputs/6-siege-flores/fg_mask.png

Paint colours: published Speedpaint 2.0 values (lexmechanic.com/paints/speedpaint-2).
fg_mask.png: hint-based GrabCut outline (busy dark fabric background).
