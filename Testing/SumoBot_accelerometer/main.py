from machine import Pin, PWM
import time 
import utime

from motorCommands import TwoMotorController
from mpu6050 import MPU6050
from mpu6050Combat import MPU6050Combat


from ir_rx.nec import NEC_8  # Use the NEC 8-bit class
from ir_rx.print_error import print_error  # for debugging
from machine import I2C

'''
pins used: 
Signal1: Pin 7
Signal2: Pin 6
Signal3: Pin 5
Signal4: Pin 4

Button: Pin 28

Motor 1:
  Phase: Pin 12 
    Enable (PWM): Pin 13
Motor 2:
  Phase: Pin 14
    Enable (PWM): Pin 15

IR Receiver: Pin 18

SCL: Pin 3 
SDA: Pin 2

led1 (slow mode): Pin 16
led2 (normal mode): Pin 17
led3 (fast mode): Pin 20

'''

# Example IR command values 
FORWARD_CODE  = 0x18 
BACKWARD_CODE = 0x17
LEFT_CODE     = 0x16
RIGHT_CODE    = 0x15
STOP_CODE     = 0x14    
MODE_SWITCH   = 0x19

last_time = 0
mode = 'normal'  # default mode
# Timestamp of the last received valid command (IR or RF)
last_signal_time = utime.ticks_ms()

motor_active = False
# Timeout (ms) after which motors should stop if no signal received
STOP_TIMEOUT_MS = 3000  # 3 seconds by default; tweak as needed
signal1 = Pin(7, Pin.IN)
signal2 = Pin(6, Pin.IN)
signal3 = Pin(5, Pin.IN)
signal4 = Pin(4, Pin.IN)  


led1_slow = Pin(16, Pin.OUT)
led2_normal = Pin(17, Pin.OUT)
led3_fast = Pin(20, Pin.OUT)

button = Pin(28, Pin.IN, Pin.PULL_UP)    

#flag for RF operation mode
RF_Operation_Mode = False

# Motor 1
ain1_ph = Pin(12, Pin.OUT)
ain2_en = PWM(Pin(13), freq= 2000)

# Motor 2
ain1_ph_2 = Pin(14, Pin.OUT)
ain2_en_2 = PWM(Pin(15), freq= 2000)

motor_controller = TwoMotorController(ain2_en, ain1_ph, ain2_en_2, ain1_ph_2)

def RF_callback(pin):
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

    s1 = signal1.value()
    s2 = signal2.value()
    s3 = signal3.value()
    s4 = signal4.value()

    if s1:
        motor_controller.move_forward(rampower=True)
        motor_active = True
        last_signal_time = now
        print("RF: signal1 held — moving forward")
    elif s2:
        motor_controller.move_backward(rampower=True)
        motor_active = True
        last_signal_time = now
        print("RF: signal2 held — moving backward")
    elif s3:
        motor_controller.turn_right(rampower=True)
        motor_active = True
        last_signal_time = now
        print("RF: signal3 held — turning right")
    elif s4:
        motor_controller.turn_left(rampower=True)
        motor_active = True
        last_signal_time = now
        print("RF: signal4 held — turning left")
    else:

        if motor_active:
            print("RF: no signals held — stopping motors")
            motor_controller.stop()
        motor_active = False
        last_signal_time = now

def ir_callback(data, addr, _):

    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")

    if RF_Operation_Mode:
        print("RF Operation Mode is enabled, ignoring IR commands.")
        return
    
    # Print received command
    if data == FORWARD_CODE:
        motor_controller.move_forward(mode = 'normal')
        # mark motors active and update last-signal timestamp
        global last_signal_time
        global motor_active
        motor_active = True
        last_signal_time = utime.ticks_ms()
    elif data == BACKWARD_CODE:
        motor_controller.move_backward(mode = 'normal')
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
    elif data == MODE_SWITCH:
        global mode
        if mode == 'slow':
            mode = 'normal'
            led2_normal.high()
            led1_slow.low()
            led3_fast.low()
            print("Switched to NORMAL mode")
        elif mode == 'normal':
            mode = 'fast'
            led3_fast.high()
            led1_slow.low()
            led2_normal.low()
            print("Switched to FAST mode")
        elif mode == 'fast':
            mode = 'slow'
            led1_slow.high()
            led2_normal.low()
            led3_fast.low()
            print("Switched to SLOW mode")
    else: 
        print("Unknown command")
    

def block_callback():
    print("Collision detected!")

    motor_controller.change_pwm_signal(int(65535/3))
    motor_controller.move_forward()

def unblock_callback():
    print("Unblocked - resuming normal speed")
    motor_controller.stop()
    motor_controller.change_pwm_signal(int(65535/5))

# for accelerometer
mpu6050 = MPU6050(I2C(1, scl=Pin(3), sda=Pin(2)))
mpu6050_combat = MPU6050Combat(mpu6050, blocked_callback= block_callback, on_unblocked= unblock_callback)

time.sleep(0.5) # Allow time for setup

# Setup the IR receiver
ir_pin = Pin(18, Pin.IN, Pin.PULL_UP) 
ir_receiver = NEC_8(ir_pin, callback=ir_callback)
ir_receiver.error_function(print_error) 

time.sleep(0.5)  # Allow time for IR receiver to initialize

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

signal1_irq = signal1.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=RF_callback)
signal2_irq = signal2.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=RF_callback)
signal3_irq = signal3.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=RF_callback)
signal4_irq = signal4.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=RF_callback)


#button for switching modes
button.irq(trigger=Pin.IRQ_RISING, handler=button_callback)

while True:
    time.sleep(0.1)

    mpu6050_combat.update()
    now = utime.ticks_ms()
    if motor_active and utime.ticks_diff(now, last_signal_time) > STOP_TIMEOUT_MS:
        print("No signal received for timeout period — stopping motors")
        motor_controller.stop()
        motor_active = False
        # update last_signal_time so stop isn't called repeatedly
        last_signal_time = utime.ticks_ms()

#below is the battery checker code

adc = ADC(Pin(28))
led = Pin(19, Pin.OUT)
MAX_READING = 65535
VREF = 3.3

# PRINT_INTERVAL_MS = 5000
# last_print = time.ticks_ms()
# last_toggle = time.ticks_ms()
# led_state = False

# def set_led(on: bool):
#     led.value(1 if on else 0)

# print("Starting ADC reader on GPIO28; LED on GPIO20")
# while True:
#     raw = adc.read_u16()
#     voltage = (raw / MAX_READING) * VREF
#     percent = (raw / MAX_READING) * 100.0

#     if voltage > 0.4:
#         set_led(True)
#         blink_half_period_ms = None
#     elif voltage >= 0.2:
#         blink_half_period_ms = 500
#     else:
#         blink_half_period_ms = 250

#     now = time.ticks_ms()

#     if blink_half_period_ms is not None:
#         if time.ticks_diff(now, last_toggle) >= blink_half_period_ms:
#             led_state = not led_state
#             set_led(led_state)
#             last_toggle = now
#     else:
#         led_state = True

#     time.sleep(0.05)
