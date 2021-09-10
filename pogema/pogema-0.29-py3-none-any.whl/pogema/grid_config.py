import sys
import numpy as np
from pydantic import BaseModel, validator


class GridConfig(BaseModel):
    seed: int = None
    size: int = 8
    density: float = 0.3
    num_agents: int = 1
    obs_radius: int = 5

    FREE = 0
    OBSTACLE = 1
    MOVES = tuple([(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),  ])

    # noinspection PyMethodParameters
    @validator('seed')
    def seed_initialization(cls, v):
        assert v is None or (0 <= v < sys.maxsize), "seed must be in [0, " + str(sys.maxsize) + ']'
        if v is None:
            return np.random.randint(sys.maxsize, dtype=np.int64)
        return v

    # noinspection PyMethodParameters
    @validator('size')
    def size_restrictions(cls, v):
        assert 2 <= v <= 1024, "size must be in [2, 1024]"
        return v

    # noinspection PyMethodParameters
    @validator('density')
    def density_restrictions(cls, v):
        assert 0.0 <= v < 1, "density must be in [0, 1)"
        return v

    # noinspection PyMethodParameters
    @validator('num_agents')
    def num_agents_must_be_positive(cls, v):
        assert 1 <= v <= 1024, "num_agents must be in [1, 1024]"
        return v

    # noinspection PyMethodParameters
    @validator('obs_radius')
    def obs_radius_must_be_positive(cls, v):
        assert 1 <= v <= 128, "obs_radius must be in [1, 128]"
        return v
