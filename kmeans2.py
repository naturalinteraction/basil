import numpy as np
import cv2
from vision import *

img = cv2.imread('downloaded/test-test_2560x1920_2000_01_01-00_00.jpg')
img = cv2.resize(img, (256 * 3, 192 * 3))
img = ToHSV(img)
pixels = img.reshape((-1,3))

Z = np.float32(pixels)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
for K in range(5, 6):
    compactness,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    print(K, compactness)  # to find the elbow

basilico_hsv,basilico_stddev = LoadColorStats('basilico.pkl')

for n,c in enumerate(center):
    d = sum(abs(basilico_hsv - c))
    print(c, d)
    if d > 100:
        center[n] = (0, 0, 0)
    else:
        center[n] = (255, 255, 255)

center = np.uint8(center)
res = center[label.flatten()]
res2 = res.reshape((img.shape))

cv2.imshow('res2', res2)
cv2.imshow('orig', cv2.cvtColor(img, cv2.COLOR_HSV2BGR))

cv2.waitKey(0)
cv2.destroyAllWindows()

