# Code used in two tests: 
# Code used to test 3 LEDS powered by the Pico on the PCB
# Connected to pins 16, 17, and 18
# Blinks all 3 LEDs on and off every second



import machine
import time
from machine import Pin 

led1 = Pin(16, Pin.OUT)
led2 = Pin(17, Pin.OUT) 
led3 = Pin(18, Pin.OUT)

while True:
    led1.value(0)
    led2.value(0)
    led3.value(0)
    time.sleep(1)
    
    led1.value(1)
    led2.value(1)
    led3.value(1)
    time.sleep(1)

