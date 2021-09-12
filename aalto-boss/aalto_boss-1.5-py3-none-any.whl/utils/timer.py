import time


class Timer:
    """
    Utility class for wall clock time keeping.
    """

    def __init__(self):
        """
        Initializes the timer and starts counting time.
        """
        self.start = time.time()
        self.lapstart = self.start

    def startLap(self):
        """
        Starts counting lap time from zero.
        """
        self.lapstart = time.time()

    def getTotalTime(self):
        """
        Returns total time since timer creation in seconds.
        """
        return time.time() - self.start

    def getLapTime(self):
        """
        Returns lap time in seconds.
        """
        return time.time() - self.lapstart

    def str_totalTime(self, units="s"):
        """
        Returns total time since timer creation in the given unit of time
        as a string.
        """
        t = self.getTotalTime()
        returnString = ""
        if units == "s":
            returnString += "%12.3f" % (t)
        elif units == "m":
            returnString += "%12.3f" % (t / 60)
        elif units == "h":
            returnString += "%6.1f" % (t / 3600)
        elif units == "d":
            returnString += "%4.1f" % (t / (3600 * 24))
        return returnString

    def str_lapTime(self, units="s"):
        """
        Returns lap time in the given unit of time as a string.
        """
        t = self.getLapTime()
        returnString = ""
        if units == "s":
            returnString += "%12.3f" % (t)
        elif units == "m":
            returnString += "%12.3f" % (t / 60)
        elif units == "h":
            returnString += "%6.1f" % (t / 3600)
        elif units == "d":
            returnString += "%4.1f" % (t / (3600 * 24))
        return returnString
