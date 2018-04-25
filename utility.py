from __future__ import print_function  # provides Python 3's print() with end=''
import subprocess
import cv2
import argparse
import collections
import numpy as np
import sys
import pickle
import time
import os
import psutil
import glob
from datetime import datetime
import globa
# to deal with timezones and tzinfo:
# from tzlocal import get_localzone
# import pytz

def LoadCustomer():
    file = open('customer.txt')
    customer_name = file.read().strip()
    print('customer: ' + customer_name)
    if customer_name == 'none':
        print('customer has not been initialized. exiting.')
        quit()
    return customer_name

globa.customer = LoadCustomer()

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


def Macduff():
    print('Macduff')
    globa.locations = []
    try:
        os.remove('colorcalibration/output.csv')
        os.remove('colorcalibration/output.jpg')
    except:
        pass
    result = cv2.resize(globa.image, (0, 0), fx=0.2, fy=0.2)
    cv2.imwrite('colorcalibration/input.jpg', result, [int(cv2.IMWRITE_JPEG_QUALITY), 100])  # up to 100, default 95
    try:
        print(os.popen("./colorcalibration/macduff colorcalibration/input.jpg colorcalibration/output.jpg > colorcalibration/output.csv").read().strip())
    except:
        return 'Could not run colorchecker finder!'
    os.remove('colorcalibration/input.jpg')
    try:
        do_not_redefine_str = open('colorcalibration/output.csv').read().strip()
    except:
        do_not_redefine_str = ''
        return 'Could not find colorchecker!'
    location_coords = do_not_redefine_str.replace(',', '\n').split('\n')
    print('location_coords', location_coords)
    print('coords = ', len(location_coords))
    if len(location_coords) == 48:
        # macduff worked
        for i in range(24):
            globa.locations.append((int(location_coords[i * 2 + 0]) * 5, int(location_coords[i * 2 + 1]) * 5))
        print('globa.locations', globa.locations)
        with open('calibration-locations.pkl', 'w') as f:
            pickle.dump(globa.locations, f, 0)
        return ''
    else:
        # macduff did not work
        return 'Could not find all the locations!'


'''
versions
'''
def OpenCVVersion():
    return 'OpenCV ' + cv2.__version__

def PiTemperature():
    return os.popen("/opt/vc/bin/vcgencmd measure_temp").read().strip().replace("'", "").replace("temp=", "")

def GitRevCount():
    return os.popen("git rev-list --count master").read().strip()
    # return os.popen("git rev-list --all --count").read().strip()

def GitBranch():
    return os.popen("git branch | grep \* | cut -d ' ' -f2").read().strip()

def GitHash():
    return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()

def GitCommitMessage():
    return subprocess.check_output(["git", "log", "-1"]).strip()

def GitCommitMessagePretty():
    return subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).strip()

# print out debug information about current source code version
# print(GitCommitMessage())

def ExifKeywords(file):
    return subprocess.check_output(["exiftool", "-Keywords", file]).strip()

def LegacySeriesStart(e):
    """for backward compatibility in batch aprile"""
    return ('series_start' in e)

def ExifBatchStart(file):
    batch_start = -1
    exif = ExifKeywords(file).split(',')
    for e in exif:
        if 'batch_start' in e or LegacySeriesStart(e):
            e = e.split('=')
            batch_start = int(e[-1])
    return batch_start

def GetCPUSerial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
  return cpuserial

def GetMAC(interface='eth0'):  # 'wlan0'
  # Return the MAC address of the specified interface
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"
  return str[0:17]

def GetSDSerial():
  try:
    str = open('/sys/block/mmcblk0/device/serial').read().strip()
  except:
    str = ''
  return str

def GetSDCID():
  try:
    str = open('/sys/block/mmcblk0/device/cid').read().strip()
  except:
    str = ''
  return str


def NumberOfUploadsInQueue():
    return str(len(glob.glob("cache/*.jpg")))

def MemoryPercent():
    mem = psutil.virtual_memory()
    return mem.percent

def CPUPercent():
    return psutil.cpu_percent(interval=1)

def DiskPercent():
    disk = os.statvfs('/')
    return 100 - 100 * disk.f_bavail / disk.f_blocks

def SensorFunctioningOK():
    if globa.initial_calibrate or globa.cameraproperties.auto_calibrate or globa.color_calibrate:  # mode
        return 'Calibrating'
    if CPUPercent() > 90:
        return 'High CPU'
    if MemoryPercent() > 90:
        return 'High Memory'
    if DiskPercent() > 90:
        return 'High Disk'
    if float(PiTemperature().replace('C', '')) > 75:
        return 'High Temperature'
    if int(NumberOfUploadsInQueue()) > 1:
        return 'Long Queue'
    return 'OK'

def UpdateFirmware():
    print('attempting to update firmware...')
    return os.popen("git pull").read().strip()

def RebootSensor():
    print('attempting to reboot sensor...')
    return os.popen("sudo /sbin/shutdown -r now").read().strip()

def RestartSensor():
    print('attempting to restart cap...')
    return os.popen("pkill -f cap").read().strip()


'''
parsing command line arguments
'''
def ParseArguments():
    parser = argparse.ArgumentParser(description='process images from the sensors')
    parser.add_argument('-p', '--prefix', default = 'redshift-callalta', help='the prefix for the images (sensor-batch^species)')
    parser.add_argument('-g', '--group', default = 'zero', help='the group the sensor belongs to')
    parser.add_argument('-s', '--substring', default='', help='the substring to filter the images')
    parser.add_argument('-r', '--routine', default='RoutineDisplay', help='the routine to process the images')
    parser.add_argument('-d', '--download', dest='download', action='store_const',
                        const=True, default=False,
                        help='download images from S3')
    parser.add_argument('-u', '--upload', dest='upload', action='store_const',
                        const=True, default=False,
                        help='upload results to S3')
    args = parser.parse_args()
    print('prefix = ' + args.prefix)
    print('group = ' + args.group)
    print('substring = ' + args.substring)
    print('routine = ' + args.routine)
    print('download = ' + str(args.download))
    print('upload = ' + str(args.upload))
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

def SaveTimeSeries(t, v, filename):
    with open(filename, 'wb') as f:
        pickle.dump((t,v), f, 0)

def LoadTimeSeries(filename):
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
