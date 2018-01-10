#!/usr/bin/python

import time
import cv2
import numpy as np
from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
from utility import *
from vision import *
from basilico import *

args = ParseArguments()

if args.download:
    DownloadImagesFromS3('cache/' + args.prefix, args.substring)

for image_file in ListLocalImages('downloaded/' + args.prefix, args.substring):
    # print('processing ' + image_file)
    bgr = cv2.imread(image_file)

    before = time.time()

    Basilico(image_file, bgr)

    print('time elapsed', time.time() - before)

    ProcessKeystrokes()

cv2.destroyAllWindows()
print('Windows destroyed.')
try:
    print("ffmpeg -r 7 -pattern_type glob -i 'temp/*.jpeg' -s hd1080 -vcodec libx264 -filter:v 'crop="
          + str(int(crop_rect.xmax - crop_rect.xmin)) + \
          ':' + str(int(crop_rect.ymax - crop_rect.ymin)) + ':' + \
          str(int(crop_rect.xmin)) + ':' + str(int(crop_rect.ymin))) + \
          "' timelapse.mp4"
except:
    print('No available crop_rect.')

