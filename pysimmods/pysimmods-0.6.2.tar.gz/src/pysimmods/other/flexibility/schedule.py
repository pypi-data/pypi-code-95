"""This module contains the :class:`.Schedule` that is used by the
:class:`.ForecastModel` and :class:`.FlexibilityModel`.

"""
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from . import LOG


class Schedule:
    """Schedule class for the :class:`.ForecastModel`.

    Calling the schedule obj like this::

        df = schedule()

    returns the data frame that stores the schedule.


    Parameters
    ----------

    """

    def __init__(
        self,
        start_date,
        step_size,
        pname,
        qname,
        forecast_horizon_hours=1,
    ):
        self._data = None
        self._forecast_horizon_hours = forecast_horizon_hours
        self._pname = pname
        self._qname = qname

        self.now_dt = start_date
        self.step_size = step_size

    def init(self):
        """Initialize the schedule data frame.

        After initialization, the schedule's data frame should have
        three columns *target*, *p_kw*, and *q_kvar* and a number of
        rows, each value initialized with np.nan.

        The number of rows is defined by the
        :attr:`_forecast_horizon_hours` as seconds divided by the
        :attr:`step_size`.

        """
        LOG.debug("Creating new schedule dataframe")
        index = pd.date_range(
            self.now_dt,
            self.now_dt
            + timedelta(hours=self._forecast_horizon_hours)
            - timedelta(seconds=self.step_size),
            freq=f"{self.step_size}S",
        )

        self._data = pd.DataFrame(
            columns=["target", self._pname, self._qname], index=index
        )

    def update(self, other):
        """Update this schedules' data with another dataframe.

        Parameters
        ----------
        other : pandas.DataFrame
            A dataframe with datetime as index and values for the
            columns *"target"*, *"p_kw"*, and *"q_kvar"*. Note that
            :attr:`pname` and :attr:`qname` match in both data frames.

        """
        if self._data is None:
            self.init()

        for index, _ in other.iterrows():
            if index not in self._data.index:
                break

        self._data.update(other.loc[:index])
        self._data = self._data.append(other.loc[index:])
        self._data = self._data[~self._data.index.duplicated()]

    def update_row(self, index, setpoint, p_val, q_val):
        if index in self._data.index:
            self._data.loc[index]["target"] = setpoint
            self._data.loc[index][self._pname] = p_val
            self._data.loc[index][self._qname] = q_val
        else:
            self._data = self._data.append(
                pd.DataFrame(
                    data={
                        "target": setpoint,
                        self._pname: p_val,
                        self._qname: q_val,
                    },
                    index=[index],
                )
            )

    def update_entry(self, index, col, val):
        self._data.loc[index][col] = val

    def has_index(self, index):
        return index in self._data.index

    def reschedule_required(self):
        """Check if a reschedule is required.

        The current schedule is checked for the next hours, specified
        by :attr:`_forecast_horizon_hours*. A reschedule is required
        when on of the indices is missing of one of the values within
        the limit is np.nan.

        Returns
        -------
        bool
            *True* when a reschedule is required and *False* otherwise.
        """
        now = self.now_dt + timedelta(seconds=self.step_size)
        limit = int(self._forecast_horizon_hours * 3_600 / self.step_size)
        reschedule = False

        for counter in range(limit):
            if now not in self._data.index:
                return True
            elif np.isnan(self._data.loc[now]["target"]):
                return True
            elif np.isnan(self._data.loc[now][self._pname]):
                return True
            elif np.isnan(self._data.loc[now][self._qname]):
                return True
            else:
                now += timedelta(seconds=self.step_size)

        return False

    def prune(self):
        self._data = self._data.loc[self.now_dt :]

    def get(self, col, now=None):
        """Return the value for a certain column.

        If no time index is provided, the current datetime object of
        the schedule is used.

        Returns
        -------
        np.float
            The value of the specified column at index *now*.

        """
        if now is None:
            now = self.now_dt

        return self._data.loc[now][col]

    def __call__(self):
        return self._data

    def from_dataframe(self, dataframe):
        # TODO:
        pass
