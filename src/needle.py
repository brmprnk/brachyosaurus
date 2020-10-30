import pyfirmata
import time
from controls import stepper_motor, controls


class Controller:

    def __init__(self, comport):
        self.port = comport
        # self.board = pyfirmata.Arduino(self.port)
        # time.sleep(1)
        self.motors = []
        # self.default_motor_setup()

    def default_motor_setup(self):
        motor0 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(3)),
                                    self.board.get_pin('d:{}:o'.format(2)))
        motor1 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(5)),
                                    self.board.get_pin('d:{}:o'.format(4)))
        motor2 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(7)),
                                    self.board.get_pin('d:{}:o'.format(6)))
        motor3 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(9)),
                                    self.board.get_pin('d:{}:o'.format(8)))
        self.motors.extend([motor0, motor1, motor2, motor3])
        
    
    def add_motor(self, dirpin, steppin, index):
        motor = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(dirpin)),
                                    self.board.get_pin('d:{}:o'.format(steppin)))
        self.motors.insert(index, motor)

    def remove_motor(self, index):
        return_value = self.motors.pop(index)
        return return_value

    def move_freely(self):
        controller = controls.Controls()
        controller.get_direction()

        # Move the needle:
        self.move_to_dir(direction)
    
    def move_to_dir(self, direction):
        """
        Krijg een richting --> Stuur de motors
        """
        print("Moving to : ", direction)


