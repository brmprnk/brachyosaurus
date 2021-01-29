"""
Manager file for the steerable needle.
"""
import time
import threading
import multiprocessing
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from queue import LifoQueue
import pyfirmata
import pygame
from labjack import ljm
from configparser import ConfigParser

from src.controls import stepper_motor
from src.controls.controller import Controller
from src.util import logger
from src.image_acquisition import ImageAcquisition
from src.image_proc2 import position_from_image


class Needle:
    """
    Needle Class.
    Configures setup of the linear motors, Arduino and FESTO stage.
    Functions as a manager for the program, always knows what is the status of needle controlling parts.
    """

    def __init__(self, comport_arduino, startsteps, sensitivity):

        self.port = comport_arduino
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

        """
        FESTO section
        !!! to use FESTO:    first upload "FESTO_controlv3.lua" to the T7 with Kipling 3 software
                            then close the connection with Kipling 3 software
        """
        # config
        config_object = ConfigParser()
        config_object.read('config.ini')
        festo = config_object["FESTO"]

        self.init_FESTO_pos = int(festo["initial_pos"])
        self.init_FESTO_speed = float(festo["initial_speed"])

        self.AIN0addr = 0               # position (0-10V)
        self.DAC0addr = 1000            # speed ref.signal (2.5V)
        self.DAC1addr = 1002            # speed out signal (-2.5 - 2.5V)
        self.initialpos_addr = 46000
        self.targetpos_addr = 46002
        self.speed_addr = 46004
        self.enable_addr = 46008
        self.f_datatype = ljm.constants.FLOAT32
        self.i_datatype = ljm.constants.UINT16

        self.offsetV = 2.5              # (offsetV+2.5V on DAC1 = 25 mm/s)
        self.offV = 0.0299544557929039  # low voltage that T7 can certainly output
        self.maxpos = 50                # mm
        self.minpos = 3                 # mm
        self.currentpos = self.init_FESTO_pos

        try:
            FESTO_handle = ljm.openS("ANY", "USB", "ANY")
        except ljm.LJMError as error:
            FESTO_handle = None
            logger.error("No FESTO_handle: thus not able to use the FESTO functions \n Error presented: " + str(error))

        if FESTO_handle is not None:
            self.FESTO_handle = FESTO_handle
            # Set initial positions (keep target pos at init_FESTO_pos at the start)
            ljm.eWriteAddress(self.FESTO_handle, self.initialpos_addr, self.f_datatype, self.init_FESTO_pos)
            ljm.eWriteAddress(self.FESTO_handle, self.targetpos_addr, self.f_datatype, self.init_FESTO_pos)
            # Set speed
            ljm.eWriteAddress(self.FESTO_handle, self.speed_addr, self.f_datatype, self.init_FESTO_speed)
            logger.success("FESTO connected, handle is available, init is set, current position =" + str(ljm.eReadAddress(self.FESTO_handle, self.AIN0addr, self.f_datatype)))
            time.sleep(0.3)

            # Enable init LUA program
            ljm.eWriteAddress(self.FESTO_handle, self.enable_addr, self.f_datatype, 1)
            logger.success("FESTO moving to initial position")
        else:
            self.FESTO_handle = None

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

    def automated_brachy_therapy(self, args) -> None:
        """
        Handler for AUTOMATED Brachy Therapy.
        Can handle two camera's, and also allows for manual inputs to overwrite aoutomated commands.
        """
        # Enter code here

    def manual_brachy_therapy(self, args) -> None:
        """
        Handler for MANUAL Brachy Therapy, with possibility of needle tracking by two cameras.
        """
        # Create instances of controller and image acquisition
        input_method = Controller()
        image_acquisition = ImageAcquisition(args.fps, args.camtop, args.camfront, args.nofeed)

        # Queues allow for communication between threads. LIFO means the most recent image/input will be used
        camera_feed = multiprocessing.Queue(maxsize=0) # Create LIFO queue of infinite size that reads camera input
        input_feed = LifoQueue(maxsize=0) # Create LIFO queue of infinite size that reads controller input

        process_1 = multiprocessing.Process(target = image_acquisition.retrieve_current_image, args = (camera_feed, ))
        process_1.name = "ImageAcquisition_process"
        thread_2 = threading.Thread(target = input_method.get_direction_from_keyboard, args = (input_feed, ))
        thread_2.name = "KeyboardListener_thread"

        process_1.start()
        thread_2.start()

        pygame.init()

        logger.success("Ready to receive inputs.\n")
        while True:
            current_frame = None
            if not camera_feed.empty():
                current_frame = camera_feed.get()
                if current_frame is None: # Sentinel value received, exit pogram loop
                    break

                # TODO: check and finish use of image proc in manual_brachy function
                if current_frame is not None:
                    tip_position, tip_ori = position_from_image(current_frame, "config.ini", flip='yes', filtering='yes', show='no')

                    if tip_position is None or tip_ori is None:
                        continue

                    logger.info("Needletip is currently at {}".format(tip_position))
                    logger.info("Needle orientation is currently {}".format(tip_ori))


                events = pygame.event.get()
                input_method.get_direction_from_pygame_events(input_feed, events)
            
                direction = None
                
                if not input_feed.empty():
                    direction = input_feed.get()
                    if direction is None: # Sentinel value was put in Queue
                        break

                # Check if faulty input and try again
                if direction is None:
                    continue
                if direction.direction == -1:
                    continue

                # Move the needle:
                # TODO: implement festo_move() on controller commands (like in move_freely())
                if direction.direction == 100:
                    logger.success("Init called: moving motors to zero then to 200 steps, FESTO to initial position")
                    self.initial_position()
                else:
                    logger.success("Moving to : {}".format(input_method.dir_to_text(direction.direction)))
                    self.move_to_dir_sync(direction)


        # Neatly exiting loop
        print("Finished Program Execution", threading.active_count())
        pygame.quit()
        image_acquisition.is_running = False
        input_method.is_running = False

        process_1.terminate()
        process_1.join()
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
                logger.success("Init called: moving FESTO to init_FESTO_pos and needle to zero then to 200 steps")
                self.initial_position()
            else:
                logger.success("Moving to : {}".format(input_method.dir_to_text(dirOutput.direction)))
                if dirOutput.direction == 200:
                    self.festo_move(-3, self.init_FESTO_speed, relative=1)
                    time.sleep(0.05)
                    continue
                if dirOutput.direction == 201:
                    self.festo_move(3, self.init_FESTO_speed, relative=1)
                    time.sleep(0.05)
                    continue
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
        Stuur de FESTO naar init en motoren terug naar 200
        """
        self.festo_move(self.init_FESTO_pos, self.init_FESTO_speed)
        # TODO: consider disconnecting needle at this point (then clicking ENTER)
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
        gdo = get direction output (an object of the class Output(direction: int, stepsout: tuple) )
        """
        # TODO implement automated needle speed adjustment
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

    def festo_move(self, targetpos: int, speed: float, relative=0) -> None:
        """
        Moves the FESTO stage to the "targetpos" with "speed"
            !!! to use this function see the instructions in the FESTO section in __init__ !!!

            1) writes "targetpos" and "speed" to the T7's data registers
            2) the LUA script takes care of the movement

            *) if the movement is to be relative to current position use 'relative' = 1
        """
        # relative function
        if relative == 1:
            if self.currentpos + targetpos < 0:
                print("NEEDLE->festo_move: Warning, currentpos is below 0")
            elif self.currentpos + targetpos > 50:
                print("NEEDLE->festo_move: Warning, currentpos is going past 50")
            targetpos = self.currentpos + targetpos

        ljm.eWriteAddress(self.FESTO_handle, self.targetpos_addr, self.f_datatype, targetpos)
        ljm.eWriteAddress(self.FESTO_handle, self.speed_addr, self.f_datatype, speed)

        self.currentpos = targetpos
