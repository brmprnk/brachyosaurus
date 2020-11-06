# CHECKING CONNECTION AND DAC0,1 AND AIN0
from labjack import ljm

# Open any found LabJack
handle = ljm.openS("ANY", "ANY", "ANY")

# Call eReadName to read the serial number from the LabJack.
name = "SERIAL_NUMBER"
result = ljm.eReadName(handle, name)

print("\neReadName result: ")
print("    %s = %s" % (name, result))

# INIT I/O of T7 to zero
print("\nINIT I/O of LABjack T7 w/ write statements w/ value 0")
f_datatype = ljm.constants.FLOAT32
ljm.eWriteAddress(handle, 1000, f_datatype, 0)
ljm.eWriteAddress(handle, 1002, f_datatype, 0)

print("\nChecking INIT ...")
DAC0V = ljm.eReadAddress(handle, 1000, f_datatype)
DAC1V = ljm.eReadAddress(handle, 1002, f_datatype)
AIN0V = ljm.eReadAddress(handle, 0, f_datatype)
print("DACs  and AIN0 voltages: ")
print("    DAC0 = %f and DAC1 = %f" % (DAC0V, DAC1V))
print("    AIN0 = %f" % AIN0V)

ljm.close(handle)
print("\n LABjack T7 closed")