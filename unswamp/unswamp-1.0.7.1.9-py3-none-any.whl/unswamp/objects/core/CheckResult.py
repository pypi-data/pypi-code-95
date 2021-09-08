import os
from datetime import datetime
from unswamp.objects.base.DatetimeHandler import DatetimeHandler


class CheckResult:
    ##################################################################################################
    # Constructor
    ##################################################################################################
    def __init__(self, check, start, end, passed, message):
        self.check = check
        self.start = start
        self.end = end
        self.passed = passed
        self.message = message

    ##################################################################################################
    # Overrides
    ##################################################################################################
    def __str__(self):
        obj = "#" * 50 + os.linesep
        obj += f"# {self.check.id}{os.linesep}"
        obj += "#" * 50 + os.linesep
        obj += f"- passed: '{self.passed}'{os.linesep}"
        obj += f"- message: '{self.message}'{os.linesep}"
        obj += "#" * 50 + os.linesep
        obj += f"- check: '{self.check}'{os.linesep}"
        obj += f"- start: '{self.start}'{os.linesep}"
        obj += f"- end: '{self.end}'{os.linesep}"
        obj += f"- duration: '{self.duration}'{os.linesep}"
        obj += os.linesep
        return obj

    ##################################################################################################
    # Properties
    ##################################################################################################
    check = None
    passed = False
    message = None
    start = datetime.min
    end = datetime.min
    duration = 0
