"""
Manager file for the steerable needle.
"""
import time
import threading
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from queue import LifoQueue
import pyfirmata
import cv2
import pygame

from src.controls import stepper_motor
from src.controls.controller import Controller
from src.util import logger
from src.image_acquisition import ImageAcquisition


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
            0: [1],
            1: [0, 1],
            2: [0],
            3: [0, 3],
            4: [3],
            5: [2, 3],
            6: [2],
            7: [2, 1],
        }

        self.dirpush = {
            0: [3],
            1: [2, 3],
            2: [2],
            3: [2, 1],
            4: [1],
            5: [0, 1],
            6: [0],
            7: [0, 3],
        }

    def default_motor_setup(self):
        """
        Initializes default motor to Arduino board configuration
        """
        motor0 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(3)),
                                     self.board.get_pin('d:{}:o'.format(2)),
                                     self.startcount, 0)
        motor1 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(5)),
                                     self.board.get_pin('d:{}:o'.format(4)),
                                     self.startcount, 1)
        motor2 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(7)),
                                     self.board.get_pin('d:{}:o'.format(6)),
                                     self.startcount, 2)
        motor3 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(9)),
                                     self.board.get_pin('d:{}:o'.format(8)),
                                     self.startcount, 3)
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

    def manual_brachy_therapy(self, args) -> None:
        """
        Handler for MANUAL Brachy Therapy, with possibility of needle tracking by two cameras.
        """
        # Create instances of controller and image acquisition
        input_method = Controller()
        image_acquisition = ImageAcquisition(args.fps, args.camtop, args.camfront, args.nofeed)

        # Queues allow for communication between threads. LIFO means the most recent image/input will be used
        camera_feed = LifoQueue(maxsize=0) # Create LIFO queue of infinite size that reads camera input
        input_feed = LifoQueue(maxsize=0) # Create LIFO queue of infinite size that reads controller input

        thread_1 = threading.Thread(target = image_acquisition.retrieve_current_image, args = (camera_feed, ))
        thread_1.name = "ImageAcquisition_thread"
        thread_2 = threading.Thread(target = input_method.get_direction_from_keyboard, args = (input_feed, ))
        thread_2.name = "KeyboardListener_thread"

        thread_1.start()
        thread_2.start()

        pygame.init()

        logger.success("Ready to receive inputs.\n")
        while True:
            current_frame = camera_feed.get()

            # Possible code for image processing
                # current_pos = get_needle_pos(current_frame)
                # logger.info("Needle is currently at {}".format(current_pos))
            
            # If camera feed is shown (nofeed == false)
            if not image_acquisition.no_cam_feed:
                cv2.imshow("Top Camera Feed", current_frame)
                if cv2.waitKey(1) == 27: # Escape Key exits loop
                    cv2.destroyAllWindows()
                    break

            events = pygame.event.get()
            input_method.get_direction_from_pygame_events(input_feed, events)
        
            direction = None
            if not input_feed.empty():
                direction = input_feed.get()

            # Check if faulty input and try again
            if direction is None or input_feed.qsize() == 0:
                continue
            if direction.direction == -1:
                continue

            # Move the needle:
            # logger.success("Moving to : {}".format(input_method.dir_to_text(direction.direction)))
            if direction.direction == 100:
                logger.success("Init called: moving to zero then to 100 steps")
                self.initial_position()
            else:
                logger.success("Moving to : {}".format(input_method.dir_to_text(direction.direction)))
                self.move_to_dir_sync(direction)


        # Neatly exiting loop
        print("Finished Program Execution", threading.active_count())
        pygame.quit()
        image_acquisition.is_running = False
        input_method.is_running = False

        thread_1.join()
        thread_2.join()        


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
                dirOutput = input_method.get_direction()

            # Move the needle:
            if dirOutput.direction == 100:
                logger.success("Init called: moving to zero then to 100 steps")
                self.initial_position()
            else:
                logger.success("Moving to : {}".format(input_method.dir_to_text(dirOutput.direction)))
                self.move_to_dir_sync(dirOutput)

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
            steps_diff = abs(200 - position)
            if position > 200:
                self.motors[motor_i].run_backward(steps_diff)
            else:
                self.motors[motor_i].run_forward(steps_diff)

    def move_to_dir_sync(self, gdo):
        """
        Krijg een richting --> Stuur de motors synchroon
        doe één stap op motor 1 dan op 2 dan 3 dan 4 dan weer één op 1 etc tot alle stappen zijn bereikt
        gdo = get direction output (an object of the class Output(direction, stepsout) )
        """

        sx = round(self.sensitivity * gdo.stepsx)
        sy = round(self.sensitivity * gdo.stepsy)

        # setting directions for each motor (pulling = 0, pushing = 1)
        motorpull = self.dirpull[gdo.direction]
        motorpush = self.dirpush[gdo.direction]
        if len(motorpull) > 1:
            self.motors[motorpull[0]].dirpin.write(0)
            self.motors[motorpull[1]].dirpin.write(0)
            self.motors[motorpush[0]].dirpin.write(1)
            self.motors[motorpush[1]].dirpin.write(1)
        else:
            self.motors[motorpull[0]].dirpin.write(0)
            self.motors[motorpush[0]].dirpin.write(1)

        # writing to the movpins in one while loop
        total_steps = sx+sy
        print('\nNEEDLE->move_to_dir_sync: starting to move sync...  total_steps =', total_steps)
        count = 0
        xcount = 0
        ycount = 0
        if len(motorpull) > 1:
            while count <= total_steps:
                if xcount < sx:
                    xcount = xcount + 1
                    self.motors[motorpull[0]].movpin.write(1)
                    self.motors[motorpush[0]].movpin.write(1)
                    time.sleep(0.01)
                    self.motors[motorpull[0]].movpin.write(0)
                    self.motors[motorpush[0]].movpin.write(0)
                    time.sleep(0.01)
                if ycount < sy:
                    ycount = ycount + 1
                    self.motors[motorpull[1]].movpin.write(1)
                    self.motors[motorpush[1]].movpin.write(1)
                    time.sleep(0.01)
                    self.motors[motorpull[1]].movpin.write(0)
                    self.motors[motorpush[1]].movpin.write(0)
                    time.sleep(0.01)
                count = count + 1
            # setting stepcounters to current positions
            self.motors[motorpull[0]].set_count(-1 * sx)
            self.motors[motorpull[1]].set_count(-1 * sy)
            self.motors[motorpush[0]].set_count(sx)
            self.motors[motorpush[1]].set_count(sy)
        else:
            while count <= sx:
                count = count + 1
                self.motors[motorpull[0]].movpin.write(1)
                self.motors[motorpush[0]].movpin.write(1)
                time.sleep(0.01)
                self.motors[motorpull[0]].movpin.write(0)
                self.motors[motorpush[0]].movpin.write(0)
                time.sleep(0.01)
            # setting stepcounters to current positions
            self.motors[motorpull[0]].set_count(-1*sx)
            self.motors[motorpush[0]].set_count(sx)
        print('\nNEEDLE->move_to_dir_sync: Movement finished.')
        self.motors[0].get_count()
        self.motors[1].get_count()
        self.motors[2].get_count()
        self.motors[3].get_count()