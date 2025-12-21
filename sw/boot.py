import machine
import time
from machine import Pin, ADC

pixel_count = 48
button_pin = 5
PRESSED = 0

if machine.unique_id().hex() == '68b6b3bc4128':
    pixel_count = 74
    button_pin = 4

button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

strip_pin = 2
poti_pin = 1

# Enter special mode
if button() == PRESSED:
    import startwifi
    import bathtub
