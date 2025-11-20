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
signal1 = Pin(7, Pin.IN)
signal2 = Pin(6, Pin.IN)
signal3 = Pin(5, Pin.IN)
signal4 = Pin(4, Pin.IN)    

button = Pin(28, Pin.IN, Pin.PULL_UP)    

RF_Operation_Mode = False

# Motor 1
ain1_ph = Pin(12, Pin.OUT)
ain2_en = PWM(Pin(13), freq= 2000)

# Motor 2
ain1_ph_2 = Pin(14, Pin.OUT)
ain2_en_2 = PWM(Pin(15), freq= 2000)


motor_controller = TwoMotorController(ain2_en, ain1_ph, ain2_en_2, ain1_ph_2)



def ir_callback_RF(pin):
    if not RF_Operation_Mode:
        print("RF Operation Mode is disabled, ignoring RF commands.")
        return

    global last_time
    global last_signal_time
    global motor_active
    now = utime.ticks_ms()
    # simple debounce: ignore edges occurring within 50 ms
    if utime.ticks_diff(now, last_time) < 50:
        return
    last_time = now

    # Read current state of all RF input pins. Motors should run only
    # while their corresponding button/wire is held (pin.value()==1).
    s1 = signal1.value()
    s2 = signal2.value()
    s3 = signal3.value()
    s4 = signal4.value()

    # Decide action based on which button is currently held. Priority order
    # is signal1 -> signal2 -> signal3 -> signal4. If none are held, stop.
    if s1:
        motor_controller.move_forward()
        motor_active = True
        last_signal_time = now
        print("RF: signal1 held — moving forward")
    elif s2:
        motor_controller.move_backward()
        motor_active = True
        last_signal_time = now
        print("RF: signal2 held — moving backward")
    elif s3:
        motor_controller.turn_right()
        motor_active = True
        last_signal_time = now
        print("RF: signal3 held — turning right")
    elif s4:
        motor_controller.turn_left()
        motor_active = True
        last_signal_time = now
        print("RF: signal4 held — turning left")
    else:
        # No RF buttons held — stop motors immediately
        if motor_active:
            print("RF: no signals held — stopping motors")
            motor_controller.stop()
        motor_active = False
        last_signal_time = now


# Callback when IR command received
def ir_callback(data, addr, _):

    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")

    if RF_Operation_Mode:
        print("RF Operation Mode is enabled, ignoring IR commands.")
        return
    
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


def button_callback(pin):
    global RF_Operation_Mode
    RF_Operation_Mode = not RF_Operation_Mode 

    if RF_Operation_Mode:
        # blink_all_leds()
        print("Interrupts ENABLED")
    else:
        # blink_all_leds()
        print("Interrupts DISABLED")
        # When disabling RF mode, stop motors for safety
        motor_controller.stop()
        global motor_active, last_signal_time
        motor_active = False
        last_signal_time = utime.ticks_ms()


signal1_irq = signal1.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=ir_callback_RF)
signal2_irq = signal2.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=ir_callback_RF)
signal3_irq = signal3.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=ir_callback_RF)
signal4_irq = signal4.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=ir_callback_RF)

button.irq(trigger=Pin.IRQ_RISING, handler=button_callback)

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
