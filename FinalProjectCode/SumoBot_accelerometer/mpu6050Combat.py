import utime
from mpu6050 import MPU6050


class MPU6050Combat:
    """
    Simple collision detector for sumo robots.
    Detects when you hit something and when you're stuck.
    """

    def __init__(self, mpu, forward_axis=0, blocked_threshold=-0.25, collision_threshold=1.8, cooldown_ms=200, collison_callback = None,
                 blocked_callback = None, on_unblocked = None):

        self.mpu = mpu
        self.forward_axis = forward_axis
        

        self.collision_threshold = 1.8  
        self.blocked_threshold = -0.25  
        

        self.prev_accel = 0.0
        self.recent_accels = [] # store readings
        self.max_readings = 10  # keep a window of 10
        

        self.last_collision_time = 0
        self.cooldown_ms = 200  # Wait 200ms between collision detections
        self.block_check_duration_ms = 150 

        self.blocked_callback = blocked_callback
        self.collison_callback = collison_callback
        self.on_unblocked = on_unblocked

    def read_forward_accel(self):
        return self.mpu.read_accel_data()[self.forward_axis]


    def update(self):
        
        print("Updating collision detection")
        current_accel = self.read_forward_accel()
        
        # calculate delta acceleration
        jerk = current_accel - self.prev_accel
        
        self.recent_accels.append(current_accel)
        
        # remove old readings when list is greater than max size
        if len(self.recent_accels) > self.max_readings:
            self.recent_accels.pop(0)  # keep window
        
        # check time difference
        now = utime.ticks_ms()
        time_since_last = utime.ticks_diff(now, self.last_collision_time)
        
        collision = False
        blocked = False
        self.on_unblocked = None
        self.was_blocked = False
        self.check_for_block = False


        if self.was_blocked:
                    if len(self.recent_accels) >= 3:
                        average_accel = sum(self.recent_accels) / len(self.recent_accels)
                        # if acceleration is going up then we are moving
                        if average_accel > 0.3  :  
                            print(f"unblocked! Average accel: {average_accel}")
                            self.was_blocked = False
                            if self.on_unblocked:
                                self.on_unblocked()

       # check for collision
        time_since_last = utime.ticks_diff(now, self.last_collision_time)
        if jerk >= self.collision_threshold and time_since_last >= self.cooldown_ms:
            collision = True
            self.last_collision_time = now
            self.check_for_block = True  

            if self.collison_callback:
                self.collison_callback()
                print("Calling collision callback")

            print(f"collison! Jerk number: {jerk}")
        
        # check for block
        if self.check_for_block:
            time_since_collision = utime.ticks_diff(now, self.last_collision_time)
            
            # check if we are still in the block check duration
            if time_since_collision < self.block_check_duration_ms:
                if len(self.recent_accels) >= 3:
                    average_accel = sum(self.recent_accels) / len(self.recent_accels)
                    if average_accel <= self.blocked_threshold:
                        
                        if self.blocked_callback:
                            self.blocked_callback()
                            print("Calling blocked callback")

                        self.was_blocked = True 
                        self.check_for_block = False  
                        self.recent_accels = []
                        print(f"blocked! Average accel: {average_accel}")
            else:
                # if not declerating after some time then stop checking
                self.check_for_block = False
        
        self.prev_accel = current_accel
        

    def reset(self):
        # reset all s
        self.prev_accel = 0.0
        self.recent_accels = []
        self.last_collision_time = 0