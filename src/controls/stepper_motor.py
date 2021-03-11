"""
Module for stepper motor class
"""
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import src.util.logger as logger
class Motor:
    """
    Class that represent stepper motor
    """

    def __init__(self, dirpin, movpin, startcount, index):
        self.dirpin = dirpin
        self.movpin = movpin
        self.stepcounter = int(startcount)
        self.index = index
        logger.info("Creating new stepper motor instance:\n" +
                    "    Directional pin: {}\n".format(self.dirpin) +
                    "    Mov pin: {}\n".format(self.movpin) +
                    "    Initial stepcount: {}\n".format(self.stepcounter))


    def get_count(self, report=0) ->int:
        """
        Getter for self.stepcounter
        """
        if report == 1:
            print(str(self.index) + " STEPPER_MOTOR.py: stepcounter = ", self.stepcounter)
        return self.stepcounter

    def set_count(self, steps_done):
        """
        Setter for self.stepcounter
        """
        self.stepcounter = self.stepcounter + steps_done
        print(str(self.index) + " STEPPER_MOTOR.py: new stepcount = ", self.stepcounter)



    def run_forward(self, runsteps, report=0):
        """
        Moves this motor forwards by runsteps amount
        """
        self.dirpin.write(1)
        if self.stepcounter + runsteps > 400:
            print("STEPPER_MOTOR.py->run_forward:    Steps make stepcounter exceed upper limit (400)")
        else:
            for _ in range(runsteps):
                self.movpin.write(1)
                time.sleep(0.01)
                self.movpin.write(0)
                time.sleep(0.01)
            self.stepcounter = self.stepcounter + runsteps
            if report == 1:
                print(str(self.index) + " STEPPER_MOTOR.py->run_forward: Current stepcount is: ", self.stepcounter)


    def run_backward(self, runsteps, report=0):
        """
        Moves this motor backwards by runsteps amount
        """
        self.dirpin.write(0)
        if self.stepcounter - runsteps < 0:
            print("STEPPER_MOTOR.py->run_backward:    Steps reduce stepcounter under lower limit (0)")
        else:
            for _ in range(runsteps):
                self.movpin.write(1)
                time.sleep(0.01)
                self.movpin.write(0)
                time.sleep(0.01)
            self.stepcounter = self.stepcounter - runsteps
            if report == 1:
                print(str(self.index) + " STEPPER_MOTOR.py--> run_backward: Current stepcount is: ", self.stepcounter)
