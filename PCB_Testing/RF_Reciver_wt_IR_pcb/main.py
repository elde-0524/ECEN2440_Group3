from machine import Pin, PWM
import time 
import utime

from motorCommands import TwoMotorController


from ir_rx.nec import NEC_8  # Use the NEC 8-bit class
from ir_rx.print_error import print_error  # for debugging
from machine import I2C


# Example IR command values (you’ll need to print them from your remote first)
FORWARD_CODE  = 0x18 
BACKWARD_CODE = 0x17
LEFT_CODE     = 0x16
RIGHT_CODE    = 0x15
STOP_CODE     = 0x14    

last_time = 0
signal1 = Pin(7, Pin.IN)
signal2 = Pin(6, Pin.IN)
signal3 = Pin(5, Pin.IN)
signal4 = Pin(4, Pin.IN)    

led1 = Pin(0, Pin.OUT)  
led2 = Pin(1, Pin.OUT)
led3 = Pin(2, Pin.OUT)
led4 = Pin(3, Pin.OUT)

led1.value(0)
led2.value(0)
led3.value(0)   
led4.value(0)

button = Pin(2, Pin.IN, Pin.PULL_DOWN)    

RF_Operation_Mode = False

def ir_callback_RF(pin):
    if not RF_Operation_Mode:
        print("RF Operation Mode is disabled, ignoring RF commands.")
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


# Motor 1
ain1_ph = Pin(12, Pin.OUT)
ain2_en = PWM(Pin(13), freq= 2000)

# Motor 2
ain1_ph_2 = Pin(14, Pin.OUT)
ain2_en_2 = PWM(Pin(15), freq= 2000)


motor_controller = TwoMotorController(ain2_en, ain1_ph, ain2_en_2, ain1_ph_2)

# Callback when IR command received
def ir_callback(data, addr, _):

    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")

    if RF_Operation_Mode:
        # print("RF Operation Mode is enabled, ignoring IR commands.")
        return
    
    # Print received command
    if data == FORWARD_CODE:
        motor_controller.move_forward()
    elif data == BACKWARD_CODE:
        motor_controller.move_backward()
    elif data == LEFT_CODE:
        motor_controller.turn_left()
    elif data == RIGHT_CODE:
        motor_controller.turn_right()
    elif data == STOP_CODE:
        motor_controller.stop()
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
ir_pin = Pin(18, Pin.IN, Pin.PULL_UP) 
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