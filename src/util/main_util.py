"""
This file creates string representing arguments entered in the command line.
And prints them.
"""
import argparse
from src.util.logger import info

def input_log(parser: argparse.Namespace) -> None:
    """
    General information, extra arguments and paths... Assemble.
    :param parser:   argparse.Namespace  The parser containing all program arguments.
    :return: None
    """
    result = "\n"
    result += general_information(parser)
    result += extra_arguments(parser)
    info(result.replace("\\", "/"))


def general_information(parser: argparse.Namespace) -> str:
    """
    Creates an input log string for the start of the program.
    :param parser:  argparse.Namespace  The parser with program arguments.
    :return:        str                 General information represented as a string.
    """
    # TVLA.
    result = "\n"
    if parser.subparse == "FESTO":
        result += "Running Linear Stage Control Module..."

	# Add new subparsers or extra inputs (speed, initLoc) here

    return result


def extra_arguments(parser: argparse.Namespace) -> str:
    """
    Return extra arguments given via the command line as a string.
    :param parser:  argparse.Namespace  The parser containing all program arguments.
    :return:        str                 Extra arguments represented as a string.
    """

    result = "\n"
    # if parser.position:
    #     result += "FESTO Initial Position = " +str(parser.position)

    return result
