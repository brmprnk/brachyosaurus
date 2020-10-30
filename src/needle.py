import pyfirmata
import time
import sys
from controls import stepper_motor, controller
import util.logger as logger


class Needle:

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
        motor0 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(3)),
                                    self.board.get_pin('d:{}:o'.format(2)), self.startcount)
        motor1 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(5)),
                                    self.board.get_pin('d:{}:o'.format(4)), self.startcount)
        motor2 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(7)),
                                    self.board.get_pin('d:{}:o'.format(6)), self.startcount)
        motor3 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(9)),
                                    self.board.get_pin('d:{}:o'.format(8)), self.startcount)
        self.motors.extend([motor0, motor1, motor2, motor3])
        
    
    def add_motor(self, dirpin, steppin, startcount, index):
        motor = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(dirpin)),
                                    self.board.get_pin('d:{}:o'.format(steppin)), startcount)
        self.motors.insert(index, motor)

    def remove_motor(self, index):
        return_value = self.motors.pop(index)
        return return_value

    def move_freely(self):
        input_method = controller.Controller()

        direction = input_method.get_direction()

        if (direction == -1):
            logger.error("No valid input given --> Undefined direction")
            sys.exit(1)
            

        # Move the needle:
        self.move_to_dir(direction)
    
    def move_to_dir(self, direction):
        """
        Krijg een richting --> Stuur de motors
        """
        stepsPerControl = 24

        print("Moving to : ", direction)
        # TODO: change from testing default to working section for all motors

        if direction == 0:
            for motor in self.dirpull[direction]:
                self.motors[motor].runBackward(stepsPerControl)
            for motor in self.dirpush[direction]:
                self.motors[motor].runForward(stepsPerControl)
        else:
            self.motors[0].runBackward(200)

