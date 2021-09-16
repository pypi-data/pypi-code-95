"""PyProjectUpVers

Copyright (c) 2021 - GitLab
"""

from sys import stderr
from subprocess import check_output
from os.path import dirname
from inspect import getfile

def run_cmd(command, split=" "):
    """
        Wrapper function to call a shell command

        :param: command (str): shell command to run
        :return: UTF-8 decoded string
    """
    return (check_output(command.split(split))).decode("UTF-8")
    
def newline_to_list(s):
    """
        Splits apart run_cmd output string to a list of values
    """
    return [x.strip("'\"") for x in filter(None, reversed(s.split("\n")))]

def get_install_dir(o):
    """
        Get install location of this library
    """
    return dirname(getfile(o))

def eprint(*args, **kwargs):
    """
        Prints message to stderr
    """
    print(*args, file=stderr, **kwargs)
