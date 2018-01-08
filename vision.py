import cv2
import numpy as np


'''
work in progress
'''
def ComputeImageDerivative(for_derivation, mask):
    for_derivation = cv2.GaussianBlur(for_derivation, (3, 3), 0)
    for_derivation = cv2.GaussianBlur(for_derivation, (5, 5), 0)
    # laplacian = cv2.Laplacian(for_derivation, cv2.CV_64F)
    mult = 5
    if False:
        sobelx = cv2.Sobel(for_derivation, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(for_derivation, cv2.CV_64F, 0, 1, ksize=3)
    else:
        sobelx = cv2.Scharr(for_derivation, cv2.CV_64F, 1, 0)
        sobely = cv2.Scharr(for_derivation, cv2.CV_64F, 0, 1)
        mult = 1.3
    if False:
        abs_sobelx = np.absolute(sobelx)
        abs_sobely = np.absolute(sobely)
        abs_sobelx = np.uint8(abs_sobelx)
        abs_sobely = np.uint8(abs_sobely)
    else:
        abs_sobelx = cv2.convertScaleAbs(sobelx)
        abs_sobely = cv2.convertScaleAbs(sobely)
    sobel = cv2.addWeighted(abs_sobelx, 0.5 * mult, abs_sobely, 0.5 * mult, 0.0)
    sobel = cv2.bitwise_and(sobel, sobel, mask=mask)
    return sobel


def Histogram(channel, output):
    hist = cv2.calcHist([channel], [0], None, [64], [1,256])
    max_hist = max(hist)
    for i in range(len(hist)):
        cv2.line(output, (i * 30, 1000), (i * 30, 1000 - hist[i] * 1000 / max_hist), (0, 255, 255), 30)
