Inputs used to build Earth Dragon (kept so it can be re-run).

python3 tools/process_mini.py --photo <original photo> \
  --paints tools/inputs/demo-earth-dragon/paints.json \
  --name "Earth Dragon" --game "Demo" --crop 440,460,1680,1990 \
  --fg-mask tools/inputs/demo-earth-dragon/fg_mask.png --background none

Colours: Dan asked for basic colour names instead of paint names, so each
colour value was sampled from this photo. Not yet checked by Dan.
