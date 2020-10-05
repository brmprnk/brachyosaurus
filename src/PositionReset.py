from labjack import ljm
import time
import sys

# Open any found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")

f_datatype = ljm.constants.FLOAT32
offsetV = 2.5                         # Volt
sc = 2                            # scaling factor

print("Reset: INIT DOUTs of T7")
ljm.eWriteAddress(handle, 1000, f_datatype, offsetV)
ljm.eWriteAddress(handle, 1002, f_datatype, offsetV)
# time.sleep(2)

print("Reset: Move back stage to minimum")
ljm.eWriteAddress(handle, 1002, f_datatype, offsetV - 1)
# time.sleep(2)

while True:
    print("Reset: current position: ", ljm.eReadAddress(handle, 0, f_datatype))
    if round(ljm.eReadAddress(handle, 0, f_datatype), 3) <= 0.032 :
        print("Reset: End reached")
        ljm.eWriteAddress(handle, 1000, f_datatype, offsetV)
        ljm.eWriteAddress(handle, 1002, f_datatype, 0)
        print("Reset: final position: ", ljm.eReadAddress(handle, 0, f_datatype))

        ljm.close(handle)
        sys.exit(0)
