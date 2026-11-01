"""Hint-based fg mask for Kapkan (composite: black velvet view left, grey backdrop view right).

Rough outline polygons (body, gun, base, clip) per view as probable foreground,
an eroded core as sure foreground, everything else background; GrabCut refines.
Whole base ellipses and clips are kept regardless (the base is dark like the velvet).
Coordinates are in composite.jpg (1600x913).

    python3 make_mask.py composite.jpg fg_mask.png
"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw

img = np.array(Image.open(sys.argv[1]).convert("RGB"))
h, w = img.shape[:2]

L_BODY = [(460, 130), (500, 115), (560, 150), (600, 175), (630, 220), (645, 280),
          (648, 350), (628, 400), (600, 440), (590, 470), (598, 560), (592, 640),
          (560, 668), (480, 672), (470, 692), (408, 692), (402, 600), (378, 530),
          (372, 480), (398, 430), (383, 390), (378, 350), (418, 330), (385, 240),
          (440, 205), (458, 180)]
L_GUN = [(95, 275), (200, 260), (500, 266), (545, 300), (500, 312), (360, 322),
         (342, 345), (332, 410), (297, 442), (272, 430), (298, 360), (278, 337),
         (210, 302), (108, 314)]
L_BASE = [240, 600, 752, 798]
L_CLIP = [(203, 665), (300, 658), (338, 690), (322, 722), (284, 782), (208, 782)]

R_BODY = [(1225, 108), (1272, 104), (1292, 138), (1342, 138), (1388, 165), (1402, 248),
          (1432, 262), (1433, 342), (1402, 356), (1407, 442), (1362, 452), (1358, 570),
          (1352, 652), (1310, 668), (1262, 652), (1272, 692), (1198, 702), (1193, 600),
          (1172, 560), (1168, 470), (1178, 420), (1163, 390), (1168, 355), (1148, 300),
          (1138, 250), (1180, 198), (1222, 193)]
R_GUN = [(922, 333), (1030, 298), (1100, 278), (1342, 292), (1342, 322), (1210, 347),
         (1180, 357), (1152, 382), (1142, 452), (1100, 472), (1083, 452), (1108, 390),
         (1030, 342), (933, 368)]
R_BASE = [988, 555, 1527, 830]
R_CLIP = [(993, 703), (1090, 686), (1142, 703), (1132, 742), (1102, 818), (998, 822)]

hint = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(hint)
for poly in (L_BODY, L_GUN, L_CLIP, R_BODY, R_GUN, R_CLIP):
    d.polygon(poly, fill=255)
d.ellipse(L_BASE, fill=255)
d.ellipse(R_BASE, fill=255)
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

keep_shapes = Image.new("L", (w, h), 0)
k = ImageDraw.Draw(keep_shapes)
k.ellipse(L_BASE, fill=255)
k.ellipse(R_BASE, fill=255)
k.polygon(L_CLIP, fill=255)
k.polygon(R_CLIP, fill=255)
m[np.array(keep_shapes) > 0] = 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

# keep the largest blob on each side
out = np.zeros_like(m)
split = 836
for x0, x1 in ((0, split), (split, w)):
    part = np.zeros_like(m)
    part[:, x0:x1] = m[:, x0:x1]
    n, lab, st, _ = cv2.connectedComponentsWithStats(part)
    if n > 1:
        out[lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))] = 255
Image.fromarray(out).save(sys.argv[2])
