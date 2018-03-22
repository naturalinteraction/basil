import io
import time
import paho.mqtt.client as mqtt
import ssl
import base64
import json
from io import BytesIO

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

class MqttImageUploader:
    def __init__(self, host, port, topic, tls, ca_certificate, client_certificate, client_key):
        self.host = host
        self.port = port
        self.topic = topic
        self.ca_certificate = ca_certificate
        self.client_key = client_key
        self.client_certificate = client_certificate
        self.tls = tls

    def UploadData(self, image_name, json_string, callback):
        client = mqtt.Client()
        if self.tls:
            client.tls_set(self.ca_certificate ,self.client_certificate, self.client_key, cert_reqs=ssl.CERT_NONE,tls_version=ssl.PROTOCOL_TLSv1_2)
            client.tls_insecure_set(True)
            client.on_connect = on_connect
            client.on_publish = callback
        print "connecting to %s on port %s\npublishing on topic %s" % (
            self.host, self.port, self.topic)
        client.connect(self.host, self.port, 60)
        client.loop_start()
        imgFile = open(image_name,"r")
        img = imgFile.read()
        asString = base64.b64encode(img)
        print(str(len(asString)) + ' bytes')
        j = json.loads(json_string)
        j['image'] = asString
        j['timestamp'] = time.time()
        client.publish(self.topic, json.dumps(j), qos=0)
        client.loop_stop()


mqtt_url = "159.100.249.153"
mqtt_port = 8883

def mqtt_publish_callback(client, userdata, result):
    print("published data")
    print(result)

def UploadMQTT(topic, filename, dictionary):
    print('UploadMQTT')
    uploader = MqttImageUploader(mqtt_url, mqtt_port, topic, True, "/etc/zero/ca.crt", "/etc/zero/client.crt","/etc/zero/client.key")
    uploader.UploadData(filename, json.dumps(dictionary), mqtt_publish_callback)
