from datetime import date, timedelta
from gcsa.google_calendar import GoogleCalendar
from google.oauth2.credentials import Credentials
from matplotlib.ticker import MaxNLocator
import numpy as np
import os
import pandas as pd


class Calendar():

    def __init__(self):
        self.__gcal_credentials__ = self.__get_gcal_credentials__()
        self.calendar = GoogleCalendar(credentials=self.__gcal_credentials__)

    def __get_gcal_credentials__(self):
        """Fetch credentials from env to authenticate against calendar."""
        return Credentials(token=os.environ["TOKEN"],
                           refresh_token=os.environ["REFRESH_TOKEN"],
                           client_id=os.environ["CLIENT_ID"],
                           client_secret=os.environ["CLIENT_SECRET"],
                           token_uri="https://oauth2.googleapis.com/token")


class Timesheet(Calendar):

    def __init__(self, days=90):
        super().__init__()
        self.end = date.today()
        self.start = self.end - timedelta(days=days)
        self.data = self.__get_timesheet__()
        clocked_on = self.data.iloc[-1]['clocked_off'] is None
        self.status = "Clocked On" if clocked_on else "Clocked Off"

    def __get_timecards__(self):
        """Fetch calendar events with 'clocked' in title."""
        return self.calendar.get_events(time_min=self.start,
                                        time_max=self.end,
                                        query="clocked")

    def __get_timesheet__(self):
        """Construct pandas DataFrame of clock on / clock off events."""
        # Create DataFrame from gcsa events
        cards = pd.DataFrame([{"time": timecard.start,
                               "event": timecard.summary}
                              for timecard in self.__get_timecards__()])

        # Preallocate dataframe for transformed data
        sheet = pd.DataFrame({"clocked_on": None,
                              "clocked_off": None},
                             index=cards["time"].dt.date.unique())

        # Loop over cards and add to correct position in timesheet
        for i, row in cards.iterrows():
            event_type = ("clocked_on" if "on" in row["event"].lower()
                          else "clocked_off")
            sheet.loc[row["time"].date(), event_type] = row["time"].time()

        # Compute hours worked from clocked on and clocked off data
        sheet["shift_length"] = (
            pd.to_datetime(sheet["clocked_off"].dropna().astype(str),
                           format='%H:%M:%S')
            - pd.to_datetime(sheet["clocked_on"].dropna().astype(str),
                             format='%H:%M:%S')
        ).dt.seconds / (60 ** 2)

        return sheet

    def get_last_n_shifts(self, n=90):
        return self.data.dropna().iloc[-n:]

    def summarise(self, n=90, dp=2):
        agg = {"Average Working Day (mean)": np.mean,
               "Average Working Week (mean)": np.mean,
               "Shortest Working Day": np.min,
               "Longest Working Day": np.max}
        summary = self.get_last_n_shifts(n)["shift_length"].agg(agg).round(dp)
        summary["Average Working Week (mean)"] *= 5
        return summary

    def hist(self, n=90):
        ax = self.get_last_n_shifts(n)["shift_length"].plot(kind="hist")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlabel("Length of working day (Hours)")
        ax.set_ylabel("Frequency")
        return ax.get_figure(), ax

    def time_series(self, n=90):
        ax = self.get_last_n_shifts(n)["shift_length"].plot(legend=False,
                                                            rot=45)
        ax.set_ylabel("Length of working day (Hours)")
        ax.set_xlabel("Date")
        return ax.get_figure(), ax

    def boxplot(self, n=90):
        c = "C0"
        ax = self.get_last_n_shifts(n)["shift_length"].plot(
            kind="box",
            vert=False,
            boxprops=dict(color=c),
            capprops=dict(color=c),
            whiskerprops=dict(color=c),
            flierprops=dict(color=c, markeredgecolor=c),
            medianprops=dict(color=c))
        ax.set_yticks([])
        ax.set_xlabel("Length of working day (Hours)")
        return ax.get_figure(), ax


class Planner(Calendar):

    def __init__(self, days=90):
        super().__init__()
        self.days = days
        self.start = date.today()
        self.end = self.start + timedelta(days=self.days)
        self.events = self.__get_events__()

    def __get_events__(self):
        """Construct pandas DataFrame of all calendar events."""
        # Create DataFrame from gcsa events
        events = self.calendar.get_events(time_min=self.start,
                                          time_max=self.end)
        events = pd.DataFrame([{"start": event.start,
                                "end": event.end,
                                "event": event.summary}
                              for event in events if event.start is not None])

        # Label CLI/PRJ events
        events["id"] = events["event"].str.extract("([A-Z]{2,4}/[A-Z]{2,4})")

        # Identify teaching events
        jr_tr_mask = events["event"].str.match("\[[A-Z]{2,4}\]") # noqa W605
        # Construct CLI/TR ids
        jr_tr_id = events.loc[jr_tr_mask,
                              "event"].str.replace("\[([A-Z]{2,4})\].*", # noqa W605
                                                   "\\1/TR",
                                                   regex=True)
        # Label CLI/TR events
        events.loc[jr_tr_mask, "id"] = jr_tr_id

        # Ensure start and end columns are proper datetimes
        events[["start", "end"]] = events[["start",
                                           "end"]].apply(pd.to_datetime,
                                                         utc=True)
        # Compute length of events
        events["length"] = events["end"] - events["start"]

        # Drop all unidentified events
        events.dropna(subset=["id"], inplace=True)
        # Drop event column
        events = events.drop("event", axis=1).reset_index(drop=True)
        return events

    def get_week_plans(self):
        return self.events.groupby([self.events["start"].dt.strftime("%W"),
                                    "id"])["length"].sum()

    def show_plans(self):
        print(self.get_week_plans().to_string())
