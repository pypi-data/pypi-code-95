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

from anna import XMLAdaptor
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as axes3d
import numpy

import run_tests
from virtual_ipm.simulation.setup import Setup
from virtual_ipm.simulation.simulation import Progress

# log.to_console()

configuration = XMLAdaptor(filepath=run_tests.CONFIG_FILENAME)
setup = Setup(configuration)

test_case = run_tests.TestCaseUniformMagneticFieldOnlyY('do_nothing')
test_case.setUp()
test_case.number_of_time_steps = 1

initial_position = numpy.array([0., 0., 0.])
initial_momentum = numpy.array([test_case.mass * 1.0e3, test_case.mass * 2.0e3, test_case.mass * 3.0e3])

electric_field = numpy.array([0., 0., 0.])
magnetic_field = numpy.array([0., 0.2, 0.])

trajectory = []
sim_trajectory = []

position = initial_position.copy()
momentum = initial_momentum.copy()

for step in range(setup.number_of_time_steps):
    progress = Progress(step, setup.number_of_time_steps, setup.time_delta)
    test_case.sim_time = progress.time
    trajectory.append(test_case.compute_final_position_and_momentum(initial_position, initial_momentum,
                                                                    electric_field, magnetic_field))
    position, momentum = test_case.simulate_final_position_and_momentum(position, momentum,
                                                                        electric_field, magnetic_field)
    sim_trajectory.append((position, momentum))
    # print trajectory[-1]

print('first computed:  ', trajectory[0])
print('first simulated: ', sim_trajectory[0])

print('final computed:  ', trajectory[-1])
print('final simulated: ', sim_trajectory[-1])

fig = plt.figure()
axes = axes3d.Axes3D(fig)
axes.set_xlabel('x')
axes.set_ylabel('y')
axes.set_zlabel('z')

position_trajectory = next(zip(*trajectory))
x_trajectory, y_trajectory, z_trajectory, *_ = zip(*position_trajectory)
line = axes.plot(x_trajectory, y_trajectory, z_trajectory, 'b')

sim_position_trajectory = next(zip(*sim_trajectory))
sim_x_trajectory, sim_y_trajectory, sim_z_trajectory, *_ = zip(*sim_position_trajectory)
sim_line = axes.plot(sim_x_trajectory, sim_y_trajectory, sim_z_trajectory, 'r')

plt.show()
