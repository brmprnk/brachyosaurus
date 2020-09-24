from labjack import ljm
import time

# Open any found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")

f_datatype = ljm.constants.FLOAT32
offsetV = 0                         # Volt
sc = 0.5                              # scaling factor

# INIT
print("\nINIT I/O of LABjack T7 w/ write statements")
ljm.eWriteAddress(handle, 1000, f_datatype, offsetV)
ljm.eWriteAddress(handle, 1002, f_datatype, offsetV)

# Move forward
print("Moving")
# ljm.eWriteAddress(handle, 1000, f_datatype, 1*sc)
ljm.eWriteAddress(handle, 1002, f_datatype, offsetV + 1)
