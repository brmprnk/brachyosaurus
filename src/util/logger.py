"""
This file contains functions for all our output of our program
"""
import os
import sys
import datetime as dt

LOG_PATH = "output/log.txt"

def info(message: str) -> None:
    """
    This functions is used for all output that is used as info.
    This prints in white
    :param message: The info message to be printed
    :return: None
    """
    print(message)

    write_to_log(message)


def error(message: str) -> None:
    """
    This functions is used for all output that is used as error message.
    This prints in red
    :param message: The error message to be printed
    :return: None
    """
    if "win32" in sys.platform.lower():
        print(message)
    else:
        print("\033[1;31mERROR: %s\033[0;0m" % message)

    write_to_log(message)


def request_input(message: str) -> str:
    """
    This function is used for all input required for the program.
    :param message: The message to print before input
    :return: A string of the user's inout
    """
    if "win32" in sys.platform.lower():
        input_res = input(message)
    else:
        input_res = input("\033[0;0m%s" % message)

    write_to_log(("{0} {1}".format(message, input_res)))

    return input_res


def write_to_log(message: str) -> None:
    """
    This functions write all output to a log file
    :param message:
    :return:
    """
    # Get path of /src folder
    src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Parent of /src folder is project folder
    project_path = os.path.dirname(src_path)

    # Get the path of output file
    path = os.path.join(project_path, LOG_PATH)

    file = open(path, "w")
    file.write(str(dt.datetime.now().replace(microsecond=0)) + ": " + message + "\n")
    file.close()
