from MqttImageUploader import *

d = dict()
d['timestamp'] = 123123123
d['farmId'] = "valliFarm"
d['batchId'] = "valliBatchBig"
d['lineId'] = 2
d['fake'] = 420
d['type'] = "image"
UploadMQTT("zero/test/images", 'downloaded/test-test_2560x1920_2000_01_01-00_00.jpg', d)
