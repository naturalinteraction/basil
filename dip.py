#!/usr/bin/python

import time
import cv2
import numpy as np
from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
from utility import *
from vision import *

args = ParseArguments()

if args.download:
    DownloadImagesFromS3('cache/' + args.prefix, args.substring)

for image_file in ListLocalImages('downloaded/' + args.prefix, args.substring):
    print('processing ' + image_file)
    bgr = cv2.imread(image_file)

    before = time.time()

    ################ PIPELINE BEGIN

    UpdateWindow('bgr', bgr)

    hsv = ToHSV(bgr)

    UpdateWindow('hsv', hsv)

    biomass_mask = SegmentBiomass(hsv)

    biomass_mask = Erode(biomass_mask)  # this might remove some noise in the form of isolated pixels, a gaussian blur might work as well or better

    UpdateWindow('biomass_mask NOT FILLED', biomass_mask)  # this is still the raw mask, without the holes filled

    # -------------------- HOLES BEGIN

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

            target_color_0 = 36
            target_color_1 = 238
            target_color_2 = 164

            weight_color_0 = 6
            weight_color_1 = 3
            weight_color_2 = 1

            color_distance = pow(mean[0] - target_color_0, 2) * weight_color_0 +  \
                             pow(mean[1] - target_color_1, 2) * weight_color_1 +  \
                             pow(mean[2] - target_color_2, 2) * weight_color_2

            segmentation_threshold_holes = (90 * 90 * 3) * 1.7

            if color_distance < segmentation_threshold_holes:
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

    # -------------------- HOLES END

    # this is done after because it needs the updated biomass_mask
    foreground = MaskedImage(bgr, biomass_mask)
    UpdateWindow('background', MaskedImage(bgr, Inverted(biomass_mask)))

    ### h,s,v = cv2.split(cv2.cvtColor(foreground, cv2.COLOR_BGR2HSV))
    ### luminance = ToGray(foreground)
    ### UpdateWindow('derivative', ComputeImageDerivative(luminance, Erode(biomass_mask, iterations=2)))  # eroded to exclude outer edges
    ### Histogram(luminance, output=foreground)

    DrawEllipses(foreground, ellipses, white)
    DrawCircles(foreground, circles, white)

    nonzero = cv2.findNonZero(biomass_mask)
    if not(nonzero is None):
        count = len(nonzero)
        print(('biomass ' + str(count)))
        bbx,bby,bbw,bbh = cv2.boundingRect(nonzero)
        current_rect = rect(int(bbx), int(bby), int(bbx + bbw), int(bby + bbh))
        try:
            crop_rect
        except:
            crop_rect = current_rect
        crop_rect = rect_union(crop_rect, current_rect)

    cv2.rectangle(foreground, (crop_rect.xmin, crop_rect.ymin), (crop_rect.xmax, crop_rect.ymax), white, 2)

    UpdateWindow('accepted-holes', MaskedImage(bgr, accepted_holes_mask))
    UpdateWindow('refused-holes', MaskedImage(bgr, refused_holes_mask))
    UpdateWindow('dip', foreground, image_file.replace('downloaded/', 'temp/') + '.jpeg')
    UpdateWindow('biomass_mask FILLED', biomass_mask)

    ################ PIPELINE END

    print('time elapsed', time.time() - before)

    ProcessKeystrokes()

cv2.destroyAllWindows()
print('Windows destroyed.')
try:
    print('ffmpeg crop = ' + str(int(crop_rect.xmax - crop_rect.xmin)) + \
          ':' + str(int(crop_rect.ymax - crop_rect.ymin)) + ':' + \
          str(int(crop_rect.xmin)) + ':' + str(int(crop_rect.ymin)))
except:
    print('No available crop_rect.')

