"""Hint-based fg mask for Recruit (Defender), two models on one speckled black-velvet photo.

Rough outline polygons per model as probable foreground, an eroded core as sure
foreground, everything else background; GrabCut refines. Both whole base ellipses kept.
Coordinates are in photo.jpg (original.jpg cropped 256,220,1934,1430 and scaled to 1594 wide).

    python3 make_mask.py photo.jpg fg_mask.png
"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw

img = np.array(Image.open(sys.argv[1]).convert("RGB"))
h, w = img.shape[:2]
m1 = [(375, 155), (462, 158), (472, 225), (502, 238), (522, 288), (565, 328),
      (645, 398), (645, 448), (600, 455), (560, 445), (545, 500), (562, 560),
      (562, 640), (568, 700), (562, 775), (498, 785), (495, 700), (478, 610),
      (425, 650), (385, 720), (345, 775), (272, 765), (318, 700), (308, 560),
      (296, 470), (302, 380), (308, 280), (328, 240), (372, 225)]
m2 = [(1103, 165), (1202, 168), (1218, 235), (1252, 278), (1302, 298), (1352, 358),
      (1452, 418), (1458, 455), (1400, 460), (1300, 425), (1252, 440), (1242, 500),
      (1262, 560), (1272, 640), (1272, 720), (1292, 768), (1292, 805), (1198, 805),
      (1198, 722), (1170, 645), (1110, 700), (1062, 760), (1042, 812), (958, 812),
      (998, 758), (998, 660), (988, 540), (1008, 450), (1028, 350), (1038, 258),
      (1078, 228), (1108, 228)]
bases = [[205, 748, 648, 912], [885, 775, 1398, 978]]
clips = [[(503, 790), (588, 772), (636, 800), (638, 860), (588, 888), (543, 885), (530, 835)],
         [(1262, 860), (1360, 828), (1395, 848), (1393, 912), (1330, 950), (1290, 942)]]

hint = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(hint)
for p in (m1, m2): d.polygon(p, fill=255)
for b in bases: d.ellipse(b, fill=255)
for c in clips: d.polygon(c, fill=255)
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
# the velvet is ~10 brightness, the darkest paint (Grim Black) ~35+: drop velvet pixels
velvet = (img.max(axis=2) < 24).astype(np.uint8)
velvet = cv2.morphologyEx(velvet, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
# torso shadows (black undershirt under the vest) stay
torso = Image.new("L", (w, h), 0)
td = ImageDraw.Draw(torso)
td.polygon([(345, 330), (505, 330), (520, 420), (470, 445), (360, 440)], fill=255)
td.polygon([(1050, 330), (1270, 350), (1270, 450), (1150, 475), (1050, 460)], fill=255)
velvet[np.array(torso) > 0] = 0
m[velvet > 0] = 0
# put back small dark recesses enclosed by the mini
inv = (m == 0).astype(np.uint8)
n0, lab0, st0, _ = cv2.connectedComponentsWithStats(inv)
for i in range(1, n0):
    x, y, bw, bh, a = st0[i]
    if a < 3000 and x > 0 and y > 0 and x + bw < w and y + bh < h:
        m[lab0 == i] = 255
keepm = Image.new("L", (w, h), 0)
kd = ImageDraw.Draw(keepm)
for b in bases: kd.ellipse(b, fill=255)
for c in clips: kd.polygon(c, fill=255)
m[np.array(keepm) > 0] = 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.zeros_like(m)
if n > 1:
    order = 1 + np.argsort(st[1:, cv2.CC_STAT_AREA])[::-1]
    for i in order[:2]:
        keep[lab == i] = 255
Image.fromarray(keep).save(sys.argv[2])
