import machine
import time
from machine import Pin, PWM
from ir_rx.nec import NEC_8
from ir_rx.print_error import print_error

# --- Motor setup ---
pwm_rate = 2000

# Motor 1
ain1_ph = Pin(21, Pin.OUT)
ain2_en = PWM(Pin(20))
ain2_en.freq(pwm_rate)
ain2_en.duty_u16(0)  # start OFF

# Motor 2
ain1_ph_2 = Pin(16, Pin.OUT)
ain2_en_2 = PWM(Pin(17))
ain2_en_2.freq(pwm_rate)
ain2_en_2.duty_u16(0)  # start OFF

# PWM value (~60% duty)
pwm = int(0.6 * 65535)

# --- Motor control functions ---
def motor_on_forward():
    print("Motor Forward")
    ain1_ph.low()       # PHASE forward
    ain1_ph_2.low()     # match motor 1
    ain2_en.duty_u16(pwm)
    ain2_en_2.duty_u16(pwm)

def motor_on_backward():
    print("Motor Backward")
    ain1_ph.high()      # PHASE backward
    ain1_ph_2.high()    # match motor 1
    ain2_en.duty_u16(pwm)
    ain2_en_2.duty_u16(pwm)

def motor_off():
    print("Motor OFF")
    ain2_en.duty_u16(0)
    ain2_en_2.duty_u16(0)
    ain1_ph.low()
    ain1_ph_2.low()

# --- IR command codes (replace with your actual remote codes) ---
IR_FORWARD_CODE  = 0x01
IR_OFF_CODE      = 0x02
IR_BACKWARD_CODE = 0x03

# --- Motor state variable ---
motor_state = "OFF"  # can be "FORWARD", "BACKWARD", "OFF"

# --- IR callback ---
def ir_callback(data, addr, _):
    global motor_state
    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")
    
    if data == IR_FORWARD_CODE:
        motor_state = "FORWARD"
    elif data == IR_OFF_CODE:
        motor_state = "OFF"
    elif data == IR_BACKWARD_CODE:
        motor_state = "BACKWARD"
    else:
        print("Unknown command")

# --- Setup the IR receiver ---
ir_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # keep your original pin
ir_receiver = NEC_8(ir_pin, callback=ir_callback)
ir_receiver.error_function(print_error)

# --- Main loop ---
while True:
    if motor_state == "FORWARD":
        motor_on_forward()
    elif motor_state == "BACKWARD":
        motor_on_backward()
    else:
        motor_off()
    time.sleep(0.5)  # small delay to keep loop responsive
