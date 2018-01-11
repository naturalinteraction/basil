import subprocess
import cv2
import argparse
import collections
import numpy as np


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
    parser.add_argument('-p', '--prefix', default = 'visible-bianco', help='the prefix for the images')
    parser.add_argument('-s', '--substring', default='2017_12_31', help='the substring to filter the images')
    parser.add_argument('-d', '--download', dest='download', action='store_const',
                        const=True, default=False,
                        help='download images from S3')
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


'''
windows
'''

class ColorStatistics:
    pixels = list()

    def ComputeStats(self):
        return np.mean(self.pixels, axis=0),np.std(self.pixels, axis=0)

    def Reset(self):
        # todo: save to disk mean and stddev
        print(self.ComputeStats())
        print('reset')
        self.pixels = list()

    def Update(self, pixel):
        self.pixels.append(pixel)
        print(self.ComputeStats())

#basilico
#('mean', 36.532258064516128, 240.87096774193549, 155.45161290322579)
#('stddev', 1.3762705793543124, 17.877255211642115, 20.630135661176425)
#('mean', array([  36.82278481,  247.97468354,  154.82278481]))
#('stddev', array([  1.28042214,  11.140046  ,  16.07085537]))
#(array([  37.11111111,  240.27777778,  153.        ]), array([  1.5234788 ,  16.41071992,  30.5777697 ]))
#bianco
#(array([  39.63636364,   17.04545455,  207.45454545]), array([ 4.78202557,  2.82001407,  8.4138807 ]))
#muro
#(array([  32.5       ,   47.64285714,  181.14285714]), array([  2.58429322,   4.38515585,  10.84868091]))

windows = {}

hsv_stats = ColorStatistics()

def mouseCallback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        #for w in windows.keys():
        #    print (w, windows[w][y,x].tolist())
        hsv_stats.Update(windows['hsv'][y,x].tolist())
    if event == cv2.EVENT_RBUTTONDOWN:
        hsv_stats.Reset()

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
