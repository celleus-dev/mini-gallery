Inputs used to build Colossus (kept so it can be re-run).

python3 tools/inputs/marvel-united-colossus/make_mask.py <padded photo> tools/inputs/marvel-united-colossus/fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/marvel-united-colossus/original.jpg \
  --paints tools/inputs/marvel-united-colossus/paints.json \
  --name "Colossus" --game "Marvel United" --id marvel-united-colossus \
  --date 2026-10-27 --crop 670,530,1440,1600 --pad 0.35 \
  --fg-mask tools/inputs/marvel-united-colossus/fg_mask.png

Photo replaced Nov 5 2026 (new black-backdrop photo set); paint areas redrawn for it.
Paint colours: Speedpaint 2.0 values from the library; Shining Silver #b5b5bd (MiniMatch);
Dead White #ffffff (Scalemates, Vallejo Model Color 70.951 White).
fg mask: the backdrop and deep shadows are both near-black, so inside the body outline only
pixels above near-black count (else Shining Silver leaks onto the backdrop). Hair added by polygon.
Grim Black is limited to the hair; yellow is kept off the face (pale eye).

Framing widened to --pad 0.35 on Nov 6 2026 (Dan: zoom out a bit). paints.json is in the
pad-0.35 frame. make_mask.py still works on the old pad-0.15 frame, so after running it, move
the mask over:
python3 tools/reframe_inputs.py --photo tools/inputs/marvel-united-colossus/original.jpg \
  --fg-mask tools/inputs/marvel-united-colossus/fg_mask.png --old-crop <crop above> --old-pad 0.15 \
  --new-crop <crop above> --new-pad 0.35
