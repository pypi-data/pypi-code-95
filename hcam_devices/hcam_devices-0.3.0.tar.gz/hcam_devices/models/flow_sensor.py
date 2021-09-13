from functools import partial
import astropy.units as u
from astropy.time import Time
from twisted.logger import Logger

from ..devices.honeywell import Minitrend, MinitrendEmulator
from ..machines import create_machine


UNITS = u.liter/u.minute


class FlowSensor(object):
    """
    Honeywell Minitrend Flow Sensor

    All flow rates in liters/minute
    """
    log = Logger()

    settable_attributes = ()
    extra_rpc_calls = ()

    def __init__(self, ip_address, port, npens=6, emulate=True):
        if emulate:
            self.dev = MinitrendEmulator(1.0, 0.05)
        else:
            self.dev = Minitrend(ip_address, port)

        # state machine to keep track of state
        self._controller = create_machine('connections',
                                          initial_context={'device': self, 'name': 'honeywell'})

        self.machines = {'connection': self._controller}
        self.npens = npens
        # map pens to ones used in hipercam
        self.pen_mapping = {0: 0, 1: 1, 2: 2, 3: 3, 4: 8, 5: 9}
        self.sensors = []

        def make_alarm_read(pen):
            def inner():
                alarm = any(self.dev.get_alarm(pen))
                return alarm
            return inner

        for i in range(self.npens):
            pen_num = self.pen_mapping[i]
            ctx = {
                'value': 0.0,
                'read_value': partial(self.dev.get_pen, pen_num),
                'read_alarm': make_alarm_read(pen_num),
                'name': 'flow{}'.format(pen_num)
            }
            sensor = create_machine('sensor', initial_context=ctx)
            self.machines['pen' + str(i+1)] = sensor
            # sensors will recieve connect/disconnect events from controller
            # and vice versa
            self._controller.bind(sensor)
            sensor.bind(self._controller)

    def try_connect(self):
        try:
            self.dev.connect()
        except Exception:
            return False
        return True

    def disconnect(self):
        self.dev.close()

    def _oldest_timestamp(self):
        """
        search all the sensors and return the oldest (stalest) timestamp
        """
        stamps = []
        for key in self.machines:
            if 'last_read' in self.machines[key].context:
                stamps.append(self.machines[key].context['last_read'])
        return min(stamps)

    def telemetry(self):
        """
        Called periodically to provide a telemetry package for the device
        """
        ts = Time(self._oldest_timestamp(), format='unix')
        ts.format = 'iso'
        tel = dict(timestamp=ts)
        tel['state'] = {key: self.machines[key].configuration for key in self.machines}
        for i in range(self.npens):
            name = 'pen' + str(i+1)
            sensor = self.machines[name]
            tel[name] = sensor.context['value'] * UNITS
            tel[name.replace('pen', 'alarm')] = sensor.context['alarm']
        return tel
