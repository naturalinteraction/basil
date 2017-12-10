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
from segment import segment

git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
print(git_hash)
git_commit_message = subprocess.check_output(["git", "log", "-1"]).strip()  # , "--pretty=%B"
print(git_commit_message)
git_commit_message_pretty = subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).strip()
print(git_commit_message_pretty)

print((cv2.__version__))

print((cv2.ocl.haveOpenCL()))
cv2.ocl.setUseOpenCL(True)
print((cv2.ocl.useOpenCL()))

def mouseCallback(event, x, y, flags, param):
    what = image  # hsv
    print((what.item(y, x, 0), what.item(y, x, 1), what.item(y, x, 2)))

cv2.namedWindow('dip', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('dip', mouseCallback)

sensor = 'visible'
campaign = 'bianco'

if False:
    files = ListFilesInCacheOnS3('cache/' + sensor + '-' + campaign)
    for f in files:
        replaced = f.replace('cache/', 'downloaded/')
        if os.path.isfile(replaced):
            print(('skipping download of %s' % f))
        else:
            print(('attempting download of %s' % f))
            DownloadFileFromCacheOnS3(f, replaced)

downloaded_files = glob.glob('downloaded/' + sensor + '-' + campaign + '_*.jpg')
key = ''
for f in sorted(downloaded_files):
    print(f)
    image = cv2.imread(f)
    average = cv2.mean(image)[0:3]
    # print(average)
    if True:  # average[0] > 30:
        # hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        before = time.time()
        image_copy = image.copy()
        count = segment(image_copy, -20, 10, -10, -1200, 70)
        # print('count ' + str(count))
        gray_image = cv2.cvtColor(image_copy, cv2.COLOR_BGR2GRAY)

        kernel = np.ones((3, 3), np.uint8)
        gray_image = cv2.erode(gray_image, kernel, iterations = 1)
        # gray_image = cv2.dilate(gray_image, kernel, iterations = 2)
        # gray_image = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, kernel)
        # gray_image = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)

        gray_image = cv2.bitwise_not(gray_image)

        im2, contours, heirarchy = cv2.findContours(gray_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            m = cv2.moments(cnt)
            area = m['m00']
            if area <= 4000:
                cv2.fillPoly(gray_image, pts = [cnt], color=(0))

        count = len(cv2.findNonZero(gray_image))
        print(('count after fill ' + str(count)))

        mask = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)

        image = cv2.addWeighted(image, 1.0, mask, 0.5, 0.0)

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

