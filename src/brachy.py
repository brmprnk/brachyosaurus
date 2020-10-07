"""
The main file for the Brachyosaurus project.
The arguments entered into the Command-Line Interface (CLI) are parsed here,
and based on those arguments the required functionalities are called.

Authors:
    Florens Helfferich       F.J.Helfferich@student.tudelft.nl
    Bram Pronk               I.B.Pronk@student.tudelft.nl
"""
import argparse
import os
import signal
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from src.util import main_util
from src.util import logger
import lin_move

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

# Set FESTO Parser options
PARSER_FESTO.add_argument("--targetpos", type=int, default=0, action="store",
                          help="Set the desired position of the linear stage (mm)")
PARSER_FESTO.add_argument("--initpos", type=int, default=0, action="store",
                          help="Set the initial position of the linear stage (mm)")
PARSER_FESTO.add_argument("--speed", type=float, default=0.2, action="store",
                          help="Set the speed of movement (V)")


def main() -> None:
    """
    Parse input and call appropriate function

    :return: None
    """
    parser = PARSER.parse_args()
    main_util.input_log(parser)

    subparser = parser.subparse

    if subparser == "FESTO":
        linear_stage(parser)
    else:
        brachy_therapy(parser)

def brachy_therapy(args: argparse.Namespace) -> None:
    """
    Handler for main purpose of program
    """

def linear_stage(args: argparse.Namespace) -> None:
    """
    Handler for controlling the linear stage
    """
    lin_move.move_to_pos(args.initpos, args.targetpos, args.speed)

if __name__ == '__main__':
    main()
