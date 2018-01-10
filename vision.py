import cv2
import numpy as np
from utility import *
from segment import *
from collections import namedtuple


white = (255, 255, 255)


'''
rectangle
'''
rectangle = namedtuple('rectangle', 'xmin ymin xmax ymax')

def rectangle_union(a, b):
    return rectangle(min(a.xmin, b.xmin), min(a.ymin, b.ymin), max(a.xmax, b.xmax), max(a.ymax, b.ymax))


'''
blurs
'''
def GaussianBlurred(image, size=3):
    return cv2.GaussianBlur(image, (size, size), 0)

def Blurred(image, size=3):
    return cv2.blur(image, (size, size))

def MedianBlurred(image, size=3):
    return cv2.medianBlur(image, size)  # supposed to be good against salt-and-pepper noise


'''
image derivatives
'''
def ComputeImageDerivative(for_derivation, mask):
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

def ToThree(one_channel_image):
    return cv2.cvtColor(one_channel_image, cv2.COLOR_GRAY2BGR)

def Inverted(image):
    return cv2.bitwise_not(image)

def MaskedImage(image, mask):
    # return cv2.multiply(image, ToThree(mask), scale = 1.0 / 255.0)
    return cv2.bitwise_and(image, image, mask=mask)

def SegmentBiomass(hsv_image, target_color_0, target_color_1, target_color_2,
                              weight_color_0, weight_color_1, weight_color_2, segmentation_threshold):

    return         Segment(hsv_image, target_color_0,
                                      target_color_1,
                                      target_color_2,
                                      weight_color_0,
                                      weight_color_1,
                                      weight_color_2, 
                                      segmentation_threshold)


def FillHoles(biomass_mask, bgr, hsv, target_color_0, target_color_1, target_color_2,
                                      weight_color_0, weight_color_1, weight_color_2, segmentation_threshold):
    # inverted mask, so that we can analyze the holes as white blobs against a black background
    ignored1, contours, ignored2 = cv2.findContours(Inverted(biomass_mask), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    holes = 0
    accepted_holes_mask = np.zeros(bgr.shape[:2], np.uint8)
    refused_holes_mask = np.zeros(bgr.shape[:2], np.uint8)

    ellipses = list()
    circles = list()

    for cnt in contours:
        area = cv2.contourArea(cnt)

        ### print(ContourStats(cnt))

        if area < 70 * 70:
            hole_mask = np.zeros(bgr.shape[:2], np.uint8)
            cv2.drawContours(hole_mask, [cnt], -1, 255, -1)
            mean = cv2.mean(hsv, mask=hole_mask)[0:3]

            color_distance = pow(mean[0] - target_color_0, 2) * weight_color_0 +  \
                             pow(mean[1] - target_color_1, 2) * weight_color_1 +  \
                             pow(mean[2] - target_color_2, 2) * weight_color_2

            if color_distance < segmentation_threshold:
                cv2.fillPoly(biomass_mask, pts = [cnt], color=(255))
                cv2.fillPoly(accepted_holes_mask, pts = [cnt], color=(255))
                # print(str(holes) + " area " + str(area) + ' dist ' + str(color_distance) + ' mean ' + str(mean))
                holes += 1
                if area > 5 * 5:
                    if len(cnt) > 4:
                        ellipses.append(cv2.fitEllipse(cnt))
                    else:
                        circles.append(cv2.minEnclosingCircle(cnt))
            else:
                cv2.fillPoly(refused_holes_mask, pts = [cnt], color=(255))

    # print('holes ' + str(holes))
    return accepted_holes_mask,refused_holes_mask,ellipses,circles


class BoundingBox:
    rect = None

    def Reset(self):
        self.rect = None

    def Update(self, biomass_mask, output_image=False):
        nonzero = cv2.findNonZero(biomass_mask)
        if not(nonzero is None):
            count = len(nonzero)
            # print(('biomass count ' + str(count)))
            bbx,bby,bbw,bbh = cv2.boundingRect(nonzero)
            current_rect = rectangle(int(bbx), int(bby), int(bbx + bbw), int(bby + bbh))
            if self.rect == None:
                self.rect = current_rect
                # print('initializing', self.rect)
            # else:
            #     print('valid', self.rect)
            self.rect = rectangle_union(self.rect, current_rect)
            if output_image.__class__.__name__ == 'ndarray':
                cv2.rectangle(output_image, (self.rect.xmin, self.rect.ymin),
                                            (self.rect.xmax, self.rect.ymax), white, 2)
            return count
        else:
            return 0


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

