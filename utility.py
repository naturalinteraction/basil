from __future__ import print_function  # provides Python 3's print() with end=''
import subprocess
import cv2
import argparse
import collections
import numpy as np
import sys
import pickle
import time


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


def CombinedMeanStandardDeviation(m1, s1, n1, m2, s2, n2):
    m1 = np.array(m1)
    m2 = np.array(m2)
    s1 = np.array(s1)
    s2 = np.array(s2)
    mean = (n1 * m1 + n2 * m2) / float(n1 + n2)
    v1 = s1 ** 2
    v2 = s2 ** 2
    d1 = m1 - mean
    d2 = m2 - mean
    variance = (n1 * (v1 + (d1 ** 2)) + n2 * (v2 + (d2 ** 2))) / float(n1 + n2)
    stddev = variance ** 0.5
    return mean,stddev


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
global means
global stddevs
global labels
global good
global bad
good = set()
bad = set()
means = []
stddevs = []

def SetMouseMeansDevsLabels(m, s, l):
    global means
    global stddevs
    global labels
    global good
    global bad
    means = m
    stddevs = s
    labels = l
    good = set()
    bad = set()
    bad.update(range(0, len(means)))
    print('bad', bad)

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

def ReplaceLabelWithColor(labels, selected, image, color, window_name):
    h,w = labels.shape
    for x in range(0, w):
        for y in range(0, h):
            if labels[y][x] == selected:
                image[y][x] = color
    UpdateWindow(window_name, image)
    cv2.setMouseCallback(window_name, mouseCallbackGoodBad)

def mouseCallbackGoodBad(event, x, y, flags, param):
    global good
    global bad
    try:
        labels
    except:
        # print('no labels')
        mouseCallback(event, x, y, flags, param)
        return
    if event == cv2.EVENT_LBUTTONDOWN:
        selected = labels[y,x]
        print('adding to good ' + str(means[selected]) + ' ' + str(selected))
        try:
            good.add(selected)
            bad.remove(selected)
        except:
            pass
        ReplaceLabelWithColor(labels, selected, windows['bgr'], (255, 0, 0), 'bgr')
    if event == cv2.EVENT_RBUTTONDOWN:
        selected = labels[y,x]
        print('adding to bad ' + str(means[selected]) + ' ' + str(selected))
        try:
            bad.add(selected)
            good.remove(selected)
        except:
            pass
        ReplaceLabelWithColor(labels, selected, windows['bgr'], (0, 255, 255), 'bgr')
    if event == cv2.EVENT_MBUTTONDOWN:
        print('good', good)
        print('bad', bad)
        print('saving.')
        with open('colors.pkl', 'w') as f:
            pickle.dump((means,stddevs,good,bad), f, 0)
        good = set()
        bad = set()
        bad.update(range(0, len(means)))

def UpdateWindow(name, image, filename=''):
    try:
        windows[name]
    except:
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)  # moveWindow
        if name == 'bgr':
            cv2.setMouseCallback(name, mouseCallbackGoodBad)
        else:
            cv2.setMouseCallback(name, mouseCallback)
    cv2.imshow(name, image)
    windows[name] = image
    if len(filename) > 0:
        cv2.imwrite(filename, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
