from datetime import timezone
from Utils.TimeZone import TimeZone


class PanelSettings(object):
    def __init__(self, input_dict):
        self.TimeZone = TimeZone(input_dict.get("TimeZone"))