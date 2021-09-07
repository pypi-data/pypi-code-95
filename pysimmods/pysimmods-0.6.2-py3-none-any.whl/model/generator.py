from .model import Model


class Generator(Model):
    """A generator subtype model.

    This class provides unified access to set_percent for all
    generators. A generator returns negative power values in the
    consumer reference arrow system (passive sign convention), which
    is hided if one uses *set_percent*, i.e. calling set_percent
    with, e.g., a value of 50 will always set the power of the
    generator to 50 percent, independently of the reference system
    used.

    """

    @property
    def set_percent(self):
        return abs(self.inputs.p_set_kw / (self.p_min_kw)) * 100.0

    @set_percent.setter
    def set_percent(self, set_percent):
        set_percent = max(min(abs(set_percent * 0.01), 1.0), 0.0)
        val_range = self.p_min_kw - self.p_max_kw
        self.inputs.p_set_kw = self.p_max_kw + set_percent * val_range
