# COMPO components
import astropy.units as u
from astropy.time import Time
from twisted.logger import Logger

from ..devices.properties import microstep
from ..devices.newport import NewportESP301
from ..machines import create_machine

equivalencies = [
    # from, to, forward, backward (assume 1-1 for now)
    (u.rad, microstep, lambda x: 1.0, lambda x: 1.0),
    (u.mm, microstep, lambda x: 1.0, lambda x: 1.0)
]

# match order in NewportESP301
esp_axes = {1: 'pickoff', 2: 'injection', 3: 'lens'}


class Compo(object):
    """
    Model for COMPO hardware.

    COMPO is controlled by a Newport ESP301 controller, which has 3 axes.

    These axes are the angles of the pickoff arm and injection arm and the
    linear lens slide.
    """
    log = Logger()

    # can be set by publishing to a device level topic of same name
    settable_attributes = ('target_injection_angle',
                           'target_pickoff_angle',
                           'target_lens_position')

    # all state change triggers are automatically addded as RPC calls
    # add any extra methods you want exposed here
    extra_rpc_calls = ('power_on_axis', 'power_off_axis')

    def __init__(self, port, emulate=False):

        self.dev = NewportESP301(port, emulate=emulate, unit_equivalencies=equivalencies)

        # state machines to track state. Controller for connections
        self._controller = create_machine('connections',
                                          initial_context={'device': self, 'name': 'compo'})
        self.machines = dict(connection=self._controller)

        # axes!
        # ORDER HERE MUST MATCH ORDER IN Newport!
        for ax in esp_axes:
            name = esp_axes[ax]
            ctx = {
                'device': self.dev.axis[ax-1],
                'current': 0*u.mm if name == 'lens' else 0*u.deg,
                'target': 0*u.mm if name == 'lens' else 0*u.deg,
                'poll_time': 2
            }
            axis = create_machine('motors', initial_context=ctx)
            self.machines[name] = axis
            # bind axes to receive connect disconnect from controller
            self._controller.bind(axis)

    @property
    def current_injection_angle(self):
        return self.machines['injection'].context['current']

    @property
    def target_injection_angle(self):
        return self.machines['injection'].context['target']

    @target_injection_angle.setter
    def target_injection_angle(self, value):
        print('setting injection angle')
        if not isinstance(value, u.Quantity):
            value = value * u.deg
        self.machines['injection'].queue('positionSet', position=value)

    @property
    def current_pickoff_angle(self):
        return self.machines['pickoff'].context['current']

    @property
    def target_pickoff_angle(self):
        return self.machines['pickoff'].context['target']

    @target_pickoff_angle.setter
    def target_pickoff_angle(self, value):
        if not isinstance(value, u.Quantity):
            value = value * u.deg
        self.machines['pickoff'].queue('positionSet', position=value)

    @property
    def current_lens_position(self):
        return self.machines['lens'].context['current']

    @property
    def target_lens_position(self):
        return self.machines['lens'].context['target']

    @target_lens_position.setter
    def target_lens_position(self, value):
        if not isinstance(value, u.Quantity):
            value = value * u.mm
        self.machines['lens'].queue('positionSet', position=value)

    def telemetry(self):
        """
        Called periodically to provide a telemetry package for the device
        """
        ts = Time.now()
        tel = dict(timestamp=ts)
        state = {key: self.machines[key].configuration for key in self.machines}
        tel['state'] = state
        tel['pickoff_angle'] = dict(current=self.current_pickoff_angle,
                                    target=self.target_pickoff_angle)
        tel['injection_angle'] = dict(current=self.current_injection_angle,
                                      target=self.target_injection_angle)
        tel['lens_position'] = dict(current=self.current_lens_position,
                                    target=self.target_lens_position)
        return tel

    # Methods REQUIRED for controller state machine
    def try_connect(self):
        try:
            self.dev.connect()
            # update device in machines
            for ax in esp_axes:
                name = esp_axes[ax]
                machine = self.machines[name]
                axis = self.dev.axis[ax-1]
                machine.context['device'] = axis
        except Exception:
            return False
        return True

    def disconnect(self):
        self.dev.disconnect()

    # additional RPC calls
    def power_on_axis(self, axis):
        self.dev.axis[axis].power_on()

    def power_off_axis(self, axis):
        self.dev.axis[axis].power_off()
