import pickle

from astropy.time import Time
from astropy import units as u
from twisted.logger import Logger

STALE_TELEMETRY_THRESHOLD = 60


class CCDHead(object):
    """
    Model for a HiPERCAM CCD head.

    This is a convenience model that listens to, and forwards,
    telemetry from the vacuum gauge, flow sensor and peltier
    controller for the relevant CCD head.

    The correct topics to subscribe to are passed as parameters
    """
    log = Logger()

    def __init__(self, pressure_channel, flow_channel,
                 peltier_channel,
                 pen_number, meerstetter_channel):

        self.pen_number = str(pen_number)
        self.meerstetter_channel = str(meerstetter_channel)

        # we subscribe to telemetry on these channels
        self.subscribed_channels = {
            'pressure': pressure_channel,
            'flow': flow_channel,
            'peltier': peltier_channel
        }

        # pass through topics merely pass any published messages on to a different topic
        setpoint_topic = 'target_temperature' + self.meerstetter_channel
        self.pass_through_topics = {
            'setpoint': '.'.join([self.subscribed_channels['peltier'], setpoint_topic])
        }

        self._telemetry_timestamps = {
            'pressure': Time.now(),
            'flow': Time.now(),
            'peltier': Time.now()
        }

        # this is the basic package we publish as telemetry
        self._telemetry_pkg = {
            'pressure': 0.0,
            'flow': 0.0,
            'heatsink': 0.0,
            'peltier_current': 0.0,
            'peltier_status': 'error',
            'setpoint': 0.0,
            'temperature': 0.0,
            'state': "ERR",
            'state_reason': 'OK'
        }

    def _check_state(self):
        """
        check current values are OK
        """
        state = "OK", 'None'

        if self._telemetry_pkg['pressure'].to_value(u.mbar) > 8.0e-3:
            state = 'ERR', 'high pressure'
        flow = self._telemetry_pkg['flow']
        if flow < 0.4 * u.liter/u.minute:
            state = 'ERR', 'low flow'
        deltaT = abs(self._telemetry_pkg['temperature'] - self._telemetry_pkg['setpoint'])
        deltaT = deltaT.to_value(u.deg_C, equivalencies=u.temperature())
        if deltaT > 2:
            state = 'WARN', 'temperature not near setpoint'
        if self._telemetry_pkg['peltier_status'] != 'run':
            state = 'ERR', 'peltier not running'
        for source, telemetry_time in self._telemetry_timestamps.items():
            telemetry_age = (Time.now() - telemetry_time).to_value(u.s)
            if telemetry_age > STALE_TELEMETRY_THRESHOLD:
                state = 'ERR', 'stale telemetry from {}'.format(source)

        return state

    def on_received_telemetry(self, data):
        """
        Handle telemetry data. Could come from any
        subscribed topics
        """
        telemetry = pickle.loads(data)
        telemetry_time = telemetry['timestamp']
        device_status = telemetry['state']['connection']

        if 'pen1' in telemetry:
            source = 'flow'
        elif 'pressure' in telemetry:
            source = 'pressure'
        elif 'heatsink1' in telemetry:
            source = 'peltier'
        else:
            raise ValueError('unexpected telemetry pkg: ', telemetry)
        self._telemetry_timestamps[source] = telemetry_time

        bad_status = set(('offline', 'error'))
        if len(bad_status.intersection(device_status)) != 0:
            self._telemetry_pkg['state'] = 'ERR'
            self._telemetry_pkg['state_reason'] = '{} offline or errored'.format(source)
        else:
            state, reason = self._check_state()
            self._telemetry_pkg['state'] = state
            self._telemetry_pkg['state_reason'] = reason

        if source == 'flow':
            # report from flow_sensor
            pen_name = 'pen' + self.pen_number
            value = telemetry[pen_name]
            self._telemetry_pkg['flow'] = value
        elif source == 'pressure':
            self._telemetry_pkg['pressure'] = telemetry['pressure']
        elif source == 'peltier':
            new_tel = {}
            new_tel['heatsink'] = telemetry['heatsink' + self.meerstetter_channel]
            new_tel['peltier_current'] = telemetry['current' + self.meerstetter_channel]
            new_tel['peltier_status'] = telemetry['status' + self.meerstetter_channel]
            new_tel['setpoint'] = telemetry['target_temperature' + self.meerstetter_channel]
            new_tel['temperature'] = telemetry['temperature' + self.meerstetter_channel]
            self._telemetry_pkg.update(new_tel)

    def telemetry(self):
        # use stalest timestamp we have as the data timestamp
        oldest_ts = min(self._telemetry_timestamps,
                        key=self._telemetry_timestamps.get)
        tel = dict(timestamp=self._telemetry_timestamps[oldest_ts])
        tel.update(self._telemetry_pkg)
        return tel
