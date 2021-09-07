"""
* Some useful time operations.
* 
* @module time.js
* @author Ralf Mosshammer <bifrost.at@siemens.com>
* @copyright Siemens AG, 2020
* Python implementation
* @author Manuel Matzinger <manuel.matzinger@siemens.com>
"""
import datetime
from datetime import timezone
class bifrostTime:
    unitInMs = {
        'ms' : 1,
        's'   : 1000,
        'm'   : 60 * 1000,
        'h'   : 60 * 60 * 1000,
        'd'   : 24 * 60 * 60 * 1000,
        'w'   : 7 * 24 * 60 * 60 * 1000,
        'M'   : 30 * 24 * 60 * 60 * 1000,
        'y'   : 365 * 24 * 60 * 60 * 1000
    }
    def msToTime(ms):
        timeObject = datetime.fromtimestamp(ms/1000.0)
        timeString = timeObject.strftime("%X")
        return timeString

    def utcString():
        timeObject = datetime.now(timezone.utc)
        UTCString = timeObject.strftime("%a %d %b %Y %X %Z")
        return UTCString

    # def durationStringToMs(str):
    #     return 1