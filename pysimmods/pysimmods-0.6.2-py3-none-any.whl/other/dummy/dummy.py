from pysimmods.model.model import Model
from pysimmods.model.config import ModelConfig
from pysimmods.model.state import ModelState
from pysimmods.model.inputs import ModelInputs


class DummyConfig(ModelConfig):
    def __init__(self, params):
        super().__init__(params)

        self._default_schedule = [0 for _ in range(24)]


class DummyState(ModelState):
    def __init__(self, inits):
        super().__init__(inits)


class DummyInputs(ModelInputs):
    pass


class DummyModel(Model):
    def __init__(self, params, inits):
        self.config = DummyConfig(params)
        self.state = DummyState(inits)
        self.inputs = DummyInputs()

    def step(self):
        self.state.p_kw = self.inputs.p_set_kw

    @property
    def set_percent(self):
        return self.inputs.p_set_kw

    @set_percent.setter
    def set_percent(self, value):
        self.inputs.p_set_kw = value
