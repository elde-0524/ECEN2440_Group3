import machine, time, math
from machine import Pin, PWM

# 1 Motor setup
pwm_rate = 2000
ain1_ph = Pin(21, Pin.OUT)  
ain2_en = PWM(Pin(20), freq = pwm_rate)    

# 2 Motor setup 
ain1_ph_2 = Pin(16, Pin.OUT)
ain2_en_2 = PWM(Pin(17), freq = pwm_rate)

ain2_en.duty_u16(0)         # start OFF

ain2_en_2.duty_u16(0)       # start OFF

pwm = min(max(int(2**16 * abs(1)), 0), 65535)
# Motor control function

def motor_on_foward():
    print("Motor Foward") # Turn on LED
    # Motor 1
    ain1_ph.low()
    ain2_en.duty_u16(pwm)  # ~60% duty cycle (adjust power here)

    # motor 2
    ain1_ph_2.low()
    ain2_en_2.duty_u16(pwm) 

def motor_off():
  # Turn off LED
    print("Motor OFF")
    
    #Motor 1
    ain1_ph.low()
    ain2_en.duty_u16(0)
    
    #motor 2
    ain1_ph_2.low()
    ain2_en_2.duty_u16(0)


# Main loop: just keep running

while True:
    motor_on_foward()
    time.sleep(1)
    motor_off()
    time.sleep(1)
