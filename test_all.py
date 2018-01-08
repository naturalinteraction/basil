from utility import *
from audio import AudioLevelPi
from audio import AudioLevelLaptop
from S3 import UploadFileToS3
from S3 import ListFilesOnS3
from S3 import DownloadFileFromS3
from S3 import DownloadImagesFromS3
from S3 import ListLocalImages
import os

def test_GitCommitMessage():
    assert len(GitCommitMessage().split('\n')) >= 5

def test_GitCommitMessagePretty():
    assert len(GitCommitMessagePretty()) > 0

def test_OpenCVVersion():
    assert len(OpenCVVersion()) > len('OpenCV ')

def test_GitHash():
    assert len(GitHash()) == 40

def test_AudioLevelPi():
    assert AudioLevelPi() == -1  # assuming there is no second sound card on the laptop

def test_AudioLevelLaptop():
    assert AudioLevelLaptop() > 0
'''
def test_UploadFileToS3():
    assert UploadFileToS3('test.txt')

def test_ListFilesOnS3():
    assert len(ListFilesOnS3('cache/test-test')) == 2

def test_DownloadFileFromS3():
    assert DownloadFileFromS3('test.txt', 'downloaded/test.txt')

def test_ListLocalImagesAndDownloadImagesFromS3():
    test_images = ListLocalImages('downloaded/test-test', '')
    for t in test_images:
        os.remove(t)
    assert len(ListLocalImages('downloaded/test-test', '')) == 0
    skipped,downloaded,failed = DownloadImagesFromS3('cache/test-test', '')
    assert (skipped == 0 and downloaded == 2 and failed == 0)
    skipped,downloaded,failed = DownloadImagesFromS3('cache/test-test', '')
    assert (skipped == 2 and downloaded == 0 and failed == 0)
    skipped,downloaded,failed = DownloadImagesFromS3('cache/test-test', '30')
    assert (skipped == 1 and downloaded == 0 and failed == 0)
    assert len(ListLocalImages('downloaded/test-test', '')) == 2
    assert len(ListLocalImages('downloaded/test-test', '30')) == 1
'''
