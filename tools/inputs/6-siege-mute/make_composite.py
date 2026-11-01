"""Build Mute's two-view composite, its fg mask and paints.json.

Left  = original-1.jpg (grey backdrop), crop 815,320,1470,1320 grown 15% per side
        (= 717,170,1568,1470), scaled to 1203 px high.
Right = original-2.jpg (black velvet), crop 830,300,1530,1225 grown 15% per side
        (= 725,161,1635,1364), unscaled (910x1203).
Right panel's mask and paints come from fg_mask-black.png / paints-black.json
(coordinates in its own padded crop), shifted right by the left panel's width.
Grey-panel shapes below are in original-1.jpg pixels.

    python3 make_composite.py      (run from this folder)
"""
import json, copy
import numpy as np, cv2
from PIL import Image, ImageDraw

G_BOX = (717, 170, 1568, 1470)
B_BOX = (725, 161, 1635, 1364)
H = B_BOX[3] - B_BOX[1]
S = H / (G_BOX[3] - G_BOX[1])

grey = Image.open("original-1.jpg").convert("RGB").crop(G_BOX)
grey = grey.resize((round(grey.width * S), H), Image.LANCZOS)
black = Image.open("original-2.jpg").convert("RGB").crop(B_BOX)
DX = grey.width
comp = Image.new("RGB", (DX + black.width, H))
comp.paste(grey, (0, 0)); comp.paste(black, (DX, 0))
comp.save("composite.jpg", quality=95)

def pt(x, y): return [round((x - G_BOX[0]) * S), round((y - G_BOX[1]) * S)]
def box(l, t, r, b): return pt(l, t) + pt(r, b)
def poly(ps): return [pt(*p) for p in ps]

body = poly([(1030, 330), (1100, 322), (1140, 380), (1150, 440), (1195, 465), (1205, 540),
             (1185, 600), (1170, 660), (1180, 730), (1195, 800), (1185, 860), (1210, 930),
             (1225, 1000), (1240, 1050), (1245, 1110), (1240, 1138), (1165, 1138), (1160, 1060),
             (1140, 1010), (1110, 950), (1095, 890), (1060, 900), (1050, 960), (1090, 1030),
             (1095, 1088), (1010, 1088), (938, 1085), (960, 1020), (990, 960), (975, 900),
             (945, 880), (930, 830), (925, 770), (960, 720), (985, 680), (960, 620),
             (920, 570), (920, 520), (945, 480), (965, 455), (1030, 445)])
gun = poly([(960, 520), (1100, 528), (1200, 558), (1260, 588), (1350, 638), (1460, 708),
            (1470, 742), (1440, 772), (1340, 722), (1240, 682), (1180, 652), (1100, 622), (965, 578)])
clip = poly([(1068, 1180), (1205, 1172), (1220, 1250), (1216, 1312), (1074, 1314), (1066, 1240)])
bootL = poly([(958, 995), (1062, 992), (1097, 1040), (1097, 1090), (936, 1090), (944, 1040)])
bootR = poly([(1158, 1035), (1238, 1035), (1250, 1142), (1162, 1142)])
BASE = box(815, 1000, 1405, 1318)
figure = box(915, 315, 1255, 1145)

# ---- fg mask: grey panel by GrabCut from the outline hints; black panel reused
img = np.array(grey)
h, w = img.shape[:2]
hint = Image.new("L", (w, h), 0); d = ImageDraw.Draw(hint)
for p in (body, gun, clip): d.polygon([tuple(q) for q in p], fill=255)
d.ellipse(BASE, fill=255)
prob = np.array(hint) > 0
gc = np.full((h, w), cv2.GC_BGD, np.uint8)
gc[cv2.dilate(prob.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0] = cv2.GC_PR_BGD
gc[prob] = cv2.GC_PR_FGD
gc[cv2.erode(prob.astype(np.uint8), np.ones((31, 31), np.uint8)) > 0] = cv2.GC_FGD
bgm, fgm = np.zeros((1, 65)), np.zeros((1, 65))
cv2.grabCut(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), gc, None, bgm, fgm, 5, cv2.GC_INIT_WITH_MASK)
m = np.isin(gc, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8) * 255
keep = Image.new("L", (w, h), 0); kd = ImageDraw.Draw(keep)
kd.ellipse(BASE, fill=255); kd.polygon([tuple(q) for q in clip], fill=255)
m[np.array(keep) > 0] = 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
gm = np.zeros_like(m)
if n > 1: gm[lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))] = 255
full = np.zeros((H, comp.width), np.uint8)
full[:, :DX] = gm
full[:, DX:] = np.array(Image.open("fg_mask-black.png").convert("L"))
Image.fromarray(full).save("fg_mask.png")

# ---- paints: shift the black panel's shapes, add the grey panel's
def shift(r):
    if isinstance(r, list): return [r[0] + DX, r[1], r[2] + DX, r[3]]
    if "polygon" in r: return {"polygon": [[x + DX, y] for x, y in r["polygon"]]}
    if "ellipse" in r: cx, cy, rx, ry = r["ellipse"]; return {"ellipse": [cx + DX, cy, rx, ry]}
    raise ValueError(r)

def ell(b): l, t, r, bb = b; return {"ellipse": [(l + r) / 2, (t + bb) / 2, (r - l) / 2, (bb - t) / 2]}

grey_add = {
    "Tyrian Navy": dict(samples=[(950, 560), (1190, 520), (1160, 900), (1200, 950), (1110, 850), (985, 530), (960, 600)],
                        regions=[figure], exclude=[{"polygon": gun}, {"polygon": bootL}, {"polygon": bootR}]),
    "Camo Cloak": dict(samples=[(1010, 720), (1140, 730), (1080, 700), (1150, 770), (1050, 750)],
                       regions=[box(955, 675, 1205, 805)]),
    "Gravelord Grey": dict(samples=[(1050, 620), (1130, 620), (1140, 860), (980, 800), (1100, 650)],
                           regions=[box(920, 560, 1220, 900)]),
    "Grim Black": dict(samples=[(1300, 660), (1400, 700), (1050, 560), (1000, 1050), (1190, 1100), (1080, 420), (1000, 920)],
                       regions=[{"polygon": gun}, {"polygon": bootL}, {"polygon": bootR}, box(1020, 325, 1150, 470)]),
    "Dark Wood": dict(samples=[(948, 790), (950, 820)], regions=[box(928, 760, 978, 880)]),
    "Electric Blue": dict(samples=[(1070, 400), (1100, 395), (1060, 405)], regions=[box(1040, 378, 1142, 422)]),
    "Hot Orange": dict(samples=[(1110, 1250), (1150, 1220), (1180, 1280)], regions=[{"polygon": clip}]),
    "Black": dict(samples=[(900, 1200), (1000, 1270), (1300, 1200), (1350, 1110), (900, 1100), (1100, 1140), (1300, 1260)],
                  regions=[ell(BASE)], exclude=[{"polygon": clip}, {"polygon": bootL}, {"polygon": bootR}]),
}
out = []
for p in json.load(open("paints-black.json")):
    q = copy.deepcopy(p)
    q["samples"] = [[x + DX, y] for x, y in p.get("samples", [])]
    q["regions"] = [shift(r) for r in p.get("regions", [])]
    if "exclude_regions" in p: q["exclude_regions"] = [shift(r) for r in p["exclude_regions"]]
    g = grey_add.get(p["name"])
    if g:
        q["samples"] = [pt(*s) for s in g["samples"]] + q["samples"]
        q["regions"] = g["regions"] + q["regions"]
        if g.get("exclude"): q["exclude_regions"] = g["exclude"] + q.get("exclude_regions", [])
    out.append(q)
# the site keeps photos at most 1600 px wide, so scale the composite (and every
# coordinate) down to that here; regions must be in the saved photo's pixels
F = min(1.0, 1600 / comp.width)
def sc(r):
    if isinstance(r, list): return [round(v * F) for v in r]
    if "polygon" in r: return {"polygon": [[round(x * F), round(y * F)] for x, y in r["polygon"]]}
    return {"ellipse": [round(v * F) for v in r["ellipse"]]}
for q in out:
    q["samples"] = [[round(x * F), round(y * F)] for x, y in q["samples"]]
    q["regions"] = [sc(r) for r in q["regions"]]
    if "exclude_regions" in q: q["exclude_regions"] = [sc(r) for r in q["exclude_regions"]]
size = (round(comp.width * F), round(comp.height * F))
comp.resize(size, Image.LANCZOS).save("composite.jpg", quality=95)
Image.fromarray(full).resize(size, Image.NEAREST).save("fg_mask.png")
json.dump(out, open("paints.json", "w"), indent=2)
print("composite", size, "left panel width", round(DX * F))
