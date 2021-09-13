import math
import random

import gym
import numpy as np

from . import agent as a
from . import terrain as t
from . import config as c
from . import gui as gui


class RocketballEnv(gym.Env):
    def __init__(
            self, maxthrust=1.0, leftborder=-1.5, rightborder=1.5,
            topborder=2.0, delta_time=1. / 30.):

        self.maxthrust = maxthrust
        self.leftborder = leftborder
        self.rightborder = rightborder
        self.topborder = topborder
        self.delta_time = delta_time
        self.agents = []
        self.obstacles = []
        self.terrains = []
        self.terrains.append(t.Terrain(np.array([leftborder, 0]), np.array([rightborder, topborder]), '', gravity=np.array([0, -1]), noise=0))

        self.sensor_dim = c.INPUT_POSITION_DIM
        self.motor_dim = c.INPUT_MOTOR_DIM

        self.sensor_dirs = calc_sensor_dirs()

    def add_agent(self, a):
        self.agents.append(a)
        self.gui.register(a)

    def add_obstacle(self, o):
        self.obstacles.append(o)
        self.gui.register(o)

    def add_terrain(self, t):
        self.terrains.append(t)
        self.gui.add_terrain(t)

    def reset(self):
        self.agents = []
        self.obstacles = []
        self.gui = gui.GUI()

    def render(self, mode='human'):
        self.gui.draw()

    def step(self, actions):
        assert(len(actions) == len(self.agents))

        for agent, action in zip(self.agents, actions):
            other_agents = [a for a in self.agents if a != agent]
            hyppos, hypvel, thrusts = agent.compute_update(self.terrains, action, self.delta_time, other_agents)

            # calculate velocity and position after consideration of borders and
            # other agents
            new_velocity, new_position = self.check_borders(
                hypvel, hyppos, agent, other_agents+self.obstacles)

            if agent.mode in (a.RB3Mode.Stepper.value, a.RB3Mode.InvStepper.value):
                new_velocity = np.zeros(c.INPUT_POSITION_DIM)

            agent.update(new_position, new_velocity, thrusts)

        observation = []
        for agent in self.agents:
            noise = 0
            for terrain in self.terrains:
                if terrain.contains(agent.position):
                    noise += terrain.noise
            observation.append((agent.id, agent.position, agent.position + np.random.normal(loc=0.0, scale=noise, size=2), self.calc_sensor_data(agent), agent.target))
        for obstacle in self.obstacles:
            observation.append((obstacle.id, obstacle.position))
        reward = 0
        done = True
        for agent in self.agents:
            if agent.target is not None:
                done = done and (np.square(agent.position - agent.target).mean() < 0.01) and np.abs(agent.velocity).mean() < 0.1
        info = {}

        return observation, reward, done, info

    def close(self):
        self.gui.gui.destroy()

    def check_borders(self, hypvel, hyppos, agent, other_agents):
        hypvel, hyppos = self.check_y_borders(hypvel, hyppos, agent)
        hypvel, hyppos = self.check_x_borders(hypvel, hyppos, agent)
        hypvel, hyppos = self.check_agents(
            hypvel, hyppos, agent, other_agents)
        return hypvel, hyppos

    def check_y_borders(self, hypvel, hyppos, agent):
        new_velocity = np.copy(hypvel)
        new_position = np.copy(hyppos)

        # new velocities and position without border
        # -----
        # differences between bottom and top border
        # -----
        bottom_diff = hyppos[1] - agent.radius  # bottom border = 0
        top_diff = hyppos[1] - (self.topborder - agent.radius)

        # check borders
        if bottom_diff <= 0:  # down at floor border
            new_velocity[0] = hypvel[0] * agent.floor_friction
            new_velocity[1] = 0.0
            new_position[1] = agent.radius

        elif top_diff >= 0:  # up at top ceiling border
            new_velocity[0] = hypvel[0] * agent.ceilingFriction
            new_velocity[1] = 0.0
            new_position[1] = self.topborder - agent.radius

        return new_velocity, new_position

    def check_x_borders(self, hypvel, hyppos, agent):
        new_velocity = np.copy(hypvel)
        new_position = np.copy(hyppos)

        # -----
        # differences between left and right border
        # -----
        left_diff = hyppos[0] - (self.leftborder + agent.radius)
        right_diff = hyppos[0] - (self.rightborder - agent.radius)

        # check borders
        # too far left
        if left_diff <= 0:
            new_velocity[0] = 0.0
            new_velocity[1] = hypvel[1] * agent.side_friction
            new_position[0] = self.leftborder + agent.radius

        # too far right:
        elif right_diff >= 0:
            new_velocity[0] = 0.0
            new_velocity[1] = hypvel[1] * agent.side_friction
            new_position[0] = self.rightborder - agent.radius

        return new_velocity, new_position

    def check_agents(self, hypvel, hyppos, agent, other_agents):
        new_velocity = np.copy(hypvel)
        new_position = np.copy(hyppos)

        # Shuffle agent list
        random.shuffle(other_agents)

        for A in other_agents:
            # Check if intersection exists
            A_current_position = A.position

            if np.array_equiv(A_current_position, np.zeros(2)):
                print("FALSCH")

            distance = np.linalg.norm(A_current_position - hyppos)
            if distance > (A.radius + agent.radius):
                # No intersection
                continue

            # Get type of intersection:
            # self is at
            # - top right
            # - top left
            # - bottom right
            # - bottom left
            # of A
            if hyppos[1] <= A_current_position[1]:
                pos = 'bottom'
            else:
                pos = 'top'

            if hyppos[0] <= A_current_position[0]:
                pos = pos + ' left'
            else:
                pos = pos + ' right'

            xdiff = abs(A_current_position[0] - hyppos[0])
            ydiff = abs(A_current_position[1] - hyppos[1])

            z = ydiff / (xdiff + .1e-30)

            a = agent.radius / math.sqrt(z**2 + 1)
            b = (z * agent.radius) / math.sqrt(z**2 + 1)

            a_A = A.radius / math.sqrt(z**2 + 1)
            b_A = (z * A.radius) / math.sqrt(z**2 + 1)

            delta_x = a - xdiff + a_A
            delta_y = b - ydiff + b_A

            # Now change position depending on direction
            if 'bottom' in pos:
                new_position[1] -= delta_y
            else:
                new_position[1] += delta_y

            if 'left' in pos:
                new_position[0] -= delta_x
            else:
                new_position[0] += delta_x

            new_velocity[0] = hypvel[0] * agent.agent_friction
            new_velocity[1] = hypvel[1] * agent.agent_friction

        return new_velocity, new_position

    def calc_sensor_data(self, agent):
        sensor_data = np.zeros([c.INPUT_SENSOR_DIM])

        my_pos = agent.position
        my_radius = agent.radius

        # Store the values at the particular rays in array
        ray_proximities = np.zeros([c.INPUT_SENSOR_DIM])

        for ray_index in range(c.INPUT_SENSOR_DIM):

            if c.BORDER_PROXIMITY_WEIGHT > 0:
                # Calculate proximity to each border
                # Left border
                border_left = np.array([[-1.5, 0], [-1.5, 2]])
                proximity = calc_border_intersection_proximity(
                    my_pos, my_radius, border_left, self.sensor_dirs[ray_index])
                if (proximity is not None) and (
                        ray_proximities[ray_index] < proximity):
                    ray_proximities[ray_index] = proximity

                # Right border
                border_right = np.array([[1.5, 0], [1.5, 2]])
                proximity = calc_border_intersection_proximity(
                    my_pos, my_radius, border_right, self.sensor_dirs[ray_index])
                if (proximity is not None) and (
                        ray_proximities[ray_index] < proximity):
                    ray_proximities[ray_index] = proximity

                # Top border
                border_top = np.array([[-1.5, 2], [1.5, 2]])
                proximity = calc_border_intersection_proximity(
                    my_pos, my_radius, border_top, self.sensor_dirs[ray_index])
                if (proximity is not None) and (
                        ray_proximities[ray_index] < proximity):
                    ray_proximities[ray_index] = proximity

                # Bottom border
                border_bottom = np.array([[-1.5, 0], [1.5, 0]])
                proximity = calc_border_intersection_proximity(
                    my_pos, my_radius, border_bottom, self.sensor_dirs[ray_index])
                if (proximity is not None) and (
                        ray_proximities[ray_index] < proximity):
                    ray_proximities[ray_index] = proximity

        # Convert the ray proximities to the whole sensor
        # A sensor's proximity is the max of its two surrounding rays
        for sensor_index in range(c.INPUT_SENSOR_DIM):
            if sensor_index == c.INPUT_SENSOR_DIM-1:
                sensor_data[sensor_index] = max(
                    [ray_proximities[sensor_index], ray_proximities[0]])
            else:
                sensor_data[sensor_index] = ray_proximities[sensor_index: sensor_index+2].max()

        # In the end calculate the closest proximity to all agents
        other_agents = [a for a in self.agents if a != agent]
        for a in other_agents + self.obstacles:
            other_pos = a.position
            other_radius = a.radius
            sensor_index, proximity = calculate_closest_agent_proximity(
                                                                        my_pos,
                                                                        other_pos,
                                                                        my_radius,
                                                                        other_radius)
            if sensor_index is not None and sensor_data[sensor_index] < proximity:
                sensor_data[sensor_index] = proximity

        # If the sensor data are not all zero
        if np.any(sensor_data):

            # Apply point spread function
            if c.POINT_SPREAD is True:
                point_spread_signal = np.zeros([c.INPUT_SENSOR_DIM])

                for sensor_index in range(c.INPUT_SENSOR_DIM):
                    point_spread_signal_tmp = point_spread(
                        sensor_index, sensor_data[sensor_index],
                        c.POINT_SPREAD_TYPE)
                    point_spread_signal_tmp[sensor_index] = 0
                    point_spread_signal += point_spread_signal_tmp

                # Only after all point spread additions is calculated, add
                # it to the sensor data
                sensor_data += point_spread_signal
                sensor_data = np.clip(sensor_data, 0, 1)
                sensor_data = np.round(sensor_data, decimals=8)

        return sensor_data

    def __set_savepoint(self):
        self.savepoint_velocity = self.velocity
        self.savepoint_current_position = self.current_position
        self.savepoint_previous_position = self.previous_position

    def __restore_savepoint(self):
        self.velocity = self.savepoint_velocity
        self.current_position = self.savepoint_current_position
        self.savepoint_previous_position = self.savepoint_previous_position

    def get_random_motor_commands(self):
        commands = []
        for agent in self.agents:
            commands.append(agent.get_random_motor_command())
        return commands

# ----------------------------
# End of class
# ----------------------------


'''
Returns the proximity to a particular agent and
the index of the sensor that can sense the closest
part of the agent.
0 = not sensing anything; high value = high proximity
'''


def calculate_closest_agent_proximity(
        my_pos, other_pos, my_radius, other_radius):
    distance = np.linalg.norm(other_pos - my_pos)
    real_distance = max([distance - my_radius - other_radius, 0])

    proximity = get_proximity_linear(real_distance, my_radius)

    if proximity == 0:
        return None, 0

    xdiff = other_pos[0] - my_pos[0]
    ydiff = other_pos[1] - my_pos[1]
    angle_rad = np.arctan2(ydiff, xdiff)

    if angle_rad < 0:
        angle_rad += 2*np.pi

    angle_deg = angle_rad * 180 / np.pi

    # with 4 sensors, the range is 90 degrees or pi/2
    sensor_range_deg = 360 / c.INPUT_SENSOR_DIM

    # Determine the id of the active sensor, clockwise
    active_sensor = int(angle_deg / sensor_range_deg)

    # If the angle is exactly 360 degrees, this will return an invalid index
    if active_sensor == c.INPUT_SENSOR_DIM:
        active_sensor -= 1

    # print('sensoractivity',str(active_sensor))

    return active_sensor, proximity


def get_proximity_tanh(distance, my_radius):
    max_distance = c.MAX_DISTANCE * my_radius
    max_proximity = 1/max_distance
    proximity = 1/(distance + 1e-30)

    # Ignore sensor data when distance is too high
    if distance >= max_distance:
        return 0

    return (math.tanh(proximity - max_proximity) + 1e-30)


def get_proximity_linear(distance, my_radius):
    max_distance = c.MAX_DISTANCE * my_radius

    # Ignore sensor data when distance is too high
    if distance >= max_distance:
        return 0

    return - 1 * (distance / max_distance) + 1


def point_spread(sensor, proximity, functiontype):
    if functiontype not in ['linear', 'gauss', 'linear_normalized']:
        raise SystemExit("Point spread function unknown")

    sensor_data = np.zeros([c.INPUT_SENSOR_DIM])

    def linear(x):
        # f(x) = m*x + c
        # m is -1* SPREADSIZE
        # c is 1.0
        # So 1.0 is the maximum value
        return (-1 * c.SPREADSIZE) * abs(x) + 1.0

    def gauss(x):
        sigma = c.SIGMA
        # gauss = 1./np.sqrt(2*np.pi*sigma**2) * math.exp(-(abs(x)**2)/(2*sigma**2))
        gauss = math.exp(-(abs(x)**2)/(2*sigma**2))
        return gauss

    if functiontype in ('linear', 'linear_normalized'):
        f = linear

    elif functiontype is 'gauss':
        f = gauss

    # Gehe von sensor aus die Indizes nach vorne (immer mit %)
    # Berechne fuer jeden Index i f(i).
    # Mache das solange nicht mehr als DIM/2 Schritte gegangen sind und solang
    # f(i) > 0 ist
    steps = 1
    result = 1

    # Not normalized
    sensor_data[sensor] = f(0) * proximity

    while result > 0 and steps < c.INPUT_SENSOR_DIM / 2:
        result = f(steps) * proximity
        sensor_data[(sensor+steps) % c.INPUT_SENSOR_DIM] = result
        sensor_data[(sensor-steps) % c.INPUT_SENSOR_DIM] = result
        steps += 1

    if functiontype is 'linear_normalized':
        # Normalize the sensor data, so that sum is 1
        sensor_data /= np.sum(sensor_data)

    return sensor_data


'''
http://mathworld.wolfram.com/Circle-LineIntersection.html

'''


def calc_agent_intersection_proximity(
        my_pos, my_radius, other_pos, other_radius, sensor_vector):

    # The algorithm works for a circle at (0,0)
    # So translate the other_pos to (0,0)
    my_pos_translated = my_pos - other_pos
    other_pos_translated = other_pos - other_pos

    x_1 = my_pos_translated[0]  # start point of ray
    y_1 = my_pos_translated[1]  # start point of ray
    L = my_pos_translated + sensor_vector * 10  # end point of ray
    x_2 = L[0]
    y_2 = L[1]
    r = other_radius

    x_2_retranslated = x_2 + my_pos[0]
    y_2_retranslated = y_2 + my_pos[1]

    d_x = x_2 - x_1
    d_y = y_2 - y_1
    d_r = math.sqrt(d_x**2 + d_y**2)
    D = x_1 * y_2 - x_2 * y_1

    # fig, ax = plt.subplots()
    # ax.set_xlim(-100, 100)
    # ax.set_ylim(-100, 100)

    # Draw line
    # ax.plot([my_pos[0], x_2_retranslated], [my_pos[1], y_2_retranslated], '-')

    # Draw circle
    # circle = plt.Circle(other_pos, r)
    # ax.add_artist(circle)

    if (r**2 * d_r**2 - D**2) < 0:
        # plt.show()
        return None

    else:
        x_plus = (D * d_y + np.sign(d_y)
                  * d_x * math.sqrt(r**2 * d_r**2 - D**2)) / d_r**2
        x_minus = (D * d_y - np.sign(d_y)
                   * d_x * math.sqrt(r**2 * d_r**2 - D**2)) / d_r**2

        y_plus = (-D * d_x + abs(d_y)
                  * math.sqrt(r**2 * d_r**2 - D**2)) / d_r**2
        y_minus = (-D * d_x - abs(d_y)
                   * math.sqrt(r**2 * d_r**2 - D**2)) / d_r**2

        intersection1 = np.array([x_plus, y_plus])
        intersection2 = np.array([x_minus, y_minus])

        # determine closest of both intersection points
        dist1 = np.linalg.norm(intersection1 - my_pos_translated)
        dist2 = np.linalg.norm(intersection2 - my_pos_translated)

        if dist1 <= dist2:
            dist = dist1
            intersection = intersection1
        else:
            dist = dist2
            intersection = intersection2

        # prevent to detect intersections in wrong direction
        # if the distance of mypos to one of the intersection points gets bigger
        # when adding a dirs-Vector to mypos, then the intersection is in the
        # wrong direction
        if ((intersection[0] <= x_2 and intersection[0] >= x_1) or (intersection[0] >= x_2 and intersection[0] <= x_1)) and (
                (intersection[1] <= y_2 and intersection[1] >= y_1) or (intersection[1] >= y_2 and intersection[1] <= y_1)):

            real_distance = dist - my_radius
            proximity = get_proximity_linear(real_distance, my_radius)
            return proximity

        else:
            return None


'''
https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
'''


def calc_border_intersection_proximity(
        my_pos, my_radius, border_pos, sensor_vector):
    x1 = my_pos[0]
    y1 = my_pos[1]

    L = my_pos + sensor_vector * 10  # end point of ray
    x2 = L[0]
    y2 = L[1]

    # plt.plot([x1, x2], [y1, y2], '-')

    x3 = border_pos[0, 0]
    y3 = border_pos[0, 1]
    x4 = border_pos[1, 0]
    y4 = border_pos[1, 1]

    denom = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    P_x = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / denom
    P_y = ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / denom

    # Check if the intersection is in the direction of the sensor vector
    # If the intersection point is between mypos and L, it's cool
    if ((P_x <= x2 and P_x >= x1) or (P_x >= x2 and P_x <= x1)) and \
       ((P_y <= y2 and P_y >= y1) or (P_y >= y2 and P_y <= y1)):

        intersection = np.array([P_x, P_y])
        distance = np.linalg.norm(intersection-my_pos)

        # plt.plot(intersection[0], intersection[1], 'r*')
        # plt.show()

        real_distance = distance - my_radius
        proximity = get_proximity_linear(real_distance, my_radius)
        return proximity * c.BORDER_PROXIMITY_WEIGHT

    else:
        # plt.show()
        return None


def calc_sensor_dirs():
    dirs = []
    for i in range(c.INPUT_SENSOR_DIM):
        sensor_range_rad = (2 * np.pi) / c.INPUT_SENSOR_DIM
        angle_rad = (i * sensor_range_rad + (i+1) * sensor_range_rad) / 2.
        dirs.append(np.array([np.cos(angle_rad), np.sin(angle_rad)]))

    dirs = np.asarray(dirs)
    return dirs
