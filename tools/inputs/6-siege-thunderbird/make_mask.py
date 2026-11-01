"""Hint-based fg mask for Thunderbird (two views side by side).

Left view: grey backdrop. Right view: speckled black-velvet backdrop.
Rough outline polygons (body + gun, base, clip) per view as probable foreground,
an eroded core as sure foreground, everything else background; GrabCut refines.
The whole base ellipse and the clip are always kept.
Coordinates are in composite.jpg (1456x1158; see README.md).

    python3 make_mask.py composite.jpg fg_mask.png
"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw

BODY = [(290, 140), (345, 135), (380, 170), (378, 240), (420, 250), (455, 285),
        (475, 330), (490, 390), (530, 420), (570, 450), (630, 480), (635, 535),
        (600, 540), (540, 505), (480, 490), (475, 560), (455, 600), (435, 645),
        (425, 700), (435, 790), (445, 855), (395, 865), (385, 785), (365, 700),
        (345, 660), (335, 700), (350, 760), (335, 835), (285, 835), (285, 760),
        (275, 700), (255, 625), (205, 605), (195, 500), (200, 400), (195, 300),
        (245, 250), (262, 220), (258, 170)]
VIEWS = [
    {"dx": 0, "dy": 0, "base": (360, 875, 268, 135),
     "clip": [(100, 905), (175, 872), (268, 905), (252, 955), (202, 1012), (108, 1008)]},
    {"dx": 738, "dy": -5, "base": (1097, 903, 268, 112),
     "clip": [(833, 915), (880, 882), (962, 878), (998, 905), (978, 945), (932, 1002), (843, 998)]},
]

img = np.array(Image.open(sys.argv[1]).convert("RGB"))
h, w = img.shape[:2]
hint = Image.new("L", (w, h), 0)
keep_always = Image.new("L", (w, h), 0)
d, k = ImageDraw.Draw(hint), ImageDraw.Draw(keep_always)
for v in VIEWS:
    d.polygon([(x + v["dx"], y + v["dy"]) for x, y in BODY], fill=255)
    cx, cy, rx, ry = v["base"]
    for dr in (d, k):
        dr.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
        dr.polygon(v["clip"], fill=255)
prob = np.array(hint) > 0

gc = np.full((h, w), cv2.GC_BGD, np.uint8)
grown = cv2.dilate(prob.astype(np.uint8), np.ones((31, 31), np.uint8)) > 0
gc[grown] = cv2.GC_PR_BGD
gc[prob] = cv2.GC_PR_FGD
core = cv2.erode(prob.astype(np.uint8), np.ones((35, 35), np.uint8)) > 0
gc[core] = cv2.GC_FGD
bgm, fgm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
cv2.grabCut(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), gc, None, bgm, fgm, 5,
            cv2.GC_INIT_WITH_MASK)
m = np.isin(gc, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8) * 255
m[np.array(keep_always) > 0] = 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
# keep the largest piece in each half
out = np.zeros_like(m)
for x0, x1 in ((0, w // 2), (w // 2, w)):
    part = m[:, x0:x1]
    n, lab, st, _ = cv2.connectedComponentsWithStats(part)
    if n > 1:
        out[:, x0:x1][lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))] = 255
Image.fromarray(out).save(sys.argv[2])
