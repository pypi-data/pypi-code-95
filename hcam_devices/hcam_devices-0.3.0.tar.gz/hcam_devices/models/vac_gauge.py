import astropy.units as u
from astropy.time import Time
from twisted.logger import Logger

from ..devices.pdr900 import PDR900, PDR900Emulator
from ..machines import create_machine

torr = u.def_unit('torr', (101325/760)*u.Pa)
UNITS = u.mbar


class VacGauge(object):
    """
    Model for PDR900 vacuum gauge.

    This is a model for a single vacuum gauge.
    """
    log = Logger()

    settable_attributes = ()
    extra_rpc_calls = ()

    def __init__(self, host, port, emulate=True):
        if emulate:
            self.dev = PDR900Emulator(1.0e-5, 0.0)
        else:
            self.dev = PDR900(host, port)

        # state machine to keep track of connections
        self._controller = create_machine('connections',
                                          initial_context={'device': self, 'name': 'vac gauge'})
        self.machines = {'connection': self._controller}

        ctx = {
            'value': 0.0,
            'read_value': lambda *args: self.dev.pressure,
            'name': 'vac_gauge'
        }
        sensor = create_machine('sensor', initial_context=ctx)
        self.gauge = sensor
        self.machines['gauge'] = sensor
        # sensors will recieve connect/disconnect events from controller
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

    def telemetry(self):
        """
        Called periodically to provide a telemetry package for the device
        """
        ts = Time(self.gauge.context['last_read'], format='unix')
        ts.format = 'iso'
        tel = dict(
            timestamp=ts,
            state={key: self.machines[key].configuration for key in self.machines}
        )
        tel['pressure'] = (self.gauge.context['value'] * UNITS).to(u.mbar)
        return tel
