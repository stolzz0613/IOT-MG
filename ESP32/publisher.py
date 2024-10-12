import time
import bluetooth
from machine import reset, deepsleep
from simpleBLE import BLECentral
from mqtt import MQTTClient
import json

not_found = False
published = False

# Bluetooth object
ble = bluetooth.BLE()

# Environmental service
service = 0x181a
characteristic = 0x2a6e

# BLE Central object
central = BLECentral(ble, service, characteristic)

with open("certs/cert", 'rb') as f:
    certf = f.read()
with open("certs/privKey", 'rb') as f:
    keyf = f.read()

def on_scan(addr_type, addr, name):
    if addr_type is not None:
        print("Found sensor:", addr_type, addr, name)
        central.connect()
    else:
        global not_found
        not_found = True
        print("No sensor found.")

central.scan(callback=on_scan)

# AWS IoT Core settings
server = "a1ztq6e5d2o4a0-ats.iot.us-east-1.amazonaws.com"
client_id = "StolzzThing"
topic_sub = "esp32/sub"
topic_pub = "esp32/sensor-andres"

def publish_callback():
    global published
    published = True
    print("Mensaje publicado correctamente.")

def publish_and_sleep(data):
    global published
    published = False

    client.publish(topic=topic_pub, msg=json.dumps({"temp": data[0] / 100, "hum": data[1] / 100}))
    print(f"Data published: Temp={data[0] / 100}, Hum={data[1] / 100}")
    time.sleep(1)
    publish_callback()

client = MQTTClient(client_id=client_id, server=server, port=8883, ssl=True, ssl_params={"cert": certf, "key": keyf})
client.set_callback(publish_callback)
client.connect()
client.subscribe(topic=topic_sub)

retries = 0
while not central.is_connected():
    time.sleep_ms(100)
    retries += 1
    if retries == 100 or not_found:
        reset()

print("Connected")

try:
    central.read(callback=publish_and_sleep)
except Exception as e:
    print("Error:", e)

while not published:
    time.sleep(0.1)

if central.is_connected():
    central.disconnect()
print("Disconnected from BLE")
    
client.disconnect()
print("Disconnected from MQTT")

deepsleep(2000)

