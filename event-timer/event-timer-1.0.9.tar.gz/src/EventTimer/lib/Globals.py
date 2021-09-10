from pytz import timezone

from EventTimer.lib.Color import Color

# Use pytz_map keys in timeformat values
pytz_map = {
    "GMT": "GMT",
    "PST": "America/Los_Angeles",
    "PDT": "US/Pacific",
    "EST": "EST",
    "EDT": "US/Eastern",
    "KTM": "Asia/Kathmandu",
    "CAL": "Asia/Calcutta",
}

gmt = timezone(pytz_map["GMT"])
pst = timezone(pytz_map["PST"])
pdt = timezone(pytz_map["PDT"])
est = timezone(pytz_map["EST"])
edt = timezone(pytz_map["EDT"])
ktm = timezone(pytz_map["KTM"])
cal = timezone(pytz_map["CAL"])

color = Color()
default_config_files = (
    "event.cfg",
    ".event.cfg",
    "event_config.cfg",
    ".event_config.cfg",
)
