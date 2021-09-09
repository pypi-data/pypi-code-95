"""Class for frequency sweeps on SHFQA
"""

# Copyright 2020 Zurich Instruments AG

from collections import namedtuple
from dataclasses import dataclass
from enum import Enum, auto
import time
import numpy as np
from .. import utils


class _Mapping(Enum):
    LIN = "linear"
    LOG = "log"


class _AveragingMode(Enum):
    CYCLIC = "cyclic"
    SEQUENTIAL = "sequential"


class _TriggerSource(Enum):
    """
    Valid trigger sources for spectroscopy
    Note: the user should write the trigger selection in lowercase letters.
    e.g. "software_trigger0". The strings are transformed to uppercase only
    for this enum, which is needed to distinguish between software and hardware
    triggers (see _HW_TRIGGER_LIMIT).
    """

    CHANNEL0_TRIGGER_INPUT0 = 0  # Important: start counting with 0
    CHAN0TRIGIN0 = CHANNEL0_TRIGGER_INPUT0

    CHANNEL0_TRIGGER_INPUT1 = auto()
    CHAN0TRIGIN1 = CHANNEL0_TRIGGER_INPUT1

    CHANNEL1_TRIGGER_INPUT0 = auto()
    CHAN1TRIGIN0 = CHANNEL1_TRIGGER_INPUT0

    CHANNEL1_TRIGGER_INPUT1 = auto()
    CHAN1TRIGIN1 = CHANNEL1_TRIGGER_INPUT1

    CHANNEL2_TRIGGER_INPUT0 = auto()
    CHAN2TRIGIN0 = CHANNEL2_TRIGGER_INPUT0

    CHANNEL2_TRIGGER_INPUT1 = auto()
    CHAN2TRIGIN1 = CHANNEL2_TRIGGER_INPUT1

    CHANNEL3_TRIGGER_INPUT0 = auto()
    CHAN3TRIGIN0 = CHANNEL3_TRIGGER_INPUT0

    CHANNEL3_TRIGGER_INPUT1 = auto()
    CHAN3TRIGIN1 = CHANNEL3_TRIGGER_INPUT1

    CHANNEL0_SEQUENCER_TRIGGER0 = auto()
    CHAN0SEQTRIG0 = CHANNEL0_SEQUENCER_TRIGGER0

    CHANNEL1_SEQUENCER_TRIGGER0 = auto()
    CHAN1SEQTRIG0 = CHANNEL1_SEQUENCER_TRIGGER0

    CHANNEL2_SEQUENCER_TRIGGER0 = auto()
    CHAN2SEQTRIG0 = CHANNEL2_SEQUENCER_TRIGGER0

    CHANNEL3_SEQUENCER_TRIGGER0 = auto()
    CHAN3SEQTRIG0 = CHANNEL3_SEQUENCER_TRIGGER0

    SOFTWARE_TRIGGER0 = auto()
    SWTRIG0 = SOFTWARE_TRIGGER0


_HW_TRIGGER_LIMIT = _TriggerSource.CHANNEL3_TRIGGER_INPUT1


def _check_trigger_source(trigger):
    try:
        _TriggerSource[trigger.upper()]
    except ValueError:
        print(
            (
                "Trigger source needs to be 'channel[0,3]_trigger_input[0,1]', "
                "'channel[0,3]_sequencer_trigger0' or 'software_trigger0'."
            )
        )


def _check_center_freq(center_freq_hz):
    min_center_freq = 0
    max_center_freq = 8e9
    center_freq_steps = 100e6
    rounding_error = 0.1

    if center_freq_hz < min_center_freq:
        raise ValueError(f"Center frequency must be greater than {min_center_freq}Hz.")
    if center_freq_hz > max_center_freq:
        raise ValueError(f"Center frequency must be less than {max_center_freq}Hz.")
    if center_freq_hz % center_freq_steps > rounding_error:
        raise ValueError(f"Center frequency must be multiple of {center_freq_steps}Hz.")


def _check_in_band_freq(start_freq, stop_freq):
    min_offset_freq = -1e9
    max_offset_freq = 1e9

    if start_freq >= stop_freq:
        raise ValueError("Stop frequency must be larger than start_freq frequency.")
    if start_freq < min_offset_freq:
        raise ValueError(f"Start frequency must be greater than {min_offset_freq}Hz.")
    if stop_freq > max_offset_freq:
        raise ValueError(f"Stop frequency must be less than {max_offset_freq}Hz.")


def _check_io_range(range_dbm, min_range):
    max_range = 10
    range_step = 5
    rounding_error = 0.001
    if range_dbm > max_range + rounding_error:
        raise ValueError(f"Maximum range is {max_range}dBm.")
    if range_dbm < min_range - rounding_error:
        raise ValueError(f"Minimum range is {min_range}dBm.")
    if range_dbm % range_step > rounding_error:
        raise ValueError(f"Range must be multiple of {range_step}dBm.")


def _check_output_range(range_dbm):
    min_range_output = -30
    _check_io_range(range_dbm, min_range_output)


def _check_input_range(range_dbm):
    min_range_input = -50
    _check_io_range(range_dbm, min_range_input)


def _check_output_gain(gain):
    max_gain = 1
    min_gain = 0
    if gain < min_gain or gain > max_gain:
        raise ValueError(f"Output gain must be within [{min_gain}, {max_gain}].")


def _check_envelope_waveform(wave_vector):

    max_envelope_length = 2 ** 16
    if len(wave_vector) > max_envelope_length:
        raise ValueError(
            f"Envelope length exceeds maximum of {max_envelope_length} samples."
        )

    # Note: here, we check that the envelope vector elements are within the unit
    #       circle. This check is repeated by the envelope/wave node but it is
    #       stated here explicitly as a guidance to the user.
    if np.any(np.abs(wave_vector) > 1.0):
        raise ValueError(
            f"The absolute value of each envelope vector element must be smaller than 1."
        )


def _check_mapping(mapping):
    try:
        _Mapping(mapping.lower())
    except ValueError:
        print("Mapping needs to be 'linear' or 'log'.")


def _check_avg_mode(mode):
    try:
        _AveragingMode(mode.lower())
    except ValueError:
        print("Averaging mode needs to be 'cyclic' or 'sequential'.")


def _print_sweep_progress(current, total, freq):
    print(
        f"Measurement ({current}/{total}) at {(freq / 1e6):.3f}MHz." + " " * 20,
        end="\r",
    )


@dataclass
class SweepConfig:
    """Frequency range settings for a sweep"""

    start_freq: float = -300e6  #: minimum frequency for the sweep
    stop_freq: float = 300e6  #: maximum frequency for the sweep
    num_points: int = 100  #: number of frequency points to measure
    mapping: str = "linear"  #: linear or logarithmic frequency axis
    oscillator_gain: float = 1  #: amplitude gain for the oscilator used for modulation


@dataclass
class RfConfig:
    """RF in- and ouput settings for a sweep"""

    channel: int = 0  #: device channel to be used
    input_range: int = -5  #: maximal Range of the Signal Input power
    output_range: int = 0  #: maximal Range of the Signal Output power
    center_freq: float = 5e9  #: Center Frequency of the analysis band


@dataclass
class AvgConfig:
    """Averaging settings for a sweep"""

    integration_time: float = 1e-3  #: total time while samples are integrated
    num_averages: int = 1  #: times to measure each frequency point
    mode: str = "cyclic"
    """averaging mode, which can be "cyclic", to first scan the
    frequency and then repeat, or "sequential", to average
    each point before changing the frequency"""
    integration_delay: float = (
        0.0  #: time delay after the trigger for the integrator to start
    )


@dataclass
class TriggerConfig:
    """Settings for the trigger"""

    source: str = "software_trigger0"  #: trigger source
    level: float = 0.5  #: trigger level
    imp50: bool = True


@dataclass
class EnvelopeConfig:
    """Settings for defining a complex envelope for pulsed spectroscopy"""

    waveform: np.complex128 = np.array([], dtype="complex128")
    delay: float = 0.0  #: time delay the waveform is generated after the trigger


Config = namedtuple("Config", ["sweep", "avg", "rf", "trig"])

# pylint: disable=too-many-instance-attributes
class ShfSweeper:
    """
    Class to set up and run a sweep on an SHFQA

    Arguments:
        daq (zhinst.ziPython.ziDAQServer):
            ziDAQServer object to communicate with a Zurich Instruments data server
        dev (str):
            The ID of the device to run the sweeper with. For example, `dev12004`.
    """

    _sweep = SweepConfig()
    _rf = RfConfig()
    _avg = AvgConfig()
    _trig = TriggerConfig()
    _envelope = None  # the envelope multiplication is enabled if and only if this member is not None

    _shf_sample_rate = 2e9
    _path_prefix = ""
    _result = []

    def __init__(self, daq, dev):
        self._daq = daq
        self._dev = dev
        self._set_path_prefix()

    def run(self):
        """
        Perform a sweep with the specified settings.
        Returns a dictionary with measurement data of the sweep
        """
        self._init_sweep()
        if (
            _TriggerSource[self._trig.source.upper()].value
            == _TriggerSource.SOFTWARE_TRIGGER0.value
        ):
            self._run_freq_sweep()
        else:
            self._run_freq_sweep_trig()
        return self.get_result()

    def get_result(self):
        """
        Returns a dictionary with measurement data of the last sweep
        """
        data = self._get_result_logger_data()
        vec = self._result
        vec = self._average_samples(vec)
        data["vector"] = vec
        props = data["properties"]
        props["centerfreq"] = self._rf.center_freq
        props["startfreq"] = self._sweep.start_freq
        props["stopfreq"] = self._sweep.stop_freq
        props["numpoints"] = self._sweep.num_points
        props["mapping"] = self._sweep.mapping
        return data

    def plot(self):
        """
        Plots power over frequency for last sweep
        """
        import matplotlib.pyplot as plt

        freq = self.get_offset_freq_vector()
        freq_mhz = freq / 1e6
        data = self.get_result()
        power_dbm = utils.volt_rms_to_dbm(data["vector"])
        phase = np.unwrap(np.angle(data["vector"]))
        fig, axs = plt.subplots(2, sharex=True)
        plt.xlabel("freq [MHz]")

        axs[0].plot(freq_mhz, power_dbm)
        axs[0].set(ylabel="power [dBm]")
        axs[0].grid()

        axs[1].plot(freq_mhz, phase)
        axs[1].set(ylabel="phase [rad]")
        axs[1].grid()

        fig.suptitle(f"Sweep with center frequency {self._rf.center_freq / 1e9}GHz")
        plt.show()

    def set_to_device(self):
        """
        Transfer settings to device
        """
        # First, make sure that the configuration is still valid. This is needed
        # since the users might change their instance of the dataclasses
        self._check_config(self._sweep, self._avg, self._rf, self._trig, self._envelope)

        # update path prefix
        self._set_path_prefix()

        # set configuration to device
        self._set_rf_paths()
        self._set_trigger()
        self._set_envelope()
        self._set_spectroscopy_delay()
        self._set_spectroscopy_length()
        self._set_result_averages()
        self._daq.sync()

    def configure(
        self,
        sweep_config=None,
        avg_config=None,
        rf_config=None,
        trig_config=None,
        envelope_config=None,
    ):
        """
        Configure and check the settings

        Arguments:

          sweep_config (SweepConfig, optional): @dataclass containing sweep configuration (None: default configuration applies)

          avg_config (AvgConfig, optional): @dataclass with averaging configuration (None: default configuration applies)

          rf_config (RfConfig, optional): @dataclass with RF configuration (None: default configuration applies)

          trig_config (TriggerConfig, optional): @dataclass with trigger configuration (None: default configuration applies)

          envelope_config: (EnvelopeConfig, optional): @dataclass configuring the envelope for pulse spectroscopy
                                                       (None: the multiplication with the envelope is disabled)
        """

        self._check_config(
            sweep_config, avg_config, rf_config, trig_config, envelope_config
        )

        self._sweep = sweep_config or self._sweep
        self._rf = rf_config or self._rf
        self._avg = avg_config or self._avg
        self._trig = trig_config or self._trig
        # Note: in the case the envelope_config argument is None, the envelope
        # multiplication will be disabled. Hence no "or" statement is used here.
        self._envelope = envelope_config

        self._set_path_prefix()

    def get_configuration(self):
        """
        Returns the configuration of the sweeper class as:
        Config(SweepConfig, AvgConfig, RfConfig, TriggerConfig)
        """
        return Config(self._sweep, self._avg, self._rf, self._trig)

    def get_offset_freq_vector(self):
        """
        Get vector of frequency points
        """
        if self._sweep.mapping == _Mapping.LIN.value:
            freq_vec = np.linspace(
                self._sweep.start_freq, self._sweep.stop_freq, self._sweep.num_points
            )
        else:  # log
            start_f_log = np.log10(self._sweep.start_freq + self._rf.center_freq)
            stop_f_log = np.log10(self._sweep.stop_freq + self._rf.center_freq)
            temp_f_vec = np.logspace(start_f_log, stop_f_log, self._sweep.num_points)
            freq_vec = temp_f_vec - self._rf.center_freq

        return freq_vec

    def _check_config(
        self,
        sweep_config=None,
        avg_config=None,
        rf_config=None,
        trig_config=None,
        envelope_config=None,
    ):

        if rf_config:
            _check_center_freq(rf_config.center_freq)
            _check_input_range(rf_config.input_range)
            _check_output_range(rf_config.output_range)
        if sweep_config:
            _check_in_band_freq(sweep_config.start_freq, sweep_config.stop_freq)
            _check_mapping(sweep_config.mapping)
            _check_output_gain(sweep_config.oscillator_gain)
        if avg_config:
            _check_avg_mode(avg_config.mode)
            self._check_integration_time(avg_config.integration_time)
            self._check_integration_delay(avg_config.integration_delay)
        if trig_config:
            _check_trigger_source(trig_config.source)
        if envelope_config:
            _check_envelope_waveform(envelope_config.waveform)
            self._check_envelope_delay(envelope_config.delay)

    def _get_acquired_node(self):
        return self._path_prefix + "spectroscopy/result/acquired"

    def _get_enable_node(self):
        return self._path_prefix + "spectroscopy/result/enable"

    def _set_rf_paths(self):
        # don't set output/input on/off, keep previous user settings
        self._daq.setInt(self._path_prefix + "input/range", self._rf.input_range)
        self._daq.setInt(self._path_prefix + "output/range", self._rf.output_range)
        self._daq.setDouble(self._path_prefix + "centerfreq", self._rf.center_freq)
        self._daq.setDouble(
            self._path_prefix + "oscs/0/gain", self._sweep.oscillator_gain
        )
        self._daq.setString(self._path_prefix + "mode", "spectroscopy")

    def _set_trigger(self):
        path = (
            f"/{self._dev}/qachannels/{self._rf.channel}/spectroscopy/trigger/channel"
        )
        trig_source = _TriggerSource[self._trig.source.upper()]
        # Note: since the trigger selection node is now public, we can directly
        # use the lower-case string to select the trigger source.
        self._daq.setString(path, self._trig.source.lower())
        if trig_source.value <= _HW_TRIGGER_LIMIT.value:
            # Note: the following index arithmetic is only valid for HW triggers:
            trig_channel = trig_source.value // 2
            trig_input = trig_source.value % 2
            trig_path = f"/{self._dev}/qachannels/{trig_channel}/triggers/{trig_input}/"
            self._daq.setDouble(trig_path + "level", self._trig.level)
            self._daq.setInt(trig_path + "imp50", self._trig.imp50)

    def _set_envelope(self):
        path = f"/{self._dev}/qachannels/{self._rf.channel}/spectroscopy/envelope"
        if self._envelope:
            self._daq.setVector(
                path + "/wave", self._envelope.waveform.astype("complex128")
            )
            self._daq.setInt(path + "/enable", 1)
            self._daq.setDouble(path + "/delay", self._envelope.delay)
        else:
            self._daq.setInt(path + "/enable", 0)

    def _set_path_prefix(self):
        self._path_prefix = f"/{self._dev}/qachannels/{self._rf.channel}/"

    def _set_spectroscopy_delay(self):
        path = f"/{self._dev}/qachannels/{self._rf.channel}/spectroscopy/delay"
        if self._avg:
            self._daq.setDouble(path, self._avg.integration_delay)

    def _set_spectroscopy_length(self):
        spectroscopy_len = round(self._avg.integration_time * self._shf_sample_rate)
        self._daq.setInt(self._path_prefix + "spectroscopy/length", spectroscopy_len)

    def _set_result_averages(self):
        # Note: averaging is done in Python, not in the result-logger on the device
        self._daq.setInt(self._path_prefix + "spectroscopy/result/averages", 1)

    def _wait_for_node(self, node_path, expected_val, time_out=1, sleep_time=0.1):
        elapsed_time = 0
        while elapsed_time < time_out:
            val = self._daq.getInt(node_path)
            if val == expected_val:
                return
            time.sleep(sleep_time)
            elapsed_time += sleep_time
        raise TimeoutError(
            f'Node "{node_path}" did not change to {expected_val} within {time_out}sec.'
        )

    def _get_freq_vec(self):
        single_freq_vec = self.get_offset_freq_vector()
        return self._concatenate_freq_vecs(single_freq_vec)

    def _concatenate_freq_vecs(self, single_freq_vec):
        triggered_sequential = (
            self._avg.mode.lower() == _AveragingMode.SEQUENTIAL.value
            and not (
                _TriggerSource[self._trig.source.upper()].value
                == _TriggerSource.SOFTWARE_TRIGGER0.value
            )
        )
        if self._avg.num_averages == 1 or triggered_sequential:
            freq_vec = single_freq_vec
        elif self._avg.mode == _AveragingMode.CYCLIC.value:
            num_concatenate = self._avg.num_averages - 1
            freq_vec = single_freq_vec
            while num_concatenate > 0:
                num_concatenate -= 1
                freq_vec = np.concatenate((freq_vec, single_freq_vec), axis=None)
        else:  # sequential + sw_trigger
            freq_vec = np.zeros(self._avg.num_averages * self._sweep.num_points)
            for i, f in enumerate(single_freq_vec):
                for j in range(self._avg.num_averages):
                    ind = i * self._avg.num_averages + j
                    freq_vec[ind] = f

        return freq_vec

    def _init_sweep(self):
        self.set_to_device()
        self._stop_result_logger()
        self._daq.sync()

    def _stop_result_logger(self):
        enable_path = self._get_enable_node()
        self._daq.setInt(enable_path, 0)
        self._daq.sync()
        self._wait_for_node(enable_path, 0)

    def _issue_single_sw_trigger(self):
        self._daq.syncSetInt(f"/{self._dev}/system/swtriggers/0/single", 1)

    def _enable_measurement(self):
        self._daq.syncSetInt(self._get_enable_node(), 1)

    def _get_data_after_measurement(self):
        data = self._get_result_logger_data()
        return data["vector"]

    def _set_freq_to_device(self, freq):
        self._daq.syncSetDouble(
            f"/{self._dev}/qachannels/{self._rf.channel}/oscs/0/freq", freq
        )

    def _wait_for_results_hw_trig(self, freq, num_results):
        enable_node = self._get_enable_node()
        acquired_node = self._get_acquired_node()

        poll_time = 0.05
        result_timeout = 10  # seconds

        # avoid too many iterations but print often enough
        print_interval = 0.5  # seconds

        elapsed_time_since_result = 0
        elapsed_time_since_print = print_interval  # force print in first iteration
        results = 0

        while elapsed_time_since_result < result_timeout:
            poll_start = time.perf_counter()
            poll_results = self._daq.poll(poll_time, timeout_ms=10, flat=True)
            poll_duration = time.perf_counter() - poll_start
            if acquired_node in poll_results:
                results = poll_results[acquired_node]["value"][-1]
                elapsed_time_since_result = 0
            else:
                elapsed_time_since_result += poll_duration

            if elapsed_time_since_print >= print_interval:
                _print_sweep_progress(results, num_results, freq)
                elapsed_time_since_print = 0
            else:
                elapsed_time_since_print += poll_duration

            if results == num_results:
                # we are done - but we must report the final progress
                _print_sweep_progress(results, num_results, freq)
                self._wait_for_node(enable_node, 0, time_out=1)
                return

        if results > 0:
            err = f"failed to get a new result in {result_timeout} seconds, so far only got {results}!"
        else:
            err = f"failed to get any result in {result_timeout} seconds!"
        raise TimeoutError(err)

    def _wait_for_results_sw_trig(self, expected_results, wait_time=1):
        acquired_node = self._get_acquired_node()
        # leave margin for the swtrigger and the dataserver to be updated
        wait_time = 1.2 * (wait_time + 0.3)
        # iterate often (20ms) to improve performance
        self._wait_for_node(
            acquired_node, expected_results, time_out=wait_time, sleep_time=0.02
        )

    def _run_freq_sweep(self):
        self._print_sweep_details()
        freq_vec = self._get_freq_vec()
        self._set_result_len()
        self._enable_measurement()

        for i, freq in enumerate(freq_vec):
            self._set_freq_to_device(freq)
            _print_sweep_progress(i + 1, len(freq_vec), freq)
            self._issue_single_sw_trigger()
            self._wait_for_results_sw_trig(
                expected_results=i + 1, wait_time=self._avg.integration_time
            )

        self._wait_for_node(self._get_enable_node(), 0, time_out=1)
        self._result = self._get_data_after_measurement()

    def _run_freq_sweep_trig(self):
        self._print_sweep_details()
        freq_vec = self._get_freq_vec()
        num_results = self._set_result_len()
        self._result = []
        acquired_node = self._get_acquired_node()
        self._daq.subscribe(acquired_node)

        for freq in freq_vec:
            self._set_freq_to_device(freq)
            self._enable_measurement()
            try:
                self._wait_for_results_hw_trig(freq, num_results)
            except TimeoutError:
                self._daq.unsubscribe(acquired_node)
                raise

            self._result = np.append(self._result, self._get_data_after_measurement())

        self._daq.unsubscribe(acquired_node)

    def _print_sweep_details(self):
        detail_str = (
            f"Run a sweep with {self._sweep.num_points} frequency points in the range of "
            f"[{self._sweep.start_freq / 1e6}, {self._sweep.stop_freq / 1e6}] MHz + "
            f"{self._rf.center_freq / 1e9} GHz. \n"
            f"Mapping is {self._sweep.mapping}. \n"
            f"Integration time = {self._avg.integration_time} sec. \n"
            f"Measures {self._avg.num_averages} times per frequency point. \n"
            f"Averaging mode is {self._avg.mode}."
        )
        print(detail_str)

    def _set_result_len(self):
        if (
            _TriggerSource[self._trig.source.upper()].value
            == _TriggerSource.SOFTWARE_TRIGGER0.value
        ):
            num_results = self._sweep.num_points * self._avg.num_averages
        elif self._avg.mode.lower() == _AveragingMode.SEQUENTIAL.value:
            num_results = self._avg.num_averages
        else:
            num_results = 1
        self._daq.setInt(self._path_prefix + "spectroscopy/result/length", num_results)
        return num_results

    def _get_result_logger_data(self):
        result_node = self._path_prefix + "spectroscopy/result/data/wave"
        data = self._daq.get(result_node, flat=True)
        return data[result_node.lower()][0]

    def _average_samples(self, vec):
        if self._avg.num_averages == 1:
            return vec

        avg_vec = np.zeros(self._sweep.num_points, dtype="complex")
        if self._avg.mode == _AveragingMode.CYCLIC.value:
            total_measurements = self._sweep.num_points * self._avg.num_averages
            for i in range(self._sweep.num_points):
                avg_range = range(i, total_measurements, self._sweep.num_points)
                avg_vec[i] = np.mean(vec[avg_range])
        else:  # sequential
            for i in range(self._sweep.num_points):
                start_ind = i * self._avg.num_averages
                avg_range = range(start_ind, start_ind + self._avg.num_averages)
                avg_vec[i] = np.mean(vec[avg_range])

        return avg_vec

    def _check_integration_time(self, integration_time_s):
        max_int_len = ((2 ** 23) - 1) * 4
        min_int_len = 4
        max_integration_time = max_int_len / self._shf_sample_rate
        min_integration_time = min_int_len / self._shf_sample_rate
        if integration_time_s < min_integration_time:
            raise ValueError(
                f"Integration time below minimum of {min_integration_time}s."
            )
        if integration_time_s > max_integration_time:
            raise ValueError(
                f"Integration time exceeds maximum of {max_integration_time}s."
            )

    def _check_delay(self, resolution_ns, min_s, max_s, val_s):
        if val_s > max_s or val_s < min_s:
            raise ValueError(f"Delay out of bounds! {min_s} <= delay <= {max_s}")
        if (val_s * 1e9) % resolution_ns != 0:
            raise ValueError(f"Delay not in multiples of {resolution_ns} ns.")

    def _check_integration_delay(self, integration_delay_s):
        resolution_ns = 2
        max_s = 131e-6
        self._check_delay(resolution_ns, 0, max_s, integration_delay_s)

    def _check_envelope_delay(self, delay_s):
        resolution_ns = 2
        max_s = 131e-6
        self._check_delay(resolution_ns, 0, max_s, delay_s)
