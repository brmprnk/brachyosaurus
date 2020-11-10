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
import reset_arduino

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
PARSER_NEEDLE.add_argument("--startsteps", type=str, default="100", action="store",
                           help="The amount of steps (max 200) performed forwards after the Crouzets are INIT at zero ")
PARSER_NEEDLE.add_argument("--sensitivity", type=str, default="1", action="store",
                           help="The sensitivity of the needle controls (between 0 and 1) ")


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
    else:
        PARSER.print_help()


def brachy_therapy(args: argparse.Namespace) -> None:
    """
    Handler for main purpose of program
    """
    if args.init:
        reset_arduino.func(args.comport, args.startsteps)
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

if __name__ == '__main__':
    main()
