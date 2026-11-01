"""Hint-based fg mask for Mute (speckled black-velvet backdrop).

Rough outline polygons (body, gun, base, clip) as probable foreground,
an eroded core as sure foreground, everything else background; GrabCut refines.
Coordinates are in the padded photo (crop 830,300,1530,1225 with --pad 0.15).

    python3 make_mask.py <padded photo> <out fg_mask.png>
"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw

img = np.array(Image.open(sys.argv[1]).convert("RGB"))
h, w = img.shape[:2]
hint = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(hint)
body = [(300, 150), (360, 138), (420, 170), (440, 250), (480, 270), (500, 330),
        (495, 400), (475, 450), (460, 470), (465, 560), (480, 640), (500, 720),
        (500, 780), (510, 830), (550, 870), (548, 905), (450, 905), (455, 830),
        (430, 720), (410, 650), (370, 640), (350, 700), (320, 790), (300, 850),
        (275, 905), (195, 905), (225, 840), (245, 750), (245, 690), (212, 675),
        (212, 575), (255, 560), (265, 500), (260, 450), (245, 400), (228, 370),
        (232, 300), (260, 258), (295, 250)]
gun = [(270, 300), (420, 305), (500, 330), (560, 355), (680, 405), (792, 428),
       (797, 452), (778, 482), (680, 452), (560, 405), (500, 382), (430, 358),
       (280, 352)]
clip = [(485, 935), (560, 906), (642, 903), (652, 960), (642, 1018), (560, 1038),
        (535, 1000), (490, 948)]
BASE = [125, 820, 665, 1046]
d.polygon(body, fill=255)
d.polygon(gun, fill=255)
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
