import machine
import time
import mpu6050 as MPU6050
from mpu6050Combat import MPU6050Combat

# Set up the I2C interface
i2c = machine.I2C(1, sda=machine.Pin(2), scl=machine.Pin(3))

def collision_callback():
    print("Collision detected!")

def blocked_callback():
    print("Robot is blocked!")


# Set up the MPU6050 class 
mpu = MPU6050.MPU6050(i2c)
mpu_combat = MPU6050Combat(mpu, collison_blocked = collision_callback, blocked_callback = blocked_callback)


# wake up the MPU6050 from sleep
mpu.wake()

# continuously print the data
while True:
    gyro = mpu.read_gyro_data()
    accel = mpu.read_accel_data()
    
    mpu_combat.update()

    # print("Gyro: " + str(gyro) + ", Accel: " + str(accel))
    time.sleep(0.1)