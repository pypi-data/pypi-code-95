import sys
import numpy as np
import signal
import time
import datetime
from toopazo_tools.file_folder import FileFolderTools as FFTools


class TelemetryLogger:
    def __init__(self, telemetry_folder, telemetry_iface, telemetry_ext):
        # assert isinstance(kdecanapi, KdeCanAPI)
        self.telemetry_iface = telemetry_iface

        # Test for the methods we need telemetry_api to have
        assert hasattr(self.telemetry_iface, 'close')
        assert hasattr(self.telemetry_iface, 'get_data')

        self.log_filename = None
        self.log_fd = None
        # log_141_2020-12-22-13-41-26.ulg
        self.log_filename_separator = '_'
        self.log_filename_logstr = 'log'
        self.log_filename_extension = telemetry_ext     # '.kdecan'

        # folder for logs
        self.log_folder = telemetry_folder
        self.logs_in_folder = None  # self.find_logs_in_folder()

        self.time0 = time.time()
        signal.signal(signal.SIGINT, self.signal_handler)

    def find_logs_in_folder(self):
        file_lognum_arr = []
        lognum_arr = []
        logdate_arr = []
        logname_arr = []

        farr = FFTools.get_file_arr(
            self.log_folder, extension=self.log_filename_extension)
        for file in farr:
            [head, tail] = FFTools.get_file_split(file)
            _ = head
            logname = tail
            res = self.parse_log_filename(logname)
            if res is not None:
                [logstr, lognum, logdate] = res
                _ = logstr
                file_lognum_arr.append(lognum)
                print('[find_logs_in_folder] lognum {}, logdate  {}, logname {}'
                      .format(lognum, logdate, logname))
                lognum_arr.append(lognum)
                logdate_arr.append(logdate)
                logname_arr.append(logname)

        logs_in_folder = {'folder': self.log_folder, 'lognum': lognum_arr,
                          'logdate': logdate_arr, 'logname': logname_arr}
        return logs_in_folder

    def parse_log_filename(self, filename):
        if self.log_filename_extension in filename:
            # log_141_2020-12-22-13-41-26.ulg
            filename = filename.replace(self.log_filename_extension, '')
            farr = filename.split(self.log_filename_separator)

            # print('[parse_log_filename] filename {}'.format(filename))
            # print('[parse_log_filename] farr {}'.format(farr))
            logstr = farr[0] == self.log_filename_logstr
            lognum = int(farr[1])
            logdate = datetime.datetime.strptime(farr[2], '%Y-%m-%d-%H-%M-%S')

            if len(farr) != 3:
                return None
            else:
                # print([logstr, lognum, logdate])
                return [logstr, lognum, logdate]
        else:
            return None

    def new_log_filename(self):
        self.logs_in_folder = self.find_logs_in_folder()
        if len(self.logs_in_folder['lognum']) > 0:
            prev_lognum = np.max(self.logs_in_folder['lognum'])
        else:
            prev_lognum = 0

        dtnow = datetime.datetime.now()
        logstr = self.log_filename_logstr
        lognum = str(prev_lognum + 1)
        logdate = dtnow.strftime("%Y-%m-%d-%H-%M-%S")

        separator = self.log_filename_separator
        extension = self.log_filename_extension
        fnarr = [
            logstr, separator, lognum, separator, logdate, extension
        ]
        log_filename = ''.join(fnarr)
        return log_filename

    def close_it_all(self):
        # Close file
        if self.log_fd is None:
            pass
        else:
            self.log_fd.close()

        # close can bus
        self.telemetry_iface.close()

    def signal_handler(self, _signal, _frame):
        print('[signal_handler] shutting down ..')
        print('[signal_handler] signal {}'.format(_signal))
        print('[signal_handler] frame  {}'.format(_frame))
        self.close_it_all()
        sys.exit(0)

    @staticmethod
    def busy_waiting(t0, period, dt):
        telap = time.time() - t0
        ncycles = int(telap / period)
        tf = ncycles*period + period
        # print("[busy_waiting] t0 %s" % t0)
        # print("[busy_waiting] tf %s" % tf)

        # Busy waiting while current time "ti" is less than final time "tf"
        telap = time.time() - t0
        while telap < tf:
            telap = time.time() - t0
            # print("[busy_waiting] telap %s" % telap)
            time.sleep(dt)

    def live_data(self, sampling_period, log_header):
        self.log_filename = self.new_log_filename()
        log_path = FFTools.full_path(self.log_folder + '/' + self.log_filename)
        self.log_fd = open(log_path, "w")
        print("[live_data] Creating log file {}".format(log_path))

        self.log_fd.write(log_header + "\r\n")
        while True:
            log_data = self.telemetry_iface.get_data()
            self.log_fd.write(log_data + "\r\n")
            TelemetryLogger.busy_waiting(
                self.time0, sampling_period, sampling_period / 8)

        # # Terminate, if out of while loop
        # self.close_it_all()
