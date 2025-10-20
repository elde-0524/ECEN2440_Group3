import machine, time, math
from machine import Pin, PWM
from ir_rx.nec import NEC_8  # Use the NEC 8-bit class
from ir_rx.print_error import print_error  # for debugging

# Example IR command values (you’ll need to print them from your remote first)
IR_FORWARD_CODE  = 0x01  
IR_OFF_CODE = 0x02  
IR_BACKWARD_Code = 0x03

# Callback when IR command received
def ir_callback(data, addr, _):
    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")
    if data == IR_FORWARD_CODE:
        time.sleep(0.1)
        print("Reci")
    elif data == IR_OFF_CODE:
        time.sleep(0.1)
        print("Stopping")
    elif data == IR_BACKWARD_Code:
        time.sleep(0.1)
        print("Moving Backward")
    else: 
        print("Unknown command")

# Setup the IR receiver
ir_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # adjust pin if needed
ir_receiver = NEC_8(ir_pin, callback=ir_callback)
ir_receiver.error_function(print_error)

# Main loop: just keep running
while True:
    time.sleep(1)
