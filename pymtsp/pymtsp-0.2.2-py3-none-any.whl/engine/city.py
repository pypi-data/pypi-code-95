import numpy as np

from pymtsp.engine.status import CityStatus


class City:
    def __init__(self,
                 idx,
                 loc):
        self.status = CityStatus.IDLE
        self.idx = idx
        self.loc = np.array(loc)
        self.assigned_by = None

    def __repr__(self):
        msg = "City {} | Pos {} | Status: {}".format(self.idx, self.loc, self.status)
        return msg

    def state_dict(self):
        state_dict = {
            'status': self.status,
            'idx': self.idx,
            'loc': np.array(self.loc),
            'assigned_by': self.assigned_by
        }
        return state_dict

    @classmethod
    def from_state_dict(cls, state_dict):
        city = cls(state_dict['idx'],
                   state_dict['loc'])
        city.status = state_dict['status']
        city.assigned_by = state_dict['assigned_by']
        return city
