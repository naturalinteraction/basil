import io
import time
import paho.mqtt.client as mqtt
import base64
import json
from io import BytesIO

from PIL import Image, ImageColor


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

# def on_message(client, userdata, msg):
# 	print(msg.topic+" "+str(msg.payload))


def on_publish(client, userdata, result):
    print("data published \n")
    print(result)


class MqttImageUploader:
    def __init__(self, host, port, topic):
        self.host = host
        self.port = port
        self.topic = topic

    def UploadData(self, image_name, json_string, callback):
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_publish = callback
        print "connecting to %s on port %s\npublishing on topic %s" % (
            self.host, self.port, self.topic)
        client.connect(self.host, self.port, 60)
        img = Image.open(image_name)

        asString = base64.b64encode(img.tobytes())
        j = json.loads(json_string)
        j['image'] = asString
        j['timestamp'] = time.time()
        client.publish(self.topic, json.dumps(j), qos=0)
