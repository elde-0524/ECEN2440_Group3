from machine import Pin
import time 
import utime

from ir_rx.nec import NEC_8  # Use the NEC 8-bit class
from ir_rx.print_error import print_error  # for debugging


# Example IR command values (you’ll need to print them from your remote first)
IR_FORWARD_CODE  = 0x01  
IR_OFF_CODE = 0x02  
IR_BACKWARD_Code = 0x03

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

button = Pin(20, Pin.IN, Pin.PULL_DOWN)    

RF_Operation_Mode = True

def ir_callback_RF(pin):
    if not RF_Operation_Mode:
        return

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


# Callback when IR command received
def ir_callback(data, addr, _):

    if RF_Operation_Mode:
        return
    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")

    if data == IR_FORWARD_CODE:
        print("Reci")
    elif data == IR_OFF_CODE:
        print("Stopping")
    elif data == IR_BACKWARD_Code:
        print("Moving Backward")
    else: 
        print("Unknown command")

def blink_all_leds():
    for _ in range(3):
        led1.value(1)
        led2.value(1)
        led3.value(1)
        led4.value(1)
        time.sleep(0.2)
        led1.value(0)
        led2.value(0)
        led3.value(0)
        led4.value(0)
        time.sleep(0.2)

# Setup the IR receiver
ir_pin = Pin(11, Pin.IN, Pin.PULL_UP)  # adjust pin if needed
ir_receiver = NEC_8(ir_pin, callback=ir_callback)
ir_receiver.error_function(print_error) 


def button_callback(pin):
    global RF_Operation_Mode
    RF_Operation_Mode = not RF_Operation_Mode 

    if RF_Operation_Mode:
        # blink_all_leds()
        print("Interrupts ENABLED")
    else:
        # blink_all_leds()
        print("Interrupts DISABLED")


signal1_irq = signal1.irq(trigger=Pin.IRQ_RISING, handler=ir_callback_RF)
signal2_irq = signal2.irq(trigger=Pin.IRQ_RISING, handler=ir_callback_RF)
signal3_irq = signal3.irq(trigger=Pin.IRQ_RISING, handler=ir_callback_RF)
signal4_irq = signal4.irq(trigger=Pin.IRQ_RISING, handler=ir_callback_RF)

button.irq(trigger=Pin.IRQ_RISING, handler=button_callback)

while True:
    time.sleep(0.1)  