# Reset the motor to zero position
import pyfirmata
import time

stepsperrev = 24
stepstotal = round(10/0.7*stepsperrev*1.2)
dir = 0

port = 'COM5'
board = pyfirmata.Arduino(port)

time.sleep(2)
dirpin = board.get_pin("d:3:o")
steppin = board.get_pin("d:2:o")

# Use iterator thread to avoid buffer overflow
it = pyfirmata.util.Iterator(board)
it.start()

dirpin.write(dir)
for x in range(stepstotal):
    steppin.write(1)
    time.sleep(0.005)
    steppin.write(0)
    time.sleep(0.005)

board.exit()