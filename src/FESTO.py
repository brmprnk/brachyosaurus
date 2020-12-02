from labjack import ljm
import time
import sys

"""
Function FESTO(endloc, startloc,speed)
Drives the linear stage to a position 'endloc' with speed 'speed' after command 'startloc' did its thing
startloc arguments: 	- position float in mm like '0' goes to minimum position or '50' goes to maximum position
						- integer '-1' keeps the stage in its current place 
"""


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

#   #   # TESTING initials
endloc = 0			# mm
startloc = 25		# mm
speed = 0			# mm/s
#   #   #

f_datatype = ljm.constants.FLOAT32
offsetV = 2.5 				# (offsetV+2.5V on DAC1 = 25 mm/s)
offV = 0 	# low voltage that T7 can certainly output
maxpos = 50					# mm
minpos = 3					# mm

ljm.eWriteAddress(handle, DAC0addr, f_datatype, offsetV)    	# INIT reference voltage

def v2d(locv: float) -> float:
	"""
	Volt to location (mm) conversion
	"""

	vmax = 9.418		# in volt, measured with labjack T7 AIN0
	vmin = 0.032
	dmax = 50.5			# in mm, measured by hand
	dmin = 3

	return ((dmax-dmin)/(vmax-vmin))*locv + dmin


# return to position startloc
if startloc >= 0:
	print("POS_SET: Going to pos: ", startloc)
	cpos = v2d(ljm.eReadAddress(handle, AIN0addr, f_datatype))	# read current pos and convert to mm
	print("POS_SET: cpos =", cpos)
	if cpos > startloc :
		while cpos > startloc :
			ljm.eWriteAddress(handle, DAC1addr, f_datatype, offsetV-0.5)
			cpos = v2d(ljm.eReadAddress(handle, AIN0addr, f_datatype))
			print("POS_SET: + running...", cpos)
		ljm.eWriteAddress(handle, DAC0addr, f_datatype, offV)
		ljm.eWriteAddress(handle, DAC1addr, f_datatype, offV)
	elif cpos < startloc:
		while cpos < startloc :
			ljm.eWriteAddress(handle, DAC1addr, f_datatype, offsetV+0.5)
			cpos = v2d(ljm.eReadAddress(handle, AIN0addr, f_datatype))
			print("POS_SET: - running...", cpos)
		ljm.eWriteAddress(handle, DAC0addr, f_datatype, offV)
		ljm.eWriteAddress(handle, DAC1addr, f_datatype, offV)
	else:
		print("POS_SET: Already at startloc, cpos = ", cpos)
		ljm.eWriteAddress(handle, DAC0addr, f_datatype, offV)
		ljm.eWriteAddress(handle, DAC1addr, f_datatype, offV)
else:
	# DAC0V = ljm.eReadAddress(handle, DAC0addr, f_datatype)
	# print("POS_HOLD: DAC0V = ", DAC0V)
	ljm.eWriteAddress(handle, DAC0addr, f_datatype, offV)
	ljm.eWriteAddress(handle, DAC1addr, f_datatype, offV)
	print("POS_HOLD: Holding stage in current pos: ", v2d(ljm.eReadAddress(handle, AIN0addr, f_datatype)))

i = 0
while i<20 :
	i += 1
	print("\nAIN0: ", ljm.eReadAddress(handle, AIN0addr,f_datatype))
	print("DAC0: ", ljm.eReadAddress(handle, DAC0addr, f_datatype))
	print("DAC1: ", ljm.eReadAddress(handle, DAC1addr, f_datatype))
	time.sleep(0.3)

ljm.close(handle)
print("\n FESTO.py: LABjack T7 closed")