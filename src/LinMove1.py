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
print("\n")

# --Connections:
# --  AIN0 = position (0-10V) (R addr. = 0)
AIN0addr = 0
# --  DAC0 = speed ref.signal (2.5V) (R addr. = 1000)
DAC0addr = 1000
# --  DAC1 = speed out signal (-2.5 - 2.5V) (R addr. = 1002)
DAC1addr = 1002

######################################
## Function FESTO(endloc, startloc,speed)
## Drives the linear stage to a position 'endloc' with speed 'speed' after command 'startloc' did its thing
## startloc arguments: 	- position float in mm like '0' goes to minimum position or '50' goes to maximum position
##						- integer '-1' keeps the stage in its current place
######################################
#   #   # TESTING initials
endloc = 0			# mm
startloc = 0		# mm
speed = 0			# mm/s
posoffset = 0.3 		#volt
#   #   #

f_datatype = ljm.constants.FLOAT32
offsetV = 2.5 		# (offsetV+2.5V on DAC1 = 25 mm/s)
maxpos = 50
minpos = 0

ljm.eWriteAddress(handle, DAC0addr, f_datatype, offsetV)    	# INIT reference voltage

def v2d(locv: float, position_offset) -> float:
	"""
	Volt to location (mm) conversion
	"""
	return 50/(9-position_offset)*locv - position_offset


# return to position startloc
if startloc >= 0 :
	print("Going to pos: ", startloc)
	cpos = v2d(ljm.eReadAddress(handle, AIN0addr, f_datatype),posoffset)	# read current pos
	if cpos > startloc :
		while cpos > startloc :
			ljm.eWriteAddress(handle, DAC1addr, f_datatype, offsetV-2.5)
			cpos = v2d(ljm.eReadAddress(handle, AIN0addr, f_datatype),posoffset)
	else :
		while cpos < startloc :
			ljm.eWriteAddress(handle, DAC1addr, f_datatype, offsetV+2.5)
			cpos = v2d(ljm.eReadAddress(handle, AIN0addr, f_datatype),posoffset)
else :
	print("Holding stage in current pos: ", v2d(ljm.eReadAddress(handle, AIN0addr, f_datatype), posoffset)

ljm.close(handle)
print("\n LABjack T7 closed")