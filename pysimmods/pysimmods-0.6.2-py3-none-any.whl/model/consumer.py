from pysimmods.model.model import Model


class Consumer(Model):
    """A consumer subtype model.

    A consumer returns positive power values in the consumer reference
    arrow system.

    """

    @property
    def set_percent(self):
        p_kw = self.inputs.p_set_kw
        if p_kw is None:
            return None

        p_kw /= self.config.pn_max_kw - self.config.pn_min_kw

        return p_kw * 100

    @set_percent.setter
    def set_percent(self, value):
        value = max(min(abs(value), 100.0), 0.0)
        if value == 0:
            p_set_kw = 0
        else:
            p_range = self.config.pn_max_kw - self.config.pn_min_kw
            p_set_kw = self.config.pn_min_kw + value / 100 * p_range
        self.inputs.p_set_kw = p_set_kw
