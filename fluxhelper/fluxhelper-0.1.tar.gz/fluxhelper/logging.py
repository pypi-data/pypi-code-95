import ntpath
import random
import time
from inspect import getframeinfo, stack

from termcolor import colored


def stackInfo():
    caller = getframeinfo(stack()[3][0])
    return ntpath.basename(caller.filename), caller.lineno


LEVELS = {
    "debug": ["magenta"],
    "info": ["cyan"],
    "success": ["green"],
    "warning": ["yellow"],
    "error": ["red"],
    "critical": ["white", "on_red"]
}


class Logger:

    """
    Yes we create our own logging module for reasons (fun and probably might come in handy soon idfk)

    Usage:
    logging.debug("this is a debug")
    logging.info("this is a info")

    Yeah you get the rest
    """

    def __init__(self, file=None, debug=False):
        self.file = file
        self._debug = debug

    def debug(self, t, **kwargs):
        if self._debug:
            self.log(t, "debug", **kwargs)

    def info(self, t, **kwargs): self.log(t, "info", **kwargs)
    def success(self, t, **kwargs): self.log(t, "success", **kwargs)
    def warning(self, t, **kwargs): self.log(t, "warning", **kwargs)
    def error(self, t, **kwargs): self.log(t, "error", **kwargs)
    def critical(self, t, **kwargs): self.log(t, "critical", **kwargs)

    def log(self, t: str, level: str = "info", **kwargs):

        ret = kwargs.get("ret", False)
        delay = kwargs.get("delay", False)

        # Get stack data (filename and line number it was called from) and add that to the text
        st, stL = stackInfo()
        text = f"[{st}:{stL}] {t}"

        if self.file:
            # If a file is provided then append this text to that file (log it to file basically)
            with open(self.file, "a") as f:
                f.write(f"[{level.upper()}]{text}\n")

        # Now we print it yeah
        text = colored(text, *LEVELS[level])
        if ret:
            return text

        if delay:
            time.sleep(random.uniform(0.05, 0.1))

        print(text)


if __name__ == "__main__":
    logging = Logger("main.log", debug=True)

    logging.debug("hi there just passing by, don't mind me")
    logging.info("just passing by, might wanna mind me")
    logging.warning("hey just a warning sleep deprivation can be fatal")
    logging.error("uh oh breath no more")
    logging.critical("the dead")
    logging.success("Successfully killed yourself.")
