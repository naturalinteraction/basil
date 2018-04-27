from utility import *
from vision import *
# from audio import AudioLevelPi
# from audio import AudioLevelLaptop
from S3 import UploadFileToS3
from S3 import ListFilesOnS3
from S3 import DownloadFileFromS3
from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
import os
from MqttImageUploader import *

def test_GitCommitMessage():
    assert len(GitCommitMessage().split('\n')) >= 5

def test_GitCommitMessagePretty():
    assert len(GitCommitMessagePretty()) > 0

def test_OpenCVVersion():
    assert len(OpenCVVersion()) > len('OpenCV ')

def test_GitHash():
    assert len(GitHash()) == 40
'''
def test_AudioLevelPi():
    assert AudioLevelPi() == -1  # assuming there is no second sound card on the laptop

def test_AudioLevelLaptop():
    assert AudioLevelLaptop() > 0
'''
'''
def test_UploadFileToS3():
    assert UploadFileToS3('test.txt')

def test_ListFilesOnS3():
    assert len(ListFilesOnS3('zero/test-test')) == 2

def test_DownloadFileFromS3():
    assert DownloadFileFromS3('test.txt', 'downloaded/test.txt')

def test_ListLocalImagesAndDownloadImagesFromS3():
    test_images = ListLocalImages('downloaded/test-test', '')
    for t in test_images:
        os.remove(t)
    assert len(ListLocalImages('downloaded/test-test', '')) == 0
    skipped,downloaded,failed = DownloadImagesFromS3('zero/test-test', '')
    assert (skipped == 0 and downloaded == 2 and failed == 0)
    skipped,downloaded,failed = DownloadImagesFromS3('zero/test-test', '')
    assert (skipped == 2 and downloaded == 0 and failed == 0)
    skipped,downloaded,failed = DownloadImagesFromS3('zero/test-test', '30')
    assert (skipped == 1 and downloaded == 0 and failed == 0)
    assert len(ListLocalImages('downloaded/test-test', '')) == 2
    assert len(ListLocalImages('downloaded/test-test', '30')) == 1
'''

def test_CombinedMeanStandardDeviation():
    assert CombinedMeanStandardDeviation(63, 9, 50, 54, 6, 40) == (59.0, 9.0)
    m,s = CombinedMeanStandardDeviation((3, 2, 1), (1, 9, 5), 80, (3, 9, 100), (1, 2, 3), 5)
    assert m.tolist() == [3.0,  2.411764705882353, 6.823529411764706]
    assert s.tolist() == [1.0, 8.898504986988558, 23.804931011965337]

def ProvideValidTestImage():
    return cv2.imread('downloaded/test-test_2560x1920_2000_01_30-00_00.jpg')

def test_Vision(image=ProvideValidTestImage()):
    assert cv2.mean(image) == (139.9120194498698, 175.01678141276042, 169.36513631184897, 0.0)
    image = ToHSV(image)
    image = GaussianBlurred(image)
    image = Blurred(image, size=3)
    image = MedianBlurred(image)
    assert((35.50775329589844, 56.24323201497396, 175.11448954264324, 0.0) == cv2.mean(image))
    '''
    mask = SegmentBiomass(image, cv2.mean(image), (0.1, 0.2, 0.3), 100.0)
    assert(1709141 == len(cv2.findNonZero(mask)))
    mask = Erode(mask, 5, 2)
    assert(1611071 == len(cv2.findNonZero(mask)))
    ignored1, contours, ignored2 = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    assert(ContourStats(contours[0]) == (39.0, 0.5735294117647058, 1.0, 0.11599151536825965))
    mask = Dilate(mask, iterations=3)
    assert(1644340 == len(cv2.findNonZero(mask)))
    image = GrayToBGR(mask)
    assert((85.30816650390625, 85.30816650390625, 85.30816650390625, 0.0) == cv2.mean(image))
    single_channel = BGRToGray(image)
    assert(cv2.mean(single_channel)[0] == 85.30816650390625)
    mask = Inverted(single_channel)
    assert(3270860 == len(cv2.findNonZero(mask)))
    mask = Dilate(mask)
    image = MaskedImage(image, mask)
    assert((1.7259918212890626, 1.7259918212890626, 1.7259918212890626, 0.0) == cv2.mean(image))
    box = BoundingBox()
    assert(box.rect == None)
    mask = Inverted(mask)
    assert(box.Update(mask) == 1611071)
    assert(box.rect == rectangle(xmin=6, ymin=6, xmax=2554, ymax=1701))
    '''

def test_ColorStatistics():
    cs = ColorStatistics()
    cs.Update((1, 2, 3))
    cs.Update((4, 5, 6))
    mean,stddev = cs.ComputeStats()
    assert(list(mean) == [2.5,  3.5,  4.5])
    assert(list(stddev) == [1.5,  1.5,  1.5])

def test_MQTT():
    d = dict()
    d['timestamp'] = 123123123
    d['farmId'] = "valliFarm"
    d['batchId'] = "valliBatchBig"
    d['lineId'] = 2
    d['fake'] = 420
    d['type'] = "image"
    assert(UploadMQTT("zero/test/images", 'test.txt', d) == 1)

