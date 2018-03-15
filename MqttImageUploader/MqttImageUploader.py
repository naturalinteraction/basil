import io
import time
import paho.mqtt.client as mqtt
import ssl
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
    def __init__(self, host, port, topic, tls, ca_certificate, client_certificate, client_key):
        self.host = host
        self.port = port
        self.topic = topic
        self.ca_certificate = ca_certificate
        self.client_key = client_key
        self.client_certificate = client_certificate

    def UploadData(self, image_name, json_string, callback):
        client = mqtt.Client()
        client.tls_set(self.ca_certificate ,self.client_certificate, self.client_key, cert_reqs=ssl.CERT_NONE,tls_version=ssl.PROTOCOL_TLSv1_2)
        client.tls_insecure_set(True)
        client.on_connect = on_connect
        client.on_publish = callback
        print "connecting to %s on port %s\npublishing on topic %s" % (
            self.host, self.port, self.topic)
        client.connect(self.host, self.port, 60)
        img = Image.open(image_name)

        asString = base64.b64encode(img.tobytes())
        print(len(asString))
        j = json.loads(json_string)
        j['image'] = asString
        j['timestamp'] = time.time()
        print('publish call about to be made')
        client.publish(self.topic, json.dumps(j), qos=0)
        print('publish called')
