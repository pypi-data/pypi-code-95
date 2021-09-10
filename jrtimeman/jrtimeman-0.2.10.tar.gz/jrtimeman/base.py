from datetime import date, timedelta
import os

from gcsa.google_calendar import GoogleCalendar
from google.oauth2.credentials import Credentials
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd


class Calendar():
    """
    Simple wrapper around gcsa's GoogleCalendar that uses credentials
    from the current environment for authentication.
    """

    def __init__(self):
        self._credentials = self._get_credentials()
        self.calendar = GoogleCalendar(credentials=self._credentials)

    def _get_credentials(self):
        """Fetch credentials from env to authenticate against calendar."""
        return Credentials(token=os.environ["TOKEN"],
                           refresh_token=os.environ["REFRESH_TOKEN"],
                           client_id=os.environ["CLIENT_ID"],
                           client_secret=os.environ["CLIENT_SECRET"],
                           token_uri="https://oauth2.googleapis.com/token")


class Timesheet(Calendar):
    """
    Inspect working patterns from daily 'clocked on' and 'clocked off'
    calendar events added to Calendar.
    """

    def __init__(self, days=90):
        # Inherit from Calendar object
        super().__init__()

        self.days = days
        self.end = date.today()
        self.start = self.end - timedelta(days=self.days)
        self.data = self._get_timesheet()

        # If the most recent entry doesn't have a clocked off time, then
        # I'm still working
        clocked_on = self.data.iloc[-1]["clocked_off"] is None
        self.status = "Clocked On" if clocked_on else "Clocked Off"

    def _get_timecards(self):
        """Fetch calendar events with 'clocked' in title."""
        return self.calendar.get_events(time_min=self.start,
                                        time_max=self.end,
                                        query="clocked")

    def _get_timesheet(self):
        """Construct pandas DataFrame of clock on / clock off events."""
        # Create DataFrame from gcsa events
        cards = pd.DataFrame([{"time": timecard.start,
                               "event": timecard.summary}
                              for timecard in self._get_timecards()])

        # Preallocate DataFrame to hold transformed data
        sheet = pd.DataFrame({"clocked_on": None,
                              "clocked_off": None},
                             index=cards["time"].dt.date.unique())

        # Loop over cards and collate
        for i, row in cards.iterrows():
            # Determine whether card represents clock-on or clock-off event
            event_type = ("clocked_on" if "on" in row["event"].lower()
                          else "clocked_off")
            # Add time from card to correct on/off column
            sheet.loc[row["time"].date(), event_type] = row["time"].time()

        # Compute hours worked per shift
        sheet["shift_length"] = (
              pd.to_datetime(sheet["clocked_off"].dropna().astype(str),
                             format="%H:%M:%S")
            - pd.to_datetime(sheet["clocked_on"].dropna().astype(str),  # noqa E131
                             format="%H:%M:%S")
        ).dt.seconds / (60**2)

        return sheet

    def get_last_n_shifts(self, n=90):
        """Return data from last n shifts."""
        return self.data.dropna().iloc[-n:]

    def summarise(self, n=90, dp=2):
        """Compute shift statistics from last n shifts."""
        agg = {"Average Working Day (mean)": np.mean,
               "Average Working Week (mean)": np.mean,
               "Shortest Working Day": np.min,
               "Longest Working Day": np.max}
        summary = self.get_last_n_shifts(n)["shift_length"].agg(agg).round(dp)
        summary["Average Working Week (mean)"] *= 5
        return summary

    def hist(self, n=90):
        """Create histogram of shift length from last n shifts."""
        ax = self.get_last_n_shifts(n)["shift_length"].plot(kind="hist")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlabel("Length of working day (Hours)")
        ax.set_ylabel("Frequency")
        return ax.get_figure(), ax

    def boxplot(self, n=90):
        """Create boxplot of shift length from last n shifts."""
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

    def time_series(self, n=90):
        """Plot shift length against date for last n shifts."""
        ax = self.get_last_n_shifts(n)["shift_length"].plot(legend=False,
                                                            rot=45)
        ax.set_ylabel("Length of working day (Hours)")
        ax.set_xlabel("Date")
        return ax.get_figure(), ax


class Planner(Calendar):
    """
    Manipulate data from calendar events for internal project-management
    purposes.
    """

    def __init__(self, days=90):
        # Inherit from Calendar object
        super().__init__()

        self.days = days
        # Start from beginning of current week
        self.start = date.today() - timedelta(days=date.today().weekday())
        self.end = self.start + timedelta(days=self.days)

        # Fetch all events
        self._raw_data = self._get_all_events()
        # Curate CLI/PROJ events
        self.events = self._get_cli_proj_events()

    def _get_all_events(self):
        """Construct pandas DataFrame of all calendar events."""
        # Query calendar
        events = self.calendar.get_events(time_min=self.start,
                                          time_max=self.end,
                                          single_events=True)

        # Create DataFrame from calendar events
        events = pd.DataFrame([{"start": event.start,
                                "end": event.end,
                                "event": event.summary}
                              for event in events if event.start is not None])

        # Ensure start and end columns are proper datetimes
        events[["start", "end"]] = (
            events[["start", "end"]].apply(pd.to_datetime, utc=True)
            )
        # Compute length of each event
        length = events["end"] - events["start"]
        # Record length in hours
        events["allotted"] = length.apply(lambda x: x.seconds / 3600).round(2)
        return events

    def _get_cli_proj_events(self):
        """Extract and tag all CLI/PROJ events."""
        # Make a copy of raw data for manipulation
        events = self._raw_data.copy()

        # Make teaching events match CLI/PROJ pattern
        events["event"] = events["event"].str.replace("\[([A-Z]{2,5})\]",  # noqa W605
                                                      "\\1/TR",
                                                      regex=True)
        # Extract CLI/PRJ and remaining description from event
        events[["proj", "details"]] = (
            events["event"].str.extract(r"([A-Z]{2,5}/[A-Z]{2,5})\s*(.*)")
        )

        # Drop all unidentified events
        events.dropna(subset=["proj"], inplace=True)
        # Drop event column
        events = events.drop("event", axis=1).reset_index(drop=True)
        return events

    def get_plans_by_week(self):
        """Get week plans."""
        # Get the week number of each event
        week_num = self.events["start"].dt.strftime("%W")
        # Sum time allotted to each project, each week, and concatenate
        # descriptions
        plans = self.events.groupby([week_num, "proj"]).agg(
            {"allotted": np.sum,
             "details": lambda x: ", ".join(x.unique())}
        )
        # Rename "start" -> "week"
        plans.index.rename(["week", "proj"], inplace=True)
        # Convert to DataFrame
        plans = plans.reset_index().rename({"start": "week"})
        return plans
