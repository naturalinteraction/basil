#!/usr/bin/python

from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
from S3 import UploadFileToS3
from utility import *
from vision import *
from display import *
from zero import *

def RemoveTemporaryFiles(also_timelapse_subdir=False):
    files = os.listdir('.')
    for file in files:
        if file.endswith(".temp"):
            os.remove(os.path.join('.', file))
    if also_timelapse_subdir:
        files = os.listdir('timelapse')
        for file in files:
            if file.endswith(".jpg"):
                os.remove(os.path.join('timelapse', file))

args = ParseArguments()

if args.download:
    DownloadImagesFromS3(args.group + '/' + args.prefix, args.substring, args.group)
    quit()

box = BoundingBox()

RemoveTemporaryFiles(True)

for image_file in ListLocalImages('downloaded/' + args.prefix, args.substring):

    bgr = cv2.imread(image_file)

    before = time.time()

    locals()[args.routine](image_file, bgr, box, args.group)

    # print(str(time.time() - before) + 's')

    ProcessKeystrokes()

cv2.destroyAllWindows()
print('Windows destroyed.')
RemoveTemporaryFiles()

if args.upload:
    sensor_hostname = args.prefix.split('-')[0]
    if not UploadFileToS3('website/CSV/' + args.prefix + '.csv', 'CSV/' + args.group + '/' + sensor_hostname + '.csv'):  # just the sensor hostname --> latest chart
        print ("now, this is a big problem. could not upload CSV results.")
        quit()

try:
    print("ffmpeg -r 15 -pattern_type glob -i 'timelapse/*.jpg' -s hd1080 -vcodec libx264 -filter:v 'crop="
          + str(int(box.rect.xmax - box.rect.xmin)) + \
          ':' + str(int(box.rect.ymax - box.rect.ymin)) + ':' + \
          str(int(box.rect.xmin)) + ':' + str(int(box.rect.ymin))) + \
          "' timelapse.mp4"
except:
    command = "ffmpeg -r 15 -pattern_type glob -i 'timelapse/*.jpg' -s hd1080 -vcodec libx264 ~/Desktop/timelapse-" + args.prefix + "-" + args.routine + ".mp4"
    print(command)
    os.popen(command)
