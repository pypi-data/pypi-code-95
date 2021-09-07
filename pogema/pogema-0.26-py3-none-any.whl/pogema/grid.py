import string
import sys
import time
from contextlib import closing

import numpy as np
from gym import utils
from io import StringIO

from pogema.generator import generate_obstacles, generate_positions_and_targets_fast
from .grid_config import GridConfig


def timeit(func):
    def wrapped(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(end - start)
        return result

    return wrapped


class Grid:

    def __init__(self, obstacles, starts, starts_xy, finishes_xy, grid_config: GridConfig):
        self.obstacles = obstacles
        self.positions = starts
        self.finishes_xy = finishes_xy
        self.positions_xy = starts_xy
        self.config = grid_config

    def get_observation_shape(self):
        full_radius = self.config.obs_radius * 2 + 1
        return 2, full_radius, full_radius

    def get_num_actions(self):
        return len(self.config.MOVES)

    def get_obstacles(self, agent_id):
        x, y = self.positions_xy[agent_id]
        r = self.config.obs_radius
        return self.obstacles[x - r:x + r + 1, y - r:y + r + 1]

    def get_positions(self, agent_id):
        x, y = self.positions_xy[agent_id]
        r = self.config.obs_radius
        return self.positions[x - r:x + r + 1, y - r:y + r + 1]

    def get_target(self, agent_id):

        x, y = self.positions_xy[agent_id]
        fx, fy = self.finishes_xy[agent_id]
        if x == fx and y == fy:
            return 0.0, 0.0
        rx, ry = fx - x, fy - y
        dist = np.sqrt(rx ** 2 + ry ** 2)
        return rx / dist, ry / dist

    def get_square_target(self, agent_id):
        c = self.config
        full_size = self.config.obs_radius * 2 + 1
        result = np.zeros((full_size, full_size))
        x, y = self.positions_xy[agent_id]
        fx, fy = self.finishes_xy[agent_id]
        dx, dy = x - fx, y - fy

        dx = min(dx, c.obs_radius) if dx >= 0 else max(dx, -c.obs_radius)
        dy = min(dy, c.obs_radius) if dy >= 0 else max(dy, -c.obs_radius)
        result[c.obs_radius + dx, c.obs_radius + dy] = 1
        return result

    def render(self, mode='human'):
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        chars = string.digits + string.ascii_letters + string.punctuation
        positions_map = {(x, y): id_ for id_, (x, y) in enumerate(self.positions_xy)}
        finishes_map = {(x, y): id_ for id_, (x, y) in enumerate(self.finishes_xy)}
        for line_index, line in enumerate(self.obstacles):
            out = ''
            for cell_index, cell in enumerate(line):
                if cell == self.config.FREE:
                    agent_id = positions_map.get((line_index, cell_index), None)
                    finish_id = finishes_map.get((line_index, cell_index), None)

                    if agent_id is not None:
                        out += str(utils.colorize(' ' + chars[agent_id % len(chars)] + ' ', color='gray', bold=True,
                                                  highlight=False))
                    elif finish_id is not None:
                        out += str(
                            utils.colorize('|' + chars[finish_id % len(chars)] + '|', 'white', highlight=False))
                    else:
                        out += str(utils.colorize(str(' . '), 'white', highlight=False))
                else:
                    out += str(utils.colorize(str('   '), 'cyan', bold=False, highlight=True))
            out += '\n'
            outfile.write(out)

        if mode != 'human':
            with closing(outfile):
                return outfile.getvalue()

    def move(self, agent_id, action):
        x, y = self.positions_xy[agent_id]
        fx, fy = self.finishes_xy[agent_id]

        dx, dy = self.config.MOVES[action]
        if self.obstacles[x + dx, y + dy] == self.config.FREE:
            if self.positions[x + dx, y + dy] == self.config.FREE:
                x += dx
                y += dy
        if fx == x and fy == y:
            self.positions[x, y] = self.config.FREE
        self.positions_xy[agent_id] = (x, y)

        if x == fx and y == fy:
            return True

        return False

    @staticmethod
    def prepare_grid(obstacles, starts_xy, finishes_xy, grid_config):
        r = grid_config.obs_radius
        filled_obstacles = np.zeros(np.array(obstacles.shape) + r * 2)
        size, size = filled_obstacles.shape
        filled_obstacles[r - 1, r - 1:size - r + 1] = 1
        filled_obstacles[r - 1:size - r + 1, r - 1] = 1
        filled_obstacles[size - r, r - 1:size - r + 1] = 1
        filled_obstacles[r - 1:size - r + 1, size - r] = 1
        filled_obstacles[r:size - r, r:size - r] = obstacles

        starts_xy = [(x + r, y + r) for x, y in starts_xy]
        finishes_xy = [(x + r, y + r) for x, y in finishes_xy]
        filled_positions = np.zeros(filled_obstacles.shape)
        for x, y in starts_xy:
            filled_positions[x, y] = 1

        return Grid(filled_obstacles, filled_positions, starts_xy, finishes_xy, grid_config, )

    @staticmethod
    def random_grid_generator(config):
        obstacles = generate_obstacles(config)
        starts_xy, finishes_xy = generate_positions_and_targets_fast(obstacles, config)
        return Grid.prepare_grid(obstacles, starts_xy, finishes_xy, config)
