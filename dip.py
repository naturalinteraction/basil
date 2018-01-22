#!/usr/bin/python

from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
from utility import *
from vision import *
from basilico import *
from modello import *
from satu import *
from display import *
from save import *
from alfalfaredshift import *
from alfalfanoir import *
from bieta import *
from rucola import *
from basilicorosso import *
from bataviarossa import *
from kappa import *

routine = {
            'basilico' :  RoutineBasilico,
            'modello'  :  RoutineModello,
            'satu'     :  RoutineSatu,
            'display'  :  RoutineDisplay,
            'save'     :  RoutineSave,
            'bieta'    :  RoutineBieta,
            'kappa'    :  RoutineKappa,
            'rucola'   :  RoutineRucola,
            'alfalfaredshift'  :  RoutineAlfalfaRedshift,
            'alfalfanoir'      :  RoutineAlfalfaNoir,
            'basilicorosso'    :  RoutineBasilicoRosso,
            'bataviarossa'     :  RoutineBataviaRossa,
          }

args = ParseArguments()

if args.download:
    DownloadImagesFromS3('cache/' + args.prefix, args.substring)
    quit()

box = BoundingBox()

for image_file in ListLocalImages('downloaded/' + args.prefix, args.substring):
    # print('processing ' + image_file)
    bgr = cv2.imread(image_file)

    before = time.time()

    routine[args.routine](image_file, bgr, box)

    # print(str(time.time() - before) + 's')

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
    print("ffmpeg -r 7 -pattern_type glob -i 'temp/*.jpeg' -s hd1080 -vcodec libx264 timelapse.mp4")
