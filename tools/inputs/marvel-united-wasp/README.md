Inputs used to build Wasp (kept so it can be re-run).

Photo only, no paint list (Dan, Oct 27 2026: "No colors for this one, just upload it").

python3 tools/process_mini.py --photo <original photo> \
  --paints tools/inputs/marvel-united-wasp/paints.json \
  --name "Wasp" --game "Marvel United" --date 2026-10-27 \
  --crop 520,400,1330,1760 --background none --no-house --no-learned

--no-house: the base is a painted rocky base, not the usual black, so the
house Black isn't added. No fg mask, since nothing is mapped.
