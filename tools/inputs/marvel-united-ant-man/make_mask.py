"""Fg mask for Ant-Man (Nov 5 2026 photo, dark velvet backdrop):
bright/saturated paint + body and arm outlines (dark undersuit) + coin + whole base.
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
d.polygon([(230, 250), (260, 170), (300, 140), (450, 140), (510, 200), (520, 300), (580, 420), (620, 500),
           (640, 620), (640, 700), (380, 760), (200, 700), (230, 640), (210, 560), (210, 450), (230, 350)], fill=255)  # body
d.polygon([(120, 300), (230, 260), (240, 350), (200, 440), (150, 430), (120, 380)], fill=255)  # left arm
d.ellipse([380 - 272, 715 - 58, 380 + 272, 715 + 58], fill=255)  # coin
d.ellipse([372 - 280, 860 - 115, 372 + 280, 860 + 115], fill=255)  # whole base
k = ndi.binary_fill_holes(np.array(pil) > 0).astype(np.uint8) * 255
k = cv2.morphologyEx(k, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
Image.fromarray(k).save(sys.argv[2])
