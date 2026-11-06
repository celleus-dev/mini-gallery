"""Fg mask for Colossus (Nov 5 2026 photo, dark velvet backdrop):
bright/saturated paint, plus anything above near-black inside the body outline
(backdrop is V~12, so shadows deeper than that stay out), plus the whole base.
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
pil = Image.new('L', keep.shape[::-1], 0); d = ImageDraw.Draw(pil)
d.polygon([(130, 330), (300, 300), (440, 240), (450, 180), (660, 190), (680, 330), (800, 480), (890, 640),
           (880, 740), (830, 790), (760, 850), (780, 970), (700, 980), (640, 880), (560, 820), (470, 830),
           (390, 880), (380, 960), (330, 1030), (250, 1030), (300, 850), (320, 760), (360, 700), (380, 640),
           (330, 560), (300, 520), (200, 520), (150, 450)], fill=255)  # body
body = np.array(pil) > 0
pil = Image.fromarray(np.where((keep > 0) | (body & (hsv[..., 2] > 32)), 255, 0).astype(np.uint8))
d = ImageDraw.Draw(pil)
d.polygon([(445, 172), (662, 188), (668, 252), (600, 236), (500, 248), (448, 282)], fill=255)  # hair (near-black)
d.ellipse([525 - 312, 1135 - 105, 525 + 312, 1135 + 105], fill=255)  # whole base
k = np.array(pil)
k = cv2.morphologyEx(k, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
Image.fromarray(k).save(sys.argv[2])
