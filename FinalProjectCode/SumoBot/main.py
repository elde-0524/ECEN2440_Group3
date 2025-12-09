from machine import Pin, PWM, I2C, ADC
import time
import utime

from motorCommands import TwoMotorController
from mpu6050 import MPU6050
from mpu6050Combat import MPU6050Combat



from ir_rx.nec import NEC_8
from ir_rx.print_error import print_error

FORWARD_CODE  = 0x18 
BACKWARD_CODE = 0x17
LEFT_CODE     = 0x16
RIGHT_CODE    = 0x15
STOP_CODE     = 0x14    
MODE_SWITCH   = 0x19

# motor control mode
mode = 'normal'

last_signal_time = utime.ticks_ms()
STOP_TIMEOUT_MS = 3000
motor_active = False
RF_Operation_Mode = False
last_time = 0

signal1 = Pin(7, Pin.IN)
signal2 = Pin(6, Pin.IN)
signal3 = Pin(5, Pin.IN)
signal4 = Pin(4, Pin.IN)

led1_slow = Pin(16, Pin.OUT)
led2_normal = Pin(17, Pin.OUT)
led3_fast = Pin(20, Pin.OUT)

# for battery level indication
led4_battery = Pin(19, Pin.OUT)
adc = ADC(Pin(28))
MAX_READING = 65535
VREF = 3.3
PRINT_INTERVAL_MS = 5000


led2_normal.high()
led1_slow.low()
led3_fast.low()

button = Pin(28, Pin.IN, Pin.PULL_UP)

ain1_ph = Pin(12, Pin.OUT)
ain2_en = PWM(Pin(13), freq=2000)

ain1_ph_2 = Pin(14, Pin.OUT)
ain2_en_2 = PWM(Pin(15), freq=2000)

motor_controller = TwoMotorController(
    ain2_en, ain1_ph,
    ain2_en_2, ain1_ph_2
)

# clear the bus to avoid reading 0.0 on accelorometer
def reset_i2c_bus(i2c_id=1, scl_pin=3, sda_pin=2):
    scl = Pin(scl_pin, Pin.OUT, value=1)
    sda = Pin(sda_pin, Pin.OUT, value=1)

    # switch scl to clear
    for _ in range(9):
        scl.value(0)
        utime.sleep_us(5)
        scl.value(1)
        utime.sleep_us(5)

    sda.init(Pin.IN)
    scl.init(Pin.IN)
    utime.sleep_us(50)

    return I2C(i2c_id, scl=Pin(scl_pin), sda=Pin(sda_pin))


def wake_mpu(i2c, addr=0x68):
    try:
        i2c.writeto_mem(addr, 0x6B, b'\x00')
    except:
        print("MPU wake failed")

def set_led(on: bool):
    led4_battery.value(1 if on else 0)

def ADC_reader():
    last_print = time.ticks_ms()
    last_toggle = time.ticks_ms()
    led_state = False

    raw = adc.read_u16()
    voltage = (raw / MAX_READING) * VREF
    percent = (raw / MAX_READING) * 100.0

    if voltage > 0.4:
        set_led(True)
        blink_half_period_ms = None
    elif voltage >= 0.2:
        blink_half_period_ms = 500
    else:
        blink_half_period_ms = 250

    now = time.ticks_ms()

    if blink_half_period_ms is not None:
        if time.ticks_diff(now, last_toggle) >= blink_half_period_ms:
            led_state = not led_state
            set_led(led_state)
            last_toggle = now
    else:
        led_state = True

def apply_mode_pwm():
    """Set motor PWM based on current mode."""
    if mode == 'slow':
        pwm_value = int(65535 / 5)  # 20%
    elif mode == 'normal':
        pwm_value = int(65535 / 4)  # 25%
    elif mode == 'fast':
        pwm_value = int(65535 / 2)  # 50%
    else:
        pwm_value = int(65535 / 4)

    motor_controller.change_pwm_signal(pwm_value)


print("resetting I2C bus... wait")
i2c_bus = reset_i2c_bus()
wake_mpu(i2c_bus)

mpu = MPU6050(i2c_bus)

mpu_combat = MPU6050Combat(
    mpu,
    forward_axis=0,
    cooldown_ms=200,
    collison_callback= lambda: print("Collision detected!"),
    blocked_callback= lambda: handle_blocked(),
    on_unblocked= lambda: handle_unblocked()
)


def handle_blocked():
    print("Blocked! callback triggered")
    #increase speed
    motor_controller.change_pwm_signal(int(65535 * 0.8))
    motor_controller.move_forward()


def handle_unblocked():
    print("Unblocked! Resuming normal speed")
    motor_controller.stop()
    motor_controller.change_pwm_signal(int(65535/5))


def RF_callback(pin):
    global last_time, last_signal_time, motor_active

    if not RF_Operation_Mode:
        print("Ignoring RF (RF mode OFF)")
        return

    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_time) < 50:
        return
    last_time = now

    s1 = signal1.value()
    s2 = signal2.value()
    s3 = signal3.value()
    s4 = signal4.value()

    if s1:
        motor_controller.move_forward(rampower=True)
    elif s2:
        motor_controller.move_backward(rampower=True)
    elif s3:
        motor_controller.turn_right(rampower=True)
    elif s4:
        motor_controller.turn_left(rampower=True)
    else:
        motor_controller.stop()
        motor_active = False
        last_signal_time = now
        return

    motor_active = True
    last_signal_time = now


def ir_callback(data, addr, _):
    global mode, motor_active, last_signal_time

    if RF_Operation_Mode:
        print("Ignoring IR (RF mode ON)")
        return

    if data == FORWARD_CODE:
        motor_controller.move_forward()
        motor_active = True
    elif data == BACKWARD_CODE:
        motor_controller.move_backward()
        motor_active = True
    elif data == LEFT_CODE:
        motor_controller.turn_left()
        motor_active = True
    elif data == RIGHT_CODE:
        motor_controller.turn_right()
        motor_active = True
    elif data == STOP_CODE:
        motor_controller.stop()
        motor_active = False
    elif data == MODE_SWITCH:
        if mode == 'slow':
            mode = 'normal'
            led2_normal.high(); led1_slow.low(); led3_fast.low()
        elif mode == 'normal':
            mode = 'fast'
            led3_fast.high(); led1_slow.low(); led2_normal.low()
        elif mode == 'fast':
            mode = 'slow'
            led1_slow.high(); led2_normal.low(); led3_fast.low()

        print("Mode switched:", mode)

    apply_mode_pwm()

    last_signal_time = utime.ticks_ms()


DEBOUNCE_MS = 200
last_button_press = 0

def button_callback(pin):
    global last_button_press, RF_Operation_Mode, motor_active, last_signal_time

    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_button_press) < DEBOUNCE_MS:
        return  # Ignore bounce

    last_button_press = now

    RF_Operation_Mode = not RF_Operation_Mode

    if not RF_Operation_Mode:
        motor_controller.stop()
        motor_active = False
        last_signal_time = now

    print("RF mode =", RF_Operation_Mode)

# interrupt setup
button.irq(trigger=Pin.IRQ_RISING, handler=button_callback)

signal1.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=RF_callback)
signal2.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=RF_callback)
signal3.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=RF_callback)
signal4.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=RF_callback)

ir_pin = Pin(18, Pin.IN, Pin.PULL_UP)
ir_receiver = NEC_8(ir_pin, callback=ir_callback)
ir_receiver.error_function(print_error)

print("initialization complete!")

while True:
    time.sleep(0.1)

    ADC_reader()

    mpu_combat.update()

    now = utime.ticks_ms()
    if motor_active and utime.ticks_diff(now, last_signal_time) > STOP_TIMEOUT_MS:
        motor_controller.stop()
        motor_active = False
        last_signal_time = now












