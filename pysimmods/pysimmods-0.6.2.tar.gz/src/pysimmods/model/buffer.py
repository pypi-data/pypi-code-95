from pysimmods.model.model import Model


class Buffer(Model):
    """A buffer subtype model.

    This class provides unified access to set_percent for all buffer
    models. With passive sign convention, the buffer returns negative
    power for generation and positive power for consumption. With
    active sign convention, it is the other way around.

    *set_percent* hides the sign convention. In contrast to generator
    and load, the battery is idle with a set_percent of 50.

    """

    @property
    def set_percent(self):
        p_kw = self.inputs.p_set_kw
        if p_kw is None:
            return None

        if p_kw * self.config.gsign > 0:
            # Generating energy
            set_percent = abs(p_kw / self.config.p_discharge_max_kw)
            set_percent *= 50 * self.config.gsign
            return 50 + set_percent
        else:
            # Consuming energy
            set_percent = abs(p_kw / self.config.p_charge_max_kw)
            set_percent *= 50 * self.config.lsign
            return 50 + set_percent

    @set_percent.setter
    def set_percent(self, value):
        value = max(min(abs(value), 100.0), 0.0)

        if value < 50:
            # Generating energy in psc
            p_max_kw = self.config.p_min_kw
        else:
            # Consuming energy in psc
            p_max_kw = self.config.p_max_kw

        set_percent = abs((50 - value) * 2 / 100)
        self.inputs.p_set_kw = set_percent * p_max_kw
        # print()
