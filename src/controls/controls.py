"""
Module to read inputs from Keyboard/Controller and convert the input to a direction
"""

from enum import Enum
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import keyboard
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import src.util.logger as logger


class Direction(Enum):
    """
    Enumerator for the directions
    """
    up = 0
    upright = 1
    right = 2
    downright = 3
    down = 4
    downleft = 5
    left = 6
    upleft = 7


class Controls:
    """
    Class that encapsulates receiving inputs and returning directions
    """

    def __init__(self):
        pygame.init()

        # Check if controller connected
        if pygame.joystick.get_count() > 0:
            print("found joystick")
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

    def get_direction(self):
        """
        Get direction from input
        """
        run = True
        while run:

            # Input recorded by keyboard module
            if keyboard.is_pressed('return'):
                up_arrow = keyboard.is_pressed('up')
                down_arrow = keyboard.is_pressed('down')
                left_arrow = keyboard.is_pressed('left')
                right_arrow = keyboard.is_pressed('right')
                return self.arrowkeys_to_dir(up_arrow, down_arrow, left_arrow, right_arrow)

            # Input recorded by pygame
            pressed = pygame.key.get_pressed()
            events = pygame.event.get()

            for event in events:
                # End loop when escape is pressed
                print(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    up_arrow = pressed[pygame.K_UP]
                    down_arrow = pressed[pygame.K_DOWN]
                    left_arrow = pressed[pygame.K_LEFT]
                    right_arrow = pressed[pygame.K_RIGHT]

                    return self.arrowkeys_to_dir(up_arrow, down_arrow, left_arrow, right_arrow)
               
                if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    print("Pressed the A button")
                    print("So print all controller events")
                    print(events)
                    return 0


    def arrowkeys_to_dir(self, up, down, left, right):
        if not up and not down and not left and not right:
            return None

        if up:
            if left:
                return Direction.upleft.value
            elif right:
                return Direction.upright.value
            else:
                return Direction.up.value
        if down:
            if left:
                return Direction.downleft.value
            elif right:
                return Direction.downright.value
            else:
                return Direction.down.value
        if left:
            return Direction.left.value
        if right:
            return Direction.right.value
