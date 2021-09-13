# focal plane slide
import astropy.units as u
from astropy.time import Time
from twisted.logger import Logger

from ..devices.properties import microstep
from ..devices.zaber import ZaberLS, ZaberLSEmulator
from ..machines import create_machine

# the next define ranges for the movement in terms of
# microsteps, millimetres and pixels
MIN_MS = 0
MAX_MS = 1664000
MIN_PX = 2760.2
MAX_PX = -1155.3
MM_PER_MS = 0.000078
MIN_MM = MM_PER_MS*MIN_MS
MAX_MM = MM_PER_MS*MAX_MS

# Standard pixel positions for unblocking and blocking the CCD
UNBLOCK_POS = 1100.
BLOCK_POS = -100.


def mm_to_ms(value):
    return MIN_MS + int((MAX_MS - MIN_MS) * (value - MIN_MM) / (MAX_MM-MIN_MM) + 0.5)


def ms_to_mm(value):
    return MIN_MM + (MAX_MM - MIN_MM)*(value - MIN_MS)/(MAX_MS - MIN_MS)


def px_to_ms(value):
    return MIN_MS + int((MAX_MS-MIN_MS) * (value - MIN_PX) / (MAX_PX - MIN_PX) + 0.5)


def ms_to_px(value):
    return MIN_PX + (MAX_PX - MIN_PX)*(value - MIN_MS)/(MAX_MS - MIN_MS)


unit_scale = [
    # from, to, forward, backward
    (u.pix, microstep, px_to_ms, ms_to_px),
    (u.mm, microstep, mm_to_ms, ms_to_mm)
]


class FocalPlaneSlide(object):
    """
    Focal plane slide.

    Uses a Motor state machine to track state, and a Zaber linear stage device to send
    messages.

    Periodically updates WAMP server with updates of position and state.

    All positions in pixels
    """

    log = Logger()

    # can be set by publishing to device level topic of same name
    settable_attributes = ('target_position',)
    # all state change triggers are automatically addded as RPC calls
    # add any extra methods you want exposed here
    extra_rpc_calls = ('block', 'unblock', 'enable', 'disable', 'reset')

    def __init__(self, ip_address, port, emulate=True):
        if emulate:
            self.dev = ZaberLSEmulator(ip_address, port, unit_equivalencies=unit_scale)
        else:
            self.dev = ZaberLS(ip_address, port, unit_equivalencies=unit_scale)

        # state machines to keep track of state
        self._controller = create_machine('connections',
                                          initial_context={'device': self, 'name': 'slide'})
        self._axis = create_machine('motors',
                                    initial_context={'device': self, 'current': 0*u.pix,
                                                     'target': 0*u.pix, 'poll_time': 1})

        self.machines = {'connection': self._controller, 'stage': self._axis}
        # axis will recieve events from controller
        self._controller.bind(self._axis)

    @property
    def current_position(self):
        return self._axis.context['current']

    @property
    def target_position(self):
        return self._axis.context['target']

    @target_position.setter
    def target_position(self, value):
        if not isinstance(value, u.Quantity):
            value = value * u.pix
        self._axis.queue('positionSet', position=value)

    def block(self):
        self.target_position = BLOCK_POS
        self._axis.queue('move')

    def unblock(self):
        self.target_position = UNBLOCK_POS
        self._axis.queue('move')

    def enable(self):
        self.dev.enable()

    def disable(self):
        self.dev.disable()

    def reset(self):
        self.dev.reset()
        self._controller.queue('disconnect')

    def telemetry(self):
        """
        Called periodically to provide a telemetry package for the device
        """
        ts = Time.now()
        return dict(
            timestamp=ts,
            position=dict(current=self.current_position,
                          target=self.target_position),
            state={key: self.machines[key].configuration for key in self.machines}
        )

    # methods and properties required for motor state machine
    # Keep these on slide object rather than moving to Zaber since
    # querying target position of Zaber stage is not implemented
    def home(self):
        try:
            self.dev.home()
        except Exception as err:
            self.log.error(str(err))

    def homed(self):
        is_homed = False
        try:
            is_homed = self.dev.homed
        except Exception as err:
            self.log.error(str(err))
        return is_homed

    def on_target(self):
        current = self.current_position.to(microstep, equivalencies=unit_scale)
        target = self.target_position.to(microstep, equivalencies=unit_scale)
        delta = abs((current-target).value)
        return int(delta) < 5

    def move(self, value):
        if not isinstance(value, u.Quantity):
            # assume pixels
            value = value * u.pix
        try:
            self.dev.move(value)
        except Exception as err:
            self.log.error(str(err))

    def stop(self):
        self.dev.stop()

    def try_connect(self):
        """
        Always needs to be defined.  Returns True on successful connection attempt.
        """
        # attempt connection, return true to allow device state to change
        try:
            self.dev.connect()
        except Exception:
            return False
        return True

    def disconnect(self):
        self.dev.close()

    def poll(self):
        """
        State machines mean that this is automatically polled.

        Update current position and return True/False for moving state
        """
        current_position = self.dev.position.to(u.pix, equivalencies=unit_scale)
        return current_position, self.dev.moving
