# GTC
import time
from itertools import cycle
from astropy.time import Time
from astropy.io.fits import Header
from twisted.logger import Logger

from ..machines import create_machine
from ..utils.filesystem import FITSWatcher
from ..wamp.utils import call
from ..gtc.headers import create_header_from_telpars
try:
    from ..gtc.corba import TelescopeServer
except Exception:
    TelescopeServer = None


class FakeTelescopeServer(object):
    def __init__(self):
        self._inpos = True
        self._last_move = time.time()
        self.ra = 100
        self.dec = 20

    @property
    def ready(self):
        return True

    def in_position(self):
        if time.time() - self._last_move > 5:
            self._inpos = True
            self.ra += self.raoff
            self.raoff = 0
            self.dec += self.decoff
            self.decoff = 0
            return True

        return False

    def requestTelescopeOffset(self, dra, ddec):
        print('offsetting ', dra, ddec)
        self._last_move = time.time()
        self.raoff = dra
        self.decoff = ddec

    def getHumidity(self):
        return 0.2

    def getCabinetTemperature1(self):
        return 25.0

    def getTelescopeParams(self):
        hdr = Header()
        hdr['RADEG'] = (self.ra, 'RA (degrees)')
        hdr['DECDEG'] = (self.dec, 'DEC (degrees)')
        hdr['INSTRPA'] = (22.1, 'Rotator PA')
        hdr['M2UZ'] = (-2.13, 'Focus offset')
        return hdr.tostring(sep=';').split(';')[:-1]


class GTC(object):
    """
    Telescope communication with GTC
    """
    log = Logger()

    settable_attributes = ()

    # all state change triggers are automatically addded as RPC calls
    # in this case this is only "do_offset"
    # add any extra methods you want exposed here
    extra_rpc_calls = ('get_telescope_pars', 'get_rack_temperature', 'get_humidity',
                       'load_nod_pattern', 'track_new_run')

    # these calls will be performed repeatedly
    extra_looping_calls = {'poll_runs': 0.1}

    def __init__(self, emulate=True, path='/data'):
        print('emulation mode: ', emulate)
        if emulate:
            self._server = FakeTelescopeServer()
        else:
            self._server = TelescopeServer()
        self._gtcmachine = create_machine('gtc', initial_context={'server': self._server})
        # route events sent by machine to our event handler
        self._gtcmachine.bind(self.machine_event_handler)
        # start clock
        self.machines = {"gtc": self._gtcmachine}

        # define dummy nod patterns
        self.ra_offsets = cycle([0.0])
        self.dec_offsets = cycle([0.0])

        # setup polling of latest run
        self.path = path
        self.track_new_run()

    def poll_runs(self):
        self.run_watcher.poll()

    def machine_event_handler(self, event):
        if event.name == 'trigger_exposure':
            call('hipercam.ngc.rpc.trigger')

    def telemetry(self):
        """
        Called periodically to provide a telemetry package
        """
        ts = Time.now()
        try:
            telpars = create_header_from_telpars(self._gtcmachine.context['telpars'])
        except TypeError:
            telpars = {}
        return dict(
            timestamp=ts,
            telpars=telpars,
            rack_temp=self._gtcmachine.context['rack_temp'],
            humidity=self._gtcmachine.context['humidity'],
            ra_offset=self.cumulative_ra_offset,
            dec_offset=self.cumulative_dec_offset,
            state={key: self.machines[key].configuration for key in self.machines}
        )

    def get_relative_offsets(self, abs_ra_offset, abs_dec_offset):
        # convert an absolute offset into one relative to current position
        return (abs_ra_offset - self.cumulative_ra_offset,
                abs_dec_offset - self.cumulative_dec_offset)

    def get_next_offsets(self):
        return self.get_relative_offsets(next(self.ra_offsets), next(self.dec_offsets))

    def on_run_modified_callback(self):
        raoff, decoff = self.get_next_offsets()
        self._gtcmachine.queue('frame_written', raoff=raoff, decoff=decoff)
        self.cumulative_ra_offset += raoff
        self.cumulative_dec_offset += decoff

    def track_new_run(self):
        self.cumulative_ra_offset = 0.0
        self.cumulative_dec_offset = 0.0
        # create a polling object to watch the data directory
        self.run_watcher = FITSWatcher(self.path, self.on_run_modified_callback)

    def load_nod_pattern(self, raoffs, decoffs):
        try:
            self.ra_offsets = cycle(list(raoffs))
            self.dec_offsets = cycle(list(decoffs))
        except ValueError:
            raise ValueError('could not create offset patterns from input')

    def get_humidity(self):
        return self._gtcmachine.context['humidity']

    def get_rack_temperature(self):
        return self._gtcmachine.context['rack_temp']

    def get_telescope_pars(self):
        return self._gtcmachine.context['telpars']
