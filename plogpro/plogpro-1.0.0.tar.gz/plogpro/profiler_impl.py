from .profiler  import *

from os         import SEEK_SET
from threading  import get_ident


class TracingProfiler(Profiler):
    """A profiler that outputs a JSON file that can be read by Chrome Tracing

    The results will be stored in a JSON file. The contents of this file, i.e.
    the profiling results, can be visualized using Chrome Tracing. To open
    Chrome Tracing, open a window in Google Chrome and type ``chrome://tracing``
    in the address bar.

    Arguments:
        fname (str)
            The name of the file in which the results will be written
    """

    def __init__(self, fname):
        self.fname = fname
        super().__init__()

    def setup(self):
        self.file = open(self.fname, 'w+')
        self.file.write("{\"otherData\":{},\"traceEvents\":[")
        self.file.flush()

    def teardown(self):
        # Check if last character is a comma and overwrite it if so
        self.file.seek(self.file.tell() - 1, SEEK_SET)
        if self.file.read() == ',':
            # calling self.file.read() puts the cursor back at the end of the
            # file, so we need to go there again to overwrite the trailing comma
            self.file.seek(self.file.tell() - 1, SEEK_SET)
        self.file.write("]}")
        self.file.close()

    def write(self, name, start_time, end_time):
        start_time *= 1e6  # Convert time to microseconds
        end_time   *= 1e6
        output_string = "{\"cat\":\"function\",\"ph\":\"X\","
        output_string += "\"name\":\"{:s}\",".format(name)
        output_string += "\"ts\":{:f},\"dur\":{:f},".format(start_time, end_time - start_time)
        output_string += "\"pid\":0,\"tid\":{:d}}},".format(get_ident())
        self.file.write(output_string)
        self.file.flush()
