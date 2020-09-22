from labjack import ljm
import time

# Open first USB connected found LabJack
handle = ljm.openS("ANY", "USB", "ANY")

# Call eReadName to read the serial number from the LabJack.
name = "SERIAL_NUMBER"
result = ljm.eReadName(handle, name)

print("\neReadName result: ")
print("    %s = %s" % (name, result))

# --Connections:
# --  AIN0 = position (0-10V) (R addr. = 0)
AIN0addr = 0
# --  DAC0 = speed ref.signal (2.5V) (R addr. = 1000)
DAC0addr = 1000
# --  DAC1 = speed out signal (-2.5 - 2.5V) (R addr. = 1002)
DAC1addr = 1002
# --  USER_RAM0 = number related to frequency (R addr. = 46000)\
RAM0addr = 46000
# --  USER_RAM1 = amplitude in mm (R addr. = 46002)
RAM1addr = 46002

f_datatype = ljm.constants.FLOAT32

ljm.eWriteAddress(handle, DAC1addr, f_datatype, 2.5)

time.sleep(2)

ljm.eWriteAddress(handle, DAC1addr, f_datatype, -2.5)
