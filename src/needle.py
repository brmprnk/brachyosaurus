"""
Manager file for the steerable needle.
"""
import time
import pyfirmata
from src.controls import stepper_motor
#from src.controls import controller
from src.controls.controller import Output,Controller
from src.util import logger


class Needle:
    """
    Needle Class.
    Configures setup of the linear motors and Arduino.
    Functions as a manager for the program, always knows what is the status.
    """

    def __init__(self, comport, startsteps, sensitivity):
        self.port = comport
        self.startcount = startsteps
        self.sensitivity = sensitivity
        self.board = pyfirmata.Arduino(self.port)
        time.sleep(1)
        self.motors = []
        self.default_motor_setup()
        self.dirpull = {

            1:[0,1],

            3:[0,3],

            5:[2,3],

            7:[2,1],
        }

        self.dirpush = {

            1: [2,3],

            3: [2,1],

            5: [0,1],

            7: [0,3],
        }

    def default_motor_setup(self):
        """
        Initializes default motor to Arduino board configuration
        """
        motor0 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(3)),
                                    self.board.get_pin('d:{}:o'.format(2)), self.startcount, 0)
        motor1 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(5)),
                                    self.board.get_pin('d:{}:o'.format(4)), self.startcount, 1)
        motor2 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(7)),
                                    self.board.get_pin('d:{}:o'.format(6)), self.startcount, 2)
        motor3 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(9)),
                                    self.board.get_pin('d:{}:o'.format(8)), self.startcount, 3)
        self.motors.extend([motor0, motor1, motor2, motor3])


    def add_motor(self, dirpin, steppin, startcount, index):
        """
        Add specific stepper_motor to Motor array
        """
        motor = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(dirpin)),
                                    self.board.get_pin('d:{}:o'.format(steppin)), startcount, index)
        self.motors.insert(index, motor)

    def remove_motor(self, index):
        """
        Remove specific motor from stepper_motor array
        """
        return_value = self.motors.pop(index)
        return return_value

    def move_freely(self):
        """
        Handler for needle movement
        """
        input_method = Controller()

        while True:
            dirOutput = input_method.get_direction()

            # Check if faulty input and try again
            while dirOutput.direction == -1:
                time.sleep(0.5) # Sleep to make sure button is unpressed
                direction = input_method.get_direction()

            # Move the needle:
            logger.success("Moving to : {}".format(input_method.dir_to_text(dirOutput.direction)))
            self.move_to_dir(dirOutput)

    def move_to_dir(self, gdo):
        """
        Krijg een richting --> Stuur de motors
        gdo = get direction output (an object of the class Output)
        """

        sx = round(self.sensitivity*gdo.stepsx)
        sy = round(self.sensitivity*gdo.stepsy)
        motorpull = self.dirpull[gdo.direction]
        motorpush = self.dirpush[gdo.direction]
        self.motors[motorpull[0]].run_backward(sx)
        self.motors[motorpull[1]].run_backward(sy)
        self.motors[motorpush[0]].run_forward(sx)
        self.motors[motorpush[1]].run_forward(sy)

