from MqttImageUploader import *

d = dict()
d['timestamp'] = 666666
d['lineId'] = 666
d['uniformity'] = 669
d['biomass'] = 969
d['type'] = "image"
d['farmId'] = "somehost"  # "valliFarm"
d['batchId'] = "somebatch"  # "valliBatchBig"
d['type'] = "image"
print(UploadMQTT("zero/test/images", 'downloaded/redshift-sanbiagio1_2560x1920_2018_01_21-13_00.jpg', d))
