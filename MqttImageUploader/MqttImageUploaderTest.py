import unittest
import sys
sys.path.append("../MqttImageUploader")
import json
from MqttImageUploader import *
import time

url = "159.100.249.153"

def publish_callback(client, userdata, result):
    print("published data motherfuckers")
    print(result)

class MqttImageUploaderTest(unittest.TestCase):

    def testWithDictionaryJson(self):
        print('testWithDictionaryJson')
        uploader = MqttImageUploader(url, 8883, "zero/test/images", True, "/home/av/ca.crt", "/home/av/client.crt","/home/av/client.key")
        j = dict()
        j['timestamp'] = 123123123
        j['farmId'] = "valliFarm"
        j['batchId'] = "valliBatchBig"
        j['lineId'] = 2
        j['fake'] = 420
        j['type'] = "image"
        uploader.UploadData('../downloaded/test-test_2560x1920_2000_01_01-00_00.jpg', json.dumps(j), publish_callback)

if __name__ == '__main__':
    unittest.main()
