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

color = Color()
default_config_files = (
    "event.cfg",
    ".event.cfg",
    "event_config.cfg",
    ".event_config.cfg",
)
