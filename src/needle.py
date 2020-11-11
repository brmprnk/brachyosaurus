"""
Manager file for the steerable needle.
"""
import time
import pyfirmata
from src.controls import stepper_motor
#from src.controls import controller
from src.controls.controller import Output, Controller
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
        self.sensitivity = float(sensitivity)
        self.board = pyfirmata.Arduino(self.port)
        time.sleep(1)
        self.motors = []
        self.default_motor_setup()
        self.dirpull = {
            0:[1],
            1:[0,1],
            2:[0],
            3:[0,3],
            4:[3],
            5:[2,3],
            6:[2],
            7:[2,1],
        }

        self.dirpush = {
            0: [3],
            1: [2,3],
            2: [2],
            3: [2,1],
            4: [1],
            5: [0,1],
            6: [0],
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
            if dirOutput.direction == 100:
                logger.success("Init called: moving to zero then to 100 steps")
                self.initial_position()
            else:
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
        # run the motors, if motorpull is length 2 than so is motorpush, otherwise run only one axis (keyboard only)
        if len(motorpull) > 1:
            self.motors[motorpull[0]].run_backward(sx)
            self.motors[motorpull[1]].run_backward(sy)
            self.motors[motorpush[0]].run_forward(sx)
            self.motors[motorpush[1]].run_forward(sy)
        else:
            self.motors[motorpull[0]].run_backward(sx)      # steps for one axis is always 100 in x and y
            self.motors[motorpush[0]].run_forward(sx)


    def initial_position(self):
        """
        Stuur de motoren terug naar 100
        """
        for motor_i in range(len(self.motors)):
            position = self.motors[motor_i].get_count()
            steps_diff = abs(100 - position)
            if position > 100:
                self.motors[motor_i].run_backward(steps_diff)
            else:
                self.motors[motor_i].run_forward(steps_diff)


    def move_to_dir_sync(self, gdo):
        """
        Krijg een richting --> Stuur de motors synchroon
        doe een stap op motor 1 dan op 2 dan 3 dan 4 tot alle stappen zijn bereikt
        gdo = get direction output (an object of the class Output(direction, stepsout) )
        """

        sx = round(self.sensitivity * gdo.stepsx)
        sy = round(self.sensitivity * gdo.stepsy)

        # setting directions for each motor (pulling = 0, pushing = 1)
        motorpull = self.dirpull[gdo.direction]
        motorpush = self.dirpush[gdo.direction]
        self.motors[motorpull[0]].dirpin.write(0)
        self.motors[motorpull[1]].dirpin.write(0)
        self.motors[motorpush[0]].dirpin.write(1)
        self.motors[motorpush[1]].dirpin.write(1)

        # writing to the movpins in one while loop
        total_steps = sx+sy
        print('NEEDLE->move_to_dir_sync: starting to move sync... \n            total_steps =', total_steps)
        count = 0
        xcount = 0
        ycount = 0
        while True:
            if count > total_steps:
                break
            if xcount < sx:
                xcount = xcount + 1
                self.motors[motorpull[0]].movpin.write(1)
                self.motors[motorpush[0]].movpin.write(1)
                time.sleep(0.005)
                self.motors[motorpull[0]].movpin.write(0)
                self.motors[motorpush[0]].movpin.write(0)
            if ycount < sy:
                ycount = ycount + 1
                self.motors[motorpull[1]].movpin.write(1)
                self.motors[motorpush[1]].movpin.write(1)
                time.sleep(0.005)
                self.motors[motorpull[1]].movpin.write(0)
                self.motors[motorpush[1]].movpin.write(0)
            count = xcount + ycount
            print('NEEDLE->move_to_dir_sync: Movement finished.')
