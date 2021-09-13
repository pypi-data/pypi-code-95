import os
import time
import six

from astropy.io import ascii
from astropy.io import fits
from astropy.time import Time
from twisted.logger import Logger

from ..utils.obsmodes import Idle, get_obsmode
from ..devices.ngc import (NGCDevice, NGCEmulator)
from ..machines import create_machine


class NGC(object):
    """
    Model for an ESO NGC controller
    """
    log = Logger()

    settable_attributes = ()
    extra_rpc_calls = ('start', 'stop', 'abort', 'pon', 'poff',
                       'seq_start', 'seq_stop', 'trigger', 'reset',
                       'summary', 'status', 'setup',
                       'online', 'standby', 'offline', 'exit',
                       'start_ngc_server', 'stop_ngc_server', 'setup_ngc_server',
                       'load_setup', 'add_hdu', 'cmd')

    def __init__(self, emulate=True):
        if emulate:
            self._dev = NGCEmulator()
        else:
            self._dev = NGCDevice()

        # NGC already has it's own state machine, so don't duplicate here
        self.machines = {}

    def online(self):
        """
        Moves NGC server into ONLINE state.

        When moving to this state the h/w is connected and the controller reset.
        """
        return self.cmd('online')

    def exit(self):
        """
        Shuts down NGC server.

        Once in this state it is impossible to talk to NGC server and it must be started
        using `NGC.start_ngc_server`
        """
        return self.cmd('exit')

    def offline(self):
        """
        Turns NGC server off, moving it into LOADED state.

        In this state, the server is running and you can communicate with it, but all sub-processes
        (e.g acquisition task) are shut down and hardware is disconnected.
        """
        return self.cmd('off')

    def standby(self):
        """
        Move NGC server to STANDBY state.

        In this state, the server is not connected to the hardware, but the sub-processes 
        (e.g acquisition task) are enabled.
        """
        return self.cmd('standby')

    def stop_ngc_server(self):
        """
        Shuts down ESO NGC Server
        """
        try:
            output = self._dev.stop_ngc_sw()
        except Exception as e:
            self.log.error('could not start NGC software: ' + str(e))
            return False

        for key in output:
            msg = output[key]
            self.log.info("cmd {}: {}".format(key, msg))
        return True

    def start_ngc_server(self):
        """
        Run commands necessary to bring up the ESO NGC server
        """
        try:
            output = self._dev.start_ngc_sw()
        except Exception as e:
            self.log.error('could not start NGC software: ' + str(e))
            return False

        for key in output:
            msg = output[key]
            self.log.info("cmd {}: {}".format(key, msg))
        return True

    def setup_ngc_server(self):
        """
        Load HiPERCAM specific settings
        """
        try:
            output = self._dev.setup_ngc_hipercam()
        except Exception as e:
            self.log.error('could not setup NGC for hipercam: ' + str(e))
            return False

        for key in output:
            msg = output[key]
            self.log.info("cmd {}: {}".format(key, msg))
        return True

    def cmd(self, cmd, *args):
        self.log.info("cmd {}: {}".format(cmd, ' '.join(args)))
        try:
            msg, cmd_ok = self._dev.send_command(cmd, *args)
            if not cmd_ok:
                self.log.error('cmd {} failed with msg {}'.format(cmd, msg))
        except Exception as e:
            msg = 'could not run command {}: {}'.format(cmd, e)
            self.log.error('could not run command {}: {}'.format(cmd, e))
            cmd_ok = False

        return msg, cmd_ok

    def telemetry(self):
        """
        Called periodically to provide status etc for the NGC
        """
        ts = Time.now()
        tel = dict(timestamp=ts)
        tel.update(self._dev.database_summary)
        frame_msg, ok = self._dev.send_command('status', 'DET.FRAM2.NO')
        try:
            frame_no = int(frame_msg.split()[1])
        except:
            frame_no = 0
        if not ok:
            tel['exposure.frame'] = 0
        else:
            tel['exposure.frame'] = frame_no
        return tel

    def start(self, *args):
        return self.cmd('start')

    def stop(self, *args):
        return self.cmd('stop')

    def abort(self, *args):
        return self.cmd('abort')

    def pon(self, *args):
        return self.cmd('cldc 0 enable')

    def poff(self, *args):
        return self.cmd('cldc 0 disable')

    def seq_start(self, *args):
        return self.cmd('seq 0 start')

    def seq_stop(self, *args):
        return self.cmd('seq 0 stop')

    def trigger(self, *args):
        return self.cmd('seq trigger')

    def reset(self, *args):
        return self.cmd('reset')

    def summary(self, *args):
        return self._dev.database_summary

    def status(self, param_name=None):
        if param_name is None:
            return self.cmd('status')

        response, response_ok = self.cmd('status', param_name)
        if not response_ok:
            return response, response_ok

        try:
            name, val = response.split()
            if name != param_name:
                msg = 'unexpected response: {} vs {}'.format(
                    name, param_name
                )
                return msg, False

            return val, response_ok
        except Exception as err:
            return str(err), False

        return self.cmd('status', param_name)

    def setup(self, param_name, value):
        return self.cmd('setup', param_name, value)

    def load_setup(self, data):
        """
        Post a JSON setup to the server

        Parameters
        -----------
        data : dict
            setup info
        """
        try:
            obsmode = get_obsmode(data)
        except Exception as err:
            self.log.error('could not parse obsmode data: ' + str(err))
            return False, 'could not parse obsmode data'

        resp = self.cmd('seq stop')
        if not resp:
            self.log.error('could not stop sequencer')
            return False, 'could not stop sequencer'

        time.sleep(0.1)
        resp = self.cmd(obsmode.readmode_command)
        if not resp:
            self.log.error('could not set read mode: ' + resp)
            return False, 'could not set read mode: ' + resp

        time.sleep(0.1)
        resp = self.cmd(obsmode.acq_command)
        if not resp:
            self.log.error('could not start acquisition process: ' + resp)
            return False, 'could not start acquisition process: ' + resp

        time.sleep(0.1)
        for header_command in obsmode.header_commands:
            resp = self.cmd(header_command)
        if not resp:
            msg = 'could not set header param {}: {} '.format(
                header_command, resp
            )
            self.log.error(msg)
            return False, msg

        time.sleep(0.1)
        resp = self.cmd(obsmode.setup_command)
        if not resp:
            self.log.error('could not setup run: ' + resp)
            return False, 'could not setup run: ' + resp

        if isinstance(obsmode, Idle):
            """
            A run start will start the sequencer, saving data and clearing the chips.
            There is no run start when we switch to idle mode, so start the sequencer
            manually
            """
            resp = self.cmd('seq start')
            if not resp:
                self.log.error('could not start sequencer: ' + resp)
                return False, 'could not start sequencer: ' + resp

        return True, 'All OK'

    def add_hdu(self, table_data, run_number):
        """
        Handle an uploaded table, and append it to the appropriate FITS file

        Parameters
        -----------
        table_data: bytes
            a binary encoded VOTable, which we will write to a FITS HDU,
            which is appended onto the original FITS file.
        run_number: int
            the run to append the table data to
        """
        try:
            t = ascii.read(table_data, format='ecsv')
        except Exception as e:
            self.log.error('cannot decode table data: ' + str(e))
            return

        filename = os.path.join('/data', "run{:04d}.fits".format(run_number))
        if not os.path.exists(filename):
            self.log.error('no such filename exists: ' + filename)
            return

        try:
            new_hdu = fits.table_to_hdu(t)
            existing_hdu_list = fits.open(
                filename, mode='append', memmap=True
            )
            existing_hdu_list.append(new_hdu)
            existing_hdu_list.flush()
        except Exception as e:
            self.log.error('could not write HDU to run: ' + str(e))
