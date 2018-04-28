#!/usr/bin/python

from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
from S3 import UploadFileToS3
from utility import *
from vision import *
from display import *
import imp
zero = imp.load_source('zero', '../basil-zero/zero.py')
from zero import *

def RemoveFiles(path, beginning):
    files = os.listdir(path)
    for file in files:
        if file.startswith(beginning):
            print('deleting %s' % os.path.join(path, file))
            os.remove(os.path.join(path, file))

args = ParseArguments()

if args.download:
    print('skipped=%d downloaded=%d failed=%d' % DownloadImagesFromS3(args.group + '/' + args.prefix, args.substring, args.group))
    quit()

if len(args.prefix.split('-')) != 2:
    print('prefix must be in the form sensorname-batchname (batchname can contain ^ (carets)')
    quit()

if args.clean:
    print(args.prefix.split('-'))
    if len(args.prefix.split('-')) == 2:
        print('cleaning')
        RemoveFiles('prior/' + args.group, args.prefix)
        RemoveFiles('CSV/' + args.group, args.prefix)

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

if not args.timelapse:
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
