import utime
from mpu6050 import MPU6050


class MPU6050Combat:
    def __init__(self, mpu, forward_axis=0, blocked_threshold=-0.25, 
                 collision_threshold=1.5, cooldown_ms=200, 
                 collison_callback=None, blocked_callback=None, on_unblocked=None):

        self.mpu = mpu
        self.forward_axis = forward_axis
        
        self.collision_threshold = collision_threshold
        self.blocked_threshold = blocked_threshold
        
        self.prev_accel = 0.0
        self.recent_accels = []
        self.max_readings = 10
        
        self.last_collision_time = 0
        self.cooldown_ms = cooldown_ms
        self.block_check_duration_ms = 150
        
        # Initialize state variables here
        self.was_blocked = False
        self.check_for_block = False
        
        # Keep callbacks (don't reset them)
        self.blocked_callback = blocked_callback
        self.collison_callback = collison_callback
        self.on_unblocked = on_unblocked

    def read_forward_accel(self):
        return self.mpu.read_accel_data()[self.forward_axis]
    def update(self):
        current_accel = self.read_forward_accel()
        jerk = current_accel - self.prev_accel
        print(jerk)

        self.recent_accels.append(current_accel)
        if len(self.recent_accels) > self.max_readings:
            self.recent_accels.pop(0)
        
        now = utime.ticks_ms()
        
        # Check for unblocking FIRST (before new collision detection)
        if self.was_blocked and len(self.recent_accels) >= 3:
            average_accel = sum(self.recent_accels) / len(self.recent_accels)
            if average_accel > 0.3:
                print(f"Unblocked! Average accel: {average_accel}")
                self.was_blocked = False
                if self.on_unblocked:
                    self.on_unblocked()
        
        # Collision detection
        time_since_last = utime.ticks_diff(now, self.last_collision_time)
        if jerk >= self.collision_threshold and time_since_last >= self.cooldown_ms:
            self.last_collision_time = now
            self.check_for_block = True
            if self.collison_callback:
                self.collison_callback()
            print(f"Collision! Jerk: {jerk}")
        
        # Blocked detection (after collision)
        if self.check_for_block:
            time_since_collision = utime.ticks_diff(now, self.last_collision_time)
            
            if time_since_collision < self.block_check_duration_ms:
                if len(self.recent_accels) >= 3:
                    average_accel = sum(self.recent_accels) / len(self.recent_accels)
                    if average_accel <= self.blocked_threshold:
                        self.was_blocked = True
                        self.check_for_block = False
                        if self.blocked_callback:
                            self.blocked_callback()
                        print(f"Blocked! Average accel: {average_accel}")
            else:
                self.check_for_block = False
        
        self.prev_accel = current_accel