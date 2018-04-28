#!/usr/bin/python

from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
from S3 import UploadFileToS3
from utility import *
from vision import *
from display import *
import imp
zero = imp.load_source('zero', './zero.py')
from zero import *

def RemoveTemporaryFiles(also_timelapse_subdir=False):
    files = os.listdir('.')
    for file in files:
        if file.endswith(".extension"):  # currently this does not delete any files
            os.remove(os.path.join('.', file))
    if also_timelapse_subdir:
        files = os.listdir('timelapse')
        for file in files:
            if file.endswith(".jpg"):
                os.remove(os.path.join('timelapse', file))

args = ParseArguments()

if args.download:
    print('skipped=%d downloaded=%d failed=%d' % DownloadImagesFromS3(args.group + '/' + args.prefix, args.substring, args.group))
    quit()

box = BoundingBox()

# attempt to load existing csv file for this analysis
processed_files = []
try:
    with open('CSV/' + args.group + '/' + args.prefix + '.csv', 'rb') as csvfile:
        csv_data = csv.reader(csvfile)
        first = True
        for row in csv_data:
            if not first:
                processed_files.append(row[10])
            first = False
    # print(processed_files)
    # print(len(processed_files))
except:
    print('dip: csv file does not exist')

for image_file in ListLocalImages('downloaded/' + args.group + '/' + args.prefix, args.substring):
    if not (image_file.replace('downloaded/', '') in processed_files):  # has not been analyzed yet
        print('processing ' + image_file)
        locals()[args.routine](image_file, cv2.imread(image_file), box, args.group)
    else:
        print('skipping ' + image_file)
    ProcessKeystrokes()

cv2.destroyAllWindows()
print('Windows destroyed.')

if args.upload:
    sensor_hostname = args.prefix.split('-')[0]
    if not UploadFileToS3('CSV/' + args.group + '/' + args.prefix + '.csv', 'CSV/' + args.group + '/' + args.prefix + '.csv'):
        print ("now, this is a big problem. could not upload CSV results.")
        quit()

try:
    print("ffmpeg -r 15 -pattern_type glob -i 'timelapse/" + args.group + '/' + args.prefix + "*.jpg' -s 1440:1080 -vcodec libx264 -filter:v 'crop="
          + str(int(box.rect.xmax - box.rect.xmin)) + \
          ':' + str(int(box.rect.ymax - box.rect.ymin)) + ':' + \
          str(int(box.rect.xmin)) + ':' + str(int(box.rect.ymin))) + \
          "' timelapse.mp4"
except:
    command = "ffmpeg -r 15 -pattern_type glob -i 'timelapse/" + args.group + '/' + args.prefix + "*.jpg' -s 1440:1080 -vcodec libx264 ~/Desktop/timelapse-" + args.prefix + "-" + args.routine + ".mp4"
    print(command)
    os.popen(command)
