Inputs used to build Rocket (kept so it can be re-run).

Photo only, no paint list (Dan, Oct 27 2026: "No colors").

python3 tools/process_mini.py --photo <original photo> \
  --paints tools/inputs/marvel-united-rocket/paints.json \
  --name "Rocket" --game "Marvel United" --date 2026-10-27 \
  --crop 480,430,1760,2230 --background none --no-house --no-learned

--no-house: nothing is mapped, so the house Black isn't added. No fg mask.
