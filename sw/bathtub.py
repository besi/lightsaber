import machine
import time
from machine import Pin, ADC
from neopixel import NeoPixel

pixel_count = 48
button_pin = 5
PRESSED = 0

if machine.unique_id().hex() == '68b6b3bc4128':
    pixel_count = 74
    button_pin = 4

button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

strip_pin = 2
poti_pin = 1


np = NeoPixel(Pin(strip_pin), pixel_count)
np1 = NeoPixel(Pin(7),1) 
poti = ADC(poti_pin)

import time
import machine
import neopixel
import secrets
from umqtt.robust import MQTTClient
import json

from machine import Pin
import time
import ubinascii

DELAY = 300

def fill(color):
    np.fill(color)
    np.write()

def clear():
    np.fill((0, 0, 0))
    np.write()

## MQTT
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'services/bathtub'

mqtt_server = secrets.mqtt.host
mqtt_port = secrets.mqtt.port
mqtt_user = secrets.mqtt.user
mqtt_password = secrets.mqtt.password

# Determine SSID
import network
sta = network.WLAN(network.STA_IF)
ssid = sta.config('essid')

# Setup Neopixel
pixelCount = pixel_count
np.fill((0,0,0));np.write()
keepalive = 65535
ideal = 42
index = 0

def connect():
  # if you set keepalive value - you have to send something to mqtt server to inform that you are alive in less time than keepalive value of seconds.
  client = MQTTClient(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password,keepalive=DELAY * 2)
  client.connect()
  print('Connected to %s MQTT broker' % mqtt_server)
  return client

def stamp():
    (year,month,mday,h,m,s,weekday,yearday) = utime.localtime()
    return f"{hour}:{minute:02d}"
    
client = connect()
print("Connected to MQTT")
mqtt_keepalive = time.time()

def setTemperature(temp, increment = 2):
    
    global index, np, pixelCount, ideal
    
    (red,green,blue) = (0,0,0)
    green = max((255 - abs(int((ideal - temp) * 30))),0)

    if temp < ideal:
        blue = max((int((ideal - temp) * 30)),0) 
    else:
        red = min((int((temp - ideal) * 60)),255)

    for i in range(index, index + increment):
        np[i] = (red,green,blue)

    # Clear upcoming pixels
    for i in range(index+increment,index+increment+10):
      np[i%pixelCount] = (0,0,0); np.write()
    
    np.write()
    index = (index + increment) % pixelCount


def sub_cb(topic, msg):
    data = msg.decode('utf-8')
    try:
        t = json.loads(data)['temp']    
        print(f"Temeperature {t:.2f}")
        setTemperature(t)
    except OSError as e:
        print(f"Failed parsing JSON: {json.loads(data)}")

def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub, mqtt_port, mqtt_user, mqtt_password,sub_cb
    client = MQTTClient(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password,keepalive=keepalive)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client

client = None

try:
    print("connecting to MQTT")
    client = connect_and_subscribe()
except OSError as e:
    print("ERRRRRROOOOOOOR reconnect")
    client = connect_and_subscribe()

while True:
    client.check_msg()
    time.sleep(1)



##### TESTING ######

def test():
    global index
    global ideal
    clear()
    
    index = 0
    for i in range(ideal-9, ideal+9):
        setTemperature(i, increment=3)
