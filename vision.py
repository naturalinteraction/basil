import cv2
import numpy as np
from segment import *


white = (255, 255, 255)


'''
work in progress
'''
def ComputeImageDerivative(for_derivation, mask):
    for_derivation = cv2.GaussianBlur(for_derivation, (3, 3), 0)
    # also checkout blur = cv2.blur(img,(5,5)) and median = cv2.medianBlur(img,5) that is supposed to be good against salt-and-pepper noise
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


# kernel_size 3, 5, 7, 9, 11 ...
def Erode(input, kernel_size=3, iterations=1):
    return cv2.erode(input, np.ones((kernel_size, kernel_size), np.uint8), iterations)

# kernel_size 3, 5, 7, 9, 11 ...
def Dilate(input, kernel_size=3, iterations=1):
    return cv2.dilate(input, np.ones((kernel_size, kernel_size), np.uint8), iterations)

# kernel_size 3, 5, 7, 9, 11 ...
def Dilate(input, kernel_size=3, iterations=1):
    return cv2.dilate(input, np.ones((kernel_size, kernel_size), np.uint8), iterations)

# biomass_mask = cv2.morphologyEx(biomass_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # erode, then dilate
# biomass_mask = cv2.morphologyEx(biomass_mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))  # dilate, then erode


def ToHSV(bgr_image):
    return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

def ToGray(bgr_image):
    return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

def SegmentBiomass(hsv_image):
    target_color_0 = 36
    target_color_1 = 238
    target_color_2 = 164

    weight_color_0 = 6
    weight_color_1 = 3
    weight_color_2 = 1

    segmentation_threshold = 90 * 90 * 3

    return         Segment(hsv_image, target_color_0,  # optionally gaussian, median or simple blur
                                      target_color_1,
                                      target_color_2,
                                      weight_color_0,
                                      weight_color_1,
                                      weight_color_2, 
                                      segmentation_threshold)


def ContourStats(cnt):
    area = cv2.contourArea(cnt)
    x,y,w,h = cv2.boundingRect(cnt)
    rect_area = w * h
    if rect_area > 0:
        extent = float(area) / rect_area
    else:
      extent = 0
    hull = cv2.convexHull(cnt)
    hull_area = cv2.contourArea(hull)
    if hull_area > 0:
        solidity = float(area) / hull_area
    else:
        solidity = 0
    perimeter = cv2.arcLength(cnt, True)
    if perimeter > 0:
        jaggedness = len(cnt) / perimeter
    else:
        jaggedness = 0
    return area,extent,solidity,jaggedness

def DrawEllipses(image, ellipses, color):
    for e in ellipses:
        center,axes,angle = e
        center = (int(center[0]), int(center[1]))
        axes = (int(axes[0] * 0.5 + 4), int(axes[1] * 0.5 + 4))
        cv2.ellipse(image, center, axes, angle, 0.0, 360.0, color, 1)

def DrawCircles(image, circles, color):
    for c in circles:
        center,radius = c
        cv2.circle(image, (int(center[0]), int(center[1])), int(radius) + 4, color, 1)

