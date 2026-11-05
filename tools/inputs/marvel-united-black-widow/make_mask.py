"""Fg mask for Black Widow (Nov 5 2026 photo, dark velvet backdrop):
bright/saturated paint, largest blob, holes filled, plus the whole base ellipse.
Usage: make_mask.py <padded photo> <out.png>"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
img = np.array(Image.open(sys.argv[1]).convert("RGB"))
hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
m = ((hsv[..., 2] > 58) | ((hsv[..., 1] > 100) & (hsv[..., 2] > 45))).astype(np.uint8) * 255
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.where(lab == 1 + np.argmax(st[1:, 4]), 255, 0).astype(np.uint8)
pil = Image.fromarray(keep); d = ImageDraw.Draw(pil)
cx, cy, rx, ry = 450, 915, 285, 115   # whole round base
d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
# dark parts the threshold misses: hair underside, left arm and leg
d.polygon([(195, 415), (330, 385), (350, 455), (300, 470), (240, 450)], fill=255)
d.polygon([(300, 460), (340, 445), (330, 560), (300, 640), (330, 700), (370, 790), (320, 810), (250, 720), (240, 620), (270, 520)], fill=255)
k = ndi.binary_fill_holes(np.array(pil) > 0).astype(np.uint8) * 255
k = cv2.morphologyEx(k, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
Image.fromarray(k).save(sys.argv[2])
