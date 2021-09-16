# ALL PHYRA COMMAND CONFIG
import os
import pathlib

# Weather Config
WX_API_KEY = os.environ.get("WX_API_KEY", "f84d93b992e83eb3756a2a802bbd2344")  # PHYRA Openweathermap Public API
WX_LOCATION = os.environ.get("WX_LOCATION", "Indonesia")
WX_METRIC_TEMP = os.environ.get("WX_METRIC_TEMP", "celsius")
WX_METRIC_WIND = os.environ.get("WX_METRIC_WIND", "km_hour")
