from functools import partial

from astropy import units as u
from astropy.time import Time
from twisted.logger import Logger

from ..devices.meerstetter import (MeerstetterTEC1090, STATUS_CODES,
                                   MeerstetterTEC1090Emulator)
from ..machines import create_machine

TEMP_UNITS = u.deg_C
CURRENT_UNITS = u.A


# define some helper functions to create sensor statemachines
def create_sensor(connection_handler, address, name, read_method, initial_value):
    sensor = create_machine('sensor',
                            initial_context={
                                'value': initial_value,
                                'read_value': read_method,
                                'name': name
                            })
    connection_handler.bind(sensor)
    sensor.bind(connection_handler)
    return sensor


def create_controller(connection_handler, address, name, read_method,
                      write_method, setpoint_read_method):
    sensor = create_machine('controller',
                            initial_context={
                                'write': write_method,
                                'read': read_method,
                                'name': name,
                                'read_setpoint': setpoint_read_method
                            })
    connection_handler.bind(sensor)
    sensor.bind(connection_handler)
    return sensor


class Meerstetter(object):
    """
    Meerstetter peltier controller.

    This is a model for a single peltier controller, that has three channels.
    """
    log = Logger()

    # can be set by publishing to device level topic of same name
    settable_attributes = ('target_temperature1', 'target_temperature2',
                           'target_temperature3')

    # all state change triggers are automatically addded as RPC calls
    # add any extra methods you want exposed here
    extra_rpc_calls = ('reset',)

    def __init__(self, ip_addr, port, emulate=True):

        if emulate:
            dev = MeerstetterTEC1090Emulator(ip_addr, port)
            self.dev = dev
        else:
            dev = MeerstetterTEC1090(ip_addr, port)
            self.dev = dev

        self._controller = create_machine('connections',
                                          initial_context={'device': self,
                                                           'name': 'meerstetter'})
        self.machines = {'connection': self._controller}

        for addr in range(1, 4):
            name = 'status{}'.format(addr)
            self.machines[name] = create_sensor(
                self._controller, addr, name, partial(self.dev.get_status, addr), 0.0)

            name = 'heatsink{}'.format(addr)
            self.machines[name] = create_sensor(
                self._controller, addr, name,
                partial(self.dev.get_heatsink_temp, addr), 0.0)

            name = 'current{}'.format(addr)
            self.machines[name] = create_sensor(
                self._controller, addr, name, partial(self.dev.get_current, addr), 0.0)

            name = 'temperature{}'.format(addr)
            self.machines[name] = create_controller(
                self._controller, addr, name,
                partial(self.dev.get_ccd_temp, addr),
                partial(self.dev.set_ccd_temp, addr),
                partial(self.dev.get_setpoint, addr))

    @property
    def target_temperature1(self):
        return self.machines['temperature1'].context['target']

    @target_temperature1.setter
    def target_temperature1(self, value):
        """
        Set target. Assume raw floats are already in degrees
        """
        if isinstance(value, u.Quantity):
            value = value.to_value(TEMP_UNITS, equivalencies=u.temperature())
        self.machines['temperature1'].queue('targetSet', target=value)

    @property
    def target_temperature2(self):
        return self.machines['temperature2'].context['target']

    @target_temperature2.setter
    def target_temperature2(self, value):
        if isinstance(value, u.Quantity):
            value = value.to_value(TEMP_UNITS, equivalencies=u.temperature())
        self.machines['temperature2'].queue('targetSet', target=value)

    @property
    def target_temperature3(self):
        return self.machines['temperature3'].context['target']

    @target_temperature3.setter
    def target_temperature3(self, value):
        if isinstance(value, u.Quantity):
            value = value.to_value(TEMP_UNITS, equivalencies=u.temperature())
        self.machines['temperature3'].queue('targetSet', target=value)

    def reset(self, address):
        self.dev.reset_tec(address)

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
        ts = Time(self._oldest_timestamp(), format='unix')
        ts.format = 'iso'
        tel = dict(
            timestamp=ts,
            state={key: self.machines[key].configuration for key in self.machines}
        )
        for key in self.machines:
            if key.startswith('status'):
                tel[key] = STATUS_CODES[self.machines[key].context['value']]
            elif key != 'connection':
                unit = CURRENT_UNITS if key.startswith('current') else TEMP_UNITS
                tel[key] = self.machines[key].context['value'] * unit
        for addr in range(1, 4):
            key = 'target_temperature{}'.format(addr)
            tel[key] = getattr(self, key) * TEMP_UNITS
        return tel

    # METHODS NEEDED FOR STATE MACHINES
    def try_connect(self):
        """
        Always needs to be defined.  Returns True on successful connection attempt.
        """
        # attempt connection, return true to allow device state to change
        try:
            connected = self.dev.connect()
        except Exception:
            return False
        return connected

    def disconnect(self):
        self.dev.disconnect()
