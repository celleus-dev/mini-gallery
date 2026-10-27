"""Hint-based fg mask for Blitz (black backdrop, Oct 27 2026 photo).

Rough outline polygons (body, shield, clip, base) as probable foreground,
an eroded core as sure foreground, everything else background; GrabCut refines.
Coordinates are in the padded photo (crop 690,890,1240,1750 with --pad 0.15).

    python3 make_mask.py <padded photo> <out fg_mask.png>
"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw

img = np.array(Image.open(sys.argv[1]).convert("RGB"))
h, w = img.shape[:2]
hint = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(hint)
body = [(300, 165), (340, 150), (380, 165), (405, 230), (430, 260), (440, 300),
        (380, 330), (375, 420), (400, 500), (410, 620), (410, 700), (400, 820),
        (300, 830), (270, 840), (220, 840), (165, 840), (190, 780), (195, 700),
        (205, 620), (215, 520), (240, 440), (200, 420), (185, 340), (195, 270),
        (240, 235), (285, 230)]
shield = [(465, 200), (475, 140), (550, 135), (550, 240), (575, 250), (570, 330),
          (560, 350), (580, 440), (600, 620), (610, 900), (600, 930), (430, 930),
          (410, 820), (410, 640), (400, 500), (370, 420), (365, 340), (410, 300),
          (440, 270)]
clip = [(570, 880), (615, 870), (625, 965), (580, 975), (565, 960)]
BASE = [90, 820, 590, 1010]
d.polygon(body, fill=255)
d.polygon(shield, fill=255)
d.polygon(clip, fill=255)
d.ellipse(BASE, fill=255)
prob = np.array(hint) > 0

gc = np.full((h, w), cv2.GC_BGD, np.uint8)
grown = cv2.dilate(prob.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
gc[grown] = cv2.GC_PR_BGD
gc[prob] = cv2.GC_PR_FGD
core = cv2.erode(prob.astype(np.uint8), np.ones((31, 31), np.uint8)) > 0
gc[core] = cv2.GC_FGD
bgm, fgm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
cv2.grabCut(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), gc, None, bgm, fgm, 5,
            cv2.GC_INIT_WITH_MASK)
m = np.isin(gc, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8) * 255
# the base and the dark shield blend into the black backdrop, so keep those hints regardless
keep_hint = Image.new("L", (w, h), 0)
kd = ImageDraw.Draw(keep_hint)
kd.ellipse(BASE, fill=255)
kd.polygon(clip, fill=255)
m[np.array(keep_hint) > 0] = 255
m[core] = 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.zeros_like(m)
if n > 1:
    keep[lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))] = 255
Image.fromarray(keep).save(sys.argv[2])
