from enum import Enum
import random

import numpy as np

from . import config as c
from .gui_attributes import Gui_attributes


class RB3Mode(Enum):
    Rocket = 0
    Glider = 1
    Stepper = 2
    InvRocket = 10
    InvGlider = 11
    InvStepper = 12


class Agent(object):
    def __init__(
        self,
        id,
        mode,
        init_pos,
        target=None,
        radius=0.06,
        color=None
    ):
        self.id = id
        self.set_mode(mode)
        self.gui_att = Gui_attributes(mode=self.mode, num_thrusts=self.num_thrusts, thrust_directions=self.thrust_directions, radius=radius, color=color)
        self.update(init_pos, None, None)
        self.update_target(target)
        self.velocity = np.zeros([2])
        self.radius = radius
        self.mass = 0.1
        self.last_motor_command = np.zeros(c.INPUT_MOTOR_DIM)

    def compute_update(self, terrains, action, delta_time, other_agents):
        previous_velocity = self.velocity
        previous_position = self.position

        mass = self.mass
        gravity = np.array([0.0, 0.0])
        for terrain in terrains:
            if terrain.contains(self.position):
                gravity += terrain.gravity * mass * self.g

        thrusts = self.get_thrusts_from_motor_commands(action)

        # compute forces in x and y direction
        thrust_forces = np.matmul(
            # (thrusts * self.maxthrust)[np.newaxis, :],  # TODO
            (thrusts * 1)[np.newaxis, :],
            self.thrust_directions)

        forcesum = thrust_forces[0] + gravity
        acceleration = forcesum / mass

        # consequent velocity without borders.
        # v = delta_s / delta_t
        # or
        # delta_v = a * delta_t
        # v = v_0 + delta_v
        velocity_change = acceleration * delta_time
        hypvel = previous_velocity + velocity_change

        # consequent position without borders
        # delta_s = v * delta_t
        # s = s_0 + delta_s
        position_change = hypvel * delta_time
        hyppos = previous_position + position_change

        return hyppos, hypvel, thrusts

    def update(self, position, velocity, thrusts):
        self.position = position
        self.velocity = velocity
        self.thrusts = thrusts
        self.gui_att.update_position(self.position, self.thrusts, np.zeros([c.INPUT_MOTOR_DIM]))

    def update_target(self, target):
        self.target = target
        if target is not None:
            self.gui_att.update_target(self.target)

    def switch_mode(self, do_random=True, mode=None):
        if mode is not None:
            next_problem_index = mode
        elif do_random:
            next_problem_index = int(
                (random.random() * c.NUMBER_OF_PROBLEMS) // 1)
        else:
            next_problem_index = (self.mode+1) % c.NUMBER_OF_PROBLEMS

        self._set_mode(next_problem_index)

    def set_mode(self, mode):
        self.mode = mode
        if mode in (RB3Mode.Rocket.value, RB3Mode.InvRocket.value):
            self.g = 9.81
            self.floor_friction = .9
            self.ceilingFriction = .9
            self.side_friction = .9
            self.agent_friction = .9
            self.num_thrusts = 2
        elif mode in (RB3Mode.Glider.value, RB3Mode.InvGlider.value):
            self.g = 0.0
            self.floor_friction = .9
            self.ceilingFriction = .9
            self.side_friction = .9
            self.agent_friction = .4
            self.num_thrusts = 4
        elif mode in (RB3Mode.Stepper.value, RB3Mode.InvStepper.value):
            self.g = 0.0
            self.floor_friction = 1
            self.ceilingFriction = 1
            self.side_friction = 1
            self.agent_friction = 1
            self.num_thrusts = 4
        else:
            raise SystemExit("SIMULATOR MODE UNKNOWN")
        tmp1 = np.array([1.0, 1.0])
        tmp2 = np.array([-1.0, 1.0])
        tmp3 = np.array([1.0, -1.0])
        tmp4 = np.array([-1.0, -1.0])
        tmp1_norm = tmp1 / np.linalg.norm(tmp1)
        tmp2_norm = tmp2 / np.linalg.norm(tmp2)
        tmp3_norm = tmp3 / np.linalg.norm(tmp3)
        tmp4_norm = tmp4 / np.linalg.norm(tmp4)
        if mode in (RB3Mode.InvRocket.value, RB3Mode.InvGlider.value, RB3Mode.InvStepper.value):
            self.thrust_directions = np.array(
                [tmp2_norm, tmp1_norm, tmp4_norm, tmp3_norm])
        else:
            self.thrust_directions = np.array(
                [tmp1_norm, tmp2_norm, tmp3_norm, tmp4_norm])


    def get_thrusts_from_motor_commands(self, motor_commands):
        motor_commands = np.clip(
            motor_commands,
            c.MIN_MOTOR_VALUE,
            c.MAX_MOTOR_VALUE)

        thrusts = np.zeros(c.INPUT_MOTOR_DIM)
        thrusts[0:2] = motor_commands[0:2]

        if self.mode in (RB3Mode.Glider.value, RB3Mode.Stepper.value, RB3Mode.InvGlider.value, RB3Mode.InvStepper.value):
            thrusts[2:4] = motor_commands[2:4]

        return thrusts

    def get_random_motor_command(self):
        if np.random.random() < 0.7:
            motor_command = np.zeros(c.INPUT_MOTOR_DIM)
            if np.random.random() < 0.05:
                motor_command = np.zeros(c.INPUT_MOTOR_DIM)
            else:
                if np.random.random() < 0.8:
                    for i in range(len(motor_command)):
                        motor_command[i] = 1 - np.random.random() * np.random.random()
                else:
                    for i in range(len(motor_command)):
                        motor_command[i] = np.random.random()
        else:
            motor_command = self.last_motor_command
        self.last_motor_command = motor_command
        return motor_command
