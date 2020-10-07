"""
Test
"""
import time
import sys
from labjack import ljm
from src.util import logger

######################################
## Function FESTO(endloc, startloc,speed)
## Drives the linear stage to a position 'endloc' with speed 'speed' after command 'startloc' did its thing
## startloc arguments:     - position float in mm like '0' goes to minimum position or '50' goes to maximum position
##                        - integer '-1' keeps the stage in its current place
######################################

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
endloc = 0            # mm
startloc = 25        # mm
speed = 0            # mm/s
#   #   #

f_datatype = ljm.constants.FLOAT32
i_datatype = ljm.constants.UINT16
offsetV = 2.5                 # (offsetV+2.5V on DAC1 = 25 mm/s)
offV = 0.0299544557929039     # low voltage that T7 can certainly output
maxpos = 50                    # mm
minpos = 3                    # mm

ljm.eWriteAddress(handle, DAC0addr, f_datatype, offsetV)        # INIT reference voltage

def v2d(locv: float) -> float:
    """
    Volt to location (mm) conversion
    """

    vmax = 9.418        # in volt, measured with labjack T7 AIN0
    vmin = 0.032
    dmax = 50.5            # in mm, measured by hand
    dmin = 3
    print("Voltage = ", locv)

    return ((dmax-dmin)/(vmax-vmin))*locv + dmin

def d2v(location: int) -> float:
    """
    Location (mm) to volt (float) conversiona
    """
    vmax = 9.418        # in volt, measured with labjack T7 AIN0
    vmin = 0.032
    dmax = 50.5            # in mm, measured by hand
    dmin = 3

    voltage = ((vmax - vmin)/(dmax-dmin))*(location - dmin)
    if voltage < 0:
        voltage = 0
    
    return voltage

def move_to_pos(init_pos: int, target_pos: int, move_speed: float) -> None:

    # Set initial pos
    ljm.eWriteAddress(handle, 46000, f_datatype, init_pos)
    # Set target pos
    ljm.eWriteAddress(handle, 46002, f_datatype, target_pos)
    # Set speed
    ljm.eWriteAddress(handle, 46004, f_datatype, move_speed)

    time.sleep(1)

    # Enable program
    ljm.eWriteAddress(handle, 46008, f_datatype, 1)
    while True:
        new_pos = logger.request_input("\nSet a new position to move towards (mm) : ")
        time.sleep(0.5)
        ljm.eWriteAddress(handle, 46002, f_datatype, new_pos)



def run(target_pos: int) -> None:
    """
    Main func
    """
    print("pos given: ", target_pos)
    print("AIN0 should then be: ", d2v(target_pos))

    ain0 = ljm.eReadAddress(handle, AIN0addr, f_datatype)
    print("AIN0 = ", ain0)
    print("current pos (mm) = ", v2d(ain0))

    while True:
        current_pos = v2d(ljm.eReadAddress(handle, AIN0addr, f_datatype))
        print("Current position (mm) = ", current_pos)
        print("Target position (mm )= ", target_pos)
        margin_of_error = 0.1
        if current_pos > target_pos:
            ljm.eWriteAddress(handle, DAC0addr, f_datatype, 2)
            ljm.eWriteAddress(handle, DAC1addr, f_datatype, 1)
        elif current_pos < target_pos:
            ljm.eWriteAddress(handle, DAC0addr, f_datatype, 1)
            ljm.eWriteAddress(handle, DAC1addr, f_datatype, 2)
        
        print("if desired pos = ", abs(current_pos - target_pos))
        if abs(current_pos - target_pos) < margin_of_error:
            print("yay, margin between desired and current = ", current_pos - target_pos)
            print("Desired pos reached")
            while True:
                ljm.eWriteAddress(handle, DAC0addr, f_datatype, 1)
                ljm.eWriteAddress(handle, DAC1addr, f_datatype, 0)
                time.sleep(0.1)
                ljm.eWriteAddress(handle, DAC0addr, f_datatype, 0)
                ljm.eWriteAddress(handle, DAC1addr, f_datatype, 1)
            sys.exit(1)
