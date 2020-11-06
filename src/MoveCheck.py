# TRYING TO FIND OUT WHEN IT MOVES
from labjack import ljm
import time

# Open any found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")

f_datatype = ljm.constants.FLOAT32
sc = 2                              # scaling factor

# cycle through positive, negative and zero-value voltages on the DACs
# first test is also INIT
print("\nINIT I/O of LABjack T7 w/ write statements w/ value 0")
print("    test 0: DAC0 = 0, DAC1 = 0")
ljm.eWriteAddress(handle, 1000, f_datatype, 0)
ljm.eWriteAddress(handle, 1002, f_datatype, 0)
time.sleep(2)

print("\n    test 1: DAC0 = 1, DAC1 = 0")
ljm.eWriteAddress(handle, 1000, f_datatype, 1*sc)
ljm.eWriteAddress(handle, 1002, f_datatype, 0)
time.sleep(2)

print("\n    test 2: DAC0 = 0, DAC1 = 1")
ljm.eWriteAddress(handle, 1000, f_datatype, 0)
ljm.eWriteAddress(handle, 1002, f_datatype, 1*sc)
time.sleep(2)

print("\n    test 3: DAC0 = 1, DAC1 = 1")
ljm.eWriteAddress(handle, 1000, f_datatype, 1*sc)
ljm.eWriteAddress(handle, 1002, f_datatype, 1*sc)
time.sleep(2)
