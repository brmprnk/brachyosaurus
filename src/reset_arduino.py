import pyfirmata
from time import sleep

# Define custom function to perform Blink action
def blinkLED(pin, message):
    print(message)
    board.digital[pin].write(1)
    sleep(1)
    board.digital[pin].write(0)
    sleep(1)

port = 'tty.usbserial-141220'
board = pyfirmata.Arduino(port)

# Use iterator thread to avoid buffer overflow
it = pyfirmata.util.Iterator(board)
it.start()

i = 0
while i < 20:
    blinkLED(13, "Calling blinkLED")
    i = i + 1

board.exit()