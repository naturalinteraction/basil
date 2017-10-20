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
    
git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
print(git_hash)
git_commit_message = subprocess.check_output(["git", "log", "-1"]).strip()  # , "--pretty=%B"
print(git_commit_message)
git_commit_message_pretty = subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).strip()
print(git_commit_message_pretty)

# cv2.namedWindow('dip', cv2.WINDOW_NORMAL)
# cv2.imshow('dip', image)

files = ListFilesInCacheOnS3()
for f in files:
    replaced = f.replace('cache/', 'downloaded/')
    if os.path.isfile(replaced):
        print('skipping download of %s' % f)
    else:
        print('attempting download of %s' % f)
        DownloadFileFromCacheOnS3(f, replaced)
    image = cv2.imread(replaced)
    average = cv2.mean(image)[0:3]
    print(average)

# cv2.destroyAllWindows()
# print('Windows destroyed.')

