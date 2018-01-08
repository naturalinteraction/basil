import subprocess
import cv2
from collections import namedtuple
import argparse


'''
rect
'''
rect = namedtuple('rect', 'xmin ymin xmax ymax')

def rect_union(a, b):
    return rect(min(a.xmin, b.xmin), min(a.ymin, b.ymin), max(a.xmax, b.xmax), max(a.ymax, b.ymax))


'''
versions
'''
def OpenCVVersion():
    return 'OpenCV ' + cv2.__version__

def GitHash():
    return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()

def GitCommitMessage():
    return subprocess.check_output(["git", "log", "-1"]).strip()

def GitCommitMessagePretty():
    return subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).strip()

# print out debug information about current source code version and OpenCV version
print(GitCommitMessage())
print(OpenCVVersion())


'''
parsing command line arguments
'''
def ParseArguments():
    parser = argparse.ArgumentParser(description='Process images from the sensors.')
    parser.add_argument('-p', '--prefix', default = 'visible-bianco', help='The prefix for the images.')
    parser.add_argument('-s', '--substring', default='', help='The substring to filter the images (e.g. 2017_12_31).')
    parser.add_argument('-d', '--download', dest='download', action='store_const',
                        const=True, default=False,
                        help='Download images from S3 (default: no)')
    args = parser.parse_args()
    print('prefix = ', args.prefix)
    print('substring = ', args.substring)  # '2017_12_31', ''  # background change on the 12th, between 15.00 and 15.31
    return args


'''
keystrokes
'''
def ProcessKeystrokes():
    key = cv2.waitKey(25) & 0xFF  # milliseconds
    if key not in [27, 255]:  # any key except ESC to toggle pause
        key = cv2.waitKey(0) & 0xFF  # milliseconds
    # if the ESC key was pressed, simply quit
    if key == 27:
        print('exiting')
        quit()

def mouseCallback(event, x, y, flags, param):
    for w in windows.keys():
        print (w, windows[w][y,x].tolist())


'''
windows
'''
windows = {}

def UpdateWindow(name, image, filename=''):
    try:
        windows[name]
    except:
        windows[name] = image
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)  # moveWindow
        cv2.setMouseCallback(name, mouseCallback)
    cv2.imshow(name, image)
    if len(filename) > 0:
        cv2.imwrite(filename, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

