from typing import Union
from math import floor, fmod, pi, cos, sin

from openspace.configs.formats import STANDARD_EPOCH_FMT
import openspace.math.time_conversions as tc

Number = Union[float, int]

class Distance:

    BASE_UNIT = "meters"
    BASE_CONVERSION_MULTIPLE = {
        "kilometers":1e-3,
        "centimeters":1e2,
        "millimeters":1e3,
        "micrometers":1e6,
        "nanometers":1e9,
        "astronomical units":1/(1.495978707e11),
        "feet":1/.3048,
        "inches":1/.3048*12,
        "miles":1/.3048/5280,
        "lightyears":1.057e-16,
        "parsecs":3.24078e-17,
        "nautical miles":1/.3048/6076.115,
        "meters":1}

    def __init__(self, value:Number, units:str):
        
        if units==self.BASE_UNIT:
            self.base = value
        elif self.BASE_CONVERSION_MULTIPLE.get(units) is not None:
            self.base = value/self.BASE_CONVERSION_MULTIPLE[units]
        else:
            return None

    def to_unit(self, units:str):
        return self.base*self.BASE_CONVERSION_MULTIPLE[units]
            
class Angle:

    SECONDS_IN_MINUTE = 60
    MINUTES_IN_DEGREE = 60
    DEGREES_IN_HOUR = 15
    BASE_UNIT = "radians"
    BASE_CONVERSION_MULTIPLE = {
        "radians":1,
        "degrees":180/pi,
        "revolutions":1/(2*pi)
    }

    def __init__(self, value:Number, units:str):
        
        if units==self.BASE_UNIT:
            self.base = value
        elif self.BASE_CONVERSION_MULTIPLE.get(units) is not None:
            self.base = value/self.BASE_CONVERSION_MULTIPLE[units]
        else:
            return None

    @classmethod
    def from_degree_minute_second(self, deg, min, sec):
        
        #preserve sign of angle
        if deg < 0:
            sign = -1
        else:
            sign = 1

        #absolute value of degrees
        d = abs(deg)

        #seconds to minutes
        dm = sec/self.SECONDS_IN_MINUTE

        #total minutes
        dm+=min

        #minutes to degree
        d+=dm/self.MINUTES_IN_DEGREE

        d*=sign

        return self(d, "degrees")

    @classmethod
    def from_hour_minute_second(self, hr, min, sec):
        return self.from_degree_minute_second(hr*15, min, sec)

    def to_degree_minute_second(self):
        degs = self.to_unit("degrees")
        if degs < 0:
            sign = -1
        else:
            sign = 1

        d = floor(abs(degs))
        m = floor((abs(degs) - d)*self.MINUTES_IN_DEGREE)
        s = ((abs(degs) - d)*self.MINUTES_IN_DEGREE - m)*self.SECONDS_IN_MINUTE

        return (sign*d, sign*m, sign*s)

    def to_hour_minute_second(self):
        degs = self.to_unit("degrees")
        if degs < 0:
            sign = -1
        else:
            sign = 1

        h = floor(abs(degs/15))
        m = floor((abs(degs/15) - h)*self.MINUTES_IN_DEGREE)
        s = ((abs(degs/15)-h)*self.MINUTES_IN_DEGREE-m)*self.SECONDS_IN_MINUTE

        return (sign*h, sign*m, sign*s)

    def to_unit(self, units:str):
        if self.BASE_CONVERSION_MULTIPLE.get(units) is not None:
            return self.base*self.BASE_CONVERSION_MULTIPLE[units]
        elif units=="DMS":
            return self.to_degree_minute_second()
        elif units=="HMS":
            return self.to_hour_minute_second()
        else:
            return None

class Epoch:
    
    def __init__(self, epoch_str:str, fmt:str):
        self.timestamp = tc.epoch_string_to_timestamp(epoch_str, fmt)

    @classmethod
    def from_julian_date(cls, jDate):
        return cls(
            tc.julian_date_to_epoch_string(jDate, STANDARD_EPOCH_FMT), 
            STANDARD_EPOCH_FMT
            )

    @classmethod
    def from_timestamp(cls, tstamp):
        ep = tc.timestamp_to_epoch_string(tstamp, STANDARD_EPOCH_FMT)
        return cls(ep, STANDARD_EPOCH_FMT)

    def to_datetime(self):
        return tc.timestamp_to_datetime(self.timestamp)
        
    def to_string_format(self, fmt):
        return tc.timestamp_to_epoch_string(self.timestamp, fmt)

    def to_julian_date(self):
        return tc.timestamp_to_julian_date(self.timestamp)

    def get_time_delta(self, epoch_to_subtract):
        d1 = tc.timestamp_to_datetime(self.timestamp) 
        d2 = tc.timestamp_to_datetime(epoch_to_subtract.timestamp)
        return (d1 - d2)

    def to_modified_julian_date(self):
        return tc.timestamp_to_modified_julian_date(self.timestamp)

    def minus_seconds(self, seconds):
        new_epoch_str = tc.timestamp_to_epoch_string(
            self.timestamp-seconds, 
            STANDARD_EPOCH_FMT
            )
        return Epoch(new_epoch_str, STANDARD_EPOCH_FMT)

    def add_seconds(self, seconds):
        new_epoch_str = tc.timestamp_to_epoch_string(
            self.timestamp+seconds, 
            STANDARD_EPOCH_FMT
            )
        return Epoch(new_epoch_str, STANDARD_EPOCH_FMT)

    def to_hours_minutes_seconds(self):
        hrs = float(self.to_string_format("%H"))
        mins = float(self.to_string_format("%M"))
        secs = float(self.to_string_format("%S.%f"))
        return hrs, mins, secs

    def get_ut1_julian_centuries_past_j2000(self, eop):
        j2000_ut1 = Epoch("Jan 01 2000 12:00:00.000", STANDARD_EPOCH_FMT)
        epoch_ut1 = self.add_seconds(eop.ut1_minus_utc)

        d_u = epoch_ut1.get_time_delta(j2000_ut1).days + .5
        t_u = d_u/36525

        return t_u

    def to_gmst_decimal_day(self, eop):

        t_u = self.get_ut1_julian_centuries_past_j2000(eop)

        gmst_hr = 6
        gmst_min = 41
        gmst_sec = 50.54841+8640184.812866*t_u+.093104*t_u**2-6.2e-6*t_u**3

        utc_hrs, utc_min, utc_sec = self.to_hours_minutes_seconds()

        gmst_0h_ut1 = tc.time_to_decimal_day(
            gmst_hr, 
            gmst_min, 
            gmst_sec
            )
        gmst_0h_ut1*=tc.SECONDS_IN_DAY

        universal_to_sidereal = 1.002737909350795+5.9006e-11*t_u-5.9e-15*t_u**2

        gmst = gmst_0h_ut1 + universal_to_sidereal*(
            eop.ut1_minus_utc + 
            tc.time_to_decimal_day(utc_hrs, utc_min, utc_sec)*tc.SECONDS_IN_DAY
            )
        
        gmst_in_decimal_day = fmod(gmst, tc.SECONDS_IN_DAY)/tc.SECONDS_IN_DAY

        return gmst_in_decimal_day

    def to_gst_decimal_day(self, eop):

        t_u = self.get_ut1_julian_centuries_past_j2000(eop)

        epsilon_sec = 84381.448 - 46.8150*t_u - .00059*t_u**2 + .001813*t_u**3
        epsilon = Angle.from_degree_minute_second(
            0, 
            0, 
            epsilon_sec
            ).to_unit("radians")
        
        omega_deg = 125.04455501
        omega_sec = (
            -6962890.2665*t_u + 
            7.4722*t_u**2 + 
            .007702*t_u**3 - 
            .00005939*t_u**4
            )
        omega = Angle.from_degree_minute_second(
            omega_deg, 
            0, 
            omega_sec
            ).to_unit("radians")

        gmst_decimal_day = self.to_gmst_decimal_day(eop)

        d, m, s = Angle(gmst_decimal_day, "revolutions").to_unit("DMS")
        d += Angle(eop.delta_psi, "degrees").to_unit("radians")*cos(epsilon)
        print(eop.delta_psi)
        s += .00264*sin(omega) + .000063*sin(2*omega)

        return Angle.from_degree_minute_second(
            d, 
            m, 
            s + eop.ut1_minus_utc
            ).to_unit("HMS")

class FinalsAll:
    def __init__(self, finals_dot_all_path):
        self.filepath = finals_dot_all_path
        self.read_data()

    def read_data(self):
        with open(self.filepath, "r") as f:
            lines = f.readlines()

        self.eop_by_date = {}
        last_psi = ""
        last_epsilon = ""
        for line in lines[1:]:
            contents = line.split(";")
            if contents[5] == "":
                break

            if contents[15] == "":
                contents[15] = last_psi
            else:
                last_psi = contents[15]

            if contents[17] == "":
                contents[17] = last_epsilon
            else:
                last_epsilon = contents[17]

            self.eop_by_date[int(contents[0])] = EOP(contents)

    def get_eop_by_epoch(self, epoch):
        mjd = epoch.to_modified_julian_date()
        return self.eop_by_date[int(mjd)]



class EOP:
    def __init__(self, finals_line_list):
        self.x_pole = Angle.from_degree_minute_second(
            0, 
            0, 
            float(finals_line_list[5])
            ).to_unit("radians")
        self.y_pole = Angle.from_degree_minute_second(
            0, 
            0, 
            float(finals_line_list[7])
            ).to_unit("radians")
        self.ut1_minus_utc = float(finals_line_list[10])
        self.delta_psi = float(finals_line_list[15])
        self.delta_epsilon = float(finals_line_list[17])

            