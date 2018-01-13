import cv2
import numpy as np
from utility import *
from segment import *
from collections import namedtuple
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


white = (255, 255, 255)


def ScatterPlotHSV(image, title='HSV'):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    small = cv2.resize(image, (0, 0), fx=0.01, fy=0.01)
    height, width, depth = small.shape
    for x in range(0, width):
       for y in range (0, height):
           col = small[y, x]
           ax.scatter(col[0], col[1], col[2], c='#%02x%02x%02x' % (col[2], col[1], col[0]))  # BGR >>> RGB
    ax.set_xlabel('H')
    ax.set_ylabel('S')
    ax.set_zlabel('V')
    plt.gcf().canvas.set_window_title(title)
    plt.show()


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

def ImageWithColor(image_for_shape, color):
    image = np.zeros(image_for_shape.shape[:], np.uint8)
    image[:] = color
    return image

def ComputeStatsOfMaskedImage(image, mask):
    mean,stddev = cv2.meanStdDev(image, mask=mask)
    return (float(mean[0]), float(mean[1]), float(mean[2])),(float(stddev[0]), float(stddev[1]), float(stddev[2]))

def ToHSV(bgr_image):
    return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

def BGRToGray(bgr_image):
    return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

def GrayToBGR(one_channel_image):
    return cv2.cvtColor(one_channel_image, cv2.COLOR_GRAY2BGR)

def Inverted(image):
    return cv2.bitwise_not(image)

def MaskedImage(image, mask):
    return cv2.bitwise_and(image, image, mask=mask)

def MaskForTone(image, filename, threshold):
    mean,stddev = LoadColorStats(filename)
    variance = stddev ** 2
    return SegmentBiomass(image, mean, 1.0 / variance, threshold)

def SegmentBiomass(hsv_image, target,
                              weight, segmentation_threshold):
    return         Segment(hsv_image,  target[0],
                                       target[1],
                                       target[2],
                                       weight[0],
                                       weight[1],
                                       weight[2],
                                       segmentation_threshold)

def FillHoles(biomass_mask, bgr, hsv, target, weight, segmentation_threshold, max_area=30 * 30, greater_than=False):
    ignored, contours, hierarchy = cv2.findContours(biomass_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    accepted_holes_mask = np.zeros(bgr.shape[:2], np.uint8)
    refused_holes_mask = np.zeros(bgr.shape[:2], np.uint8)
    circles = list()
    # cs = ColorStatistics()
    for index,cnt in enumerate(contours):
        # print(ContourStats(cnt))
        if hierarchy[0][index][3] >= 0 and cv2.contourArea(cnt) <= max_area:
            hole_mask = np.zeros(bgr.shape[:2], np.uint8)
            cv2.drawContours(hole_mask, [cnt], -1, 255, -1)
            mean = cv2.mean(hsv, mask=hole_mask)[0:3]

            color_distance = (mean[0] - target[0]) ** 2 * weight[0] +  \
                             (mean[1] - target[1]) ** 2 * weight[1] +  \
                             (mean[2] - target[2]) ** 2 * weight[2]

            if ((not greater_than) and color_distance <= segmentation_threshold) or (greater_than and color_distance > segmentation_threshold):
                # cs.Update(mean)
                cv2.fillPoly(biomass_mask, pts = [cnt], color=(255))
                cv2.fillPoly(accepted_holes_mask, pts = [cnt], color=(255))
                # print(" area " + str(cv2.contourArea(cnt)) + ' dist ' + str(color_distance) + ' mean ' + str(mean))
                circles.append(cv2.minEnclosingCircle(cnt))
            else:
                cv2.fillPoly(refused_holes_mask, pts = [cnt], color=(255))
                # print("REFUSED  area " + str(cv2.contourArea(cnt)) + ' dist ' + str(color_distance) + ' mean ' + str(mean))
    # print(cs.ComputeStats())
    return accepted_holes_mask,refused_holes_mask,circles


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
