"""Hint-based fg mask for Tachanka (speckled black-velvet backdrop).

Rough outline polygons (body, gun, drum, base, clip) as probable foreground,
an eroded core as sure foreground, everything else background; GrabCut refines.
Coordinates are in the padded photo (crop 480,490,1340,1540 with --pad 0.15).

    python3 make_mask.py <padded photo> <out fg_mask.png>
"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw

img = np.array(Image.open(sys.argv[1]).convert("RGB"))
h, w = img.shape[:2]
hint = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(hint)
body = [(355, 168), (420, 180), (458, 225), (455, 300), (500, 315), (545, 345),
        (600, 400), (680, 445), (690, 470), (600, 480), (520, 470), (510, 520),
        (520, 600), (575, 610), (580, 700), (600, 830), (610, 870), (660, 960),
        (670, 1000), (545, 990), (530, 940), (480, 750), (435, 690), (400, 760),
        (300, 780), (250, 880), (245, 1000), (145, 1005), (150, 950), (195, 850),
        (200, 720), (235, 660), (210, 600), (205, 520), (200, 400), (215, 350),
        (260, 310), (300, 300), (298, 210)]
gun = [(310, 480), (450, 480), (550, 490), (760, 500), (775, 530), (900, 545),
       (975, 560), (978, 602), (900, 600), (690, 575), (530, 560), (420, 545),
       (330, 505)]
d.polygon(body, fill=255)
d.polygon(gun, fill=255)
d.ellipse([540, 455, 722, 560], fill=255)                 # drum
d.ellipse([120, 925, 730, 1200], fill=255)                # whole base
d.polygon([(568, 1050), (650, 1008), (722, 1030), (724, 1105), (662, 1170),
           (625, 1168)], fill=255)                        # clip
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
# the base is dark like the velvet, so keep the whole base ellipse regardless
base = Image.new("L", (w, h), 0)
ImageDraw.Draw(base).ellipse([120, 925, 730, 1200], fill=255)
m[np.array(base) > 0] = 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.zeros_like(m)
if n > 1:
    keep[lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))] = 255
Image.fromarray(keep).save(sys.argv[2])
