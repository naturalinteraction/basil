from __future__ import print_function  # provides Python 3's print() with end=''
import subprocess
import cv2
import argparse
import collections
import numpy as np
import sys
import pickle


def interrogate(item):
    if hasattr(item, "__name__"):
        print("name: ", item.__name__)
    if hasattr(item, "__class__"):
        print("class: ", item.__class__.__name__)
    print("type: ", type(item))
    print("value: ", repr(item))
    print("callable: ", isinstance(item, collections.Callable))
    if hasattr(item, '__doc__'):
        doc = getattr(item, '__doc__')
        # doc = doc.strip()
        print('doc: ', doc)


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
    parser = argparse.ArgumentParser(description='process images from the sensors')
    parser.add_argument('-p', '--prefix', default = 'visible-sanbiagio1', help='the prefix for the images')
    parser.add_argument('-s', '--substring', default='', help='the substring to filter the images')
    parser.add_argument('-r', '--routine', default='display', help='the routine to process the images')
    parser.add_argument('-d', '--download', dest='download', action='store_const',
                        const=True, default=False,
                        help='download images from S3')
    args = parser.parse_args()
    print('prefix = ' + args.prefix)
    print('substring = ' + args.substring)  # '2017_12_31', ''  # background change on the 12th, between 15.00 and 15.31
    print('routine = ' + args.routine)
    print('download = ' + str(args.download))
    return args


'''
keystrokes
'''
def ProcessKeystrokes():
    key = cv2.waitKey(500) & 0xFF  # milliseconds
    if key not in [27, 255]:  # any key except ESC to toggle pause
        key = cv2.waitKey(0) & 0xFF  # milliseconds
    # if the ESC key was pressed, simply quit
    if key == 27:
        print('exiting')
        quit()


'''
windows
'''

class ColorStatistics:
    pixels = list()

    def ComputeStats(self):
        return np.mean(self.pixels, axis=0),np.std(self.pixels, axis=0)

    def Reset(self):
        print('Enter filename without extension: ')
        filename = sys.stdin.readline()
        filename = filename.strip() + '.pkl'
        with open(filename, 'wb') as f:
            pickle.dump((self.ComputeStats()), f, 0)
        print('Saved ' + filename)
        print('Reset')
        self.pixels = list()

    def Update(self, pixel):
        self.pixels.append(pixel)
        # print(np.var(self.pixels, axis=0))  # variance

def SaveColorStats(mean, stddev, filename):
    with open(filename, 'wb') as f:
        pickle.dump((mean,stddev), f, 0)

def LoadColorStats(filename):
    with open(filename, 'rb') as f:
        return np.array(pickle.load(f))

windows = {}

hsv_stats = ColorStatistics()

def mouseCallback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        for w in windows.keys():
            print (w + str(windows[w][y,x].tolist()))
        try:
            hsv_stats.Update(windows['hsv'][y,x].tolist())
            print(hsv_stats.ComputeStats())
        except:
            pass
    if event == cv2.EVENT_RBUTTONDOWN:
        hsv_stats.Reset()

def UpdateWindow(name, image, filename=''):
    try:
        windows[name]
    except:
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)  # moveWindow
        cv2.setMouseCallback(name, mouseCallback)
    cv2.imshow(name, image)
    windows[name] = image
    if len(filename) > 0:
        cv2.imwrite(filename, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
