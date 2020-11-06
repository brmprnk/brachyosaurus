"""
This file creates string representing arguments entered in the command line.
And prints them.
"""
import argparse
import src.util.logger as logger

def input_log(parser: argparse.Namespace) -> None:
    """
    General information, extra arguments and paths... Assemble.
    :param parser:   argparse.Namespace  The parser containing all program arguments.
    :return: None
    """
    if parser.subparse is None:
        return
    result = "\n"
    result += general_information(parser)
    result += extra_arguments(parser)
    logger.info(result.replace("\\", "/"))


def general_information(parser: argparse.Namespace) -> str:
    """
    Creates an input log string for the start of the program.
    :param parser:  argparse.Namespace  The parser with program arguments.
    :return:        str    ()             General information represented as a string.
    """
    # FESTO.
    if parser.subparse == "FESTO":
        result = "Running FESTO -> Solely controlling the FESTO Linear Stage"

    # NEEDLE
    elif parser.subparse == "NEEDLE":
        result = "Running NEEDLE -> Solely controlling the moving needle"
        if parser.init:
            result += "\n The init module is called. Resetting all motors to their start positions..."
 
    # FESTO & NEEDLE
    else:
        result = ""

    return result



def extra_arguments(parser: argparse.Namespace) -> str:
    """
    Return extra arguments given via the command line as a string.
    :param parser:  argparse.Namespace  The parser containing all program arguments.
    :return:        str                 Extra arguments represented as a string.
    """
    # FESTO
    if parser.subparse == "FESTO":
        result = ""
        if parser.targetpos:
            result += "\nThe desired position of the linear stage : " + parser.targetpos

        if parser.initpos:
            result += "\nThe initial position of the linear stage : " + parser.initpos

        if parser.speed:
            result += "\nMoving the linear stage at a speed of : " + parser.speed

        return "\n" + result

    # NEEDLE
    elif parser.subparse == "NEEDLE":
        result = ""
        result += "\nConnecting to Arduino Board at COM port : " + parser.comport

        if parser.startsteps:
            result += "\nThe amount of steps (max 200) performed forwards after the Crouzets are INIT at zero : " + parser.startsteps

        return "\n" + result

    # FESTO & NEEDLE
    else:
        result = ""

    return "\n" + result
