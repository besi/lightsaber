import machine
import time
from machine import Pin, ADC
from neopixel import NeoPixel
from time import sleep


pixel_count = 48
button_pin = 5

if machine.unique_id().hex() == '68b6b3bc4128':
    pixel_count = 74
    button_pin = 4

PRESSED = 0
animate_delay = 0.008
strip_pin = 2
poti_pin = 1

np = NeoPixel(Pin(strip_pin), pixel_count)
np1 = NeoPixel(Pin(7),1) 
button = Pin(button_pin, Pin.IN, Pin.PULL_UP)
poti = ADC(poti_pin)

purple = (128,0,128)
blue = (0,0,255)
red = (255,0,0)
yellow = (150,105,0)
green = (0,255,0)
white = (85,85,85)

color_index = 0
colors = [blue, red, yellow, purple, green, white]

current_color = colors[color_index]
last_color = colors[len(colors)-1]


def next_color(store = True):
    global color_index
    index = color_index
    index += 1
    index = index % len(colors)
    if store:
        color_index = index
    return colors[index]

def dim_factor():
    return int(poti.read() * 77 / 4095) + 1
    
def clear(fade = False):
    if fade:
        c = last_color
        c = dim(c, dim_factor())
        for x in range(max(c)+1):
            n = ((max(c[0] - x,0), max(c[1] - x, 0), max(c[2] - x, 0) ))
            np.fill(n)
            np.write()
    else:
        np.fill((0,0,0))
        np1.fill((0,0,0))
        np.write()
        np1.write()

        
def show(c, animated = True):
    color = dim(c, dim_factor())
    brightness = dim_factor()
    if animated:
        for x in range(pixel_count - 1):
            np[x] = color
            np[pixel_count -1 - x] = color
            np.write()
            sleep(animate_delay)
    else:
        np.fill(color)
        np.write()

        
def wait_for_button():
    while button() != PRESSED:
        sleep(.01)

def dim(c, f=100):
    return (( max(int(c[0]/f),0), max(int(c[1]/f),0), max(int(c[2]/f),0) ))
 
def swap(c):
    return ((c[1], c[0], c[2]))

def status(c):
    np1.fill(swap(c))
    np1.write()
 
clear()
state = 'start'
status(dim(current_color))


while True:
    
    if state == 'start':
        wait_for_button()
        status(dim(next_color(False)))
        show(current_color)
        state = 'light'
        print("state = light")
        last_color = current_color

    elif state == 'light':
        if button() != PRESSED:
            show(current_color, False)
        elif button() == PRESSED:
            clear(True)
            state = 'start'
            print("state = start")
            current_color = next_color(True)

            sleep(.2)
    sleep(.1)

