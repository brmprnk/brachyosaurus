# Reset the motor to zero position
import pyfirmata
import time


def func(comport):
    stepsperrev = 24
    stepstotal = round(10/0.7*stepsperrev*1.2)
    dir = 0

    port = 'COM5'
    board = pyfirmata.Arduino(port)

    time.sleep(2)
    dirpin1 = board.get_pin("d:3:o")
    steppin1 = board.get_pin("d:2:o")
    dirpin2 = board.get_pin("d:5:o")
    steppin2 = board.get_pin("d:4:o")
    dirpin3 = board.get_pin("d:7:o")
    steppin3 = board.get_pin("d:6:o")
    dirpin4 = board.get_pin("d:9:o")
    steppin4 = board.get_pin("d:8:o")
    print("INIT: pins set")

    # Use iterator thread to avoid buffer overflow
    it = pyfirmata.util.Iterator(board)
    it.start()

    dirpin1.write(dir)
    dirpin2.write(dir)
    dirpin3.write(dir)
    dirpin4.write(dir)
    print("INIT: start running...")
    for x in range(stepstotal):
        steppin1.write(1)
        steppin2.write(1)
        steppin3.write(1)
        steppin4.write(1)
        time.sleep(0.005)
        steppin1.write(0)
        steppin2.write(0)
        steppin3.write(0)
        steppin4.write(0)
        time.sleep(0.005)

    print("INIT: finished")

    board.exit()


# if __name__ == "__main__":
#     func(comport)