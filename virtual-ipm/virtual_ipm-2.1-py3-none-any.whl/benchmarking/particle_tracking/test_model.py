#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from argparse import Namespace

import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import numpy
import scipy.constants as constants
from scipy.constants import physical_constants

from virtual_ipm.simulation.auxiliaries import ParticleSupervisor
from virtual_ipm.simulation.particle_tracking.models import Boris, RadialFields, RadialFieldsBx0, RungeKutta4
from virtual_ipm.simulation.setup import Setup
from virtual_ipm.simulation.simulation import Progress


class AnalyticalSolution:
    LINE_STYLE = '--'

    def __init__(self, setup, _):
        super().__init__()
        self._time = 0.
        self._dt = setup.time_delta
        self.charge = setup.particle_type.charge
        self.mass = setup.particle_type.mass
        self._initial_position = numpy.zeros((3,), dtype=float)
        self._initial_momentum = numpy.zeros((3,), dtype=float)
        self._initial_set = False

    def prepare(self):
        pass

    def initialize(self, particle):
        pass

    def propagate(self, particle):
        self._time += self._dt
        if not self._initial_set:
            self._initial_position[:] = particle.position
            self._initial_momentum[:] = particle.momentum
            self._initial_set = True


class DriftSpace(AnalyticalSolution):
    """No electromagnetic fields.

    F = 0   (non-relativistic)
    """

    def __init__(self, setup, configuration):
        super().__init__(setup, configuration)

    def propagate(self, particle):
        super().propagate(particle)

        final_momentum = self._initial_momentum.copy()
        final_position = self._initial_momentum / self.mass * self._time + self._initial_position

        particle.position = final_position
        particle.momentum = final_momentum


class OnlyE(AnalyticalSolution):
    """Uniform electric field, no magnetic field.

    F = q*E   (non-relativistic)
    """

    def __init__(self, setup, configuration):
        super().__init__(setup, configuration)

    def propagate(self, particle):
        super().propagate(particle)

        electric_field = self.em_fields.electric_field_at()

        final_momentum = self.charge * electric_field * self._time + self._initial_momentum
        final_position = (self.charge / (2 * self.mass) * electric_field * self._time ** 2
                          + self._initial_momentum / self.mass * self._time + self._initial_position)

        particle.position = final_position
        particle.momentum = final_momentum


class OnlyB(AnalyticalSolution):
    """Uniform magnetic field, no electric field.

    F = q*v x B   (non-relativistic)
    Magnetic field must point in y-direction: B = (0, B, 0)
    """

    def __init__(self, setup, configuration):
        super().__init__(setup, configuration)

    def propagate(self, particle):
        super().propagate(particle)

        x0, y0, z0 = self._initial_position
        px, py, pz = self._initial_momentum

        magnetic_field = self.em_fields.magnetic_field_at()

        w = self.charge * magnetic_field[1] / self.mass
        mass = self.mass
        sin_wt, cos_wt = numpy.sin(w * self._time), numpy.cos(w * self._time)
        final_momentum = (
            px * cos_wt - pz * sin_wt,
            py,
            pz * cos_wt + px * sin_wt
        )
        final_position = (
            x0 + px / (mass * w) * sin_wt + pz / (mass * w) * (cos_wt - 1.),
            y0 + py / self.mass * self._time,
            z0 + pz / (mass * w) * sin_wt + px / (mass * w) * (1. - cos_wt)
        )

        particle.position = final_position
        particle.momentum = final_momentum


class ParallelEandB(AnalyticalSolution):
    """Uniform electric and magnetic field.

    F = q * (E + v x B)   (non-relativistic)
    Electric field must point in y-direction: E = (0, E, 0)
    Magnetic field must point in y-direction: B = (0, B, 0)
    """

    def __init__(self, setup, configuration):
        super().__init__(setup, configuration)

    def propagate(self, particle):
        super().propagate(particle)

        x0, y0, z0 = self._initial_position
        px, py, pz = self._initial_momentum

        electric_field = self.em_fields.electric_field_at()
        magnetic_field = self.em_fields.magnetic_field_at()

        w = self.charge * magnetic_field[1] / self.mass
        charge, mass, sim_time = self.charge, self.mass, self._time
        sin_wt, cos_wt = numpy.sin(w * self._time), numpy.cos(w * self._time)
        final_momentum = (
            px * cos_wt - pz * sin_wt,
            charge * electric_field[1] * sim_time + py,
            pz * cos_wt + px * sin_wt
        )
        final_position = (
            x0 + px / (mass * w) * sin_wt + pz / (mass * w) * (cos_wt - 1.),
            y0 + py / mass * sim_time + charge / (2 * mass) * electric_field[1] * sim_time ** 2,
            z0 + pz / (mass * w) * sin_wt + px / (mass * w) * (1. - cos_wt)
        )

        particle.position = numpy.array(final_position)
        particle.momentum = numpy.array(final_momentum)


class ExBDrift(AnalyticalSolution):
    """E x B drift.

    F = q*(E + v x B)
    Electric field must point in x-direction: E = (E, 0, 0)
    Magnetic field must point in y-direction: B = (0, B, 0)
    """

    def __init__(self, setup, configuration):
        super().__init__(setup, configuration)

    def propagate(self, particle):
        super().propagate(particle)

        x0, y0, z0 = self._initial_position
        px, py, pz = self._initial_momentum

        electric_field = self.em_fields.electric_field_at()
        magnetic_field = self.em_fields.magnetic_field_at()

        w = self.charge * magnetic_field[1] / self.mass
        m = self.mass
        E_over_B = electric_field[0] / magnetic_field[1]
        sin_wt, cos_wt = numpy.sin(w * self._time), numpy.cos(w * self._time)
        final_momentum = (
            (m * E_over_B - pz) * sin_wt + px * cos_wt,
            py,
            -(m * E_over_B - pz) * cos_wt + px * sin_wt + m * E_over_B
        )
        final_position = (
            x0 - pz / (m * w) + E_over_B / w - (E_over_B / w - pz / (m * w)) * cos_wt + px / (m * w) * sin_wt,
            y0 + py / self.mass * self._time,
            z0 + px / (m * w) + E_over_B * self._time - (E_over_B / w - pz / (m * w)) * sin_wt -
            px / (m * w) * cos_wt
        )

        particle.position = numpy.array(final_position)
        particle.momentum = numpy.array(final_momentum)


# Monkey patch models.
RadialFieldsBx0._magnetic_field_strength_in_y = 0.1

# Specify the models to be used (and plotted).
tracking_models = [Boris, ExBDrift]

# Monkey patch components.
# Specify simulation parameters here (use SI units except for energy use [eV]):
Setup._maximum_number_of_particles = len(tracking_models)
Setup._number_of_time_steps = 10000
Setup._simulation_time = 10e-9
Setup._tracked_particle_type = Namespace(
    charge=constants.elementary_charge,
    mass=constants.electron_mass,
    rest_energy=physical_constants['electron mass energy equivalent in MeV'][0] * 1.0e6,
)
# Gas type is not required.
Setup._gas_type = None

# Instantiate components without configuration (parameters were already specified above):
setup = Setup(None)
particle_supervisor = ParticleSupervisor(setup)


# Define electromagnetic fields and provide them to the tracking model:
class EMFields:
    # ExB drift:
    electric_field = numpy.array([10000., 0., 0])
    magnetic_field = numpy.array([0., -0.1, 0])

    # Gyro motion:
    # electric_field = numpy.array([0., 1000., 0])
    # magnetic_field = numpy.array([0., -0.1, 0])

    @classmethod
    def electric_field_at(cls, *args, **kwargs):
        return cls.electric_field

    @classmethod
    def magnetic_field_at(cls, *args, **kwargs):
        return cls.magnetic_field


trajectories = []

for tracking_model_cls in tracking_models:
    print('')
    print('------------------------------')
    print('Running model: ', tracking_model_cls)
    print('')

    tracking_model = tracking_model_cls(setup, None)
    tracking_model.em_fields = EMFields
    tracking_model.prepare()

    # Create test particle and specify initial parameters:
    particle = particle_supervisor.create_particle(
        Progress(0, setup.number_of_time_steps, setup.time_delta)
    )
    particle.position = numpy.array([0., 0., 0.])
    # particle.momentum = numpy.array([0., 0., 0.])
    # 1875537.2689456875 m/s corresponds to a electron kinetic energy of 10eV.
    particle.momentum = numpy.array([1875537.2689456875, 2 * 1875537.2689456875, 3 * 1875537.2689456875]) \
                        * constants.electron_mass

    # Propagate particle and store trajectory:
    tracking_model.initialize(particle)
    trajectory = [particle.position.copy()]
    for i in range(setup.number_of_time_steps):
        tracking_model.propagate(particle)
        trajectory.append(particle.position.copy())

    trajectory = numpy.array(trajectory)
    x_trajectory = trajectory[:, 0]
    y_trajectory = trajectory[:, 1]
    z_trajectory = trajectory[:, 2]

    print('x_trajectory: ', x_trajectory)
    print('y_trajectory: ', y_trajectory)
    print('z_trajectory: ', z_trajectory)

    trajectories.append((x_trajectory, y_trajectory, z_trajectory))

time_steps = numpy.arange(setup.number_of_time_steps+1) * setup.time_delta


# Plot trajectory:
# plt.figure()
# plt.plot(time_steps, x_trajectory)


# Plot 3D trajectory:
figure = plt.figure()
axes = figure.gca(projection='3d')
axes.set_xlabel('x [mm]')
axes.set_ylabel('y [mm]')
axes.set_zlabel('z [mm]')
axes.set_title('Trajectory')

for tracking_model_cls, trajectory in zip(tracking_models, trajectories):
    try:
        axes.plot(trajectory[0] * 1000, trajectory[1] * 1000, trajectory[2] * 1000, tracking_model_cls.LINE_STYLE,
                  label=tracking_model_cls.__name__)
    except AttributeError:
        axes.plot(trajectory[0] * 1000, trajectory[1] * 1000, trajectory[2] * 1000,
                  label=tracking_model_cls.__name__)

plt.legend()

plt.show()
