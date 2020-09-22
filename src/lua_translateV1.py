from labjack import ljm
import time
import math
#############################################################################
# CRACK CODE NIET GEBRUIKEN
############################################################################
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
AIN0addr = 0
# --  DAC0 = speed ref.signal (2.5V) (R addr. = 1000)
DAC0addr = 1000
# --  DAC1 = speed out signal (-2.5 - 2.5V) (R addr. = 1002)
DAC1addr = 1002
# --  USER_RAM0 = number related to frequency (R addr. = 46000)\
RAM0addr = 46000
# --  USER_RAM1 = amplitude in mm (R addr. = 46002)
RAM1addr = 46002

timeStep = 10         #timestep of the loop in ms, change according to your process (see theory on sampling rate in PID control)
inputV = 0
outputV = 0
setpointV = 0
offsetV = 2.5           #offset voltage on output (2.5V is speed 0)
initposV = 5           #initial position (5V = 25mm or halfway)

kp = 2.0                #change the PID terms according to your process
ki = 0.0
kd = 0.0

polOut = 1              #output polarity +1 or -1, i.e. for a positive error, negative output: -1

outputMin = -2.5        #bounds for the output value
outputMax = 2.5

outputCheck = 0
lastInput = 0
intterm = 0
difterm = 0

#sine wave properties
frequency = 0                                   #a number related to frequency
amplitude = 0                                   # amplitude in mm
radstep = 0.01                                  # nr. of radians per step. A smaller number increases waveform resolution
rads = 0


#INIT0 no movement at starting position
print("INIT0: NO initial position and speed")
dataTypeFlt = ljm.constants.FLOAT32
ljm.eWriteAddress(handle, DAC0addr, dataTypeFlt, offsetV)
ljm.eWriteAddress(handle, DAC1addr, dataTypeFlt, offsetV)

#INIT1 initial pos
print("Bring to initial pos")
inputV = ljm.eReadAddress(handle, AIN0addr, dataTypeFlt)
print("what is inputV? %f" % (inputV)) #read AIN0 as the position
while inputV < initposV :
    print("Loop counter obama| inputV: %f " % (inputV))
    ljm.eWriteAddress(handle, DAC1addr, dataTypeFlt, offsetV+2.5)   # move (2.5V = 25 mm/s)  to new position
    inputV = ljm.eReadAddress(handle, AIN0addr, dataTypeFlt)                         # get a new position value

ljm.eWriteAddress(handle, DAC1addr, dataTypeFlt, 3)   # move (2.5V = 25 mm/s)  to new position
time.sleep(1)
ljm.eWriteAddress(handle, DAC1addr, dataTypeFlt, 5)  # move (2.5V = 25 mm/s)  to new position

# INIT2 stop stage at initial position
# print("Stopping stage.")
ljm.eWriteAddress(handle, DAC0addr, dataTypeFlt, offsetV)  #ref signal
# readDAC0 = ljm.eReadAddress(handle, DAC0addr, dataTypeFlt)
# print("DAC0 is %f" % (readDAC0))
# ljm.eWriteAddress(handle, DAC1addr, dataTypeFlt, 10)  # drive signal
# readDAC1 = ljm.eReadAddress(handle, AIN0addr, dataTypeFlt)
# print("AIN0 is %f" % (readDAC1))
# ljm.eWriteAddress(handle, RAM0addr, dataTypeFlt, 0)         # init freq in RAM at 0
# ljm.eWriteAddress(handle, RAM1addr, dataTypeFlt, 0)         # init amp in RAM at 0

# # RUN: PID control of sine wave position
# print("Starting sine wave.")
#
# # ljm.startInterval(0, 10000)
# time.sleep(5)
# i = 0
# while i < 20:
#     # skippedIntervals = ljm.waitForNextInterval(0)
#     # if skippedIntervals == 0:
#     print("Ever here?")
#     skippedIntervals = 0;
#
#     frequency = 1
#     amplitude = 10
#     inputV = ljm.eReadAddress(handle, AIN0addr, dataTypeFlt) #read AIN0 as feedback
#     if rads >= 2 :
#         radstep = radstep * -1
#     setpointV = (amplitude / 5) * -1 * math.cos(frequency * rads) + (amplitude / 5) #calc new setpoint
#     rads = rads + radstep
#
#     intterm = setpointV
#     err = setpointV - inputV + initposV
#
#     outputV = polOut * kp * err             # calculate new output signal
#     print("OutputV %f" % (outputV))
#
#     # if outputV > outputMax :                           #saturate output signal
#     #     outputV = outputMax
#     # elif outputV < outputMin :
#     #     outputV = outputMin
#
#     if i % 2 == 0:
#         outputV = 5
#     else:
#         outputV = 0
#     print("after brilliant if? OutputV %f" % (outputV))
#
#     ljm.eWriteAddress(handle, DAC1addr, dataTypeFlt, offsetV + outputV) # set DAC1 to new output (offset+signal)
#     lastInput = inputV
#     i += 1
#     time.sleep(1)

# ljm.cleanInterval(0)