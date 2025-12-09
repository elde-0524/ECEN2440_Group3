import machine
from machine import Pin, PWM
import utime

class TwoMotorController:
    """
    A class to control a pair of motors for directional movement.
    Stores pin configurations for both motors and provides movement commands.
    """
    
    def __init__(self, motor1_pin_en, motor1_pin_ph,  motor2_pin_en, motor2_pin_ph, **kwargs):

        self.motor1_pin_en = motor1_pin_en
        self.motor1_pin_ph = motor1_pin_ph
        self.motor2_pin_en = motor2_pin_en
        self.motor2_pins_ph = motor2_pin_ph

        self.pwm_rate = 2000
        self.pwm_signal = int(65535/5)  # 20% duty cycle

        if 'pwm_signal' in kwargs:
            self.pwm_signal = kwargs['pwm_signal']
        if 'pwm_rate' in kwargs:
            self.pwm_rate = kwargs['pwm_rate']

    def change_pwm_signal(self, new_signal):
        """Change the PWM signal duty cycle for both motors."""
        if new_signal < 0 or new_signal > 65535:
            raise ValueError("PWM signal must be between 0 and 65535")
        self.pwm_signal = new_signal

    def move_forward(self, rampower = False, mode = 'normal' ):
        """Move both motors forward."""
        print("Both motors moving forward")
        self.motor1_pin_ph.low()
        self.motor2_pins_ph.high()

        if mode == 'slow':
            self.pwm_signal = int(65535/5)  # 10% duty cycle for slow mode
        if mode == 'normal':
            self.pwm_signal = int(65535/4)  # 20% duty cycle for normal mode
        if mode == 'fast':
            self.pwm_signal = int(65535/2)  # 50% duty cycle for fast mode  

        if rampower:
            for duty in range(0, self.pwm_signal, 1024):
                self.motor1_pin_en.duty_u16(duty)
                self.motor2_pin_en.duty_u16(duty)
                utime.sleep_ms(50)
        else:
            self.motor1_pin_en.duty_u16(self.pwm_signal)
            self.motor2_pin_en.duty_u16(self.pwm_signal)


    def move_backward(self, rampower = False, mode = 'normal' ):
        """Move both motors backward."""
        print("Both motors moving backward")
        self.motor1_pin_ph.high()
        self.motor2_pins_ph.low()

        if mode == 'slow':
            self.pwm_signal = int(65535/5)  # 10% duty cycle for slow mode
        if mode == 'normal':
            self.pwm_signal = int(65535/4)  # 20% duty cycle for normal mode
        if mode == 'fast':
            self.pwm_signal = int(65535/2)  # 50% duty cycle for fast mode  

        if rampower:
            for duty in range(0, self.pwm_signal, 1024):
                self.motor1_pin_en.duty_u16(duty)
                self.motor2_pin_en.duty_u16(duty)
                utime.sleep_ms(50)
            else:
                self.motor1_pin_en.duty_u16(self.pwm_signal)
                self.motor2_pin_en.duty_u16(self.pwm_signal)    

    def turn_right(self, rampower = False ):
        """Turn right by moving left motor forward, right motor backward."""
        print("Turning right")
        self.motor1_pin_ph.low()
        self.motor2_pins_ph.low()

        if rampower:
            for duty in range(0, self.pwm_signal, 1024):
                self.motor1_pin_en.duty_u16(duty)
                self.motor2_pin_en.duty_u16(duty)
                utime.sleep_ms(50)
        else:
            self.motor1_pin_en.duty_u16(self.pwm_signal)
            self.motor2_pin_en.duty_u16(self.pwm_signal) 

    def turn_left(self, rampower = False ):
        """Turn left by moving right motor forward, left motor backward."""
        print("Turning left")
        self.motor1_pin_ph.high()
        self.motor2_pins_ph.high()

        if rampower:
            for duty in range(0, self.pwm_signal, 1024):
                self.motor1_pin_en.duty_u16(duty)
                self.motor2_pin_en.duty_u16(duty)
                utime.sleep_ms(50)
        else:
            self.motor1_pin_en.duty_u16(self.pwm_signal)
            self.motor2_pin_en.duty_u16(self.pwm_signal) 

    def stop(self):
        """Stop motors """
        print("Both motors stopped")

        self.motor1_pin_ph.low()
        self.motor2_pins_ph.low()

        self.motor1_pin_en.duty_u16(0)
        self.motor2_pin_en.duty_u16(0) 
    
    def get_motor1_pins(self):
        """Return the pin configuration for motor 1."""
        return self.motor1_pin_ph, self.motor1_pin_en
    
    def get_motor2_pins(self):
        """Return the pin configuration for motor 2."""
        return self.motor2_pins_ph, self.motor2_pin_en