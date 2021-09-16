import re
import math


__ALL__ = ["mask"]


def mask(string: str, coverage: float = 0.5):
    if re.search(r"^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$", string):
        string = string.split("@")
        masked = mask(string[0])+"@"+string[1]
    else:
        masked = ""
        length = len(string)
        for i in range(0, math.ceil(length*coverage)):
            masked += string[i]
        for i in range(math.ceil(length*coverage)+1, length+1):
            masked += "*"
    return masked


