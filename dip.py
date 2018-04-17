#!/usr/bin/python

from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
from utility import *
from vision import *
from display import *
from curves import *

customer = 'zero'

def RemoveTemporaryFiles(also_temp_subdir=False):
    files = os.listdir('.')
    for file in files:
        if file.endswith(".temp"):
            os.remove(os.path.join('.', file))
    if also_temp_subdir:
        files = os.listdir('temp')
        for file in files:
            if file.endswith(".jpeg"):
                os.remove(os.path.join('temp', file))

args = ParseArguments()

if args.download:
    DownloadImagesFromS3(customer + '/' + args.prefix, args.substring, customer)
    quit()

box = BoundingBox()

RemoveTemporaryFiles(True)

for image_file in ListLocalImages('downloaded/' + args.prefix, args.substring):

    bgr = cv2.imread(image_file)

    before = time.time()

    locals()[args.routine](image_file, bgr, box)

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
