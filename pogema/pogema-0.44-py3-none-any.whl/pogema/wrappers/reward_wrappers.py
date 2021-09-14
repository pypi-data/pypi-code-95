import gym

from pogema import GridConfig
from pogema.grid import Grid


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


class TrueRewardWrapper(gym.Wrapper):
    """
        Replaces reward function for each agent with 0 for non-terminal states and
        f* / (g + h) for terminal states, where
        f* - length of the optimal path for i-th agent (ignoring others),
        g - length of the agent path,
        h - length of the optimal path to the target from
            current position of the i-th agent
    """

    def __init__(self, env):
        super().__init__(env)
        self.shortest_paths = None
        self.step_cnt = None

    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        self.step_cnt += 1

        grid: Grid = self.env.grid
        config: GridConfig = self.env.config

        reward = 0
        index = 0
        if done:
            x, y = grid.positions_xy[index]
            fx, fy = grid.finishes_xy[index]
            f_star = self.shortest_paths[index]
            g = self.step_cnt
            bfs_results = grid.obstacles.copy()
            bfs_results[bfs_results == 1] = -1

            self.bfs(bfs_results, config.MOVES, x, y, config.FREE)
            h = bfs_results[fx, fy] - 1
            reward = f_star / (g + h)

        return obs, reward, done, info

    @staticmethod
    def bfs(grid, moves, sx, sy, free_cell):
        q = [(sx, sy)]
        grid[sx, sy] = 1

        while len(q):
            x, y = q.pop(0)
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if grid[nx, ny] == free_cell:
                    grid[nx, ny] = grid[x, y] + 1
                    q.append((nx, ny))

    def reset(self, **kwargs):
        self.step_cnt = 0
        result = self.env.reset(**kwargs)
        grid: Grid = self.env.grid
        config: GridConfig = self.env.config
        self.shortest_paths = []
        bfs_results = grid.obstacles.copy()
        bfs_results[bfs_results == 1] = -1
        for x, y in grid.positions_xy:
            bfs_results[x, y] = config.FREE

        for agent_index in range(config.num_agents):
            x, y = grid.positions_xy[agent_index]

            bfs_results[bfs_results > 0] = 0

            self.bfs(bfs_results, moves=config.MOVES, sx=x, sy=y, free_cell=config.FREE)
            self.shortest_paths.append(bfs_results[grid.finishes_xy[agent_index]] - 1)
        return result


class PrimalRewardWrapper(gym.Wrapper):

    def get_reward(self, agent_index, action):
        grid: Grid = self.env.grid

        x, y = grid.positions_xy[agent_index]
        fx, fy = grid.finishes_xy[agent_index]

        reward = -0.3
        if action == 0:
            reward = -0.5
        if x == fx and y == fy:
            reward = 20.0
        return reward

    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        reward = self.get_reward(0, action)
        return obs, reward, done, info


class NormalizedPrimalRewardWrapper(PrimalRewardWrapper):
    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        reward = self.get_reward(0, action) / 20.0
        return obs, reward, done, info


class HammingRewardWrapper(gym.Wrapper):
    def __init__(self, env, max_rewarded_dist=32):
        super().__init__(env)
        self.max_rewarded_dist = max_rewarded_dist

    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        agent_index = 0
        grid: Grid = self.env.grid

        if done:
            x, y = grid.positions_xy[agent_index]
            fx, fy = grid.finishes_xy[agent_index]
            hamming_dist = min(self.max_rewarded_dist, abs(x - fx) + abs(y - fy))
            reward = (self.max_rewarded_dist - hamming_dist) / self.max_rewarded_dist
        else:
            reward = 0

        return obs, reward, done, info
