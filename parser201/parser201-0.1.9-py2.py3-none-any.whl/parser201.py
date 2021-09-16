"""Main module."""

# Author: Peter Nardi
# Date: 09/15/20
# License: MIT (terms at the end of this file)

# Title: parser201 - Apache Log Parser

# imports

# Heavy use of regular expressions
import re


class LogParser:
    """
    Creates an object using a line from an Apache log file.

    .. automethod:: __init__
    .. automethod:: __str__
    """

    # ---------------------------------------------------------------------

    def __init__(self, line):
        """
        LogParser Class initializer

        Returns an object with the properties set as described below. In the
        event a line from a log file cannot be parsed (for example, is
        corrupted), then the object returned from the initializer will have all
        properties set to ``None``.

        :param line: A single line from an Apache log file.
        :type line: str
        """

        # Initial check. If the line passed to the initializer is not a string
        # (type == str), then return an empty LogParser object.

        if type(line) != str:
            self.__noneFields()
            return

        # If a valid string is entered, then perform pre-processing. For some
        # lines, an empty field is represented as two quotes back-to-back, like
        # this: "". The regex to pull out agent strings between quotes will
        # incorrectly ignore that field, rather than returning an empty string.
        # Replace "" with "-" to prevent that.

        clean = line.replace('\"\"', '\"-\"')

        # agentStrings: This part of the regex:(?<!\\)\" is a negative
        # lookbehind assertion. It says, "end with a quote mark, unless that
        # quote mark is preceded by an escape character '\'"

        agentStrings = re.findall(r'\"(.+?)(?<!\\)\"', clean)

        # The next one's tricky. We're looking to extract the statuscode and
        # datasize fields. For some entires, the datasize field is '-', but for
        # all entries the returncode field is a reliable integer. If we split
        # the log line on space, then the first purely isnumeric() item in the
        # resulting list should be the returncode. If we capture the index of
        # that code, and take that code and the one next to it from the list,
        # we should have both fields. If the fields are valid integers, then
        # cast to them int; else set them to 0. If any of this fails, then
        # consider that we have a malformed log line and set all the properties
        # to None.

        try:
            L = clean.split(' ')
            i = [j for j in range(len(L)) if L[j].isnumeric()][0]
            codeAndSize = [int(n) if n.isnumeric() else 0 for n in L[i:i+2]]
            # Splitting on '[' returns a list where item [0] contains the first
            # three fields (ipaddress; userid; username), each separated by
            # space.
            first3 = clean.split('[')[0].split()
        except Exception as e:
            print(str(e))
            self.__noneFields()
            return

        # Set properties. If any of these fail, then consider that we have a
        # malformed log line and set all the properties to None.

        try:
            self.__ipaddress = first3[0]
            self.__userid = first3[1]
            self.__username = first3[2]
            self.__timestamp = re.search(
                r'\[(.+?)\]', clean).group().strip('[]')
            self.__requestline = agentStrings[0]
            self.__referrer = agentStrings[1]
            self.__useragent = agentStrings[2]
            self.__statuscode = codeAndSize[0]
            self.__datasize = codeAndSize[1]
        except Exception as e:
            print(str(e))
            self.__noneFields()

        return

    # ---------------------------------------------------------------------

    # Method to set every field to None, in the event of a corrupted log line.

    def __noneFields(self):

        self.__ipaddress = None
        self.__userid = None
        self.__username = None
        self.__timestamp = None
        self.__requestline = None
        self.__statuscode = None
        self.__datasize = None
        self.__useragent = None
        self.__referrer = None

        return

    # ---------------------------------------------------------------------

    # Method for string rendering of a LogParser object

    def __str__(self):
        """
        Returns a string representation of a LogParser object. An example looks
        like this:

        .. code-block:: console

             ipaddress: 81.48.51.130
                userid: -
              username: -
             timestamp: 24/Mar/2009:18:07:16 +0100
           requestline: GET /images/puce.gif HTTP/1.1
            statuscode: 304
              datasize: 2454
               referer: -
             useragent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1;
             GTB5; .NET CLR 1.1.4322)
        """
        labels = ['ipaddress', 'userid',
                  'username', 'timestamp', 'requestline']
        labels += ['statuscode', 'datasize', 'referrer', 'useragent']
        padding = len(max(labels, key=len))
        fmtStr = '{0:>' + str(padding) + 's}: {1}'
        L = []

        L.append(fmtStr.format(labels[0], self.__ipaddress))
        L.append(fmtStr.format(labels[1], self.__userid))
        L.append(fmtStr.format(labels[2], self.__username))
        L.append(fmtStr.format(labels[3], self.__timestamp))
        L.append(fmtStr.format(labels[4], self.__requestline))
        L.append(fmtStr.format(labels[5], self.__statuscode))
        L.append(fmtStr.format(labels[6], self.__datasize))
        L.append(fmtStr.format(labels[7], self.__referrer))
        L.append(fmtStr.format(labels[8], self.__useragent))

        return '\n'.join(L)

    # ---------------------------------------------------------------------

    # Setters and Getters. Might need to perform input validation at some point
    # in the future.

    # -------------------------------
    # ipaddress property

    @property
    def ipaddress(self):
        """
        The remote host (the client IP)

        :type: str
        """
        return self.__ipaddress

    @ipaddress.setter
    def ipaddress(self, value):
        self.__ipaddress = value

    # -------------------------------
    # userid property

    @property
    def userid(self):
        """
        The identity of the user determined by ``identd`` (not usually used
        since not reliable). If ``identd`` is not present,
        :attr:`.LogParser.userid` == ``"-"``

        :type: str
        """
        return self.__userid

    @userid.setter
    def userid(self, value):
        self.__userid = value

    # -------------------------------
    # username property

    @property
    def username(self):
        """
        The user name determined by HTTP authentication. If no username is
        present, :attr:`.LogParser.username` == ``"-"``

        :type: str
        """
        return self.__username

    @username.setter
    def username(self, value):
        self.__username = value

    # -------------------------------
    # timestamp property

    @property
    def timestamp(self):
        """
        The time the request was received, in the following format:

        [dd/MMM/YYYY:HH:MM:SS –hhmm]

        NOTE: ``-hhmm`` is the time offset from Greenwich Mean Time (GMT).
        Usually (but not always) ``mm == 00``. Negative offsets (``-hhmm``) are
        West of Greenwich; positive offsets (``+hhmm``) are East of Greenwich.
        The date/time component has a guaranteed length of 28 characters (which
        includes the leading and training brackets). Every other component of a
        log entry is variable length.

        :type: str
        """
        return self.__timestamp

    @timestamp.setter
    def timestamp(self, value):
        self.__timestamp = value

    # -------------------------------
    # requestline property

    @property
    def requestline(self):
        """
        The request line from the client. (e.g. ``"GET / HTTP/1.0"``)

        :type: str
        """
        return self.__requestline

    @requestline.setter
    def requestline(self, value):
        self.__requestline = value

    # -------------------------------
    # statuscode property

    @property
    def statuscode(self):
        """
        The status code sent from the server to the client (``200``, ``404``,
        etc.)

        :type: int
        """
        return self.__statuscode

    @statuscode.setter
    def statuscode(self, value):
        self.__statuscode = value

    # -------------------------------
    # datasize property

    @property
    def datasize(self):
        """
        The size of the response to the client (in bytes)

        :type: int
        """
        return self.__datasize

    @datasize.setter
    def datasize(self, value):
        self.__datasize = value

    # -------------------------------
    # referrer property

    @property
    def referrer(self):
        """
        The Referrer header of the HTTP request (containing the URL of the page
        from which this request was initiated) if any is present, and ``"-"``
        otherwise.

        :type: str
        """
        return self.__referrer

    @referrer.setter
    def referrer(self, value):
        self.__referrer = value

    # -------------------------------
    # useragent property

    @property
    def useragent(self):
        """
        The browser identification string if any is present, and ``"-"``
        otherwise.

        :type: str
        """
        return self.__useragent

    @useragent.setter
    def useragent(self, value):
        self.__useragent = value

# ---------------------------------------------------------------------


if __name__ == '__main__':
    pass

# ---------------------------------------------------------------------

# MIT License
#
# Copyright (c) 2020 Peter Nardi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions: # The above
# copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
