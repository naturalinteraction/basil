#!/usr/bin/python

import time
import cv2
import numpy as np
from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
from utility import *
from vision import *
from basilico import *
from senape import *
from modello import *
from satu import *

routine = {
            'basilico' :  RoutineBasilico,
            'senape'   :  RoutineSenape,
            'modello'  :  RoutineModello,
            'satu'     :  RoutineSatu,
          }

args = ParseArguments()

if args.download:
    DownloadImagesFromS3('cache/' + args.prefix, args.substring)

box = BoundingBox()

for image_file in ListLocalImages('downloaded/' + args.prefix, args.substring):
    print('processing ' + image_file)
    bgr = cv2.imread(image_file)

    before = time.time()

    routine[args.routine](image_file, bgr, box)

    print(str(time.time() - before) + 's')

    ProcessKeystrokes()

cv2.destroyAllWindows()
print('Windows destroyed.')
try:
    print("ffmpeg -r 7 -pattern_type glob -i 'temp/*.jpeg' -s hd1080 -vcodec libx264 -filter:v 'crop="
          + str(int(box.rect.xmax - box.rect.xmin)) + \
          ':' + str(int(box.rect.ymax - box.rect.ymin)) + ':' + \
          str(int(box.rect.xmin)) + ':' + str(int(box.rect.ymin))) + \
          "' timelapse.mp4"
except:
    print('No available bounding box.')
