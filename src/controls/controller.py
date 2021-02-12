"""
Module to read inputs from Keyboard/Controller and convert the input to a direction
"""
# pylint: disable=no-member
from enum import Enum
import sys
import math
import os
import time
from queue import LifoQueue
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import src.util.logger as logger


class Direction(Enum):
    """
    Enumerator for the directions
    """
    NULL = -1
    up = 0
    upright = 1
    right = 2
    downright = 3
    down = 4
    downleft = 5
    left = 6
    upleft = 7
    init = 100
    festo_backward = 200
    festo_forward = 201

# pylint: disable=too-few-public-methods
class Output:
    """
    Class that encapsulates the result of a Controller press.
    A user input should have a direction, but it needs to incorporate how far it should move.
    Used in other files and referred to as Get Direction Output (GDO).
    """
    def __init__(self, direction, stepsout):
        self.direction = direction
        self.stepsx = stepsout[0]
        self.stepsy = stepsout[1]
        self.stepsout = stepsout

class Controller:
    """
    Class that encapsulates receiving inputs and returning directions.
    """
    def __init__(self) -> None:
        self.deadzone = 0.2
        self.diagonal_margin = 0.4
        self.joystick = None
        self.is_running = True
        self.get_input_method()

    def get_input_method(self) -> None:
        """
        Setup controls. Support for controllers and keyboard.
        """
        pygame.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            logger.success("Controller connected : " + self.joystick.get_name())
            logger.info(
                "While holding the left stick pointed towards a direction, press the A button to confirm your choice.\n")
        else:
            logger.info("A Keyboard is connected.")
            logger.info(
                "While pressing the arrowkeys to a desired direction, " +
                "press the Return (Enter) Key to confirm your choice.\n")

    def get_direction_from_pygame_events(self, input_feed, events):
        """
        Receives a list of PYGAME events, that will be analyzed and then an appropriate direction is added to a Queue.
        """
        pressed = pygame.key.get_pressed()

        for event in events:
            # End loop when escape is pressed
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.is_running = False
                input_feed.put(None) # Sentinel Value

            # Pygame ArrowKey Handler
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                up_arrow = pressed[pygame.K_UP]
                down_arrow = pressed[pygame.K_DOWN]
                left_arrow = pressed[pygame.K_LEFT]
                right_arrow = pressed[pygame.K_RIGHT]
                input_feed.put(Output(self.arrowkeys_to_dir(up_arrow, down_arrow, left_arrow, right_arrow), [100, 100]))
                time.sleep(0.1) # Make sure only one input is registered

            # Joystick controls
            if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                input_feed.put(self.analog_stick_to_dir(self.joystick.get_axis(0), self.joystick.get_axis(1) * -1))
            if event.type == pygame.JOYBUTTONDOWN and event.button == 1:
                input_feed.put(Output(100, [100, 100]))
            if event.type == pygame.JOYBUTTONDOWN and event.button == 4:
                input_feed.put(Output(200, [1, 1]))
            if event.type == pygame.JOYBUTTONDOWN and event.button == 5:
                input_feed.put(Output(201, [1, 1]))

    @staticmethod
    # pylint: disable=too-many-return-statements
    def arrowkeys_to_dir(up_arrow: bool, down_arrow: bool, left_arrow: bool, right_arrow: bool) -> int:
        """
        Function that converts arrowkey presses (at most 2 simultaneously) to a direction in range 0..7 including
        """
        if not up_arrow and not down_arrow and not left_arrow and not right_arrow:
            logger.error("Direction not clear --> No arrowkeys pressed. Try again.")
            return Direction.NULL.value

        if up_arrow:
            if left_arrow:
                return Direction.upleft.value
            if right_arrow:
                return Direction.upright.value
            return Direction.up.value
        if down_arrow:
            if left_arrow:
                return Direction.downleft.value
            if right_arrow:
                return Direction.downright.value
            return Direction.down.value
        if left_arrow:
            return Direction.left.value
        return Direction.right.value

    # pylint: disable=too-many-return-statements
    def analog_stick_to_dir(self, x_coord: float, y_coord: float):
        """
        Maps the (x, y) coordinate of the analog stick to 100 different amplitudes
        and 360 different angles (degrees) ;
        """
        abs_x = abs(x_coord)
        abs_y = abs(y_coord)

        # If the direction is not clear enough (stick not far away from center)
        distance_from_origin = math.sqrt(pow(abs_x, 2) + pow(abs_y, 2))
        # steps to do according to amplitude of the joystick

        if distance_from_origin < self.deadzone:
            logger.error("Direction not clear --> Analog stick not far away from center. Try again.")
            return Output(Direction.NULL.value, [0, 0])

        # xy_coords to steps to output per x or y motors
        x_steps = round(x_coord*100)
        y_steps = round(y_coord*100)
        stepsout = [x_steps, y_steps]

        if abs_y > abs_x:
            if y_coord > 0:
                print("CONTROLLER:      up direction cone, stepsout = ", stepsout)
                return Output(Direction.up.value, stepsout)
            if y_coord < 0:
                print("CONTROLLER:      down direction cone, stepsout = ", stepsout)
                return Output(Direction.down.value, stepsout)
        else:
            if x_coord > 0:
                print("CONTROLLER:      right direction cone, stepsout = ", stepsout)
                return Output(Direction.right.value, stepsout)
            if x_coord < 0:
                print("CONTROLLER:      left direction cone, stepsout = ", stepsout)
                return Output(Direction.left.value, stepsout)

    @classmethod
    def dir_to_text(cls, direction) -> str:
        """
        Converts a direction to a String representation of that direction.
        """
        return Direction(direction)
