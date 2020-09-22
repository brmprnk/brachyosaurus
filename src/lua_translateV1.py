from labjack import ljm

# Open first USB connected found LabJack
handle = ljm.openS("ANY", "USB", "ANY")

# Call eReadName to read the serial number from the LabJack.
name = "SERIAL_NUMBER"
result = ljm.eReadName(handle, name)

print("\neReadName result: ")
print("    %s = %s" % (name, result))

# --Scaling factors:
# --  position: 10V = 50mm
# --  speed: 2.5V = 25mm/s
#
# --Connections:
# --  AIN0 = position (0-10V) (R addr. = 0)
# --  DAC0 = speed ref.signal (2.5V) (R addr. = 1000)
# --  DAC1 = speed out signal (-2.5 - 2.5V) (R addr. = 1002)
# --  USER_RAM0 = number related to frequency (R addr. = 46080)
# --  USER_RAM1 = amplitude in mm (R addr. = 46082)

outputMin = -2.5        #bounds for the output value
outputMax = 2.5