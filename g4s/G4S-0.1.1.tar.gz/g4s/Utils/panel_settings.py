from g4s.utils.time_zone import TimeZone


class PanelSettings:
    def __init__(self, input_dict):
        self.time_zone = TimeZone(input_dict.get("TimeZone"))
        self.default_temperature_device_id = input_dict.get(
            "DefaultTemperatureDevice"
        ).get("Id")
        self.default_temperature_device = None
