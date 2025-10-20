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

