from time import sleep
from datetime import datetime
import subprocess
from enum import IntEnum

import RPi.GPIO as gpio

from .base import PWMDevice


class SM(IntEnum):
    """ Variable positions inside speed_mapping """
    TEMP = 0
    SPEED = 1


class Fan(PWMDevice):
    """ Class for controlling a fan. You can use any fan that has at least 2 wires.
    If your fan has 3-4 wires (sense and PWM) you can control it with PWM signal,
    and even measure it's RPM (this can be inaccurate).
    You need either power or pwm (or both) pins defined to control the fan!

    -:param power: Pin used for giving power supply to the fan (through a relay or fet module)
    -:param sense: Pin used for measuring RPM
    -:param pwm: Pin used for PWM control
    -:param cycletime: Cycle time of auto fan control (s)
    -:param frequency: Frequency used for the pwm signal (hz)
    -:param idle_limit: If fan is on automode, and the temp is below min, only turn off after this limit is reached (s)
    -:param speed_mapping: This is used to match temperature readings to fan speed
        Values are series of tuples in form of: (from_temp, duty_cycle)
    -:param rpm_measurement_timeout: Timeout for the edge detection (ms)
    -:param rpm_measurement_edges: How many edges to record for the calculation
    -:param rpm_measurement_bouncetime: After an edge detection, the next edge will be ignored for this duration (ms)
        This value is in miliseconds, and should be less than the time for half revolution on maximum speed.
        Calculation: rev_per_sec = max_rpm / 60 --> 1000 / rev_per_sec / 2 = max_bouncetime
    """
    def __init__(self, power=False, sense=False, pwm=False, cycletime=5, frequency=25000, idle_limit=300,
                 speed_mapping=False, rpm_measurement_timeout=2000, rpm_measurement_edges=40,
                 rpm_measurement_bouncetime=10, **kwargs):
        super().__init__(pwm, power, frequency, **kwargs)
        self.idle_limit = idle_limit
        self.speed_mapping = speed_mapping or [
            (20, 1),
            (40, 30),
            (70, 50),
            (75, 70),
            (80, 100)
        ]
        self.cycletime = cycletime
        self.rpm_measurement_timeout = rpm_measurement_timeout
        self.rpm_measurement_edges = rpm_measurement_edges
        self.rpm_measurement_bouncetime = rpm_measurement_bouncetime
        # GPIO pin setup
        self.sense = sense
        if sense:
            gpio.setup(sense, gpio.IN, pull_up_down=gpio.PUD_UP)
        if not power and not pwm:
            raise ValueError('No pins provided for controlling the fan!')

    def set_speed(self, percent):
        """ Set fan speed.

        -:param percent: Fan speed between 0% and 100%
        """
        z_off = True
        # If the desired speed is very low, convert it
        # because some fans doesn`t run on lowest speed if the value is not 0.
        if 0 < percent <= 1:
            percent = 0
            z_off = False
        self.set_duty_cycle(percent, z_off)

    def smart_set_speed(self, percent):
        """ Set fan speed with respect to other parameters """
        # If the desired speed is 0, but the fan not reached the idle limit, set idle speed
        if percent == 0 and self.is_on() and self.ontime() < self.idle_limit:
            percent = 1
        self.set_speed(percent)

    def read_hw_temperature(self):
        """ Read hardware temperatures """
        cpu_temp = round(int(subprocess.check_output(['cat', '/sys/class/thermal/thermal_zone0/temp']).strip()) / 1000)
        self.message(f'Temperature reading {cpu_temp}c.')
        return cpu_temp

    def measure_rpm(self):
        """ Measure fan rpm.

        Note: Measuring RPM from a script running under an OS (with many other things) can be inaccurate.
        You can improve it by fine tune the "rpm_measurement_..." variables for a given fan.
        """
        if not self.sense:
            raise ValueError('No pin was provided for sensing rpm.')
        edges = self.rpm_measurement_edges
        start_time = datetime.now()
        for _ in range(edges):
            channel = gpio.wait_for_edge(self.sense, gpio.FALLING,
                                         timeout=self.rpm_measurement_timeout,
                                         bouncetime=self.rpm_measurement_bouncetime)
            if channel is None:
                self.message('RPM measurement timeout.')
                edges = 0
                break
        end_time = datetime.now()
        difference = (end_time - start_time).total_seconds()
        rpm = int((edges * (60 / difference)) / 2)
        self.message(f'Current rpm: {rpm}')
        return rpm

    def temp_to_speed(self, temp):
        """ Determine speed setting for the current temperature.

        -:param temp: Temperature in celsius
        """
        # If the temp is below the minimum level, we dont need further processing
        if temp < self.speed_mapping[0][SM.TEMP]:
            self.message('Temperature below minimum.')
            return 0

        for i in range(len(self.speed_mapping)):
            current_mapping = self.speed_mapping[i]
            next_mapping = self.speed_mapping[i+1] if len(self.speed_mapping) > i+1 else (500, 100)
            if current_mapping[SM.TEMP] <= temp < next_mapping[SM.TEMP]:
                return current_mapping[SM.SPEED]

    def auto_set(self, temp=False):
        """ Set fan speed automatically based on temperature and the speedmap

        -:param temp: Provide a temperature value, otherwise the CPU temp will be used
        """
        ctemp = temp or self.read_hw_temperature()
        speed = self.temp_to_speed(ctemp)
        self.smart_set_speed(speed)
        sleep(self.cycletime)
