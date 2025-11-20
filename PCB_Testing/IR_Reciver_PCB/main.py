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
# Timestamp of the last received valid command (IR or RF)
last_signal_time = utime.ticks_ms()
# Whether motors are currently considered active (moving)
motor_active = False
# Timeout (ms) after which motors should stop if no signal received
STOP_TIMEOUT_MS = 3000  # 3 seconds by default; tweak as needed


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
    
    # Print received command
    if data == FORWARD_CODE:
        motor_controller.move_forward()
        # mark motors active and update last-signal timestamp
        global last_signal_time
        global motor_active
        motor_active = True
        last_signal_time = utime.ticks_ms()
    elif data == BACKWARD_CODE:
        motor_controller.move_backward()
        motor_active = True
        last_signal_time = utime.ticks_ms()
    elif data == LEFT_CODE:
        motor_controller.turn_left()
        motor_active = True
        last_signal_time = utime.ticks_ms()
    elif data == RIGHT_CODE:
        motor_controller.turn_right()
        motor_active = True
        last_signal_time = utime.ticks_ms()
    elif data == STOP_CODE:
        motor_controller.stop()
        motor_active = False
        last_signal_time = utime.ticks_ms()
    else: 
        print("Unknown command")


# Setup the IR receiver
ir_pin = Pin(18, Pin.IN, Pin.PULL_UP) 
ir_receiver = NEC_8(ir_pin, callback=ir_callback)
ir_receiver.error_function(print_error) 


while True:
    # Periodically check for motor timeout
    time.sleep(0.1)

    now = utime.ticks_ms()
    if motor_active and utime.ticks_diff(now, last_signal_time) > STOP_TIMEOUT_MS:
        print("No signal received for timeout period — stopping motors")
        motor_controller.stop()
        motor_active = False
        # update last_signal_time so stop isn't called repeatedly
        last_signal_time = utime.ticks_ms()
