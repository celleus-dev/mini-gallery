Inputs used to build Smoke (black velvet backdrop; kept so it can be re-run).

Paints copied from Mute (Dan, Nov 1 2026: "same colors as Mute"): Tyrian Navy uniform,
Camo Cloak harness + grenade, Gravelord Grey vest/pouches, Grim Black gun/gloves/mask/boots,
Dark Wood hip pouch, Vallejo Electric Blue goggle lens, Hot Orange clip, Black base.

Mask: crop the photo first (same crop/pad as below), then make_mask.py on that padded crop.
python3 tools/process_mini.py --photo tools/inputs/6-siege-smoke/original.jpg \
  --crop 870,515,1520,1290 --pad 0.15 --paints tools/inputs/6-siege-smoke/paints.json \
  --name "Smoke" --game "6 Siege" --id 6-siege-smoke --date 2026-11-01 \
  --fg-mask tools/inputs/6-siege-smoke/fg_mask.png
