Inputs used to build Recruit (Defender) — two models on one photo, black velvet backdrop.

photo.jpg = original.jpg cropped 256,220,1934,1430 (whole minis + ~15% margin) and scaled to 1594 wide.
python3 tools/inputs/6-siege-recruit-defender/make_mask.py tools/inputs/6-siege-recruit-defender/photo.jpg tools/inputs/6-siege-recruit-defender/fg_mask.png
python3 tools/process_mini.py --photo tools/inputs/6-siege-recruit-defender/photo.jpg \
  --paints tools/inputs/6-siege-recruit-defender/paints.json \
  --name "Recruit (Defender)" --game "6 Siege" --id 6-siege-recruit-defender --date 2026-11-01 \
  --fg-mask tools/inputs/6-siege-recruit-defender/fg_mask.png

Hot Orange = clips (Vallejo Game Color 72.009, Scalemates #e64c2a). Red shotgun rail left unmarked (not in Dan's list).
