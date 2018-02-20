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
from curves import *
from basilicorosso import *
from bataviarossa import *
from kappa import *

print(GetCPUSerial())
print(GetMAC('eth0'))
print(GetMAC('wlan0'))
print(GetSDSerial())
print(GetSDCID())

routine = {
            'basilico' :  RoutineBasilico,
            'modello'  :  RoutineModello,
            'satu'     :  RoutineSatu,
            'display'  :  RoutineDisplay,
            'save'     :  RoutineSave,
            'bieta'    :  RoutineBieta,
            'kappa'    :  RoutineKappa,
            'curves'   :  RoutineCurves,
            'alfalfaredshift'  :  RoutineAlfalfaRedshift,
            'alfalfanoir'      :  RoutineAlfalfaNoir,
            'basilicorosso'    :  RoutineBasilicoRosso,
            'bataviarossa'     :  RoutineBataviaRossa,
          }

def RemoveTemporaryFiles(also_temp_subdir=False):
    files = os.listdir('.')
    for file in files:
        if file.endswith(".temp"):
            os.remove(os.path.join('.', file))
    files = os.listdir('temp')
    if also_temp_subdir:
        for file in files:
            os.remove(os.path.join('temp', file))

args = ParseArguments()

if args.download:
    DownloadImagesFromS3('cache/' + args.prefix, args.substring)
    quit()

box = BoundingBox()

RemoveTemporaryFiles(True)

for image_file in ListLocalImages('downloaded/' + args.prefix, args.substring):
    # print('processing ' + image_file)
    bgr = cv2.imread(image_file)

    before = time.time()

    routine[args.routine](image_file, bgr, box)

    # print(str(time.time() - before) + 's')

    ProcessKeystrokes()

cv2.destroyAllWindows()
print('Windows destroyed.')
RemoveTemporaryFiles()

try:
    print("ffmpeg -r 7 -pattern_type glob -i 'temp/*.jpeg' -s hd1080 -vcodec libx264 -filter:v 'crop="
          + str(int(box.rect.xmax - box.rect.xmin)) + \
          ':' + str(int(box.rect.ymax - box.rect.ymin)) + ':' + \
          str(int(box.rect.xmin)) + ':' + str(int(box.rect.ymin))) + \
          "' timelapse.mp4"
except:
    command = "ffmpeg -r 7 -pattern_type glob -i 'temp/*.jpeg' -s hd1080 -vcodec libx264 ~/Desktop/timelapse-" + args.prefix + "-" + args.routine + ".mp4"
    print(command)
    os.popen(command)
