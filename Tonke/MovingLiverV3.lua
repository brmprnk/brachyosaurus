print("This is Moving Liver v2")

--Moving Liver v1, 1-12-2017, Arjan van Dijke, Delft University of Technology
--For a LabJack T7 with a Festo Controller and Linear Actuator
--Requires LabJack firmware 1.0166 or greater

--Get initial value, frequency and amplitide from host computer.  Host computer writes new setpoint to modbus address 46000

--Scaling factors:
--  position: 10V = 50mm
--  speed: 2.5V = 25mm/s

--Connections:
--  AIN0 = position (0-10V)
--  DAC0 = speed ref.signal (2.5V)
--  DAC1 = speed out signal (-2.5 - 2.5V)
--  USER_RAM0 = number related to frequency
--  USER_RAM1 = amplitide in mm

timeStep = 10         --timestep of the loop in ms, change according to your process (see theory on sampling rate in PID control)
inputV = 0
outputV = 0
setpointV = 0
offsetV = 2.5           -- offset voltage on output (2.5V is speed 0)
initposV = 0           -- initial position (5V = 25mm or halfway)

kp = 2.0                --change the PID terms according to your process
ki = 0.0
kd = 0.0

polOut = 1              --output polarity +1 or -1, i.e. for a positive error, negative output: -1

outputMin = -2.5        --bounds for the output value
outputMax = 2.5

outputCheck = 0
lastInput = 0
intterm = 0
difterm = 0

-- sine wave properties
frequency = 0                                   -- a number related to frequency
amplitude = 0                                   -- amplitude in mm
radstep = 0.01                                  -- nr. of radians per step. A smaller number increases waveform resolution
rads = 0

-- INIT0: start with no movement
print("Starting with no movement.")
MB.W(1000, 3, offsetV)                          --set DAC0 (reference) to offset value. Address is 1000, type is 3
MB.W(1002, 3, offsetV)                          --set DAC1 (signal)  to offset value. Address is 1002, type is 3

-- INIT1: bring stage to initial poisition
print("Bringing stage to initial position.")
inputV = MB.R(0, 3)                             --read AIN0 as the position
while inputV < initposV do
  MB.W(1002, 3, offsetV+2.5)                    -- move (2.5V = 25 mm/s)  to new position
  inputV = MB.R(0, 3)                           -- get a new position value
end

-- INIT2: stop stage at initial position
print("Stopping stage.")
MB.W(1000, 3, offsetV)                          --set DAC0 (reference) to offset value. Address is 1000, type is 3
MB.W(1002, 3, offsetV)                          --set DAC1 (signal)  to offset value. Address is 1002, type is 3
MB.W(46000, 3, 0)                               --make sure frequency in RAM is 0
MB.W(46002, 3, 0)                               --make sure amplitude in RAM is 0



-- RUN: PID control of sine wave position
print("Starting sine wave.")

LJ.IntervalConfig(0, timeStep)                  --set interval to 100 for 100ms

-- main run loop
while true do
  if LJ.CheckInterval(0) then                   --interval completed
    frequency = MB.R(46000, 3)                  --get new "frequency" from USER_RAM0_F32
    --print("frequency =", frequency)
    amplitude = MB.R(46002, 3)                  --get new amplitude in mm from USER_RAM1_F32
    --print("amplitude =", amplitude, "mm")
    inputV = MB.R(0, 3)                         --read AIN0 as the feedback source
    if rads >= 2 then
      radstep = radstep * -1                    -- reverse sinewave
    end
    setpointV = (amplitude/5) *-1* math.cos(frequency*rads)+(amplitude/5)                           -- calcultate new setpoint
    rads = rads + radstep
    
    --print("AIN0 =", inputV, "V")
    --print("position =", inputV-5, "V")
    --print("setpoint =", setpointV, "V")
    
    intterm = setpointV
    err = setpointV - inputV + initposV                -- calculate error signal (mind the initposV offset!)
    --print("The error is ", err)

-- I-action    
--    intterm = intterm + ki * err
--    intterm = intterm * polOut
--    if intterm > outputMax then
--      intterm = outputMax
--    elseif intterm < outputMin then
--      intterm = outputMin
--    end
--    print("The Int term is ", intterm)
    
-- D-action
--    difterm = inputV -5 - lastInput
--    difterm = polOut * difterm 
--    print("The Diff term is ", difterm * kd)
    
    --outputV = polOut* kp * err + intterm + kd * difterm   -- calculate new output signal
    outputV = polOut * kp * err                           -- calculate new output signal

    if outputV > outputMax then                           -- saturate output signal
      outputV = outputMax
    elseif outputV < outputMin then
      outputV = outputMin
    end
    --print("The output is ", outputV)
    
    MB.W(1002, 3, offsetV + outputV)                      --set DAC1 to new output (offset + signal)
    lastInput = inputV
    
    --print("")
    -- get new values from RAM
    --setpointV = MB.R(46000, 3)              --get new setpoint from USER_RAM0_F32, address 46000

  end
end
