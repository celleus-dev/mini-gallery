"""Hint-based fg mask for Pulse (speckled black-velvet backdrop).

Rough outline polygons (body, gun, base, clip) as probable foreground,
an eroded core as sure foreground, everything else background; GrabCut refines.
Coordinates are in the padded photo (crop 920,540,1500,1400 with --pad 0.15).

    python3 make_mask.py <padded photo> <out fg_mask.png>
"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw

BASE = [95, 755, 625, 990]
img = np.array(Image.open(sys.argv[1]).convert("RGB"))
h, w = img.shape[:2]
hint = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(hint)
body = [(345, 140), (425, 140), (440, 190), (445, 225), (490, 255), (520, 320),
        (545, 375), (590, 385), (600, 430), (575, 465), (565, 520), (520, 545),
        (495, 560), (490, 610), (470, 665), (430, 700), (420, 730), (420, 810),
        (395, 822), (350, 790), (352, 860), (268, 862), (262, 760), (270, 720),
        (275, 640), (240, 605), (228, 520), (245, 450), (205, 395), (205, 310),
        (235, 255), (290, 220), (340, 205)]
gun = [(255, 330), (300, 335), (420, 440), (500, 500), (560, 530), (648, 570),
       (645, 592), (560, 560), (470, 520), (400, 470), (250, 350)]
d.polygon(body, fill=255)
d.polygon(gun, fill=255)
d.ellipse(BASE, fill=255)
d.polygon([(430, 875), (535, 845), (575, 860), (585, 940), (575, 968),
           (470, 975), (455, 910)], fill=255)
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
base = Image.new("L", (w, h), 0)
ImageDraw.Draw(base).ellipse(BASE, fill=255)
m[np.array(base) > 0] = 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.zeros_like(m)
if n > 1:
    keep[lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))] = 255
Image.fromarray(keep).save(sys.argv[2])
