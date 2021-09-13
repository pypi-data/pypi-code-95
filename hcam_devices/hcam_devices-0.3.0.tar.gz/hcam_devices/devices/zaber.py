#!/usr/bin/env python
"""
Zaber Linear Stages, including T-LLS devices
"""
from __future__ import (print_function, division, absolute_import)
import struct
import six
import socket
import threading
import time

from .properties import DeviceProperty, BooleanDeviceProperty, microstep

# rename socket.error
if six.PY2:
    ConnectionRefusedError = socket.error


class ZaberError(Exception):
    pass


# how long to wait before giving up on a response
DEFAULT_TIMEOUT = 5

# number of bytes to transmit & recieve
PACKET_SIZE = 6

# command numbers
RESET = 0
HOME = 1
MOVE_ABSOLUTE = 20
MOVE_RELATIVE = 21
STOP = 23
RESTORE = 36
SET_MODE = 40
RETURN_SETTING = 53
RETURN_STATUS = 54
POSITION = 60
NULL = 0

# error return from slide
ERROR = 255

# unit number, may depend upon how device is connected to the port
UNIT = 1

PERIPHERAL_ID = 0
POTENTIOM_OFF = 8
POTENTIOM_ON = 0

TRUE = 1
FALSE = 0


class ZaberLS(object):
    position = DeviceProperty(POSITION, readonly=True)
    moving = BooleanDeviceProperty(RETURN_STATUS, readonly=True)

    def __init__(self, host='192.168.1.3', port=10001, unit_equivalencies=None):
        """
        Creates a Zaber device. Arguments::

         host: IP address of terminal server
         port: port device representing the slide

        """
        self.port = port
        self.host = host
        # thread lock for threadsafe operations
        self._lock = threading.Lock()
        self.unit = UNIT
        self.unit_equivalencies = unit_equivalencies
        self.units = microstep

    def __del__(self):
        # must close connection on object deletion
        self.close()

    def connect(self):
        # connect to socket on terminal server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        self.sock = s
        self.sock.settimeout(DEFAULT_TIMEOUT)

    def close(self):
        if self.sock is not None:
            self.sock.close()
        self.sock = None

    def _format_get_command(self, code):
        return code

    def _format_set_command(self, code):
        return code

    def _cmd(self, cmd, params=NULL, errcheck=True):

        # set command data
        to_send = self._encodeCommandData(params)
        # add bytes to define instruction at start of array
        to_send.insert(0, cmd)
        # add unit byte
        to_send.insert(0, self.unit)

        received = self._sendRecv(to_send)
        value = self._decodeCommandData(received)

        if received[1] == ERROR and errcheck:
            # spontaneous error reply
            raise ZaberError('Error occured with code: {}'.format(value))
        """
        if errcheck:
            error_code = self._cmd(ERROR, errcheck=False)
            if error_code != 0:
                raise ZaberError('Device error code {}'.format(error_code))
        """
        return value

    def _sendRecv(self, byteArr):
        # only one thread at a time talks to the slide
        with self._lock:
            try:
                self.sock.send(byteArr)
            except socket.timeout:
                raise ZaberError('timed out waiting for slide response. this is normal on long moves')
            except Exception as e:
                raise ZaberError('failed to send bytes to slide' + str(e))
            msg = self.sock.recv(6)
        return bytearray(msg)

    def _decodeCommandData(self, byteArr):
        return struct.unpack('<L', byteArr[2:])[0]

    def _encodeCommandData(self, int):
        return bytearray(struct.pack('<L', int))

    def _encodeByteArr(self, intArr):
        if len(intArr) != 6:
            raise ZaberError('must send 6 bytes to slide: cannot send ' +
                             repr(intArr))
        return bytearray(intArr)

    @property
    def homed(self):
        """
        returns true if the slide has been homed and has a calibrated
        position
        """
        byteArr = self._encodeByteArr([UNIT, RETURN_SETTING,
                                       SET_MODE, NULL, NULL, NULL])
        byteArr = self._sendRecv(byteArr)
        if byteArr[1] == ERROR:
            raise ZaberError('Error trying to get the setting byte')

        # if 7th bit is set, we have been homed
        if byteArr[2] & 128:
            return True
        else:
            return False

    def move(self, position):
        """
        move to a defined position
        """
        nstep = int(position.to(microstep, equivalencies=self.unit_equivalencies).value)
        self._cmd(MOVE_ABSOLUTE, nstep, errcheck=True)

    def home(self):
        """
        move the slide to the home position. This is needed after a power on
        to calibrate the slide
        """
        self._cmd(HOME)

    def reset(self):
        """
        carry out the reset command, equivalent to turning the slide off and
        on again. The position of the slide will be lost and a home will be
        needed
        """
        self._cmd(RESET)

    def restore(self):
        """
        carry out the restore command. restores the device to factory settings
        very useful if the device does not appear to function correctly
        """
        self._cmd(RESTORE, params=PERIPHERAL_ID)

    def disable(self):
        """
        carry out the disable command. disables the potentiometer preventing
        manual adjustment of the device
        """
        self._cmd(SET_MODE, POTENTIOM_OFF)

    def enable(self):
        """
        carry out the enable command. enables the potentiometer allowing
        manual adjustment of the device
        """
        self._cmd(SET_MODE, POTENTIOM_ON)

    def stop(self):
        """stop the slide"""
        self._cmd(STOP)


class ZaberLSEmulator(ZaberLS):

    def __init__(self, host='192.168.1.3', port=10001, unit_equivalencies=None):
        super(ZaberLSEmulator, self).__init__(host, port, unit_equivalencies)
        self.target_position = None
        self.current_position = None
        self._homed = False
        self._moving = False
        self._running_thread = None
        self.abort_thread = False

    @property
    def homed(self):
        return self._homed

    @homed.setter
    def homed(self, value):
        self._homed = value

    @property
    def moving(self):
        return self._moving

    @moving.setter
    def moving(self, value):
        self._moving = value

    def connect(self):
        pass

    def close(self):
        pass

    def stop(self):
        self.abort_thread = True
        self._moving = False

    def _cmd(self, cmd, params=NULL, errcheck=True):

        response_data = params

        if cmd == HOME:
            self.target_position = 0 * microstep
            if self.current_position is None:
                self.current_position = 19000 * microstep
            self.homed = True
            self.moving = True
            t = threading.Thread(target=self._move_thread)
            t.start()
            self._running_thread = t

        elif cmd == MOVE_ABSOLUTE:
            self.target_position = params * microstep
            self.moving = True

            t = threading.Thread(target=self._move_thread)
            t.start()
            self._running_thread = t

        elif cmd == POSITION:
            response_data = int(self.current_position.value)

        # set command data
        to_send = self._encodeCommandData(response_data)
        # add bytes to define instruction at start of array
        to_send.insert(0, cmd)
        # add unit byte
        to_send.insert(0, self.unit)
        return self._decodeCommandData(to_send)

    def _move_thread(self):
        self.abort_thread = False
        speed = 9000  # steps/s
        step_time = 0.1  # s
        nsteps = int(abs((self.target_position - self.current_position).value)/speed/step_time)
        step = (self.target_position - self.current_position)/nsteps
        for l in range(nsteps):
            self.current_position += step
            time.sleep(step_time)
            if self.abort_thread:
                break
        self.moving = False
