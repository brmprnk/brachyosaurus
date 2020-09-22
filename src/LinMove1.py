from labjack import ljm
import time
import sys

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

######################################
## Pushes linear stage outwards, inwards, back outwards if start position is around 0
## Else, only inwards and outwards
######################################

f_datatype = ljm.constants.FLOAT32
offsetV = 2.5

ljm.eWriteAddress(handle, DAC0addr, f_datatype, offsetV)

# Return to beginning
print("Initial pos AIN0 is : ", ljm.eReadAddress(handle, AIN0addr, f_datatype))
ljm.eWriteAddress(handle, DAC1addr, f_datatype, offsetV + 2)

time.sleep(4)

# If reached start
print("AIN0 is : ", ljm.eReadAddress(handle, AIN0addr, f_datatype))
if ljm.eReadAddress(handle, AIN0addr, f_datatype) >= 5:
	print("End reached")
	ljm.eWriteAddress(handle, DAC1addr, f_datatype, offsetV - 2)

time.sleep(4)

# Reached pos start
if ljm.eReadAddress(handle, AIN0addr, f_datatype) <= 1:
	print("back at start")
	ljm.eWriteAddress(handle, DAC1addr, f_datatype, offsetV + 2)
	sys.exit(0)