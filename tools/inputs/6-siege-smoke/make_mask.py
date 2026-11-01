"""Hint-based fg mask for Smoke (speckled black-velvet backdrop).

Rough outline polygons (body + gun, base, clip) as probable foreground,
an eroded core as sure foreground, everything else background; GrabCut refines.
Coordinates are in the padded photo (crop 870,515,1520,1290 with --pad 0.15).

    python3 make_mask.py <padded photo> <out fg_mask.png>
"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw

img = np.array(Image.open(sys.argv[1]).convert("RGB"))
h, w = img.shape[:2]
hint = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(hint)
body = [(118, 128), (195, 118), (198, 165), (170, 205), (165, 235), (235, 225),
        (245, 135), (300, 120), (340, 150), (370, 175), (400, 198), (510, 203),
        (540, 196), (545, 148), (600, 140), (738, 212), (732, 242), (690, 245),
        (670, 282), (600, 300), (560, 315), (548, 260), (515, 245), (415, 255),
        (418, 300), (410, 370), (425, 410), (440, 470), (470, 560), (500, 625),
        (500, 665), (530, 700), (548, 740), (480, 745), (470, 690), (455, 650),
        (420, 620), (400, 580), (370, 520), (330, 470), (300, 520), (300, 600),
        (290, 650), (270, 700), (210, 720), (200, 700), (225, 650), (215, 590),
        (205, 540), (215, 475), (240, 440), (235, 400), (232, 350), (205, 320),
        (160, 330), (120, 300), (112, 250), (128, 210)]
clip = [(505, 760), (560, 738), (625, 740), (640, 790), (630, 840), (560, 855),
        (535, 840), (510, 790)]
BASE = [152, 670, 642, 880]
d.polygon(body, fill=255)
d.ellipse(BASE, fill=255)
d.polygon(clip, fill=255)
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
# the base and clip are kept whole regardless (base is dark like the velvet)
keepers = Image.new("L", (w, h), 0)
kd = ImageDraw.Draw(keepers)
kd.ellipse(BASE, fill=255)
kd.polygon(clip, fill=255)
m[np.array(keepers) > 0] = 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.zeros_like(m)
if n > 1:
    keep[lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))] = 255
Image.fromarray(keep).save(sys.argv[2])
