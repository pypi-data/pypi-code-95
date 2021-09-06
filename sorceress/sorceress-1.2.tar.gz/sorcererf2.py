import cv2
import numpy as np

img=128*np.ones((800,800,3),dtype=np.uint8)
h,w,_=img.shape

#black rectangles
for i in range(0,h,160):
    for j in range(0,w,160):
        cv2.rectangle(img,(i,j),(i+75,j+75),(0,0,0),5)
        cv2.rectangle(img, (i + 80, j + 80), (i + 155, j + 155), (0, 0, 0), 5)

for i in range(0,h,160):
    for j in range(0,w,160):
        cv2.rectangle(img,(i+80,j),(i+155,j+75),(255,255,255),2)
        cv2.rectangle(img, (i, j + 80), (i + 75, j + 155), (255, 255, 255), 2)

cv2.imwrite("optikil/last.jpg",img)
cv2.imshow("img",img)
cv2.waitKey(0)