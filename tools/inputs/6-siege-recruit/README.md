Inputs used to build Recruit (two models on one page, kept so it can be re-run).

The photo is a side-by-side composite of Dan's two photos:
  model 1 (blue sleeves)  = photo 1 cropped to 350,370,1450,2140
  model 2 (green jacket)  = photo 2 cropped to 410,370,1510,2140
pasted left/right (2200x1770) and scaled to 1600 wide.

python3 tools/process_mini.py --photo composite.jpg \
  --paints tools/inputs/6-siege-recruit/paints.json \
  --name "Recruit" --game "6 Siege" \
  --fg-mask tools/inputs/6-siege-recruit/fg_mask.png

fg_mask.png: hint-based GrabCut (make_fg_mask.py composite.jpg fg_mask.png view.jpg hints.json;
hint coordinates are at half scale). Busy dark fabric background.
Paint colours: published Speedpaint 2.0 values (lexmechanic.com/paints/speedpaint-2).
