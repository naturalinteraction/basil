from MqttImageUploader import *

d = dict()
d['timestamp'] = 123123123
d['farmId'] = "valliFarm"
d['batchId'] = "valliBatchBig"
d['lineId'] = 2
d['fake'] = 420
d['type'] = "image"
print(UploadMQTT("zero/test/images", 'test.txt', d))
