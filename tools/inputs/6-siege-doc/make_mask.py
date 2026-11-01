"""Hint-based fg mask for Doc (speckled black-velvet backdrop, like Tachanka).

Rough outline polygons (body, gun, base, clip) as probable foreground,
an eroded core as sure foreground, everything else background; GrabCut refines.
Coordinates are in the padded photo (crop 750,525,1280,1310 with --pad 0.15).

    python3 make_mask.py <padded photo> <out fg_mask.png>
"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw

BODY = [(370, 138), (420, 158), (442, 200), (440, 240), (458, 262), (462, 300),
        (452, 345), (455, 385), (432, 398), (402, 402), (398, 420), (442, 470),
        (465, 505), (445, 512), (402, 485), (402, 520), (388, 560), (412, 580),
        (420, 620), (398, 652), (372, 662), (378, 700), (402, 758), (428, 785),
        (420, 802), (328, 802), (318, 712), (300, 682), (282, 652), (272, 700),
        (290, 726), (250, 738), (202, 722), (172, 662), (178, 628), (228, 598),
        (252, 560), (248, 500), (238, 452), (212, 422), (206, 362), (202, 330),
        (213, 288), (233, 250), (268, 220), (298, 210), (302, 170), (338, 143)]
BASE = [82, 696, 606, 916]          # whole base ellipse (bbox)
CLIP = [(405, 800), (470, 778), (542, 788), (556, 840), (552, 872), (460, 897),
        (440, 852), (408, 818)]

img = np.array(Image.open(sys.argv[1]).convert("RGB"))
h, w = img.shape[:2]
hint = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(hint)
d.polygon(BODY, fill=255)
d.ellipse(BASE, fill=255)
d.polygon(CLIP, fill=255)
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
# the base is dark like the velvet, so keep the whole base ellipse and clip regardless
keepshape = Image.new("L", (w, h), 0)
kd = ImageDraw.Draw(keepshape)
kd.ellipse(BASE, fill=255)
kd.polygon(CLIP, fill=255)
m[np.array(keepshape) > 0] = 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.zeros_like(m)
if n > 1:
    keep[lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))] = 255
Image.fromarray(keep).save(sys.argv[2])
