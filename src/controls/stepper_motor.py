"""
Module for stepper motor class
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import src.util.logger as logger
import time
class Motor:
    """
    Class that represent stepper motor
    """

    def __init__(self, dirpin, movpin, startcount):
        self.dirpin = dirpin
        self.movpin = movpin
        self.stepcounter = int(startcount)
        logger.info("Creating new stepper motor instance:\n" +
                    "    Directional pin: {}\n".format(self.dirpin) +
                    "    Mov pin: {}\n".format(self.movpin) +
                    "    Initial stepcount: {}\n".format(self.stepcounter))


    def getCount(self):
        print("STEPPER_MOTOR.py: stepcounter = ", self.stepcounter)
        return self.stepcounter


    def runForward(self, runsteps):
        x=0
        self.dirpin.write(1)
        if self.stepcounter + runsteps  > 200:
            print("STEPPER_MOTOR.py--> runForward:    Steps make stepcounter exceed upperlimit (200)")
        else:
            for x in range(runsteps):
                self.movpin.write(1)
                time.sleep(0.01)
                self.movpin.write(0)
                time.sleep(0.01)
            self.stepcounter = self.stepcounter + runsteps
            print("STEPPER_MOTOR.py--> runForward: New stepcount is: ", self.stepcounter)


    def runBackward(self, runsteps):
        x = 0
        self.dirpin.write(0)
        if self.stepcounter - runsteps < 0:
            print("STEPPER_MOTOR.py--> runBackward:    Steps reduce stepcounter under lowerlimit (0)")
        else:
            for x in range(runsteps):
                self.movpin.write(1)
                time.sleep(0.01)
                self.movpin.write(0)
                time.sleep(0.01)
            self.stepcounter = self.stepcounter - runsteps
            print("STEPPER_MOTOR.py--> runBackward: New stepcount is: ", self.stepcounter)

