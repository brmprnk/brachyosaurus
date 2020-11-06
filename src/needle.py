"""
Manager file for the steerable needle.
"""
import time
import pyfirmata
from src.controls import stepper_motor
from src.controls import controller
from src.util import logger


class Needle:
    """
    Needle Class.
    Configures setup of the linear motors and Arduino.
    Functions as a manager for the program, always knows what is the status.
    """

    def __init__(self, comport, startsteps):
        self.port = comport
        self.startcount = startsteps
        self.board = pyfirmata.Arduino(self.port)
        time.sleep(1)
        self.motors = []
        self.default_motor_setup()
        self.dirpull = {
            0:[0,1],
            1:[1],
            2:[1,3],
            3:[3],
            4:[2,3],
            5:[2],
            6:[0,2],
            7:[0],
        }

        self.dirpush = {
            0: [2, 3],
            1: [2],
            2: [0, 2],
            3: [0],
            4: [0, 1],
            5: [1],
            6: [1, 3],
            7: [3],
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
                                    self.board.get_pin('d:{}:o'.format(steppin)), startcount)
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
        input_method = controller.Controller()

        while True:
            direction = input_method.get_direction()

            # Check if faulty input and try again
            while direction == -1:
                time.sleep(0.5) # Sleep to make sure button is unpressed
                direction = input_method.get_direction()

            # Move the needle:
            logger.success("Moving to : {}".format(input_method.dir_to_text(direction)))
            self.move_to_dir(direction)

    def move_to_dir(self, direction):
        """
        Krijg een richting --> Stuur de motors
        """
        steps_per_control = 24

        # TODO: change from testing default to working section for all motors

        for motor in self.dirpull[direction]:
            self.motors[motor].run_backward(steps_per_control)
        for motor in self.dirpush[direction]:
            self.motors[motor].run_forward(steps_per_control)
