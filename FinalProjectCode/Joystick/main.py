# Kiran Jojare
# University of Colorado Boulder
# Graduate Student, Department of Electrical Engineering, Embedded Systems Specialization
# Test code to check the interfaced seesaw library for interacting with Gamepad QT with PICO
from machine import I2C, Pin
import seesaw
import time

from ir_tx.nec import NEC


# Initialize I2C. Adjust pin numbers based on your Pico's configuration
i2c = I2C(1, scl=Pin(15), sda=Pin(14))

#setting up transmitter 
tx_pin = Pin(16, Pin.OUT, value = 0)  # Transmitter connected to GPIO15
device_addr = 0x01
transmitter = NEC(tx_pin)

FORWARD = 0x18
BACKWARD = 0x17
LEFT = 0x16
RIGHT = 0x15
STOP = 0x14
MODE_SWITCH = 0x19


commands = [FORWARD, BACKWARD, LEFT, RIGHT]

seesaw_device = seesaw.Seesaw(i2c, addr=0x50)

BUTTON_A = 5
BUTTON_B = 1
BUTTON_X = 6
BUTTON_Y = 2
BUTTON_START = 16
BUTTON_SELECT = 0
JOYSTICK_X_PIN = 14
JOYSTICK_Y_PIN = 15
# Button mask based on Arduino code

BUTTONS_MASK = (1 << BUTTON_X) | (1 << BUTTON_Y) | \
 (1 << BUTTON_A) | (1 << BUTTON_B) | \
 (1 << BUTTON_SELECT) | (1 << BUTTON_START)
def setup_buttons():
    """Configure the pin modes for buttons."""
    seesaw_device.pin_mode_bulk(BUTTONS_MASK, seesaw_device.INPUT_PULLUP)

def read_buttons():
    """Read and return the state of each button."""
    return seesaw_device.digital_read_bulk(BUTTONS_MASK)

def read_joystick():
    """Read and return the joystick's X and Y positions."""
    x_value = seesaw_device.analog_read(JOYSTICK_X_PIN)
    y_value = seesaw_device.analog_read(JOYSTICK_Y_PIN)
    return x_value, y_value


def main():
    """Main program loop."""
    setup_buttons()
    last_buttons = 0
    last_x, last_y = -1, -1
    joystick_threshold = 10  # Sensitivity for detecting meaningful movement
    # Joystick center and deadzone for stable direction detection
    
    center_x = 512
    center_y = 512
    deadzone = 100
    last_direction = None
    while True:
        current_buttons = read_buttons()
        current_x, current_y = read_joystick()

        # Check if button state has changed
        if current_buttons != last_buttons:
            if (current_buttons & (1 << BUTTON_B)) and not (last_buttons & (1 << BUTTON_B)):
                transmitter.transmit(device_addr, MODE_SWITCH)
                print("Button B is pressed")
                print("transmitted command: {}".format(MODE_SWITCH))

            last_buttons = current_buttons


        # Check if joystick position has changed significantly
        if abs(current_x - last_x) > joystick_threshold or abs(current_y - last_y) > joystick_threshold:
            
            # Determine joystick direction using deadzone and dominant axis
            dx = current_x - center_x
            dy = current_y - center_y

            direction = None
            if abs(dx) < deadzone and abs(dy) < deadzone:
                direction = None
            else:
                if abs(dx) > abs(dy):
                    direction = 'left' if dx > 0 else 'right'
                else:
                    direction = 'backward' if dy > 0 else 'forward'

            # Map direction to command and send on change
            cmd = None
            if direction == 'forward':
                cmd = FORWARD
            elif direction == 'backward':
                cmd = BACKWARD
            elif direction == 'left':
                cmd = LEFT
            elif direction == 'right':
                cmd = RIGHT

            if direction is not None:
                # if its new direction
                if direction != last_direction:
                    print("Joystick Direction: {} - X: {}, Y: {}".format(direction, current_x, current_y))

                    # Send the mapped IR command
                    if cmd is not None:
                        transmitter.transmit(device_addr, cmd)
                        print("transmitted command: {}".format(cmd))
                    last_direction = direction
            else:
                if last_direction is not None:
                    print("Stop - Joystick back to center - X: {}, Y: {}".format(current_x, current_y))

                    transmitter.transmit(device_addr, STOP)
                    print("transmitted command: {}".format(STOP))
                    # joystick is back to center
                    last_direction = None

            last_x, last_y = current_x, current_y
        
        time.sleep(0.1) 

if __name__ == "__main__":
    main()