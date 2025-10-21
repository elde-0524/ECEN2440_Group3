`from machine import Pin
import time 
import utime


last_time = 0
signal1 = Pin(16, Pin.IN)
signal2 = Pin(17, Pin.IN)
signal3 = Pin(18, Pin.IN)
signal4 = Pin(19, Pin.IN)    

led1 = Pin(12, Pin.OUT)  
led2 = Pin(13, Pin.OUT)
led3 = Pin(14, Pin.OUT)
led4 = Pin(15, Pin.OUT)

led1.value(0)
led2.value(0)
led3.value(0)   
led4.value(0)

def ir_callback(pin):

    global last_time
    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_time) < 100:  # ignore within 200 ms
        return
    last_time = now

    if pin == signal1:
        led1.value(1)
        led2.value(0)
        led3.value(0)
        led4.value(0)
        print("Button A pressed")
    elif pin == signal2:
        led1.value(0)
        led2.value(1)
        led3.value(0)
        led4.value(0)
        print("Button B pressed")
    elif pin == signal3:
        led1.value(0)
        led2.value(0)
        led3.value(1)
        led4.value(0)
        print("Button C pressed")   
    elif pin == signal4:
        led1.value(0)
        led2.value(0)
        led3.value(0)
        led4.value(1)
        print("Button D pressed")  


signal1.irq(trigger=Pin.IRQ_RISING, handler=ir_callback)
signal2.irq(trigger=Pin.IRQ_RISING, handler=ir_callback)
signal3.irq(trigger=Pin.IRQ_RISING, handler=ir_callback)
signal4.irq(trigger=Pin.IRQ_RISING, handler=ir_callback)


while True:
    time.sleep(0.1)  `