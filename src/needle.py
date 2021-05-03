"""
Manager file for the steerable needle.
"""
import time
import multiprocessing
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from queue import LifoQueue
import argparse
import pyfirmata
import pygame
import numpy as np
from labjack import ljm
from configparser import ConfigParser

from src.controls import stepper_motor
from src.controls.controller import Controller
from src.util import logger
from src.image_acquisition import ImageAcquisition


class Needle:
    """
    Needle Class.
    Configures setup of the linear motors, Arduino and FESTO stage.
    Functions as a manager for the program, always knows what is the status of needle controlling parts.
    """

    def __init__(self, comport_arduino, startsteps, sensitivity, invertx: bool):
        # Handle input parameters
        self.port = comport_arduino
        self.startcount = startsteps
        self.init_pos = 0
        self.sensitivity = float(sensitivity)
        if self.sensitivity > 1:
            self.sensitivity = 0.5
            logger.info("Invalid sensitivity entered: new value = {}".format(self.sensitivity))
        self.invert_x_axis = invertx

        # Setup Arduino and Stepper Motors
        self.board = pyfirmata.Arduino(self.port)
        time.sleep(1)
        self.motors = []
        self.default_motor_setup()
        self.dirpull = {
            0: [0, 1],
            1: [0],
            2: [0, 3],
            3: [3],
            4: [2, 3],
            5: [2],
            6: [1, 2],
            7: [1],
        }

        self.dirpush = {
            0: [2, 3],
            1: [2],
            2: [1, 2],
            3: [1],
            4: [0, 1],
            5: [0],
            6: [0, 3],
            7: [3],
        }

        # motor vectors that code for the directions in the x-y space of the needle
        self.motorvec = {
            0: np.array([1, 1]),
            1: np.array([-1, 1]),
            2: np.array([-1, -1]),
            3: np.array([1, -1]),
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
        motor0 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(7)),
                                     self.board.get_pin('d:{}:o'.format(6)),
                                     self.startcount, 0)
        motor1 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(5)),
                                     self.board.get_pin('d:{}:o'.format(4)),
                                     self.startcount, 1)
        motor2 = stepper_motor.Motor(self.board.get_pin('d:{}:o'.format(3)),
                                     self.board.get_pin('d:{}:o'.format(2)),
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
        Can handle two camera's, and also allows for manual inputs to overwrite automated commands.
        """
        # Enter code here

    def manual_brachy_therapy(self, args: argparse.Namespace) -> None:
        """Main Program Loop for MANUAL Brachy Therapy, with possibility of needle tracking by two cameras.

        Parameters
        ----------
        args : argparse.Namespace

        Returns
        -------
        None
        """
        # Create Class instances of controller and image acquisition
        input_method = Controller(self.invert_x_axis)
        image_acquisition = ImageAcquisition(args.fps, args.camtop, args.camfront, args.nofeed)

        # Queues allow for communication between threads/processes. LIFO means the most recent image/input will be used
        input_feed = LifoQueue(maxsize=0) # Create LIFO queue of infinite size that reads controller input
        needle_pos_feed = multiprocessing.Queue(maxsize=0) # Create Queue for communication of needle tip pos/ori

        # Create and start Process for Image Acq/Proc
        process_1 = multiprocessing.Process(target=image_acquisition.retrieve_current_image, args=(needle_pos_feed, ))
        process_1.name = "ImageAcquiProc_process"

        # Start pygame to allow controller and keyboard inputs
        pygame.init()

        logger.success("Ready to receive inputs.\n")
        while True:
            # Check for needle coordinates in the Multiprocessing Queue
            if not needle_pos_feed.empty():

                tip_position, tip_ori = needle_pos_feed.get()

                # Sentinel value found, exit program
                if tip_position is None and tip_ori is None:
                    break

                logger.info("Needletip is currently at {}".format(tip_position))
                logger.info("Needle orientation is currently {}".format(tip_ori))
                # TODO: check and finish use of image proc in manual_brachy function

            # Retrieve any user inputs
            events = pygame.event.get()
            input_method.get_direction_from_pygame_events(input_feed, events)

            direction = None

            if not input_feed.empty():
                direction = input_feed.get()

                # Sentinel value was put in Queue, exit program
                if direction is None:
                    break

            # Check if faulty input and try again
            if direction is None:
                continue
            if direction.direction == -1:
                continue

            # TODO: update to synced_motorV2 way of steering
            # Move the needle:
            if direction.direction == 100:
                logger.success("Init called: moving to midpoint then to zero")
                self.initial_position()

            else:
                logger.success("Moving to : {}".format(input_method.dir_to_text(direction.direction)))
                self.move_to_dir_sync(direction)
                logger.success("\nReady to receive inputs.\n")


        # Neatly exiting main program loop
        pygame.quit()
        image_acquisition.is_running = False
        input_method.is_running = False

        process_1.terminate()
        process_1.join()
        print("Finished Program Execution.")

    def move_freely(self):
        """
        Handler for needle movement
        """
        input_method = Controller(self.invert_x_axis)
        input_feed = LifoQueue(maxsize=0) # Create LIFO queue of infinite size that reads controller input

        while True:
            # Retrieve user inputs
            events = pygame.event.get()
            input_method.get_direction_from_pygame_events(input_feed, events)

            dir_output = None

            if not input_feed.empty(): # An input was entered
                dir_output = input_feed.get()

                # Sentinel value was put in Queue, exit program
                if dir_output is None:
                    break

                if dir_output.direction == -1:
                    time.sleep(0.5) # Sleep to make sure button is unpressed
                    continue

                # Move the needle:
                if dir_output.direction == 100:
                    logger.success("Init called: Needle motors moving to midpoint then to zero \n"
                                   "                FESTO returning to initial point")
                    self.initial_position()
                elif dir_output.direction == -3: # The X-Button: a counter part of the Y-button
                    # Set the init_pos back to 0
                    self.init_pos = 0
                    print("The new initial position is 0")
                elif dir_output.direction == -2: # Special value for pressing the Y-button
                    # We want a new initial position, update initial position to current position
                    currentpos = []
                    for motor_i in range(len(self.motors)):
                        position = self.motors[motor_i].get_count()
                        currentpos = currentpos + [position]

                    # When I press init, this is where I want to go instead of 0.
                    midpoint = int((max(currentpos) + min(currentpos)) / 2)
                    print("The new initial position instead of 0 is the average of current pos: ", midpoint)
                    self.init_pos = midpoint


                elif dir_output.direction == 200:
                    logger.success("Moving to : {}".format(input_method.dir_to_text(dir_output.direction)))
                    self.festo_move(-3, self.init_FESTO_speed, relative=1)
                    time.sleep(0.05)
                    continue
                elif dir_output.direction == 201:
                    logger.success("Moving to : {}".format(input_method.dir_to_text(dir_output.direction)))
                    self.festo_move(3, self.init_FESTO_speed, relative=1)
                    time.sleep(0.05)
                    continue
                else:
                    logger.success("Moving to : {}".format(input_method.dir_to_text(dir_output.direction)))
                    self.move_to_dir_syncv2(dir_output, report=1)
                    logger.success("\nReady to receive inputs.\n")

        # Neatly exiting main program loop
        pygame.quit()
        input_method.is_running = False

    def move_to_dir_syncv2(self, gdo, report=0):
        """
        Receive direction (gdo) --> Drive needle with motors synchronously
        1) Find A and B such that gdo.stepsout = (stepsx, stepsy) = A(motor_u) + B(motor_Z)
            (linear combination of 2 motor vectors to reach gdo.stepsout vector)
        2a) view the push option (corresponds with run_forward() method) ELSE do 2b)
        2b) view the pull option (corresponds with run_backward() method ELSE do *)
        *) return error in case both options do not work

        gdo = get direction output (an object of the class Output(direction, stepsout) )
        """

        # 1) if push available then find the steps for motorpush0 and motorpush1
        motor_matrix_push = []
        for n in self.dirpush[gdo.direction]:
            motor_matrix_push.append(self.motorvec[n])
        a = np.array(motor_matrix_push, dtype=int)
        b = np.array([int(gdo.stepsout[0]*self.sensitivity), int(gdo.stepsout[1]*self.sensitivity)], dtype=int)
        x = np.linalg.solve(a.transpose(), b)
        big_a = int(abs(x[0]))
        big_b = int(abs(x[1]))
        if report == 1:
            print("NEEDLE->move_syncV2: PUSH system of equations: \n"
                  "|     a = " + str(a.transpose()[0]) + "\n"
                  "|         " + str(a.transpose()[1]) + "\n"
                  "|     b = " + str(b) + "\n"
                  "|     [big_a, big_b] = " + str([big_a, big_b]) + "\n")

        motorpush0 = self.dirpush[gdo.direction][0]
        motorpush1 = self.dirpush[gdo.direction][1]
        if report == 1:
            print("|     motorpush0 = " + str(motorpush0) + " motorpush1 = " + str(motorpush1))

        # can we push? IF yes ==> then push ELSE continue to pull
        if self.motors[motorpush0].get_count() + abs(big_a) <= 400 and self.motors[motorpush1].get_count() + abs(big_b) <= 400:
            print("NEEDLE->move_syncV2: PUSH available, starting...")
            if big_b > big_a:
                if big_a == 0: # removing division by zero error
                    big_a = 1
                ratio = int(big_b/big_a)
                #print(" mod ratio = ", ratio)
                for i in range(big_a + big_b):
                    if i % (ratio+1) == 0 and i != 0:
                        #print("big_a at i = ", i)
                        self.motors[motorpush0].run_forward(1)
                    else:
                        self.motors[motorpush1].run_forward(1)
            else:
                if big_b == 0:
                    big_b = 1
                ratio = int(big_a/big_b)
                #print(" mod ratio = ", ratio)
                for i in range(big_a + big_b):
                    if i % (ratio+1) == 0 and i != 0:
                        #print("big_b at i = ", i)
                        self.motors[motorpush1].run_forward(1)
                    else:
                        self.motors[motorpush0].run_forward(1)
            # report final motor positions to user
            for motor_i in range(len(self.motors)):
                self.motors[motor_i].get_count(report=1)
            return 0

        print("\nNEEDLE->move_syncV2: PUSH not available, trying PULL")
        # 2) if pull available then find the steps for motorpull0 and motorpull1
        motor_matrix_pull = []
        for n in self.dirpull[gdo.direction]:
            motor_matrix_pull.append(self.motorvec[n])
        a = np.array(motor_matrix_pull, dtype=int)
        b = np.array([int(gdo.stepsout[0]*self.sensitivity), int(gdo.stepsout[1]*self.sensitivity)], dtype=int)
        x = np.linalg.solve(a.transpose(), b)
        big_a = int(abs(x[0]))
        big_b = int(abs(x[1]))
        if report == 1:
            print("NEEDLE->move_syncV2: PULL system of equations: \n"
                  "|     a = " + str(a.transpose()[0]) + "\n"
                  "|         " + str(a.transpose()[1]) + "\n"
                  "|     b = " + str(b) + "\n"
                  "|     [big_a, big_b] = " + str([big_a, big_b]) + "\n")

        motorpull0 = self.dirpull[gdo.direction][0]
        motorpull1 = self.dirpull[gdo.direction][1]
        if report == 1:
            print("|     motorpull0 = " + str(motorpull0) + " motorpull1 = " + str(motorpull1))

        # can we pull? IF yes ==> then pull ELSE report the movement requested is not possible
        if self.motors[motorpull0].get_count() - abs(big_a) >= 0 and self.motors[motorpull1].get_count() - abs(big_b) >= 0:
            print("NEEDLE->move_syncV2: PULL available, starting...")
            if big_b > big_a:
                if big_a == 0: # removing division by zero error
                    big_a = 1
                ratio = int(big_b/big_a)
                #print(" mod ratio = ", ratio)
                for i in range(big_a + big_b):
                    if i % (ratio+1) == 0 and i != 0:
                        #print("big_a at i = ", i)
                        self.motors[motorpull0].run_backward(1)
                    else:
                        self.motors[motorpull1].run_backward(1)
            else:
                if big_b == 0:
                    big_b = 1
                ratio = int(big_a/big_b)
                #print(" mod ratio = ", ratio)
                for i in range(big_a + big_b):
                    if i % (ratio+1) == 0 and i != 0:
                        #print("big_b at i = ", i)
                        self.motors[motorpull1].run_backward(1)
                    else:
                        self.motors[motorpull0].run_backward(1)
            # report final motor positions to user
            for motor_i in range(len(self.motors)):
                self.motors[motor_i].get_count(report=1)
            return 0
        else:
            logger.error("\n NEEDLE->move_syncV2: neither PUSH nor PULL available; no movement of needle occurred")


    def initial_position(self):
        """
        Send motors back to zero
        """
        self.festo_move(self.init_FESTO_pos, self.init_FESTO_speed)
        # TODO: consider disconnecting needle at this point (then clicking ENTER)
        currentpos = []
        for motor_i in range(len(self.motors)):
            position = self.motors[motor_i].get_count()
            currentpos = currentpos + [position]

        midpoint = int((max(currentpos) + min(currentpos))/2)
        print("Midpoint = ", midpoint)


        # return to midpoint individually
        print('\nNEEDLE->initial_position: starting to move to midpoint...  midpoint =', midpoint)
        for motor_i in range(len(self.motors)):
            if currentpos[motor_i] > midpoint:
                self.motors[motor_i].run_backward(currentpos[motor_i] - midpoint)
            else:
                self.motors[motor_i].run_forward(midpoint - currentpos[motor_i])

        # all return simultaneously to init_pos
        print('\nNEEDLE->initial_position: starting to move to zero...')
        # for _ in range(midpoint):
        nr_of_steps_to_init = midpoint - self.init_pos
        print("I am going to take nr_of_steps_to_init : ", nr_of_steps_to_init)
        for motor_i in range(len(self.motors)):
            self.motors[motor_i].run_backward(nr_of_steps_to_init)

        print("\nReady to receive input again")
        for motor_i in range(len(self.motors)):
            self.motors[motor_i].get_count(report=1)

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
        print('\nNEEDLE->move_to_dir_sync: Movement finished. Step count after movement : ')
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
