from abc import ABC

import numpy as np
import gym
from gym.error import ResetNeeded

from pogema.generator import generate_obstacles
from pogema.grid import Grid
from pogema.grid_config import GridConfig


class PogesaBase(gym.Env):

    def __init__(self, config: GridConfig = GridConfig(num_agents=1)):
        # noinspection PyTypeChecker
        self.grid: Grid = None
        self.config = config

        full_size = self.config.obs_radius * 2 + 1
        self.observation_space = gym.spaces.Box(0.0, 1.0, shape=(3, full_size, full_size))
        self.action_space = gym.spaces.Discrete(len(self.config.MOVES))

    def step(self, action):
        raise NotImplemented

    def reset(self):
        self.grid: Grid = Grid.random_grid_generator(config=self.config)
        return self._get_obs()

    def render(self, mode='human'):
        self.check_reset()
        return self.grid.render(mode=mode)

    def check_reset(self):
        if self.grid is None:
            raise ResetNeeded("Please reset environment first!")

    def _get_obs(self, agent_id=0):
        return np.concatenate([
            self.grid.get_obstacles(agent_id)[None],
            self.grid.get_positions(agent_id)[None],
            self.grid.get_square_target(agent_id)[None]
        ])

    def _get_obs_dict(self, agent_id=0):
        observation = dict(
            obs=np.concatenate([
                self.grid.get_obstacles(agent_id)[None],
                self.grid.get_positions(agent_id)[None],
                self.grid.get_square_target(agent_id)[None]
            ]),
            target_vector=self.grid.get_target(agent_id)
        )
        return observation


class StochasticPogesa(PogesaBase):
    def __init__(self, config: GridConfig = GridConfig(num_agents=1), morph_tau=1):
        super().__init__(config)
        self.morph_tau = morph_tau
        self.rnd = np.random.default_rng(self.config.seed)
        self._steps = 0

    def morph_obstacles(self):
        r = self.config.obs_radius
        self.grid.obstacles[r:-r, r:-r] = generate_obstacles(self.config, self.rnd)
        for position in self.grid.positions_xy:
            self.grid.obstacles[position] = self.config.FREE

    def step(self, action):
        self.check_reset()

        if self._steps % self.morph_tau == 0:
            self.morph_obstacles()

        finish = self.grid.move(0, action)
        info = dict()
        reward = 1.0 if finish else 0.0

        self._steps += 1
        return self._get_obs(), reward, finish, info

    def reset(self):
        self._steps = 0
        self.grid: Grid = Grid.random_grid_generator(config=self.config)
        return self._get_obs()


class Pogesa(PogesaBase):

    def __init__(self, config: GridConfig = GridConfig(num_agents=1)):
        # noinspection PyTypeChecker
        super().__init__(config)

    def step(self, action):
        self.check_reset()

        finish = self.grid.move(0, action)
        info = dict()
        reward = 1.0 if finish else 0.0
        return self._get_obs(), reward, finish, info


class SingleAgentPogema(Pogesa):
    pass


def main():
    env = gym.make('StochasticPogesa-v0', )
    env.reset()
    for _ in range(100):
        _, _, done, _ = env.step(env.action_space.sample())
        env.render()
        if done:
            break


if __name__ == '__main__':
    main()
