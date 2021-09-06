import sys
import subprocess


def commandline_exec(lst):
    """
    Executes an external program.

    Executes a program given as a list with the executable name 
    followed by the command line arguments. The external program's
    standard output and standard error will be captured and returned.

    Args:
        lst: A list with the name of the executable that needs to be called, 
          followed by its command line arguments.

    Returns:
        A tuple consisting of the return code, the standard output, and the standard error output
        of the executed program.         
    """

    proc = subprocess.Popen(lst, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    encoding = sys.stdout.encoding
    return proc.returncode, out.decode(encoding), err.decode(encoding)
