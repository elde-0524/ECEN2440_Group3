import machine, time, math
from machine import Pin, PWM

# ----- 1 Motor setup -------
pwm_rate = 2000
ain1_ph = Pin(12, Pin.OUT)  
ain2_en = PWM(Pin(13), freq = pwm_rate)    

# ------ 2 Motor setup ------
ain1_ph_2 = Pin(14, Pin.OUT)
ain2_en_2 = PWM(Pin(15), freq = pwm_rate)


#initialize motors to off
ain2_en.duty_u16(0)        
ain2_en_2.duty_u16(0)       

pwm = min(max(int(2**16 * abs(1)), 0), 65535)

# Functions to control motors
def motor_on_foward():
    print("Motor Foward") # Turn on LED
    # Motor 1
    ain1_ph.low()
    ain2_en.duty_u16(pwm)  

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



# keep the program running
# turn the motors on and off every second
while True:
    motor_on_foward()
    time.sleep(1)
    motor_off()
    time.sleep(1)
