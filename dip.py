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

    accepted_holes_mask,refused_holes_mask,ellipses,circles = FillHoles(biomass_mask, bgr, hsv)

    # this is done after because it needs the updated biomass_mask
    foreground = MaskedImage(bgr, biomass_mask)
    UpdateWindow('background', MaskedImage(bgr, Inverted(biomass_mask)))

    ### h,s,v = cv2.split(cv2.cvtColor(foreground, cv2.COLOR_BGR2HSV))
    ### luminance = ToGray(foreground)
    ### UpdateWindow('derivative', ComputeImageDerivative(luminance, Erode(biomass_mask, iterations=2)))  # eroded to exclude outer edges
    ### Histogram(luminance, output=foreground)

    DrawEllipses(foreground, ellipses, white)
    DrawCircles(foreground, circles, white)

    # todo: function
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

