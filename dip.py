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

# print out debug information about current source code version and OpenCV version
# git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
# print(git_hash)
# git_commit_message = subprocess.check_output(["git", "log", "-1"]).strip()  # , "--pretty=%B"
# print(git_commit_message)
# git_commit_message_pretty = subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).strip()
# print(git_commit_message_pretty)
# print((cv2.__version__))

def mouseCallback(event, x, y, flags, param):
    what = bgr
    print('bgr ', (what.item(y, x, 0), what.item(y, x, 1), what.item(y, x, 2)))
    what = hsv
    print('hsv ', (what.item(y, x, 0), what.item(y, x, 1), what.item(y, x, 2)))
    what = biomass_mask
    print('biomass_mask ', (what.item(y, x) == 0))

# main window
cv2.namedWindow('dip', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('dip', mouseCallback)

# debug window
cv2.namedWindow('background', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('background', mouseCallback)

sensor = 'visible'
campaign = 'bianco'
day = '2017_12_10'  # '2017_12_14', ''  # background change on th 12th, between 15.00 and 15.31

if False:  # download new images from S3?
    files = ListFilesInCacheOnS3('cache/' + sensor + '-' + campaign)
    # filter out based on day string
    if len(day) > 0:
        files = list(filter(lambda x: day in x, files))
    for f in files:
        replaced = f.replace('cache/', 'downloaded/')
        if os.path.isfile(replaced):
            print(('skipping download of %s' % f))
        else:
            print(('attempting download of %s' % f))
            DownloadFileFromCacheOnS3(f, replaced)

# list files with given prefix in directory 'downloaded/'
downloaded_files = glob.glob('downloaded/' + sensor + '-' + campaign + '_*.jpg')
# optionally filter out those that are not from given day/time
if len(day) > 0:
    downloaded_files = list(filter(lambda x: day in x, downloaded_files))

# last key pressed, only needed for if ord('p') == key below...
key = ''

for f in sorted(downloaded_files):
    print(f)
    bgr = cv2.imread(f)
    # average = cv2.mean(bgr)[0:3]
    # print(average)
    if True:  # average[0] > 30:
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        # before = time.time()
        hsv_copy = hsv.copy()

        target_color_0 = 36
        target_color_1 = 240
        target_color_2 = 166

        weight_color_0 = 6
        weight_color_1 = 3
        weight_color_2 = 1

        segmentation_threshold = 90 * 90 * 3

        count = segment_target(hsv_copy,   target_color_0,
                                           target_color_1,
                                           target_color_2,
                                           weight_color_0,
                                           weight_color_1,
                                           weight_color_2, segmentation_threshold)

        # print('count ' + str(count))
        biomass_mask = cv2.cvtColor(hsv_copy, cv2.COLOR_BGR2GRAY)

        kernel = np.ones((3, 3), np.uint8)
        # biomass_mask = cv2.erode(biomass_mask, kernel, iterations = 1)  # todo: parameter
        # biomass_mask = cv2.dilate(biomass_mask, kernel, iterations = 2)
        # biomass_mask = cv2.morphologyEx(biomass_mask, cv2.MORPH_OPEN, kernel)
        # biomass_mask = cv2.morphologyEx(biomass_mask, cv2.MORPH_CLOSE, kernel)

        # invert mask
        biomass_mask = cv2.bitwise_not(biomass_mask)

        temp, contours, hierarchy = cv2.findContours(biomass_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        holes = 0
        for cnt in contours:
            # if len(cnt) < 200:  # fast way to ignore huge blobs?
            # m = cv2.moments(cnt)
            # area = m['m00']
            area = cv2.contourArea(cnt)

            # extent and solidity
            x,y,w,h = cv2.boundingRect(cnt)
            rect_area = w * h
            if rect_area > 0:
                extent = float(area) / rect_area  # could be useful for the holes
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            if hull_area > 0:
                solidity = float(area)/hull_area  # could be useful for the holes

            if area < 70 * 70:  # todo: parameter
                hole_mask = np.zeros(bgr.shape[:2], np.uint8)
                cv2.drawContours(hole_mask, [cnt], -1, 255, -1)
                # np.where()
                mean = cv2.mean(hsv, mask=hole_mask)[0:3]

                color_distance = pow(mean[0] - target_color_0, 2) * weight_color_0 +  \
                                 pow(mean[1] - target_color_1, 2) * weight_color_1 +  \
                                 pow(mean[2] - target_color_2, 2) * weight_color_2

                if color_distance < segmentation_threshold * 2:  # todo: parameter
                    cv2.fillPoly(biomass_mask, pts = [cnt], color=(0))
                    cv2.fillPoly(hsv, pts = [cnt], color=(255, 0, 255))
                    holes += 1
                else:
                    print(str(holes) + " area " + str(area) + ' dist ' + str(color_distance) + ' mean ' + str(mean))
                    cv2.fillPoly(hsv, pts = [cnt], color=(255, 0, 0))

        print('holes ' + str(holes))

        # count non zero pixels in mask
        # TypeError: object of type 'NoneType' has no len()
        # nonzero = cv2.findNonZero(biomass_mask)
        # if not(nonzero is None):
        #     count = len(nonzero)
        #     print(('count after fill ' + str(count)))

        foreground_mask = cv2.cvtColor(biomass_mask, cv2.COLOR_GRAY2BGR)
        foreground = cv2.addWeighted(bgr, 1.0, foreground_mask, -1.0, 0.0)
        background_mask = cv2.bitwise_not(foreground_mask)
        background = cv2.addWeighted(bgr, 1.0, background_mask, -1.0, 0.0)

        # print((time.time() - before))
        cv2.imshow('dip', foreground)
        cv2.imshow('background', background)

        # save resulting image to disk
        # filename = f.replace('downloaded/', 'temp/')
        # cv2.imwrite(filename + '.jpeg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

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

