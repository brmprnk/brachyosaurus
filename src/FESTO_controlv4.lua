--[[
    Name: FESTO_controlv4.lua
    Desc: This is a PID example script that sets a DAC0 output using AIN2 for
          feedback
    Note: Gets a setpoint from a host computer.  Host computer writes the new
          setpoint to modbus address 46000 (USER_RAM0_F32)

          Requires FW 1.0282 or greater on the T7
--]]

--_______TESTING_____________
MB.W(46002,3,8)
--MB.W(46008,3,1) -- turn on enable

--Connections:
--  AIN0 = [0] position (0-10V)
--  DAC0 = [1000] ref.signal (2.5V)
--  DAC1 = [1002] speed out signal (-2.5 - 2.5V)
--  USER_RAM0 = [46000] initial position (startloc) !HAS TO BE >= 3 mm!
--  USER_RAM1 = [46002] necessary position (endloc)
--  USER_RAM2 = [46004] speed !has to be between 0 and 2.5!
--  USER_RAM2 = [46008] enable signal starts the program at a positive value

-- Set DAC0 to be higher than DAC1
MB.W(1000,3,0.5)
MB.W(1002,3,0)

print("This is a PID example script that sets a DAC0 output using AIN2 for feedback.")
print("Write a non-zero value to USER_RAM0_F32 to change the set point.")
-- Timestep of the loop in ms. Change according to your process
-- (see theory on sampling rate in PID control)
local timestep = 100
local targetpos = 0
local vin = 0
local vout = 0
-- Change the PID terms according to your process
local kp = 2
local ki = 0
local kd = 0
-- Bounds for the output value
local minout = -1.5
local maxout = 1.5
-- Variables for PID
local lastin = 0
local intterm = 0
local difterm = 0

offsetV = 2.5           -- offset voltage on output (2.5V is speed 0)

-- Add enabling functionality
print("Ready for enable input")
while true do
  enable = MB.R(46008,3)      -- check for positive enable signal
  if enable > 0 then
    break
  end
end
MB.W(46008,3,0)       -- deINIT enable

-- Configure the timestep interval
LJ.IntervalConfig(0, timestep)

-- targetpos = MB.readName("USER_RAM0_F32")
-- if targetpos > maxout then
--     targetpos = maxout
--     MB.writeName("USER_RAM0_F32", targetpos)
-- elseif targetpos < minout then
--     targetpos = minout
--     MB.writeName("USER_RAM0_F32", targetpos)
-- end

MB.W(1000, 3, offsetV)                          --set DAC0 (reference) to offset value. Address is 1000, type is 3
MB.W(1002, 3, offsetV)                          --set DAC1 (signal)  to offset value. Address is 1002, type is 3

while true do
  -- If an interval is done
  if LJ.CheckInterval(0) then
    -- Get a new targetpos from from 46002
    targetpos = MB.R(46002,3)

    -- Read AIN0 as the feedback source
    currentpos = MB.R(0, 3)
    print("The currentpos is ", currentpos)
    -- Calculate integral term
    difference = targetpos - currentpos
    intterm = intterm + ki * difference

    difterm = currentpos - lastin

    vout = kp * difference + intterm - kd * difterm
    vout = vout + offsetV

    -- Limit the maximum output voltage
    if vout > offsetV + maxout then
      vout = maxout + offsetV
    elseif vout < offsetV + minout then
      vout = minout + offsetV
    end

    -- Write the output voltage to DAC1
    -- print("The output is ", vout)
    MB.W(1002, 3, vout)

    -- Keep track of lastin
    lastin = currentpos
    print("overshoot =", currentpos - targetpos)
    print("")
  end
end