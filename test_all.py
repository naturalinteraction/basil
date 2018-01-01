from git import OpenCVVersion
from git import GitHash
from git import GitCommitMessage
from git import GitCommitMessagePretty
from audio import AudioLevelPi
from audio import AudioLevelLaptop

def test_GitCommitMessage():
    assert len(GitCommitMessage().split('\n')) >= 5

def test_GitCommitMessagePretty():
    assert len(GitCommitMessagePretty()) > 0

def test_OpenCVVersion():
    assert len(OpenCVVersion()) > len('OpenCV ')

def test_GitHash():
    assert len(GitHash()) == 40

def test_AudioLevelPi():
    assert AudioLevelPi() > 0

def test_AudioLevelLaptop():
    assert AudioLevelLaptop() > 0
