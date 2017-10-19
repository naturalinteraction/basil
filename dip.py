import time
import os
import cv2
import math
import subprocess
from S3 import ListFilesInCacheOnS3
from pyexif import ExifEditor
import glob
import shutil
import pickle
    
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
    print(replaced)
print(len(files))

# cv2.destroyAllWindows()
# print('Windows destroyed.')

