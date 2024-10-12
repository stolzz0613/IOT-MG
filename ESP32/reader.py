import bluetooth
import time
from simpleBLE import BLEPeripheral
from machine import Pin
import dht

# Bluetooth object
ble = bluetooth.BLE()

# AWS IoT Core settings
server = "a1ztq6e5d2o4a0-ats.iot.us-east-1.amazonaws.com"
client_id = "StolzzThing"
topic_sub = "esp32/sub"
topic_pub = "esp32/sensor-andres"

service = 0x181a
combined_characteristic = 0x2a6e
env_sensor = BLEPeripheral(ble, "env_sensor", service, combined_characteristic)
dht_sensor = dht.DHT22(Pin(4))

i = 0

while True:
    try:
        dht_sensor.measure()
        t = dht_sensor.temperature()
        h = dht_sensor.humidity()
        
        temp_value = int(t * 100)
        humidity_value = int(h * 100)
        print(temp_value)
        print(humidity_value)
        env_sensor.set_values([temp_value, humidity_value], notify=i == 0, indicate=False)
        i = (i + 1) % 10
        
    except OSError as e:
        print("Error al leer el sensor DHT:", e)
    
    time.sleep_ms(1000)


