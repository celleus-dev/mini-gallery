Inputs used to build Rocket (kept so it can be re-run).

Photo only, no paint list (Dan, Oct 27 2026: "No colors").

python3 tools/process_mini.py --photo tools/inputs/marvel-united-rocket/original.jpg \
  --paints tools/inputs/marvel-united-rocket/paints.json \
  --name "Rocket" --game "Marvel United" --id marvel-united-rocket --date 2026-10-27 \
  --crop 905,645,1535,1450 --pad 0.15 --background none --no-house --no-learned

--no-house: nothing is mapped, so the house Black isn't added. No fg mask.

Re-cropped Oct 27 2026 with --pad 0.15 (Dan: photos looked too zoomed in); paint areas shifted with tools/recrop.py.

Photo replaced Nov 5 2026 (new black-backdrop photo set).
