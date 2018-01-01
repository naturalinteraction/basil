import subprocess
import cv2

def OpenCVVersion():
    return 'OpenCV ' + cv2.__version__

def GitHash():
    return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()

def GitCommitMessage():
    return subprocess.check_output(["git", "log", "-1"]).strip()

def GitCommitMessagePretty():
    return subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).strip()
