from SapphireQuant.Core.Enum.EnumBarType import EnumBarType


class BarProviderInfo:
    """
    K线提供器信息
    """
    def __init__(self):
        self.time_slices = []
        self.offset = 0
        self.living_time = None
        self.interval = 0
        self.bar_type = EnumBarType.minute
