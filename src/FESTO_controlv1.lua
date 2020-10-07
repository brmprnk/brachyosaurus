-- FESTO_control v1, 6-10-2020, Florens Helfferich & Bram Pronk, TU Delft MISIT
-- Holds FESTO stage in place if not given a move command on its Registers
-- By setting RAM0 on a position other than its current, it will start to move
-- at a speed given by RAM1

--_______TESTING_____________
--MB.W(46000,3,40)
--MB.W(46002,3,20)
--MB.W(46004,3,0.5)
--MB.W(46008,3,0)

--Scaling factors:
--  position: 9.418 = 50.5mm
--    	      0.032 = 3 mm
--  speed: +2.5V = 25mm/s
--	   -2.5V = -25mm/s

--Connections:
--  AIN0 = [0] position (0-10V)
--  DAC0 = [1000] ref.signal (2.5V)
--  DAC1 = [1002] speed out signal (-2.5 - 2.5V)
--  USER_RAM0 = [46000] initial position (startloc) !HAS TO BE >= 3 mm!
--  USER_RAM1 = [46002] necessary position (endloc)
--  USER_RAM2 = [46004] speed !has to be between 0 and 2.5!
--  USER_RAM2 = [46008] enable signal starts the program at a positive value

-- defining limits
dmax = 50.5
dmin = 3
vmax = 9.418
vmin = 0.032
--  ((dmax-dmin)/(vmax-vmin))*locv + dmin

outputMin = -1.5        --bounds for the output value
outputMax = 1.5

offsetV = 2.5           -- offset voltage on output (2.5V is speed 0)

while true do
  enable = MB.R(46008,3)      -- check for positive enable signal
  if enable > 0 then
    break
  end
end
MB.W(46008,3,0)       -- deINIT enable

-- INIT0: start with no movement
print("Starting with no movement.")
MB.W(1000, 3, offsetV)                          --set DAC0 (reference) to offset value. Address is 1000, type is 3
MB.W(1002, 3, offsetV)                          --set DAC1 (signal)  to offset value. Address is 1002, type is 3
start = MB.R(46000,3)
startposV = ((vmax - vmin)/(dmax-dmin))*(start - dmin) -- given startpos in volt
if startposV > vmax then
  startposV = vmax
elseif startposV < vmin then
  startposV = vmin
  end

-- INIT1: move to initial position (startloc in python)
LJ.IntervalConfig(1,3000)
print("INIT1: Going to starting position")
while true do
  cposV = MB.R(0,3) -- current position in volt
  if startposV >= 0 then
    if cposV > startposV then
  	  while cposV > startposV do
			  cposV = MB.R(0,3)
			  MB.W(1002,3, offsetV+outputMin)
			  print("INIT1: running back... ", cposV)
		  end
		  MB.W(1002, 3, offsetV) 
	  elseif cposV < startposV then
  	  while cposV < startposV do
			  cposV = MB.R(0,3)
			  MB.W(1002,3,offsetV+outputMax)
			  print("INIT1: running forward... ", cposV)
		  end
		  MB.W(1002, 3, offsetV) 
	  else print("INIT1: Already at startloc, holding now")
	  end
  else 
    print("INIT1: Holding at current position")
  end
  if LJ.CheckInterval(1) then break end
end
print("INIT1: routine finished")

-- main running loop 
print("Main: starting main loop")
LJ.IntervalConfig(0, 20)             --set interval to 100 for 100ms
while true do
  speed = MB.R(46004,3)
  if speed > outputMax then
    speed = outputMax
  end
--  print("Main: speed = ", speed)
  
  targetpos = MB.R(46002,3)
  tposV = ((vmax - vmin)/(dmax-dmin))*(targetpos - dmin)
  
  if tposV > vmax then
    tposV = vmax
  elseif tposV < vmin then
    tposV = vmin
  end
--  print("Main: tposV = ", tposV)
  
  if LJ.CheckInterval(0) then
    cposV = MB.R(0,3)
    if cposV > tposV then 
      LJ.IntervalConfig(2,40)
      while true do
        MB.W(1002,3, offsetV-speed)
        if LJ.CheckInterval(2) then
          MB.W(1002,3, offsetV)
          break
        end
      end
    elseif cposV < tposV then 
      LJ.IntervalConfig(2,40)
      while true do
        MB.W(1002,3, offsetV+speed)
        if LJ.CheckInterval(2) then
          MB.W(1002,3, offsetV)
          break
        end
      end
    end
  end
print("Main: iteration finished ", cposV)

end

print("Error: end reached")
