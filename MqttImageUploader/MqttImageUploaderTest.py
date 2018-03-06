import unittest
import sys
sys.path.append("../MqttImageUploader")
import json
from MqttImageUploader import *

url = "159.100.249.153"

def publish_callback(client, userdata, result):
    print("published data motherfuckers")
    print(result)

class MqttImageUploaderTest(unittest.TestCase):

    def testPublish(self):
        print('tp')
        uploader = MqttImageUploader(
            url, 1883, "test/test")
        uploader.UploadData(
            "../downloaded/test-test_2560x1920_2000_01_01-00_00.jpg", '{"timestamp":123123123}', publish_callback)

    def testWithDictionryJson(self):
        print('twdj')
        uploader = MqttImageUploader(url, 1883, "test/test")
        j = dict()
        j['timestamp'] = 123123123
        uploader.UploadData('../downloaded/test-test_2560x1920_2000_01_01-00_00.jpg', json.dumps(j), publish_callback)

 
if __name__ == '__main__':
    unittest.main()
