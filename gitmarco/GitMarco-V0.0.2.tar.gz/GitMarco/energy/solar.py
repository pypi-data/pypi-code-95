import datetime
import matplotlib.pyplot as plt
import pysolar
plt.style.use('seaborn-darkgrid')


class DirectRadiation(object):
    def __init__(self, latitude: float,
                 longitude: float,
                 nmin: int,
                 start_year: int,
                 start_day: int,
                 start_month: int,
                 timezone: int = 0,
                 surface: float = 1.0):
        """
        :param latitude: latitude
        :param longitude: longitude
        :param nmin: number of minutes to be considered
        :param start_year: starting date year
        :param start_day: starting date day
        :param start_month: starting date month
        :param timezone: desired timezone (i.e. Rome => +1)
        :param surface: planar radiated surface

        DirectRadiation class
        """
        self.latitude = latitude
        self.longitude = longitude
        self.nmin = nmin
        self.start_year = start_year
        self.start_day = start_day
        self.start_month = start_month
        self.actual_timezone = timezone
        self.surface = surface

        # Dates, altitudes, radiations
        self.dates, self.altitudes_deg, self.radiations = list(), list(), list()

        self.timezone = datetime.timezone(datetime.timedelta(hours=self.actual_timezone))
        self.start = datetime.datetime(self.start_year, self.start_month, self.start_day, tzinfo=self.timezone)

    def estimate_direct_radiation(self):
        # Iterating for hours in nhr
        for imin in range(self.nmin):
            # Actual Date
            date = self.start + datetime.timedelta(minutes=imin)

            #  Getting actual altitude from latitude, longitude and date
            altitude_deg = pysolar.solar.get_altitude(self.latitude, self.longitude, date)

            # Setting radion to 0 if the altidune in below 0
            if altitude_deg <= 0:
                radiation = 0.
            else:
                radiation = pysolar.radiation.get_radiation_direct(date, altitude_deg)

            # Appending results
            self.dates.append(date)
            self.altitudes_deg.append(altitude_deg)
            self.radiations.append(radiation)

    def plot_direct_radiation(self):
        days = [imin / 24 / 60 for imin in range(self.nmin)]
        fig, axs = plt.subplots(nrows=2,
                                ncols=1,
                                sharex=True,
                                figsize=(12, 12))
        axs[0].plot(days, self.altitudes_deg)
        axs[0].set_title('Solar altitude, degrees')
        axs[1].plot(days, self.radiations)
        axs[1].set_title('Solar radiation, W/m2')
        axs[1].set_xlabel('Days since ' + self.start.strftime('%Y/%m/%d %H:%M UTC'))
        plt.show()