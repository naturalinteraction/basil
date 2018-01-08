#!/usr/bin/python

import time
import cv2
import numpy as np
from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
from segment import *
from utility import *
from vision import *

args = ParseArguments()

if args.download:
    DownloadImagesFromS3('cache/' + args.prefix, args.substring)

for f in ListLocalImages('downloaded/' + args.prefix, args.substring):
    print('processing ' + f)
    bgr = cv2.imread(f)

    # before = time.time()

    # **************** todo: pipeline starts

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    target_color_0 = 36
    target_color_1 = 238
    target_color_2 = 164

    weight_color_0 = 6
    weight_color_1 = 3
    weight_color_2 = 1

    segmentation_threshold = 90 * 90 * 3
    segmentation_threshold_holes = segmentation_threshold * 1.7

    biomass_mask = Segment(hsv, target_color_0,
                                target_color_1,
                                target_color_2,
                                weight_color_0,
                                weight_color_1,
                                weight_color_2, 
                                segmentation_threshold)

    UpdateWindow('bgr', bgr)
    UpdateWindow('hsv', hsv)

    biomass_mask = Erode(biomass_mask)  # this might remove some noise in the form of isolated pixels, a gaussian blur might work as well or better

    UpdateWindow('biomass_mask', biomass_mask)  # this is still the raw mask, without the holes filled

    # invert mask, so that we can analyze the holes as white blobs against a black background
    biomass_mask = cv2.bitwise_not(biomass_mask)

    temp, contours, hierarchy = cv2.findContours(biomass_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
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

    biomass_eroded = Erode(biomass_eroded, iterations=2)

    h,s,v = cv2.split(cv2.cvtColor(foreground, cv2.COLOR_BGR2HSV))
    luminance = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)

    ### UpdateWindow('derivative', ComputeImageDerivative(luminance, biomass_eroded))

    ### Histogram(luminance, output=foreground)

    # count non zero pixels in mask, and find its bounding box
    nonzero = cv2.findNonZero(biomass_eroded)
    if not(nonzero is None):
        count = len(nonzero)
        print(('biomass ' + str(count)))
        bbx,bby,bbw,bbh = cv2.boundingRect(nonzero)

        current_rect = rect(int(bbx - 8), int(bby - 8), int(bbx + bbw + 8), int(bby + bbh + 8))

        try:
            crop_rect
        except:
            crop_rect = current_rect
        crop_rect = rect_union(crop_rect, current_rect)

        cv2.rectangle(foreground, (crop_rect.xmin, crop_rect.ymin), (crop_rect.xmax, crop_rect.ymax), (255, 255, 255), 2)

    hole_color = (255, 255, 255)

    for e in ellipses:
        center,axes,angle = e
        # print(center, axes, angle)
        center = (int(center[0]), int(center[1]))
        axes = (int(axes[0] * 0.5 + 4), int(axes[1] * 0.5 + 4))
        cv2.ellipse(foreground, center, axes, angle, 0.0, 360.0, hole_color, 1)

    for c in circles:
        center,radius = c
        cv2.circle(foreground, (int(center[0]), int(center[1])), int(radius) + 4, hole_color, 1)

    # UpdateWindow('accepted-holes', cv2.bitwise_and(bgr, bgr, mask=accepted_holes_mask))
    # UpdateWindow('refused-holes', cv2.bitwise_and(bgr, bgr, mask=refused_holes_mask))
    UpdateWindow('dip', foreground, f.replace('downloaded/', 'temp/') + '.jpeg')

    # **************** todo: pipeline ends

    # print((time.time() - before))

    ProcessKeystrokes()

cv2.destroyAllWindows()
print('Windows destroyed.')
try:
    print('ffmpeg crop = ' + str(int(crop_rect.xmax - crop_rect.xmin)) + \
          ':' + str(int(crop_rect.ymax - crop_rect.ymin)) + ':' + \
          str(int(crop_rect.xmin - 8)) + ':' + str(int(crop_rect.ymin - 8)))
except:
    print('no available crop_rect')

