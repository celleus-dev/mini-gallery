"""Hint-based fg mask for Captain Marvel: saturated paint + face + base ellipse."""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw
img = np.array(Image.open(sys.argv[1]).convert("RGB"))
hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
m = ((hsv[..., 1] > 95) & (hsv[..., 2] > 55)).astype(np.uint8) * 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.zeros_like(m)
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] > 1500:
        keep[lab == i] = 255
pil = Image.fromarray(keep); d = ImageDraw.Draw(pil)
d.polygon([(405, 520), (470, 545), (540, 545), (560, 600), (520, 640), (450, 640), (395, 590)], fill=255)  # face
d.ellipse([440 - 325, 1222 - 175, 440 + 325, 1222 + 175], fill=255)  # whole base
k = cv2.morphologyEx(np.array(pil), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
k = cv2.morphologyEx(k, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
Image.fromarray(k).save(sys.argv[2])
