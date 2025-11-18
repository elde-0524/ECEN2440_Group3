import machine, time, math
from machine import Pin, PWM
from ir_rx.nec import NEC_8  
from ir_rx.print_error import print_error  # for debugging

# LED pin setup
LED1 = Pin(16, Pin.OUT)
LED2 = Pin(17, Pin.OUT)
LED3 = Pin(18, Pin.OUT)


# define IR command codes
IR_FORWARD_CODE  = 0x18  
IR_OFF_CODE = 0x14  
IR_BACKWARD_Code = 0x03

# Function to blink all LEDs
def blink_all_leds(times=3, delay=0.3):
    for _ in range(times):
        LED1.on()
        LED2.on()
        LED3.on()
        time.sleep(delay)
        LED1.off()
        LED2.off()
        LED3.off()
        time.sleep(delay)



# Callback function for when IR command received
def ir_callback(data, addr, _):
    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")
    if data == IR_FORWARD_CODE:
        print("Command 0x01: Blinking all LEDs")
        blink_all_leds()
    elif data == IR_OFF_CODE:
        print("Command 0x02: Blinking all LEDs")
        blink_all_leds()
    elif data == IR_BACKWARD_Code:
        print("Command 0x03: Blinking all LEDs")
        blink_all_leds()
    else: 
        print("Unknown command")

# Setup the IR receiver
ir_pin = Pin(18, Pin.IN, Pin.PULL_UP)  # adjust pin if needed
ir_receiver = NEC_8(ir_pin, callback=ir_callback)
ir_receiver.error_function(print_error)

# continue running
while True:
    time.sleep(0.5)
