Inputs used to build Star-Lord (kept so it can be re-run).

Photo only, no paint list (Dan, Oct 27 2026: "No colors").

python3 tools/process_mini.py --photo <original photo> \
  --paints tools/inputs/marvel-united-star-lord/paints.json \
  --name "Star-Lord" --game "Marvel United" --id marvel-united-star-lord \
  --date 2026-10-27 --crop 40,520,1590,2040 --pad 0.15 \
  --background none --no-house --no-learned

--no-house: nothing is mapped, so the house Black isn't added. No fg mask.
