Inputs used to build Blitz (front and back views on one page, kept so it can be re-run).

The photo is a side-by-side composite of Dan's two photos:
  front = photo 1000002176 cropped to 330,370,1730,2470
  back  = photo 1000002175 cropped to 60,370,1460,2470
pasted left/right (2800x2100) and scaled to 1600x1200.

python3 tools/process_mini.py --photo composite.jpg \
  --paints tools/inputs/6-siege-blitz/paints.json \
  --name "Blitz" --game "6 Siege" \
  --fg-mask tools/inputs/6-siege-blitz/fg_mask.png

fg_mask.png: hint-based GrabCut (make_fg_mask.py composite.jpg fg_mask.png view.jpg hints.json;
hint coordinates are at half scale). Busy dark fabric background.
Paint colours: published Speedpaint 2.0 values (lexmechanic.com/paints/speedpaint-2);
Vallejo Electric Blue and Magic Blue from Scalemates.

Re-cropped Oct 27 2026 (Dan: photos looked too zoomed in): composite.jpg is now
original-front.jpg cropped 330,370,1730,2470 and original-back.jpg cropped 60,370,1460,2470, each grown 15% per side
(clamped to the photo), pasted side by side and scaled to max 1600 (tools/recrop.py).
Add --date 2026-10-26 when re-running.
