from collections import defaultdict
from itertools import cycle

import gym
import numpy as np
import drawSvg
from pathlib import Path

from pogema.grid_config import GridConfig

from pogema.grid import Grid


class MarlSvgVisualization:
    EMPTY = 0
    MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1), ]
    RADIUS = 30

    SCALE_SIZE = 100
    CIRCLE_STROKEWIDTH = 10
    MOVING_CIRCLE_SIZE = 15
    ANIMATION_TIME_SCALE = 0.07 * 4
    OPACITY = 0.1
    COLORS = ('#ff5447', '#3F51B5', '#ecbb33',
              '#3d9e3e', '#da7424', '#c1433c', '#ade6ad', '#5cbbb9', '#9C27B0', '#5a349c')

    def __init__(self, obstacles, num_agents, targets, obs_radius, drawing_size=(500, 500), cut_borders=True):
        """
        :param obstacles:
        :param num_agents:
        :param targets:
        :param obs_radius:
        :param drawing_size:
        """
        self.num_agents = num_agents

        self.cut_borders = cut_borders
        self.obs_radius = obs_radius

        if self.cut_borders:
            self.targets = {agent_idx: (tx - self.obs_radius, ty - self.obs_radius)
                            for agent_idx, (tx, ty) in targets.items()}
        else:
            self.targets = targets

        if self.cut_borders:
            self.obstacles = obstacles[obs_radius:-obs_radius, obs_radius:-obs_radius]
        else:
            self.obstacles = obstacles

        self.color = cycle(self.COLORS)
        self.settings = {"base_inner_color": '#7b8594', "base_outer_color": None, }
        self.agents_colors = {index: next(self.color) for index in range(self.num_agents)}
        self.paths = {index: [] for index in range(self.num_agents)}
        self.done_statuses = {index: [] for index in range(self.num_agents)}
        self.drawing_size = drawing_size

        self.START_I = 50
        self.START_J = 50

    def store(self, positions, done_statuses):
        """
        Stores agents positions and done statuses in episode buffer.
        :param positions: positions of agents
        :param done_statuses: done statuses of agents
        :return:
        """
        for agent_id, (x, y) in enumerate(positions):
            if self.cut_borders:
                x -= self.obs_radius
                y -= self.obs_radius
            self.paths[agent_id].append((x, y))
        for agent_id, done_status in enumerate(done_statuses):
            self.done_statuses[agent_id].append(done_status)

    def draw(self):
        """
        Main function for visualization.
        Creates connections, nodes, targets and agents.
        :return: DrawSvg object
        """

        size = len(self.obstacles)

        drawing = drawSvg.Drawing(size * self.SCALE_SIZE,
                                  size * self.SCALE_SIZE,
                                  origin=(0, 0),
                                  displayInline=False)
        drawing.setRenderSize(*self.drawing_size)

        self.create_connections(drawing, size)
        self.create_nodes(drawing, size, self.settings, self.obstacles, self.paths, self.done_statuses, self.obs_radius)
        self.create_targets(drawing, self.targets, size, self.agents_colors, self.done_statuses)
        self.create_agents(drawing, self.paths, size, self.agents_colors, self.done_statuses)

        return drawing

    def check_connection(self, first_x, first_y, second_x, second_y, connection_id=0):
        """
        Checks connection between 2 nodes.
        :param first_x:
        :param first_y:
        :param second_x:
        :param second_y:
        :param connection_id:
        :return:
        """
        board_size = len(self.obstacles)
        if not (0 <= first_x < board_size and 0 <= first_y < board_size):
            return False

        if not (0 <= second_x < board_size and 0 <= second_y < board_size):
            return False

        return self.obstacles[first_x][first_y] == connection_id and self.obstacles[second_x][second_y] == connection_id

    def create_connections(self, drawing, size):
        """
        Creates connections between nodes.
        Current implementations ignores existing connection (duplicates them).
        :param drawing: drawSvg object to which the nodes will be assigned
        :param size: board size
        :return:
        """
        for i in range(size):
            for j in range(size):
                for di, dj in self.MOVES:
                    if not self.check_connection(*self.fix_point(i, j, size), *self.fix_point(i + di, j + dj, size)):
                        continue
                    sx, sy = self.START_I + i * self.SCALE_SIZE, self.START_J + j * self.SCALE_SIZE
                    fx, fy = self.START_I + (i + di) * self.SCALE_SIZE, self.START_J + (j + dj) * self.SCALE_SIZE,

                    if fx < sx or fy < sy:
                        sx, fx = fx, sx
                        sy, fy = fy, sy
                    radius_offset = 0
                    if di:
                        element = drawSvg.Line(sx + self.RADIUS + radius_offset, sy, fx - self.RADIUS - radius_offset,
                                               fy, stroke='black', stroke_width=self.CIRCLE_STROKEWIDTH, fill='black',
                                               opacity=self.OPACITY)
                        drawing.append(element)
                    elif dj:
                        element = drawSvg.Line(sx, sy + self.RADIUS + radius_offset, fx,
                                               fy - self.RADIUS - radius_offset, stroke='black',
                                               stroke_width=self.CIRCLE_STROKEWIDTH, fill='black', opacity=self.OPACITY)
                        drawing.append(element)
                    else:
                        raise KeyError

    @staticmethod
    def fix_point(x, y, length):
        """
        Fixes coordinates to match their positions in arrays.
        :param x:
        :param y:
        :param length:
        :return: fixed coordinates pair
        """
        return length - y - 1, x

    def create_nodes(self, drawing, size, settings, board, paths, done_statuses, obs_radius):
        """
        Fully creates nodes and animation staff for agents observations.
        :param drawing: drawSvg object to which the nodes will be assigned
        :param size: board size
        :param settings: some settings TODO replace with self.attribute
        :param board:
        :param paths: agents paths
        :param done_statuses:
        :param obs_radius: agents observation radius
        :return:
        """
        nodes = defaultdict(lambda: [])

        for i in range(size):
            for j in range(size):
                x, y = self.fix_point(i, j, size)
                if board[x][y] == self.EMPTY:
                    # drawing inner circle
                    inner_color = None
                    if "base_inner_color" in settings:
                        inner_color = settings['base_inner_color']
                    inner_circle = drawSvg.Circle(self.START_I + i * self.SCALE_SIZE,
                                                  self.START_J + j * self.SCALE_SIZE,
                                                  self.RADIUS - self.CIRCLE_STROKEWIDTH // 2,
                                                  stroke='black', stroke_width=0, fill=inner_color,
                                                  opacity=self.OPACITY)
                    drawing.append(inner_circle)
                    # store nodes to apply opacity
                    nodes[x, y].append(inner_circle)

                    # drawing outer circle
                    outer_color = None
                    if "base_outer_color" in settings:
                        outer_color = settings['base_outer_color']

                    outer_circle = drawSvg.Circle(self.START_I + i * self.SCALE_SIZE,
                                                  self.START_J + j * self.SCALE_SIZE,
                                                  self.RADIUS + self.CIRCLE_STROKEWIDTH,
                                                  stroke=outer_color, stroke_width=self.CIRCLE_STROKEWIDTH, fill='none',
                                                  opacity=self.OPACITY)
                    drawing.append(outer_circle)
                    nodes[x, y].append(outer_circle)

                    # clearing connections with white circle
                    white_circle = drawSvg.Circle(self.START_I + i * self.SCALE_SIZE,
                                                  self.START_J + j * self.SCALE_SIZE,
                                                  self.RADIUS, stroke='white', stroke_width=self.CIRCLE_STROKEWIDTH,
                                                  fill='none', opacity=1.0)
                    drawing.append(white_circle)

                    # drawing black border circle
                    border_circle = drawSvg.Circle(self.START_I + i * self.SCALE_SIZE,
                                                   self.START_J + j * self.SCALE_SIZE,
                                                   self.RADIUS, stroke='black', stroke_width=self.CIRCLE_STROKEWIDTH,
                                                   fill='none', opacity=self.OPACITY)
                    drawing.append(border_circle)
                    nodes[x, y].append(border_circle)

        # change nodes opacity based on agents vision (obs_radius)
        animation_length = 0
        for agent_id in sorted(paths.keys()):
            animation_length = max(len(paths[agent_id]), animation_length)

        view_range = [np.zeros((size, size), dtype=np.uint8) for _ in range(animation_length)]
        for agent_id in sorted(paths.keys()):
            agent_xy = paths[agent_id]
            for index, (x, y) in enumerate(agent_xy):
                # skip highlighting for done agents
                if done_statuses[agent_id][index]:
                    break
                lower_x, upper_x = max(0, x - obs_radius), min(size, x + obs_radius + 1)
                lower_y, upper_y = max(0, y - obs_radius), min(size, y + obs_radius + 1)
                view_range[index][lower_x:upper_x, lower_y:upper_y] = 1

        for x, y in nodes:
            for element in nodes[x, y]:
                if view_range[0][x, y] != 0:
                    element.args['opacity'] = '1.0'
                if len(view_range) > 1:
                    p = [str(self.OPACITY) if view_range[index][x, y] == 0 else "1.0" for index in
                         range(len(view_range))]
                    p = ';'.join(p)

                    element.appendAnim(drawSvg.Animate('opacity', f'{animation_length * self.ANIMATION_TIME_SCALE}s', p,
                                                       repeatCount='indefinite'))

    def create_targets(self, drawing, targets, size, targets_colors, done_statuses):
        """
        Creates agent's targets, also adds animation to hide
        target after reaching.
        :param drawing: drawSvg object to which the nodes will be assigned
        :param targets:
        :param size:
        :param targets_colors:
        :param done_statuses:
        :return:
        """
        for agent_id in sorted(targets.keys()):
            tx, ty = targets[agent_id]

            # fix coordinates
            x, y = ty, size - tx - 1

            target = drawSvg.Circle(self.START_I + x * self.SCALE_SIZE, self.START_J + y * self.SCALE_SIZE,
                                    self.RADIUS + self.CIRCLE_STROKEWIDTH,
                                    stroke=targets_colors[agent_id], stroke_width=self.CIRCLE_STROKEWIDTH, fill='none')
            animation_length = len(done_statuses[agent_id]) * self.ANIMATION_TIME_SCALE
            visibility = ";".join(['hidden' if is_done else "visible" for is_done in done_statuses[agent_id]])
            if len(done_statuses[agent_id]) > 1:
                target.appendAnim(
                    drawSvg.Animate('visibility', f'{animation_length}s', visibility, repeatCount='indefinite'))
            drawing.append(target)

    def create_agents(self, drawing, paths, size, agents_colors, done_statuses):
        """
        Creates agents and their move animations, also hides
        agents after reaching a target.
        :param drawing: drawSvg object to which the nodes will be assigned
        :param paths:
        :param size:
        :param agents_colors:
        :param done_statuses:
        :return:
        """
        for agent_id in sorted(paths.keys()):
            # skip agent drawing if its done
            if self.done_statuses[agent_id][0] is True:
                continue

            agent_xy = paths[agent_id]

            pr = self.RADIUS - self.CIRCLE_STROKEWIDTH // 2
            agent = drawSvg.Circle(self.START_I + agent_xy[0][1] * self.SCALE_SIZE,
                                   self.START_J + (size - agent_xy[0][0] - 1) * self.SCALE_SIZE,
                                   pr, stroke='black', stroke_width=0,
                                   fill=agents_colors[agent_id])
            x_path = "".join([str(self.START_I + qy * self.SCALE_SIZE) + ";" for qx, qy in agent_xy])
            y_path = "".join([str(-self.START_J + -(size - qx - 1) * self.SCALE_SIZE) + ";" for qx, qy in agent_xy])
            if len(agent_xy) > 1:
                animation_length = len(agent_xy) * self.ANIMATION_TIME_SCALE
                agent.appendAnim(drawSvg.Animate('cy', f'{animation_length}s', y_path, repeatCount='indefinite'))
                agent.appendAnim(drawSvg.Animate('cx', f'{animation_length}s', x_path, repeatCount='indefinite'))

                visibility = ";".join(['hidden' if is_done else "visible" for is_done in done_statuses[agent_id]])
                agent.appendAnim(
                    drawSvg.Animate('visibility', f'{animation_length}s', visibility, repeatCount='indefinite'))
            drawing.append(agent)

    @staticmethod
    def get_frame(obstacles, agents, targets, obs_radius=5, done=None):
        targets = {agent_id: target for agent_id, target in enumerate(targets)}
        msv = MarlSvgVisualization(obstacles=obstacles, num_agents=len(agents), targets=targets, obs_radius=obs_radius)
        if done is None:
            done = [False for _ in range(len(agents))]
        msv.store(agents, done)
        return msv.draw()

    @staticmethod
    def draw_frame(obstacles, agents, targets, filename, obs_radius=5, done=None):
        Path(filename).parents[0].mkdir(parents=True, exist_ok=True)
        drawing = MarlSvgVisualization.get_frame(obstacles, agents, targets, obs_radius, done)
        drawing.saveSvg(Path(filename))

    def draw_frames(self, folder_name):
        for frame in range(len(self.paths[0])):
            agents = [self.paths[agent][frame] for agent in self.paths]
            done = [self.done_statuses[agent][frame] for agent in self.paths]
            targets = [self.targets[t] for a, t in enumerate(self.targets)]
            self.draw_frame(self.obstacles, targets=targets, filename=Path(folder_name) / f'{str(frame).zfill(3)}.svg',
                            agents=agents, obs_radius=self.obs_radius, done=done)


class AnimationMonitor(gym.Wrapper):
    """
    Saves svg animation renders on reset.
    """

    def __init__(self, env, directory='./animations', force=False, use_seed_name=False, min_save_length=None):
        super().__init__(env)
        self._drawer = None
        self._directory = directory

        self._force = force
        self.episode_id = 0
        self.use_seed_name = use_seed_name
        self.min_save_length = min_save_length

    def step(self, action):
        """
        Stores agents positions and done statuses on every step.
        """
        obs, reward, done, info = self.env.step(action)

        grid: Grid = self.env.grid
        self._drawer.store(positions=grid.positions_xy, done_statuses=done)
        return obs, reward, done, info

    def reset(self, **kwargs):
        """
        Renders svg files in self._directory folder.
        """

        if self._drawer:
            if not self.min_save_length or self.min_save_length <= max(
                    [len(self._drawer.paths[agent]) for agent in self._drawer.paths]):
                drawing = self._drawer.draw()
                if self.use_seed_name:
                    filename = str(self.seed_).zfill(4) + '.svg'
                else:
                    filename = str(self.episode_id).zfill(5) + '.svg'

                path = Path(self._directory) / Path(filename)
                Path(self._directory).mkdir(parents=True, exist_ok=True)
                drawing.saveSvg(path)

        result = self.env.reset(**kwargs)
        grid: Grid = self.env.grid
        config: GridConfig = self.env.config
        targets = {index: target for index, target in enumerate(grid.finishes_xy)}
        self._drawer = MarlSvgVisualization(grid.obstacles, config.num_agents, targets, config.obs_radius)
        self._drawer.store(positions=grid.positions_xy, done_statuses=[False for _ in range(config.num_agents)])

        self.episode_id += 1
        return result
