from gym import register
from pogema.grid_config import GridConfig

__version__ = '0.26'

__all__ = [
    'GridConfig',
]

register(
    id="SingleAgentPogema-v0",
    entry_point="pogema.envs:SingleAgentPogema",
    max_episode_steps=256,
)

register(
    id="Pogesa-v0",
    entry_point="pogema.envs:Pogesa",
    max_episode_steps=256,
)

register(
    id="StochasticPogesa-v0",
    entry_point="pogema.envs:StochasticPogesa",
    max_episode_steps=256,
)

