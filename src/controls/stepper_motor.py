"""
Module for stepper motor class
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import src.util.logger as logger

class Motor:
    """
    Class that represent stepper motor
    """

    def __init__(self, dirpin, movpin):
        self.dirpin = dirpin
        self.movpin = movpin
        self.stepcounter = 100
        logger.info("Creating new stepper motor instance:\n" +
                    "    Directional pin: {}\n".format(self.dirpin) +
                    "    Mov pin: {}\n".format(self.movpin))
    