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
import threading

# sys.path.append is used to import local modules from the project.
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.util import input_processing
from src.util import logger
# from src.util.saving import Saving
import src.needle as needle
from src.reset_arduino import func as reset_arduino
from src.image_proc2 import position_from_image
# TODO: import configparser and use it to update parameters

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
    for thread in threading.enumerate():
        print("Thread running on shutdown: ", thread.name)
    sys.exit(sig)


# Defines which handler to be called on a SIGINT (KeyboardInterrupt) event
signal.signal(signal.SIGINT, async_event_handler)

# Create the parser object
PARSER = argparse.ArgumentParser(prog="brachy.py", description="Program to control needle and linear stage movement")
SUBPARSERS = PARSER.add_subparsers(dest="subparse")
PARSER_FESTO = SUBPARSERS.add_parser("FESTO", help="Control the FESTO linear stage")
PARSER_NEEDLE = SUBPARSERS.add_parser("NEEDLE", help="Control the movement of the needle")
PARSER_POSITION = SUBPARSERS.add_parser("POSITION", help="Gain feedback on the position of the needle")
PARSER_IMAGEPROC = SUBPARSERS.add_parser("IMAGEPROC", help="Test the image processing performance")

# Arguments for main module (Needle and Camera's)
PARSER.add_argument("-init", action="store_true", help="Initializes Crouzet Stepper Motor positions.")
PARSER.add_argument("-manual", action="store_true", default=True,
                    help="Determines control mode. Automatic is the default.")
PARSER.add_argument("--comport", type=str, default="COM5", action="store",
                    help="The comport on which the Arduino is connected")
PARSER.add_argument("--startsteps", type=str, default="200", action="store",
                    help="The amount of steps (max 200) performed forwards after the Crouzets are INIT at zero ")
PARSER.add_argument("--sensitivity", type=str, default="0.1", action="store",
                    help="The sensitivity of the needle controls (between 0 and 1) ")
PARSER.add_argument("--fps", action="store", type=int, default=1,
                    help="The number of times (per second) the module should check for its position using camera's")
PARSER.add_argument("--camtop", action="store", type=str, default="https://192.168.43.1:8080/video",
                    help="The URL or path to the (live) video of the camera positioned above the needle")
PARSER.add_argument("--camfront", action="store", type=str, default="",
                    help="The URL or path to the (live) video of the camera positioned in front of the needle")
PARSER.add_argument("-nofeed", action="store_true", help="Should the camera feed be displayed on screen")

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
PARSER_NEEDLE.add_argument("--sensitivity", type=str, default="0.1", action="store",
                           help="The sensitivity of the needle controls (between 0 and 1) ")

# Parser for the IMAGEPROC command with all the options
PARSER_IMAGEPROC.add_argument("--configpath", type=str, default="config.ini", action="store",
                           help="The path to the config file")
PARSER_IMAGEPROC.add_argument("--imagepath", type=str, default="image_pos/photos/bending2.jpg", action="store",
                           help="The path to the config file")
PARSER_IMAGEPROC.add_argument("--filtering", type=str, default="no", action="store",
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
    elif subparser == "NEEDLE":
        needle_movement(parser)
    elif subparser == "IMAGEPROC":
        image_proc(parser)
    else:
        if len(sys.argv) <= 1: # No optional arguments given --> print help
            PARSER.print_help()
        else:
            brachy_therapy(parser)

def brachy_therapy(args: argparse.Namespace) -> None:
    """
    Handler for positional feedback using image acquisition & processing
    """
    if args.init:
        reset_arduino(args.comport, args.startsteps)
    else:
        logger.success("Starting Brachy Therapy.\n")

        # Create Needle object
        board_controller = needle.Needle(args.comport, args.startsteps, args.sensitivity)
        # Call its movement function
        if args.manual:
            logger.info("Input type is MANUAL.")
            board_controller.manual_brachy_therapy(args)
        else:
            logger.info("Automated Control. Computer will output its predicted trajectory.")
            board_controller.automated_brachy_therapy(args)

def needle_movement(args: argparse.Namespace) -> None:
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


def image_proc(args: argparse.Namespace) -> None:
    """"
    Handler for testing image processing
    useful for testing new functions on a single image
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
