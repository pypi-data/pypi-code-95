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
import inspect
import logging
import pprint
import sys
import types
import unittest

from anna import XMLAdaptor
import injector
import numpy

import virtual_ipm.log as log
import virtual_ipm.simulation.particle_tracking.models as models
import virtual_ipm.di as di
from virtual_ipm.di.bindings import create_binding
from virtual_ipm.simulation.auxiliaries import ParticleSupervisor
from virtual_ipm.simulation.setup import Setup
from virtual_ipm.simulation.simulation import Progress

CONFIG_FILENAME = 'config.xml'

# Patch Setup.
Setup._gas_type = None
Setup._maximum_number_of_particles = 1


class EMFieldsWrapper:
    def __init__(self, electric_field, magnetic_field):
        super().__init__()
        self._electric_field = electric_field
        self._magnetic_field = magnetic_field

    def electric_field_at(self, *args, **kwargs):
        return self._electric_field

    def magnetic_field_at(self, *args, **kwargs):
        return self._magnetic_field


class TestCase(unittest.TestCase):
    ACCEPTANCE_THRESHOLD = 1.0e-3

    def setUp(self):
        # # Monkey-patch Setup to remove configuration parameters that won't be used.
        # Setup._number_of_time_steps = None
        # Setup._simulation_time = None
        # Setup._tracked_particle_type = Namespace(charge=-1.0, mass=0.5)

        model_configuration = XMLAdaptor(filepath=CONFIG_FILENAME)

        model_cls = getattr(
            models, model_configuration.get_text(models.ParticleTrackingModel.CONFIG_PATH_TO_IMPLEMENTATION))

        bindings = [
            create_binding('ConfigurationModule', di.components.configuration, model_configuration,
                           provider=injector.InstanceProvider),
            create_binding('SetupModule', di.components.setup, Setup),
            create_binding('ParticleTrackingModule', di.models.particle_tracking, model_cls)
        ]

        self.model = injector.Injector(bindings).get(model_cls)
        self.model.prepare()

        setup = injector.Injector(bindings).get(Setup)
        self.sim_time = setup.simulation_time
        self.number_of_time_steps = setup.number_of_time_steps
        self.charge = setup.particle_type.charge
        self.mass = setup.particle_type.mass
        self.particle_type = setup.particle_type

        setup._maximum_number_of_particles = 1
        self.particle_supervisor = ParticleSupervisor(setup)
        self.particle = self.particle_supervisor.create_particle(
            Progress(0, setup.number_of_time_steps, setup.time_delta)
        )

    def check_against_reference(self, value, reference, threshold):
        if abs(reference) <= sys.float_info.min:
            self.assertAlmostEqual(value, reference, places=int(abs(numpy.log10(threshold))))
        else:
            self.assertAlmostEqual(value / reference, 1.0, delta=threshold)

        # self.assertAlmostEqual(value, reference, delta=threshold)

    def simulate_final_position_and_momentum(self, initial_position, initial_momentum, electric_field, magnetic_field):
        self.model.em_fields = EMFieldsWrapper(electric_field.copy(), magnetic_field.copy())
        # RadialFieldsBx0 requires this parameter.
        self.model._magnetic_field_strength_in_y = magnetic_field[1]
        particle = self.particle
        particle.position, particle.momentum = initial_position.copy(), initial_momentum.copy()
        self.model.initialize(particle)
        for _ in range(self.number_of_time_steps):
            self.model.propagate(particle)
        return particle.position, particle.momentum

    def do_nothing(self):
        pass


class TestCaseDriftSpace(TestCase):
    """No electromagnetic fields.

    F = 0   (non-relativistic)
    """

    def compute_final_position_and_momentum(self, initial_position, initial_momentum, electric_field, magnetic_field):
        final_momentum = initial_momentum.copy()
        final_position = initial_momentum / self.mass * self.sim_time + initial_position
        return final_position, final_momentum

    def simulate_final_position_and_momentum(self, initial_position, initial_momentum, electric_field, magnetic_field):
        electric_field = numpy.array([0., 0., 0.])
        magnetic_field = numpy.array([0., 0., 0.])
        return super().simulate_final_position_and_momentum(
            initial_position, initial_momentum, electric_field, magnetic_field)


class TestCaseUniformElectricField(TestCase):
    """Uniform electric field, no magnetic field.

    F = q*E   (non-relativistic)
    """

    def compute_final_position_and_momentum(self, initial_position, initial_momentum, electric_field, magnetic_field):
        final_momentum = self.charge * electric_field * self.sim_time + initial_momentum
        final_position = (self.charge / (2 * self.mass) * electric_field * self.sim_time ** 2
                          + initial_momentum / self.mass * self.sim_time + initial_position)
        return final_position, final_momentum

    def simulate_final_position_and_momentum(self, initial_position, initial_momentum, electric_field, magnetic_field):
        magnetic_field = numpy.array([0., 0., 0.])
        return super().simulate_final_position_and_momentum(
            initial_position, initial_momentum, electric_field, magnetic_field)


class TestCaseUniformMagneticFieldOnlyY(TestCase):
    """Uniform magnetic field, no electric field.

    F = q*v x B   (non-relativistic)
    Magnetic field must point in y-direction: B = (0, B, 0)
    """

    def compute_final_position_and_momentum(self, initial_position, initial_momentum, electric_field, magnetic_field):
        x0, y0, z0 = initial_position
        px, py, pz = initial_momentum
        w = self.charge * magnetic_field[1] / self.mass
        mass = self.mass
        sin_wt, cos_wt = numpy.sin(w * self.sim_time), numpy.cos(w * self.sim_time)
        final_momentum = (
            px * cos_wt - pz * sin_wt,
            py,
            pz * cos_wt + px * sin_wt
        )
        final_position = (
            x0 + px / (mass * w) * sin_wt + pz / (mass * w) * (cos_wt - 1.),
            y0 + py / self.mass * self.sim_time,
            z0 + pz / (mass * w) * sin_wt + px / (mass * w) * (1. - cos_wt)
        )
        return numpy.array(final_position), numpy.array(final_momentum)

    def simulate_final_position_and_momentum(self, initial_position, initial_momentum, electric_field, magnetic_field):
        electric_field = numpy.array([0., 0., 0.])
        magnetic_field[0], magnetic_field[2] = 0., 0.
        return super().simulate_final_position_and_momentum(
            initial_position, initial_momentum, electric_field, magnetic_field)


class TestCaseParallelElectricAndMagneticFieldInY(TestCase):
    """Uniform electric and magnetic field.

    F = q * (E + v x B)   (non-relativistic)
    Electric field must point in y-direction: E = (0, E, 0)
    Magnetic field must point in y-direction: B = (0, B, 0)
    """

    def compute_final_position_and_momentum(self, initial_position, initial_momentum, electric_field, magnetic_field):
        x0, y0, z0 = initial_position
        px, py, pz = initial_momentum
        w = self.charge * magnetic_field[1] / self.mass
        charge, mass, sim_time = self.charge, self.mass, self.sim_time
        sin_wt, cos_wt = numpy.sin(w * self.sim_time), numpy.cos(w * self.sim_time)
        final_momentum = (
            px * cos_wt - pz * sin_wt,
            charge * electric_field[1] * sim_time + py,
            pz * cos_wt + px * sin_wt
        )
        final_position = (
            x0 + px / (mass * w) * sin_wt + pz / (mass * w) * (cos_wt - 1.),
            y0 + py / mass * sim_time + charge / (2 * mass) * electric_field[1] * sim_time**2,
            z0 + pz / (mass * w) * sin_wt + px / (mass * w) * (1. - cos_wt)
        )
        return numpy.array(final_position), numpy.array(final_momentum)

    def simulate_final_position_and_momentum(self, initial_position, initial_momentum, electric_field, magnetic_field):
        electric_field[0], electric_field[2] = 0., 0.
        magnetic_field[0], magnetic_field[2] = 0., 0.
        return super().simulate_final_position_and_momentum(
            initial_position, initial_momentum, electric_field, magnetic_field)


class TestCaseECrossBDrift(TestCase):
    """E x B drift.

    F = q*(E + v x B)
    Electric field must point in x-direction: E = (E, 0, 0)
    Magnetic field must point in y-direction: B = (0, B, 0)
    """

    def compute_final_position_and_momentum(self, initial_position, initial_momentum, electric_field, magnetic_field):
        x0, y0, z0 = initial_position
        px, py, pz = initial_momentum
        w = self.charge * magnetic_field[1] / self.mass
        m = self.mass
        E_over_B = electric_field[0] / magnetic_field[1]
        sin_wt, cos_wt = numpy.sin(w * self.sim_time), numpy.cos(w * self.sim_time)
        final_momentum = (
            (m * E_over_B - pz) * sin_wt + px * cos_wt,
            py,
            -(m * E_over_B - pz) * cos_wt + px * sin_wt + m * E_over_B
        )
        final_position = (
            x0 - pz / (m * w) + E_over_B / w - (E_over_B / w - pz / (m * w)) * cos_wt + px / (m * w) * sin_wt,
            y0 + py / self.mass * self.sim_time,
            z0 + px / (m * w) + E_over_B * self.sim_time - (E_over_B / w - pz / (m * w)) * sin_wt -
            px / (m * w) * cos_wt
        )
        return numpy.array(final_position), numpy.array(final_momentum)

    def simulate_final_position_and_momentum(self, initial_position, initial_momentum, electric_field, magnetic_field):
        electric_field[1], electric_field[2] = 0., 0.
        magnetic_field[0], magnetic_field[2] = 0., 0.
        return super().simulate_final_position_and_momentum(
            initial_position, initial_momentum, electric_field, magnetic_field)


TestCaseExBDrift = TestCaseECrossBDrift


def new_test_function(initial_position, initial_velocity, electric_field, magnetic_field, threshold):
    def test_function(self):
        self.model.em_fields = EMFieldsWrapper(electric_field, magnetic_field)

        initial_momentum = initial_velocity * self.mass
        final_position, final_momentum = self.compute_final_position_and_momentum(initial_position, initial_momentum,
                                                                                  electric_field, magnetic_field)
        position, momentum = self.simulate_final_position_and_momentum(initial_position, initial_momentum,
                                                                       electric_field, magnetic_field)

        self.check_against_reference(position[0], final_position[0], threshold)
        self.check_against_reference(position[1], final_position[1], threshold)
        self.check_against_reference(position[2], final_position[2], threshold)
        self.check_against_reference(momentum[0], final_momentum[0], threshold)
        self.check_against_reference(momentum[1], final_momentum[1], threshold)
        self.check_against_reference(momentum[2], final_momentum[2], threshold)

    return test_function


initial_positions = {
    'zero': numpy.zeros(shape=(3,)),
    'nonzero': numpy.array([1.e-3, 2.e-3, 3.e-3]),
}

initial_velocity = {
    'zero': numpy.zeros(shape=(3,)),
    # 1875537.2689456875 m/s corresponds to a electron kinetic energy of 10eV.
    'nonzero': numpy.array([1875537.2689456875, 2 * 1875537.2689456875, 3 * 1875537.2689456875]),
}

electric_fields = {
    'zero': numpy.zeros(shape=(3,)),
    'only_x_1kV': numpy.array([1.0e3, 0., 0.]),
    'only_x_5kV': numpy.array([5.0e3, 0., 0.]),
    'only_x_10kV': numpy.array([10.0e3, 0., 0.]),
    'only_y': numpy.array([0., 1.0e3, 0.]),
    # Does not work with RadialFieldsBx0.
    # 'only_z': numpy.array([0., 0., 1.0e3]),
}

magnetic_fields = {
    'zero': numpy.zeros(shape=(3,)),
    '200mT': numpy.array([0., 0.2, 0.]),
    '500mT': numpy.array([0., 0.5, 0.]),
    '800mT': numpy.array([0., 0.8, 0.]),
}

# Drift space.
for x_name, position in initial_positions.items():
    for v_name, velocity in initial_velocity.items():
        method_name = 'test_%s_initial_position_%s_initial_velocity' % (x_name, v_name)
        test_function = new_test_function(position, velocity, electric_fields['zero'], magnetic_fields['zero'],
                                          TestCaseDriftSpace.ACCEPTANCE_THRESHOLD)
        setattr(TestCaseDriftSpace, method_name, test_function)

# Electric field only.
for x_name, position in initial_positions.items():
    for v_name, velocity in initial_velocity.items():
        for e_name, e_field in electric_fields.items():
            if e_name == 'zero':
                continue
            method_name = 'test_%s_initial_position_%s_initial_velocity_%s_electric_field' % (x_name, v_name, e_name)
            test_function = new_test_function(position, velocity, e_field, magnetic_fields['zero'],
                                              TestCaseUniformElectricField.ACCEPTANCE_THRESHOLD)
            setattr(TestCaseUniformElectricField, method_name, test_function)

# Magnetic field only.
for x_name, position in initial_positions.items():
    for v_name, velocity in initial_velocity.items():
        if v_name == 'zero':
            continue
        for b_name, b_field in magnetic_fields.items():
            if b_name == 'zero':
                continue
            method_name = 'test_%s_initial_position_%s_initial_velocity_%s_magnetic_field' % (x_name, v_name, b_name)
            test_function = new_test_function(position, velocity, electric_fields['zero'], b_field,
                                              TestCaseUniformMagneticFieldOnlyY.ACCEPTANCE_THRESHOLD)
            setattr(TestCaseUniformMagneticFieldOnlyY, method_name, test_function)

# Parallel electric and magnetic field.
for x_name, position in initial_positions.items():
    for v_name, velocity in initial_velocity.items():
        for e_name, e_field in electric_fields.items():
            if 'only_y' not in e_name:
                continue
            for b_name, b_field in magnetic_fields.items():
                if b_name == 'zero':
                    continue
                method_name = 'test_%s_initial_position_%s_initial_velocity_%s_electric_field_%s_magnetic_field' % (
                    x_name, v_name, e_name, b_name)
                test_function = new_test_function(position, velocity, e_field, b_field,
                                                  TestCaseParallelElectricAndMagneticFieldInY.ACCEPTANCE_THRESHOLD)
                setattr(TestCaseParallelElectricAndMagneticFieldInY, method_name, test_function)

# ExB drift.
for x_name, position in initial_positions.items():
    for v_name, velocity in initial_velocity.items():
        for e_name, e_field in electric_fields.items():
            if not ('only_x' in e_name):
                continue
            for b_name, b_field in magnetic_fields.items():
                if b_name == 'zero':
                    continue
                method_name = 'test_%s_initial_position_%s_initial_velocity_%s_electric_field_%s_magnetic_field' % \
                              (x_name, v_name, e_name, b_name)
                test_function = new_test_function(position, velocity, e_field, b_field,
                                                  TestCaseECrossBDrift.ACCEPTANCE_THRESHOLD)
                setattr(TestCaseECrossBDrift, method_name, test_function)


if __name__ == '__main__':
    test_cases_specifier = XMLAdaptor(filepath=CONFIG_FILENAME).get_text('TestCases')
    if test_cases_specifier.lower().strip() == 'all':
        test_cases = filter(lambda obj: inspect.isclass(obj) and issubclass(obj, TestCase), globals().values())
    else:
        test_case_names = map(lambda name: name.strip(), test_cases_specifier.split(','))
        test_case_names = map(lambda name: 'TestCase' + name if not name.startswith('TestCase') else name,
                              test_case_names)
        test_cases = map(lambda name: globals()[name], test_case_names)

    print('Run the following cases:')
    print(pprint.pformat(test_cases))


    def load_tests(loader, tests, pattern):
        suite = unittest.TestSuite()
        for test_class in test_cases:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        return suite


    log.to_console(level=logging.INFO)
    unittest.main()
