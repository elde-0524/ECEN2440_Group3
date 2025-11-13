import machine
import time
from machine import Pin, PWM
from ir_rx.nec import NEC_8
from ir_rx.print_error import print_error
from ir_rx import IR_RX


pwm_rate = 2000

# Motor 1
ain1_ph = Pin(12, Pin.OUT)
ain2_en = PWM(Pin(13))
ain2_en.freq(pwm_rate)
ain2_en.duty_u16(0)  # start OFF

# Motor 2
ain1_ph_2 = Pin(14, Pin.OUT)
ain2_en_2 = PWM(Pin(15))
ain2_en_2.freq(pwm_rate)
ain2_en_2.duty_u16(0)  # start OFF

# pwm
pwm = min(max(int(2**16 * abs(1)), 0), 65535)

# --- LED setup (blink all 3 LEDs on single press) ---
# LEDs on pins GP16, GP17, GP18
led_pins = [16, 17, 18]
leds = [Pin(p, Pin.OUT) for p in led_pins]

def blink_leds(times=3, on_time=0.15, off_time=0.15):
    for _ in range(times):
        for l in leds:
            l.high()
        time.sleep(on_time)
        for l in leds:
            l.low()
        time.sleep(off_time)

# --- Motor control functions ---
def motor_on_forward():
    print("Motor Forward")
    
    # turn low
    ain1_ph.low()       
    ain1_ph_2.low()     

    # turn on
    ain2_en.duty_u16(pwm)
    ain2_en_2.duty_u16(pwm)

def motor_on_backward():
    print("Motor Backward")
    # turn high 
    ain1_ph.high()      
    ain1_ph_2.high()    

    #turn on 
    ain2_en.duty_u16(pwm)
    ain2_en_2.duty_u16(pwm)

def motor_off():
    print("Motor OFF")

    #turn off 
    ain2_en.duty_u16(0)
    ain2_en_2.duty_u16(0)
    ain1_ph.low()
    ain1_ph_2.low()

# --- IR command codes --- 
IR_FORWARD_CODE  = 0x01
IR_OFF_CODE      = 0x02
IR_BACKWARD_CODE = 0x03

#  flag for motor state
motor_state = "OFF"  

# --- IR callback ---
def ir_callback(data, addr, _):
    global motor_state

    #terminal printing for debugging
    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")

    blink_leds()

    if data == IR_FORWARD_CODE:
        motor_state = "FORWARD"
    elif data == IR_OFF_CODE:
        motor_state = "OFF"
    elif data == IR_BACKWARD_CODE:
        motor_state = "BACKWARD"
    else:
        print("Unknown command")

# --- IR receiver setup ---
ir_pin = Pin(18, Pin.IN, Pin.PULL_UP)
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
    time.sleep(0.5)  # let settle
