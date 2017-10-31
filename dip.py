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

print(cv2.__version__)

print(cv2.ocl.haveOpenCL())
cv2.ocl.setUseOpenCL(True)
print(cv2.ocl.useOpenCL())

def mouseCallback(event, x, y, flags, param):
    what = image  # hsv
    print(what.item(y, x, 0), what.item(y, x, 1), what.item(y, x, 2))

cv2.namedWindow('dip', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('dip', mouseCallback)
'''
files = ListFilesInCacheOnS3()
for f in files:
    replaced = f.replace('cache/', 'downloaded/')
    if os.path.isfile(replaced):
        print('skipping download of %s' % f)
    else:
        print('attempting download of %s' % f)
        DownloadFileFromCacheOnS3(f, replaced)
'''    
downloaded_files = glob.glob("downloaded/visible-2_*.jpg")
key = ''
for f in sorted(downloaded_files):
    # print(f)
    image = cv2.imread(f)
    average = cv2.mean(image)[0:3]
    # print(average)
    if True:  # average[0] > 30:
        # hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        before = time.time()
        segment(image, -10, 10, -10, 20)
        print(time.time() - before)
        cv2.imshow('dip', image)
        if ord('p') == key:
            key = cv2.waitKey(0) & 0xFF  # milliseconds
        else:
            key = cv2.waitKey(25) & 0xFF  # milliseconds

        # if the `q` or ESC key was pressed, break from the for loop
	if key == ord('q') or key == 27:
                print('exiting')
		break
'''
image = cv2.imread("downloaded/blueshift-2_2560x1920_2017_10_24-10_00.jpg")
M = np.float32([[1,0,100], [0,1,50]])
rows,cols,ch = image.shape
pts1 = np.float32([[56,65], [368,52], [28,387], [389,390]])
pts2 = np.float32([[0,0], [300,0], [0,300], [300,300]])
MP = cv2.getPerspectiveTransform(pts1, pts2)
kernel = np.ones((5, 5), np.float32)/25

def test():
    before = time.time()
    for i in range (10):    
        resized = cv2.resize(image, (10000, 10000))
        warped = cv2.warpAffine(image, M, (2000, 2000))
        blur = cv2.blur(image, (5,5))
        canned = cv2.Canny(image, 100, 200) 
        filtered = cv2.filter2D(image, -1, kernel)
        sobel = cv2.Sobel(image, cv2.CV_64F, 1, 1, ksize=5)
        persp = cv2.warpPerspective(image, MP, (cols,rows))
    print(time.time() - before, cv2.ocl.useOpenCL())

test()
cv2.ocl.setUseOpenCL(False)
test()
# print(cv2.getBuildInformation())
'''

cv2.destroyAllWindows()
print('Windows destroyed.')

