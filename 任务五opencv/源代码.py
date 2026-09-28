
import cv2
import numpy as np
from matplotlib import pyplot as plt
img=cv2.imread("原图.jpg")
# 形态学卷积核设为5*5
kernel=np.ones((5,5),np.uint8)
# 将照片从BGR转成HSV降低光照影响
img3=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
lower_yellow=np.array([15,80,80])
upper_yellow=np.array([35,255,255])
# 获取二值图
mask=cv2.inRange(img3,lower_yellow,upper_yellow)
# 进行形态学开运算再闭运算
opening=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
close=cv2.morphologyEx(opening,cv2.MORPH_CLOSE,kernel)
# 寻找二值图轮廓
contours,hierarchy=cv2.findContours(close,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
# 复制原图
draw=img.copy()
# 画出轮廓图
cv2.drawContours(draw,contours,-1,(0,255,0),2)
height,width=close.shape
# 列扫描求赛道中心线
for y in range(0,height):
  row=close[y,:]
  idx=np.where(row==255)[0]
  if len(idx)>10:
    x_left =idx[0]
    x_right=idx[-1]
    x_mid =(x_left+x_right)//2
    cv2.circle(draw,(x_mid,y),1,(0,0,255),-1)
# 进行BGR转RGB
res=cv2.cvtColor(draw,cv2.COLOR_BGR2RGB)
plt.imshow(res)
plt.show()