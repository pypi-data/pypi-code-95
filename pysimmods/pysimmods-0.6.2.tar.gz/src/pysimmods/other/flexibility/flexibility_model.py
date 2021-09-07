"""This module contains the flexibility model."""
from datetime import datetime, timedelta

import numpy as np

import pandas as pd
from pysimmods.util.dateformat import GER

from .forecast_model import ForecastModel


class FlexibilityModel(ForecastModel):
    """The flexibility model for all pysimmods."""

    def generate_schedules(self, start, forecast_horizon_hours, num_schedules):
        """Perform sampling and generate a set of schedules for the
        specified time interval.

        Args:
            start (str): Is the start of the planning horizon for which
                the sampling is done. It has to be provided as ISO 8601
                timezone string such as '2020-06-22 12:00:00+0000'

            forecast_horizon_hours (int): The planning horizon is divided into.

        """
        state_backup = self.model.get_state()
        step_size = self.step_size

        now_dt = self.now_dt
        start_dt = datetime.strptime(start, GER)
        end_dt = (
            start_dt
            + timedelta(hours=forecast_horizon_hours)
            - timedelta(seconds=step_size)
        )
        periods = forecast_horizon_hours * 3_600 / step_size

        # Fast forward to the planning interval
        while start_dt > now_dt:
            try:
                self._perform_step(
                    now_dt,
                    self.schedule.get("target", now_dt) / self.percent_factor,
                )
                now_dt += timedelta(seconds=step_size)
            except KeyError:
                return dict()

        index = pd.date_range(start_dt, end_dt, periods=periods)

        self.flexibilities = dict()

        for schedule_id in range(num_schedules):
            schedule = self._generate_schedule(
                pd.DataFrame(
                    columns=["target", self.pname, self.qname], index=index
                )
            )

            self.flexibilities[schedule_id] = schedule

        self.model.set_state(state_backup)
        return self.flexibilities

    def _generate_schedule(self, dataframe):
        num_steps = len(dataframe.index)
        dataframe["target"] = self.rng.uniform(size=num_steps) / (
            0.01 / self.percent_factor
        )

        state_backup = self.model.get_state()
        for index, row in dataframe.iterrows():
            try:
                self._perform_step(index, row["target"])
                dataframe.loc[index, self.pname] = (
                    self.model.p_kw * self.unit_factor
                )
                dataframe.loc[index, self.qname] = (
                    self.model.q_kvar * self.unit_factor
                )

            except KeyError:
                # Forecast is missing
                dataframe.loc[index, self.pname] = np.nan
                dataframe.loc[index, self.qname] = np.nan
                dataframe.loc[index, "target"] = np.nan
        self.model.set_state(state_backup)

        return dataframe
