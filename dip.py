import time
import os
import cv2
import math
import subprocess
from S3 import ListFilesInCacheOnS3
from S3 import DownloadFileFromCacheOnS3
from pyexif import ExifEditor
import glob
import shutil
import pickle
import os.path
import numpy as np
from segment import segment_linear
from segment import segment_target

git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
print(git_hash)
git_commit_message = subprocess.check_output(["git", "log", "-1"]).strip()  # , "--pretty=%B"
print(git_commit_message)
git_commit_message_pretty = subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).strip()
print(git_commit_message_pretty)

print((cv2.__version__))

def mouseCallback(event, x, y, flags, param):
    what = image  # hsv
    print((what.item(y, x, 0), what.item(y, x, 1), what.item(y, x, 2)))

cv2.namedWindow('dip', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('dip', mouseCallback)

sensor = 'visible'  # 'noir', 'visible', 'redshift', 'blueshift'
campaign = 'bianco'
day = '2017_12_14'  # '2017_12_14', ''

if False:  # download new images from S3?
    files = ListFilesInCacheOnS3('cache/' + sensor + '-' + campaign)
    if len(day) > 0:
        files = list(filter(lambda x: day in x, files))
    for f in files:
        replaced = f.replace('cache/', 'downloaded/')
        if os.path.isfile(replaced):
            print(('skipping download of %s' % f))
        else:
            print(('attempting download of %s' % f))
            DownloadFileFromCacheOnS3(f, replaced)

downloaded_files = glob.glob('downloaded/' + sensor + '-' + campaign + '_*.jpg')
key = ''

if len(day) > 0:
    downloaded_files = list(filter(lambda x: day in x, downloaded_files))

for f in sorted(downloaded_files):
    print(f)
    image = cv2.imread(f)
    average = cv2.mean(image)[0:3]
    # print(average)
    if True:  # average[0] > 30:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        before = time.time()
        image_copy = image.copy()
        # count = segment_linear(image_copy, 0, 1, 0, 150, 0)
        if sensor == 'visible':
            count = segment_target(image_copy, 36, 240, 166, 6, 3, 1, 90 * 90 * 3)  # visible
        if sensor == 'noir':
            count = segment_target(image_copy, 31, 195, 161, 6, 3, 1, 90 * 90 * 3)  # noir
        if sensor == 'blueshift':
            count = segment_target(image_copy, 34, 158, 118, 16, 3, 1, 90 * 90 * 3)  # blueshift

        # print('count ' + str(count))
        gray_image = cv2.cvtColor(image_copy, cv2.COLOR_BGR2GRAY)

        kernel = np.ones((3, 3), np.uint8)
        # gray_image = cv2.erode(gray_image, kernel, iterations = 1)
        # gray_image = cv2.dilate(gray_image, kernel, iterations = 2)
        # gray_image = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, kernel)
        # gray_image = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)

        gray_image = cv2.bitwise_not(gray_image)

        im2, contours, heirarchy = cv2.findContours(gray_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            m = cv2.moments(cnt)
            area = m['m00']
            if area <= 0:
                cv2.fillPoly(gray_image, pts = [cnt], color=(0))

        # TypeError: object of type 'NoneType' has no len()
        nonzero = cv2.findNonZero(gray_image)
        if not(nonzero is None):
            count = len(nonzero)
            print(('count after fill ' + str(count)))

        mask = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)

        image = cv2.addWeighted(image, 1.0, mask, -0.9, 0.0)

        print((time.time() - before))
        cv2.imshow('dip', image)

        filename = f.replace('downloaded/', 'temp/')
        cv2.imwrite(filename + '.jpeg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

        #if ord('p') == key:
        key = cv2.waitKey(0) & 0xFF  # milliseconds
        #else:
        #    key = cv2.waitKey(25) & 0xFF  # milliseconds

        # if the `q` or ESC key was pressed, break from the for loop
        if key == ord('q') or key == 27:
                print('exiting')
                quit()

cv2.destroyAllWindows()
print('Windows destroyed.')

