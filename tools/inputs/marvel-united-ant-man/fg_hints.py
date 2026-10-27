import cv2, numpy as np, sys
from PIL import Image
img = np.array(Image.open(sys.argv[1]).convert('RGB').crop((370,560,1340,1960)))
h,w = img.shape[:2]
g = [(170,210),(380,100),(450,100),(500,160),(700,70),(760,80),(780,130),(850,330),(870,520),(980,650),(990,900),(950,1000),(1000,1240),(930,1330),(700,1410),(400,1410),(130,1360),(60,1250),(100,1000),(140,880),(270,820),(280,680),(240,560),(150,490),(140,400),(170,300)]
poly = np.array([(x-40,y-40) for x,y in g], np.int32)
out = np.zeros((h,w),np.uint8); cv2.fillPoly(out,[poly],1)
mask = np.full((h,w), cv2.GC_BGD, np.uint8)
mask[cv2.dilate(out,np.ones((61,61)))>0] = cv2.GC_PR_BGD
mask[out>0] = cv2.GC_PR_FGD
mask[cv2.erode(out,np.ones((81,81)))>0] = cv2.GC_FGD
gap=np.array([(618,645),(700,618),(790,640),(812,690),(815,830),(770,858),(690,858),(640,820),(622,760)],np.int32)
cv2.fillPoly(mask,[gap],cv2.GC_BGD)
bgd=np.zeros((1,65)); fgd=np.zeros((1,65))
cv2.grabCut(cv2.cvtColor(img,cv2.COLOR_RGB2BGR),mask,None,bgd,fgd,6,cv2.GC_INIT_WITH_MASK)
fg = np.where((mask==1)|(mask==3),255,0).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(fg)
big = 1+np.argmax(st[1:,4]); fg = np.where(lab==big,255,0).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9,9)))
Image.fromarray(fg).save(sys.argv[2])
v = img.copy(); v[fg==0] = (v[fg==0]*0.25).astype(np.uint8)
Image.fromarray(v).save(sys.argv[3])
