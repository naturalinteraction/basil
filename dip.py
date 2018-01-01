import time
import os
import cv2
import math
from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
from pyexif import ExifEditor
import shutil
import pickle
import os.path
import numpy as np
from segment import segment_linear
from segment import segment_target
from git import OpenCVVersion
from git import GitCommitMessage
from audio import AudioLevelLaptop

print(AudioLevelLaptop())

# print out debug information about current source code version and OpenCV version
print(GitCommitMessage())
print(OpenCVVersion())

def mouseCallback(event, x, y, flags, param):
    what = bgr
    print('bgr ', (what.item(y, x, 0), what.item(y, x, 1), what.item(y, x, 2)))
    what = hsv
    print('hsv ', (what.item(y, x, 0), what.item(y, x, 1), what.item(y, x, 2)))
    what = biomass_mask
    print('biomass_mask ', (what.item(y, x) == 0))

# debug windows
cv2.namedWindow('refused-holes', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('refused-holes', mouseCallback)
cv2.namedWindow('accepted-holes', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('accepted-holes', mouseCallback)
cv2.namedWindow('background', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('background', mouseCallback)

# main window
cv2.namedWindow('dip', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('dip', mouseCallback)

sensor = 'visible'
campaign = 'bianco'
substring = '2017_12_31'  # '2017_12_22', ''  # background change on the 12th, between 15.00 and 15.31
prefix = 'cache/' + sensor + '-' + campaign

# DownloadImagesFromS3(prefix, substring)

prefix = prefix.replace('cache/', 'downloaded/')

# last key pressed, only needed for if ord('p') == key below...
key = ''

min_bbx = 6666
min_bby = 6666
max_bbx2 = -1
max_bby2 = -1

for f in ListLocalImages(prefix, substring):
    print(f)
    bgr = cv2.imread(f)
    # average = cv2.mean(bgr)[0:3]
    # print(average)
    if True:  # average[0] > 30:
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        # before = time.time()
        hsv_copy = hsv.copy()

        target_color_0 = 36
        target_color_1 = 238
        target_color_2 = 164

        weight_color_0 = 6
        weight_color_1 = 3
        weight_color_2 = 1

        segmentation_threshold = 90 * 90 * 3
        segmentation_threshold_holes = segmentation_threshold * 1.7

        count = segment_target(hsv_copy,   target_color_0,
                                           target_color_1,
                                           target_color_2,
                                           weight_color_0,
                                           weight_color_1,
                                           weight_color_2, segmentation_threshold)

        # print('count ' + str(count))
        biomass_mask = cv2.cvtColor(hsv_copy, cv2.COLOR_BGR2GRAY)

        kernel = np.ones((3, 3), np.uint8)
        biomass_mask = cv2.erode(biomass_mask, kernel, iterations = 1)
        # biomass_mask = cv2.dilate(biomass_mask, kernel, iterations = 2)
        # biomass_mask = cv2.morphologyEx(biomass_mask, cv2.MORPH_OPEN, kernel)
        # biomass_mask = cv2.morphologyEx(biomass_mask, cv2.MORPH_CLOSE, kernel)

        # invert mask
        biomass_mask = cv2.bitwise_not(biomass_mask)

        temp, contours, hierarchy = cv2.findContours(biomass_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        holes = 0
        accepted_holes_mask = np.zeros(bgr.shape[:2], np.uint8)
        refused_holes_mask = np.zeros(bgr.shape[:2], np.uint8)

        ellipses = list()
        circles = list()

        for cnt in contours:
            # if len(cnt) < 200:  # fast way to ignore huge blobs?
            # m = cv2.moments(cnt)
            # area = m['m00']
            area = cv2.contourArea(cnt)

            # extent and solidity
            x,y,w,h = cv2.boundingRect(cnt)
            rect_area = w * h
            if rect_area > 0:
                extent = float(area) / rect_area  # could be useful for shape analysis
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            if hull_area > 0:
                solidity = float(area) / hull_area  # could be useful for shape analysis
            perimeter = cv2.arcLength(cnt, True)
            if perimeter > 0:
                jaggedness = len(cnt) / perimeter  # could be useful for shape analysis

            if area < 70 * 70:
                hole_mask = np.zeros(bgr.shape[:2], np.uint8)
                cv2.drawContours(hole_mask, [cnt], -1, 255, -1)
                # np.where()
                mean = cv2.mean(hsv, mask=hole_mask)[0:3]

                color_distance = pow(mean[0] - target_color_0, 2) * weight_color_0 +  \
                                 pow(mean[1] - target_color_1, 2) * weight_color_1 +  \
                                 pow(mean[2] - target_color_2, 2) * weight_color_2

                if color_distance < segmentation_threshold_holes:
                    cv2.fillPoly(biomass_mask, pts = [cnt], color=(0))
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

        foreground_mask = cv2.cvtColor(biomass_mask, cv2.COLOR_GRAY2BGR)
        foreground = cv2.addWeighted(bgr, 1.0, foreground_mask, -1.0, 0.0)
        background_mask = cv2.bitwise_not(foreground_mask)
        background = cv2.addWeighted(bgr, 1.0, background_mask, -1.0, 0.0)

        # exclude biomass edge
        biomass_eroded = cv2.bitwise_not(biomass_mask)
        biomass_eroded = cv2.erode(biomass_eroded, kernel, iterations = 2)

        # compute derivatives of foreground
        h,s,v = cv2.split(cv2.cvtColor(foreground, cv2.COLOR_BGR2HSV))
        luminance = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)
        for_derivation = s  # luminance
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
        sobel = cv2.bitwise_and(sobel, sobel, mask=biomass_eroded)

        # luminance histogram
        hist = cv2.calcHist([luminance], [0], None, [64], [1,256])
        max_hist = max(hist)
        for i in range(len(hist)):
            cv2.line(foreground, (i * 30, 1000), (i * 30, 1000 - hist[i] * 1000 / max_hist), (255, 255, 255), 30)

        # count non zero pixels in mask, and find its bounding box
        nonzero = cv2.findNonZero(biomass_eroded)
        if not(nonzero is None):
            count = len(nonzero)
            print(('biomass ' + str(count)))
            bbx,bby,bbw,bbh = cv2.boundingRect(nonzero)
            # print(bbx, bby, bbw, bbh)
            p1 = (int(bbx - 8), int(bby - 8))
            p2 = (int(bbx + bbw + 8), int(bby + bbh + 8))
            if bbx < min_bbx:
                min_bbx = bbx
            if bby < min_bby:
                min_bby = bby
            if bbw + bbx > max_bbx2:
                max_bbx2 = bbw + bbx
            if bbh + bby > max_bby2:
                max_bby2 = bbh + bby
            p1m = (int(min_bbx - 8), int(min_bby - 8))
            p2m = (int(max_bbx2 + 8), int(max_bby2 + 8))
            cv2.rectangle(foreground, p1m, p2m, (160, 160, 160), 2)
            cv2.rectangle(foreground, p1, p2, (255, 255, 255), 2)

        hole_color = (255, 255, 255)

        for e in ellipses:
            center,axes,angle = e
            # print(center, axes, angle)
            center = (int(center[0]), int(center[1]))
            axes = (int(axes[0] * 0.5 + 4), int(axes[1] * 0.5 + 4))
            cv2.ellipse(foreground, center, axes, angle, 0.0, 360.0, hole_color, 1)
            # cv2.ellipse(foreground, e, hole_color, 1)

        for c in circles:
            center,radius = c
            cv2.circle(foreground, (int(center[0]), int(center[1])), int(radius) + 4, hole_color, 1)
            # cv2.circle(foreground, (int(center[0]), int(center[1])), int(radius), hole_color, 1)

        # print((time.time() - before))

        # cv2.imshow('background', background)
        # cv2.imshow('accepted-holes', cv2.bitwise_and(bgr, bgr, mask=accepted_holes_mask))
        # cv2.imshow('refused-holes', cv2.bitwise_and(bgr, bgr, mask=refused_holes_mask))
        cv2.imshow('dip', foreground)  # sobel

        # save resulting image to disk
        filename = f.replace('downloaded/', 'temp/')
        cv2.imwrite(filename + '.jpeg', foreground, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

        key = cv2.waitKey(25) & 0xFF  # milliseconds
        # if ord('p') == key:
        #     key = cv2.waitKey(0) & 0xFF  # milliseconds
        # else:
        #     key = cv2.waitKey(25) & 0xFF  # milliseconds

        # if the `q` or ESC key was pressed, break from the for loop
        if key == ord('q') or key == 27:
                print('exiting')
                quit()

cv2.destroyAllWindows()
print('Windows destroyed.')

print('ffmpeg crop = ' + str(int(max_bbx2 - min_bbx + 16)) + \
      ':' + str(int(max_bby2 - min_bby + 16)) + ':' + \
      str(int(min_bbx - 16)) + ':' + str(int(min_bby - 16)))

