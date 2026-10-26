import cv2, numpy as np, sys, json
from scipy import ndimage as ndi
img=cv2.imread(sys.argv[1]); h,w=img.shape[:2]
H=json.load(open(sys.argv[4]))
gc=np.full((h,w),cv2.GC_BGD,np.uint8)
for x,y,rw,rh in H["rects"]: gc[y:y+rh,x:x+rw]=cv2.GC_PR_BGD
for s in H["fg"]:
    pts=np.array(s,np.int32)*2
    if len(pts)==1: cv2.circle(gc,tuple(pts[0]),10,cv2.GC_FGD,-1)
    else: cv2.polylines(gc,[pts],False,cv2.GC_FGD,12)
for s in H.get("bg",[]):
    pts=np.array(s,np.int32)*2; cv2.polylines(gc,[pts],False,cv2.GC_BGD,10)
b=np.zeros((1,65)); f=np.zeros((1,65))
cv2.grabCut(img,gc,None,b,f,10,cv2.GC_INIT_WITH_MASK)
m=(gc==1)|(gc==3)
m=ndi.binary_opening(m,iterations=2); m=ndi.binary_closing(m,iterations=3)
lab,n=ndi.label(m); s=ndi.sum(m,lab,range(1,n+1)); keep=np.zeros(n+1,bool); keep[1:]=s>m.sum()*0.05; m=keep[lab]
holes=ndi.binary_fill_holes(m)&~m; l2,n2=ndi.label(holes)
if n2:
    sz=ndi.sum(holes,l2,range(1,n2+1)); small=np.zeros(n2+1,bool); small[1:]=sz<m.sum()*0.002; m|=small[l2]
cv2.imwrite(sys.argv[2],(m*255).astype(np.uint8))
v=img.copy(); v[~m]=(v[~m]*0.25+np.array([90,60,20])*0.75).astype(np.uint8)
cv2.imwrite(sys.argv[3],cv2.resize(v,(800,644)))
