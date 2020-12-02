"""
The main file for the Brachyosaurus project.
The arguments entered into the Command-Line Interface (CLI) are parsed here,
and based on those arguments the required functionalities are called.

Adding functionalities is as easy as adding a small parser using the argparse library,
and creating a function here that calls the functionalities. We've tried to keep as much of the
logic outside this file, only setup functions are required.

Authors:
    Florens Helfferich       F.J.Helfferich@student.tudelft.nl
    Bram Pronk               I.B.Pronk@student.tudelft.nl
"""
import argparse
import os
import sys
import signal

# sys.path.append is used to import local modules from the project.
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.util import input_processing
from src.util import logger
# from src.util.saving import Saving
import src.needle as needle
from src.reset_arduino import func as reset_arduino
from src.image_proc2 import position_from_image

# pylint: disable=unused-argument
# Disable unused argument because the SIGINT event handler always takes two parameters, but for the
# purposes of our program we are not interested in showing the stack frame of the interrupt,
# the goal is to gracefully exit the program without a stack trace.
def async_event_handler(sig: int, frame: object) -> None:
    """
    A Handler function for asynchronous KeyboardInterrupt events (SIGINT).
    From the Python docs:
    The handler is called with two arguments:
    :param sig:   int          The signal number
    :param frame: frame object The current stack frame

    :return: None
    """
    logger.error("\nInterrupted program execution...")
    sys.exit(sig)


# Defines which handler to be called on a SIGINT (KeyboardInterrupt) event
signal.signal(signal.SIGINT, async_event_handler)

# Create the parser object
PARSER = argparse.ArgumentParser(prog="brachy.py", description="Program to control needle and linear stage movement")
SUBPARSERS = PARSER.add_subparsers(dest="subparse")
PARSER_FESTO = SUBPARSERS.add_parser("FESTO", help="Control the FESTO linear stage")
PARSER_NEEDLE = SUBPARSERS.add_parser("NEEDLE", help="Control the movement of the needle")
PARSER_IMAGEPOS = SUBPARSERS.add_parser("IMAGEPOS", help="Control the camera and image processing")

# Parser for the FESTO command with all the options
PARSER_FESTO.add_argument("--targetpos", type=int, default=0, action="store",
                          help="Set the desired position of the linear stage (mm)")
PARSER_FESTO.add_argument("--initpos", type=int, default=0, action="store",
                          help="Set the initial position of the linear stage (mm)")
PARSER_FESTO.add_argument("--speed", type=float, default=0.2, action="store",
                          help="Set the speed of movement (V)")

# Parser for the NEEDLE command with all the options
PARSER_NEEDLE.add_argument("-init", action="store_true", help= "INITs Crouzet positions")
PARSER_NEEDLE.add_argument("--comport", type=str, default="COM5", action="store",
                           help="The comport on which the Arduino is connected")
PARSER_NEEDLE.add_argument("--startsteps", type=str, default="200", action="store",
                           help="The amount of steps (max 400) performed forwards after the Crouzets are INIT at zero ")
PARSER_NEEDLE.add_argument("--sensitivity", type=str, default="1", action="store",
                           help="The sensitivity of the needle controls (between 0 and 1) ")

# Parser for the IMAGEPOS command with all the options
PARSER_IMAGEPOS.add_argument("--configpath", type=str, default="config.ini", action="store",
                           help="The path to the config file")
PARSER_IMAGEPOS.add_argument("--imagepath", type=str, default="image_pos/photos/bending2.jpg", action="store",
                           help="The path to the config file")
PARSER_IMAGEPOS.add_argument("--filtering", type=str, default="no", action="store",
                           help="Use a 3x3 low-pass filter before edge processing")


def main() -> None:
    """
    The start of the program. This function determines from user input which function handlerit should call.

    :return: None
    """
    # Print all the user's entered arguments in a neatly organized fashion
    parser = PARSER.parse_args()
    input_processing.input_log(parser)

    subparser = parser.subparse

    if subparser == "FESTO":
        linear_stage(parser)
    if subparser == "NEEDLE":
        brachy_therapy(parser)
    if subparser == "IMAGEPOS":
        image_pos(parser)
    else:
        PARSER.print_help()


def brachy_therapy(args: argparse.Namespace) -> None:
    """
    Handler for main purpose of program
    """
    if args.init:
        reset_arduino(args.comport, args.startsteps)
    else:
        # Create Needle object
        board_controller = needle.Needle(args.comport, args.startsteps, args.sensitivity)
        # Call its movement function
        board_controller.move_freely()


def linear_stage(args: argparse.Namespace) -> None:
    """
    Handler for controlling the linear stage
    """
    # lin_move.move_to_pos(args.initpos, args.targetpos, args.speed)


def image_pos(args: argparse.Namespace) -> None:
    """"
    Handler for the camera and image processing
    useful for checking position feedback module
    """
    tip_position, tip_ori = position_from_image(args.imagepath, args.configpath, filtering=args.filtering, show='yes')
    print("brachy.py: tip_position is: ", tip_position)
    print("brachy.py: tip orientation is: ", tip_ori)

    # TODO suggested route manager and movement recommendation code:
    # waypoints2D = some function
    # route_on_image(args.imagepath, waypoints2D)
    # route_check(args.imagepath, tip_pos, tip_ori)  gives a recommendation to move


if __name__ == '__main__':
    main()
