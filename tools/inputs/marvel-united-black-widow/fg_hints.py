import cv2, numpy as np, sys
from PIL import Image
img = np.array(Image.open(sys.argv[1]).convert('RGB').crop((380,760,1380,2000)))
h,w = img.shape[:2]
g = [(300,110),(390,85),(500,90),(620,150),(700,220),(750,285),(920,228),(935,250),(725,355),(650,395),(625,470),(650,560),(700,640),(710,700),(780,750),(800,880),(830,990),(825,1080),(700,1150),(450,1165),(200,1125),(120,1050),(135,900),(200,810),(230,700),(220,620),(260,540),(285,480),(200,485),(65,485),(60,440),(150,320),(200,200)]
poly = np.array(g, np.int32)
out = np.zeros((h,w),np.uint8); cv2.fillPoly(out,[poly],1)
mask = np.full((h,w), cv2.GC_BGD, np.uint8)
mask[cv2.dilate(out,np.ones((41,41)))>0] = cv2.GC_PR_BGD
mask[out>0] = cv2.GC_PR_FGD
mask[cv2.erode(out,np.ones((61,61)))>0] = cv2.GC_FGD
bgd=np.zeros((1,65)); fgd=np.zeros((1,65))
cv2.grabCut(cv2.cvtColor(img,cv2.COLOR_RGB2BGR),mask,None,bgd,fgd,6,cv2.GC_INIT_WITH_MASK)
fg = np.where((mask==1)|(mask==3),255,0).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(fg)
big = 1+np.argmax(st[1:,4]); fg = np.where(lab==big,255,0).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9,9)))
Image.fromarray(fg).save(sys.argv[2])
v = img.copy(); v[fg==0] = (v[fg==0]*0.25).astype(np.uint8)
Image.fromarray(v).save(sys.argv[3])
