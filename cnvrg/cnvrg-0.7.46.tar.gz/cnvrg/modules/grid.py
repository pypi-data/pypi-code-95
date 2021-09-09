from cnvrg.modules.base_module import CnvrgBase
#import numpy as np
import itertools
from functools import reduce


class Grid(CnvrgBase):
    def __init__(self):
        pass

    def exec(self, object, **kwargs):
        pass

    @staticmethod
    def calculate_params(**kwargs):
        values = {k: Grid.__inflate_values(v) for k, v in kwargs.items()}
        values = [[{k: x} for x in v] for k, v in values.items()]
        return [reduce(lambda t, y: {**y, **t}, x) for x in itertools.product(*values)]

    @staticmethod
    def __inflate_values(definition):
        key_type = definition.get("type")
        if key_type == "array":
            return definition.get("values")

        if key_type == "range":
            d_start, d_stop = definition.get("start"), definition.get("stop")
            d_step = definition.get("step") or 1
            return range(d_start, d_stop, d_step)

        # if key_type == 'logspace':
        #     d_min, d_max, d_num = definition.get("start"), definition.get("stop"), definition.get("num")
        #     d_base = definition.get("base") or 10
        #     return np.logspace(d_min, d_max, num=d_num, base=d_base)