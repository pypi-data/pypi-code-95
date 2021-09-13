"""
Low level interface to NGC controller sending messages over
TCP/IP ports using ngcbCmd and reading instance database.
"""
import subprocess
import re
import os
import time
import glob
import sqlite3  # only needed for testing


class NGCDevice(object):
    """
    Class to wrap low-level communication with the NGC control software
    """
    def send_command(self, command, *command_pars):
        """
        Use low level ngcbCmd to send command to control server.
        """
        command_array = ['ngcbCmd', command]
        if command_pars:
            command_array.extend(command_pars)
        # must contain only strings
        command_array = [str(val) for val in command_array]

        # now attempt to send command to control server
        try:
            ret_msg = subprocess.check_output(command_array).strip().decode()
            # make sure all successful return true as status
            result = (ret_msg, True)
        except subprocess.CalledProcessError as err:
            # make sure all failed commands end with NOK line
            result = (err.output.strip().decode(), False)
        return result

    def stop_ngc_sw(self):
        """
        Shuts down ESO server
        """
        output = {}
        cmd = ['ngcdcsStopServer', 'IRCAM1']
        result = subprocess.check_output(cmd).strip().decode()
        output[' '.join(cmd)] = result
        return output

    def start_ngc_sw(self, gui=False):
        """
        Setup NGC controller for use with HiPERCAM
        """
        output = {}
        port = str(os.getenv('NGC_PORT', 8080))
        if gui:
            cmd = ['ngcdcsStartServer', 'IRCAM1', '-port', port, '-gui']
        else:
            cmd = ['ngcdcsStartServer', 'IRCAM1', '-port', port]
        result = subprocess.check_output(cmd).strip().decode()
        output[' '.join(cmd)] = result

        return output

    def setup_ngc_hipercam(self):
        """
        To be run when device moves to standby state
        """
        output = {}
        # get last file name
        runs = glob.glob('/data/run*.fits')
        if len(runs) == 0:
            last = 'run0000.fits'
        else:
            last = sorted(runs)[-1]
        cmds = [
            'ngcbCmd setup DET.SYSCFG hipercam_5ccd.cfg',
            'ngcbCmd setup DET.FRAM.NAMING auto',
            'ngcbCmd setup DET.FRAM.FILENAME run',
            'dbWrite "<alias>ngcircon_ircam1:exposure.newDataFileName" {}'.format(last)
        ]
        for cmd in cmds:
            cmd = cmd.split()
            result = subprocess.check_output(cmd).strip().decode()
            time.sleep(0.05)
            output[' '.join(cmd)] = result
            time.sleep(0.05)

        return output

    @property
    def database_summary(self):
        """
        Get a summary of system state and exposure state from database.
        """
        cmdTemplate = 'dbRead "<alias>ngcircon_ircam1:{}"'
        database_attributes = [
            'system.stateName',
            'system.subStateName',
            'cldc_0.statusName',
            'seq_0.statusName',
            'exposure.time',  # total exposure time for run
            'exposure.countDown',  # time remaining
            'exposure.expStatusName',
            'exposure.baseName',
            'exposure.newDataFileName']  # LAST WRITTEN FILE
        results = {}
        for attribute in database_attributes:
            cmd = cmdTemplate.format(attribute)
            try:
                response = subprocess.check_output(cmd, shell=True)
                results[attribute] = response.decode().split('=')[-1].strip()
            except Exception:
                results[attribute] = 'ERR'
        return results


class NGCEmulator(object):

    known_params = {
        'DET.NDIT': 10,
        'DET.SEQ1.DIT': 5,
        'DET.SEQ2.DIT': 5,
        'DET.SEQ3.DIT': 5,
        'DET.SEQ4.DIT': 5,
        'DET.SEQ5.DIT': 5,
        'DET.FRAM2.NO': 1
    }
    database = ".test_ngc_server.db"

    def __init__(self):
        self.past_time = 1400000000
        self.create_db()

    def send_command(self, command, *command_pars):
        known_commands = {
            'start': self.start,
            'abort': self.abort,
            'stop': self.stop,
            'online': self.online,
            'off': self.off,
            'standby': self.standby,
            'reset': self.reset,
            'status': self.status,
            'acqproc': self.acqproc,
            'seq 0 start': self.seqstart,
            'seq 0 stop': self.seqstop,
            'seq start': self.seqstart,
            'seq stop': self.seqstop,
            'cldc 0 enable': self.pon,
            'cldc 0 disable': self.poff,
            'trigger': self.trigger,
            'exit': self.exit,
            'setup': self.setup
        }
        if command not in known_commands:
            commands = command.split()
            command = commands[0]
            args = commands[1:]
            command_pars = list(command_pars)
            command_pars.extend(args)
            if command not in known_commands:
                raise ValueError('unknown command: ' + command)

        cmd = known_commands[command]
        result, ok = cmd(*command_pars)
        return result, ok

    def acqproc(self, *args):
        print('setting acquisition process', args)

    def start(self, *args):
        # start run
        self.query_db("update run set startTime = ? WHERE id = 1", time.time())
        self.query_db("update run set expState = ? WHERE id = 1", "active")
        return "OK", True

    def pon(self, *args):
        self.query_db("update run set clocks = ? WHERE id = 1", 'enabled')
        return "OK", True

    def poff(self, *args):
        self.query_db("update run set clocks = ? WHERE id = 1", 'disabled')
        return "OK", True

    def seqstart(self, *args):
        self.query_db("update run set sequencer = ? WHERE id = 1", 'running')
        return "OK", True

    def seqstop(self, *args):
        self.query_db("update run set sequencer = ? WHERE id = 1", 'idle')
        return "OK", True

    def abort(self, *args):
        # abort run
        # fake stopping run by setting starttime a long time in the past
        self.query_db("update run set startTime = ? WHERE id = 1", self.past_time)
        return "OK", True

    def stop(self, *args):
        # stop run
        # fake stopping run by setting starttime a long time in the past
        self.query_db("update run set startTime = ? WHERE id = 1", self.past_time)
        # add 1 to run number
        row = self.query_db("select * from run", one=True)
        run_number = int(row['run'])
        run_number += 1
        self.query_db("update run set run = ? WHERE id = 1", run_number)
        return "OK", True

    def online(self, *args):
        # bring sw online
        self.query_db("update run set stateName = ? WHERE id = 1", 'ONLINE')
        return "OK", True

    def off(self, *args):
        # move to loaded state
        self.query_db("update run set stateName = ? WHERE id = 1", 'LOADED')
        return "OK", True

    def exit(self, *args):
        # move to off state
        self.query_db("update run set stateName = ? WHERE id = 1", 'OFF')
        return "OK", True

    def standby(self, *args):
        # standby state
        self.query_db("update run set stateName = ? WHERE id = 1", 'STANDBY')
        return "OK", True

    def reset(self, *args):
        # reset controller
        self.create_db()
        return "OK", True

    def trigger(self, *args):
        return "OK", True

    def status(self, *args):
        # get status. either of whole system or requested param
        if args:
            param = args[0]
            if param not in self.known_params:
                raise ValueError('param {} not in known parameters: '.format(param))
            val = self.known_params[param]
        else:
            row = self.query_db("select * from run", one=True)
            val = row['stateName']
        return val, True

    def setup(self, *parval_list):
        if len(parval_list) % 2 != 0:
            raise ValueError('uneven pairing of params and values')
        print('setup', ' '.join(parval_list))
        for param, value in zip(parval_list[::2], parval_list[1::2]):
            # set param to value
            if re.match('DET\.SEQ\d\.DIT', param):
                self.known_params[param] = value
                self.query_db("update run set DIT = ? WHERE id = 1", value)
            elif param == 'NDIT':
                self.known_params['NDIT'] = value
                self.query_db("update run set NDIT = ? WHERE id = 1", value)
            else:
                self.known_params[param] = value
        return "OK", True

    def start_ngc_sw(self, gui=False):
        print('starting NGC Software')
        self.query_db("update run set stateName = ? WHERE id = 1", 'LOADED')
        return {}

    def setup_ngc_hipercam(self):
        print('Initialising HiPERCAM specific settings')
        return {}

    @property
    def database_summary(self):
        row = self.query_db("select * from run", one=True)
        elapsedTime = time.time() - row['startTime']
        TOTAL = float(row['DIT']) * float(row['NDIT'])
        countDown = TOTAL - float(elapsedTime)
        run = int(row['run'])
        if elapsedTime > TOTAL:
            expStatusName = "success"
            subState = "idle"
            if row['expState'] != 'idle':
                self.query_db("update run set run = ? WHERE id = 1", run+1)
                self.query_db("update run set expState = ? WHERE id = 1", "idle")
        else:
            expStatusName = "integrating"
            subState = "active"

        summary_dictionary = {
            "exposure.baseName": "/data",
            "exposure.countDown": str(countDown),
            "exposure.expStatusName": expStatusName,
            "exposure.newDataFileName": "run{:04d}.fits".format(run),
            "exposure.time": "6",
            "cldc_0.statusName": row['clocks'],
            'seq_0.statusName': row['sequencer'],
            "system.stateName": row['stateName'],
            "system.subStateName": subState
        }
        return summary_dictionary

    def create_db(self):
        if os.path.exists(self.database):
            os.unlink(self.database)
        with sqlite3.connect(self.database) as conn:
            conn.execute(
                'CREATE TABLE run (id INT, startTime FLOAT, clocks TEXT, sequencer TEXT' +
                ', NDIT INT, DIT FLOAT, stateName TEXT, run INT, expState TEXT)'
            )
            keys = ('DET.SEQ{}.DIT'.format(seq+1) for seq in range(5))
            DIT = max([self.known_params[key] for key in keys])
            conn.execute(
                "INSERT INTO run (id, startTime, clocks, sequencer, NDIT, DIT, stateName, run, expState) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (1, self.past_time, 'disabled', 'idle', self.known_params['DET.NDIT'], DIT, 'OFFLINE', 1, "idle")
            )
            conn.commit()

    def get_db(self):
        db = sqlite3.connect(self.database)
        db.row_factory = sqlite3.Row
        return db

    def close_db(self, db):
        db.close()

    def query_db(self, query, *args, **kwargs):
        one = kwargs.get('one', False)
        conn = self.get_db()
        try:
            cur = conn.execute(query, args)
            rv = cur.fetchall()
            conn.commit()
            cur.close()
        finally:
            self.close_db(conn)
        return (rv[0] if rv else None) if one else rv
