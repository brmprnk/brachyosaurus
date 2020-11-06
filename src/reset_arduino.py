# Reset the motor to zero position
import pyfirmata
import time


def func(comport, startsteps):
    stepsperrev = 24
    stepstotal = round(10/0.7*stepsperrev*1.2)
    dirstart = 0

    stepsmax = 200
    stepsmid = int(startsteps)
    if stepsmid > stepsmax:
        stepsmid = stepsmax
    dirmid = 1

    port = comport
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

    dirpin1.write(dirstart)
    dirpin2.write(dirstart)
    dirpin3.write(dirstart)
    dirpin4.write(dirstart)
    print("INIT: start running to zero...")
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

    print("INIT: at zero")
    dirpin1.write(dirmid)
    dirpin2.write(dirmid)
    dirpin3.write(dirmid)
    dirpin4.write(dirmid)
    print("INIT: running to mid (steps= " + str(stepsmid) + ")...")
    for x in range(stepsmid):
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

    print("INIT: currently at mid (steps= " + str(stepsmid) + "), exiting board")
    board.exit()


# if __name__ == "__main__":
#     func(comport)