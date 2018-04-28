from MqttImageUploader import *

d = dict()
d['timestamp'] = 666666
d['lineId'] = 666
d['uniformity'] = 669
d['biomass'] = 969
d['type'] = "image"
d['farmId'] = "somehost"
d['batchId'] = "somebatch"
d['type'] = "image"
print(UploadMQTT("zero/test/images", 'timelapse/timelapse.txt', d))
