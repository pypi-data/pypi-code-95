import numpy as np
import gym
from gym.error import ResetNeeded
from gym.wrappers import TimeLimit

from pogema.animation import AnimationMonitor
from pogema.generator import generate_obstacles
from pogema.grid import Grid
from pogema.grid_config import GridConfig


class PogemaBase(gym.Env):

    def __init__(self, config: GridConfig = GridConfig()):
        # noinspection PyTypeChecker
        self.grid: Grid = None
        self.config = config

        full_size = self.config.obs_radius * 2 + 1
        self.observation_space = gym.spaces.Box(0.0, 1.0, shape=(3, full_size, full_size))
        self.action_space = gym.spaces.Discrete(len(self.config.MOVES))

    def _get_agents_obs(self, agent_id=0):
        return np.concatenate([
            self.grid.get_obstacles(agent_id)[None],
            self.grid.get_positions(agent_id)[None],
            self.grid.get_square_target(agent_id)[None]
        ])

    def check_reset(self):
        if self.grid is None:
            raise ResetNeeded("Please reset environment first!")

    def render(self, mode='human'):
        self.check_reset()
        return self.grid.render(mode=mode)


class PogesaBase(PogemaBase):

    def __init__(self, config: GridConfig = GridConfig(num_agents=1)):
        # noinspection PyTypeChecker
        super().__init__(config)
        self.grid: Grid = None
        self.config = config

        full_size = self.config.obs_radius * 2 + 1
        self.observation_space = gym.spaces.Box(0.0, 1.0, shape=(3, full_size, full_size))
        self.action_space = gym.spaces.Discrete(len(self.config.MOVES))

    def step(self, action):
        raise NotImplemented

    # def _get_obs_dict(self, agent_id=0):
    #     observation = dict(
    #         obs=np.concatenate([
    #             self.grid.get_obstacles(agent_id)[None],
    #             self.grid.get_positions(agent_id)[None],
    #             self.grid.get_square_target(agent_id)[None]
    #         ]),
    #         target_vector=self.grid.get_target(agent_id)
    #     )
    #     return observation


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


class Pogema(PogemaBase):
    def __init__(self, config=GridConfig(num_agents=2)):
        super().__init__(config)
        self.num_agents = self.config.num_agents
        self.is_multiagent = True
        self.active = None

    def _obs(self):
        return [self._get_agents_obs(index) for index in range(self.num_agents)]

    def step(self, action: list):
        assert len(action) == self.config.num_agents
        rewards = []

        infos = [dict() for _ in range(self.num_agents)]

        dones = []
        for agent_idx in range(self.config.num_agents):
            agent_done = self.grid.move(agent_idx, action[agent_idx])
            infos[agent_idx]['is_active'] = self.active[agent_idx]

            if agent_done and self.active[agent_idx]:
                rewards.append(1.0)

            else:
                rewards.append(0.0)

            dones.append(agent_done)
            if agent_done:
                self.active[agent_idx] = False


        # if all(rewards):
        #     # multi-agent environments should auto-reset!
        #     obs = self.reset()
        # else:
        #     obs = self._obs()
        obs = self._obs()
        return obs, rewards, dones, infos

    def reset(self):
        self.grid: Grid = Grid.random_grid_generator(config=self.config)
        self.active = {agent_idx: True for agent_idx in range(self.config.num_agents)}
        return self._obs()


class DenseRewardWrapper(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)
        self._best_distance = None

    def reset(self, *args, **kwargs):
        obs = self.env.reset(*args, **kwargs)
        config: GridConfig = self.env.config
        grid: Grid = self.env.grid
        self._best_distance = []
        for agent_idx in range(config.num_agents):
            x, y = grid.positions_xy[agent_idx]
            fx, fy = grid.finishes_xy[agent_idx]
            self._best_distance.append(self._manhattan_distance(x, y, fx, fy))
        return obs

    def step(self, action):
        obs, _, dones, infos = self.env.step(action)

        grid: Grid = self.env.grid
        rewards = []
        for agent_idx, best_distance in enumerate(self._best_distance):
            x, y = grid.positions_xy[agent_idx]
            fx, fy = grid.finishes_xy[agent_idx]
            distance = self._manhattan_distance(x, y, fx, fy)
            if distance < best_distance:
                self._best_distance[agent_idx] = distance
                rewards.append(1.0)
            else:
                rewards.append(0.0)

        return obs, rewards, dones, infos

    @staticmethod
    def _manhattan_distance(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)


class MultiTimeLimit(TimeLimit):
    def step(self, action):
        observation, reward, done, info = self.env.step(action)
        self._elapsed_steps += 1
        if self._elapsed_steps >= self._max_episode_steps:
            done = [True] * self.num_agents
        return observation, reward, done, info


class AutoResetWrapper(gym.Wrapper):
    def step(self, action):
        observations, rewards, dones, infos = self.env.step(action)
        if all(dones):
            observations = self.env.reset()
        return observations, rewards, dones, infos


def main():
    env = gym.make('Pogema-v0', config=GridConfig(num_agents=8, size=6))
    env = AnimationMonitor(env=env)
    env = MultiTimeLimit(env, max_episode_steps=256)
    env = AutoResetWrapper(env)
    env.reset()

    done = [False, ...]
    while not all(done):
        obs, reward, done, info = env.step([env.action_space.sample() for _ in range(env.config.num_agents)])
        print(reward, done, info)
        # env.render()


if __name__ == '__main__':
    main()
