"""
Module to read inputs from Keyboard/Controller and convert the input to a direction
"""

from enum import Enum
import sys
import os
import pygame
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
        self.dir_map = {
            Direction.up : [2, 3],
            Direction.right : [0, 2],
            Direction.down : [0, 1],
            Direction.left : [1, 3]
        }

    def get_direction(self):
        """
        Get direction from input
        """
        pygame.init()

        # Check if controller connected
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

        run = True
        while run:
            # Keep track of all pressed keyboard keys
            pressed = pygame.key.get_pressed()

            events = pygame.event.get()

            for event in events:
                # End loop when escape is pressed
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    print(events)
                    up = pressed[pygame.K_UP]
                    down = pressed[pygame.K_DOWN]
                    left = pressed[pygame.K_LEFT]
                    right = pressed[pygame.K_RIGHT]

                    print(up, down, left, right)

                    # Always go up for testing purposes
                    return 0
               
                if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                    print("Pressed the A button")
                    print("So print all controller events")
                    print(events)
                    return 0
    

        





