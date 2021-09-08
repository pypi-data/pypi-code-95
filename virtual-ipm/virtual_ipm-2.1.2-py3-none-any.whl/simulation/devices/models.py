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

from __future__ import annotations

import abc
from pathlib import Path
from typing import Callable

from anna import PhysicalQuantity, SubstitutionGroup, Duplet, parametrize, Vector, Filepath
import injector
import numpy as np

from virtual_ipm.components import Model
import virtual_ipm.di as di
from virtual_ipm.simulation.errors import MissingOptionalDependencyError

try:
    from . import obstacles
except ImportError:
    obstacles = None


class DeviceModel(Model):
    """
    (Abstract) Base class for device models.

    A device model is responsible for

    * defining the boundaries of the simulation region. This information is for example used by
      bunch electric field models in order to confine the volume in which the field must be
      precomputed.
    * deciding when particles are detected or invalidated (invalidated means a particle stopped
      tracking but was not detected; e.g. it hit the boundary of the chamber).

    The task of identifying which particles are detected is a very general one and extends
    for example to the use case of studying BIF monitors. The device would compute
    the decay probabilities per particle and use this information in order to determine when
    the particle is considered detected.

    Status updates must not be performed manually via assignment but using the dedicated methods
    provided by this base class instead:

    * :method:`Device.invalidate`
    * :method:`Device.detect`

    This is because for each status update a corresponding status update notification will be
    generated and published on the :method:`ParticleSupervisor.status_updates` stream.
    When using manual assignment those notifications are not created.
    """

    CONFIG_PATH_TO_IMPLEMENTATION = 'Device/Model'
    CONFIG_PATH = 'Device/Parameters'

    @injector.inject(
        particle_supervisor=di.components.particle_supervisor,
        configuration=di.components.configuration
    )
    def __init__(self, particle_supervisor, configuration):
        """
        Initialize the device model.

        Parameters
        ----------
        particle_supervisor : :class:`ParticleSupervisor`
        configuration : :class:`ConfigurationAdaptor` derived class
        """
        super().__init__(configuration)
        self._particle_supervisor = particle_supervisor

    def invalidate(self, particles, progress):
        """
        Set the status of the given particles to "invalid".

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
            The current simulation progress at which the status change happens.
        """
        self.log.debug('Particles invalidated: %s', particles)
        if particles:
            self._particle_supervisor.invalidate(particles, progress)

    def detect(self, particles, progress):
        """
        Set the status of the given particles to "detected".

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
            The current simulation progress at which the status change happens.
        """
        self.log.debug('Particles detected: %s', particles)
        if particles:
            self._particle_supervisor.detect(particles, progress)

    @abc.abstractmethod
    def scan_particles(self, particles, progress):
        """
        Check the given particles and change their statuses if appropriate.
        This method must be implemented by all Device subclasses.

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
            The current simulation progress at which this method is invoked.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def x_boundaries(self):
        """
        The x-boundaries of the device.

        Returns
        -------
        x_boundaries : :class:`~np.ndarray`, shape (2,)
            In units of [m]. The first item denotes the lower and the second item the upper
            boundary: ``x_boundaries[0] < x_boundaries[1]``.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def y_boundaries(self):
        """
        The y-boundaries of the device.

        Returns
        -------
        y_boundaries : :class:`~np.ndarray`, shape (2,)
            In units of [m]. The first item denotes the lower and the second item the upper
            boundary: ``y_boundaries[0] < y_boundaries[1]``.
        """
        raise NotImplementedError

    @property
    def z_boundaries(self):
        """
        The z-boundaries of the device.

        Returns
        -------
        z_boundaries : :class:`~np.ndarray`, shape (2,)
            In units of [m]. The first item denotes the lower and the second item the upper
            boundary: ``z_boundaries[0] < z_boundaries[1]``. Returns ``array([-inf,  inf])``.
        """
        return np.array((-np.inf, np.inf))

Interface = DeviceModel


class FreeSpace(DeviceModel):
    """
    A no-op device model. This model won't change particle statuses and lets them propagate freely.
    """

    def __init__(self):
        super().__init__()
        self._xyz_boundaries = np.array((-np.inf, np.inf))

    @property
    def x_boundaries(self):
        return self._xyz_boundaries

    @property
    def y_boundaries(self):
        return self._xyz_boundaries

    def scan_particles(self, particles, progress):
        pass


@parametrize(
    Duplet[PhysicalQuantity](
        'XBoundaries',
        unit='m',
        info='The x-boundaries of the beam pipe at the BIF location.'
    ).use_container(np.array),
    Duplet[PhysicalQuantity](
        'YBoundaries',
        unit='m',
        info='The y-boundaries of the beam pipe at the BIF location.'
    ).use_container(np.array),
    SubstitutionGroup(
        PhysicalQuantity('Lifetime', unit='s')
    ).add_option(
        PhysicalQuantity('DecayRate', unit='Hz'),
        lambda x: 1./x
    )
)
class BIF(DeviceModel):
    @injector.inject(
        setup=di.components.setup
    )
    def __init__(self, setup):
        super().__init__()
        self._decay_probability = 1. - np.exp(-setup.time_delta / self._lifetime)

    @property
    def x_boundaries(self):
        return self._x_boundaries

    @property
    def y_boundaries(self):
        return self._y_boundaries

    def scan_particles(self, particles, progress):
        decays = np.random.uniform(size=len(particles)) < self._decay_probability
        self.detect(particles[decays], progress)


@parametrize(
    Duplet[PhysicalQuantity](
        'XBoundaries',
        unit='m'
    ).use_container(np.array),
    Duplet[PhysicalQuantity](
        'YBoundaries',
        unit='m'
    ).use_container(np.array)
)
class BasicIPM(DeviceModel):
    """
    Allows for specification of upper and lower boundaries with respect to x- and y-direction.
    The detector is located at the lower y-boundary. When particles reach this level they are
    considered detected.
    """

    def __init__(self):
        super().__init__()
        self._lower_transverse_boundaries = np.array([
            self.x_boundaries[0], self.y_boundaries[0]
        ])
        self._upper_transverse_boundaries = np.array([
            self.x_boundaries[1], self.y_boundaries[1]
        ])

    @property
    def x_boundaries(self):
        return self._x_boundaries

    @property
    def y_boundaries(self):
        return self._y_boundaries

    def scan_particles(self, particles, progress):
        # Detector is located at the lower y-boundary.
        invalid = (
            np.any(
                particles.position[:-1].T >= self._upper_transverse_boundaries,
                axis=1
            )
            |
            (particles.x <= self.x_boundaries[0])
        )
        self.invalidate(particles[invalid], progress)
        # `particles` is a view which corresponds to all "tracked" particles so we don't need to
        # check for `~invalid` here because the above call to `invalidate` already changed the
        # statuses appropriately (from "tracked" to "invalid").
        self.detect(particles[particles.y <= self.y_boundaries[0]], progress)


class InterpolatingIPM(BasicIPM):
    __doc__ = BasicIPM.__doc__.rstrip() + """
    This device model uses the current and the previous position of particles in order to
    interpolate their final positions at the detector level.
    """

    @injector.inject(
        setup=di.components.setup
    )
    def __init__(self, setup):
        super().__init__()
        self._dt = setup.time_delta

    def detect_particle(self, particles, progress):
        # Interpolate final positions at detector level.
        inverse_y_slope = self._dt / (particles.y - particles.previous_y)
        delta_time_to_detector = (
            inverse_y_slope
            * (self.y_boundaries[0] - particles.previous_y)
        )
        slopes = (particles.position - particles.previous_position) / self._dt
        particles.position = particles.previous_position + slopes * delta_time_to_detector
        super().detect_particle(particles, progress)


@parametrize(
    Vector[Filepath]('Detectors'),
    Vector[Filepath]('Obstacles'),
)
class Obstacles(DeviceModel):
    """
    Allows for specification of various obstacles via .STL files.

    Particles that hit one of the specified ``Detectors`` will be marked ``DETECTED`` and they will be marked
    ``INVALID`` if they hit one of the ``Obstacles``.

    .. note::
       This model requires optional dependencies which can be installed via
       ``python -m pip install Virtual-IPM[Obstacles]``.

    .. warning::
       This model only performs point-collision, i.e. it checks whether particles are *inside* the specified obstacles
       at any time during the simulation. This means that there is no protection against "jump-through" in case the
       specified obstacles are very thin. If obstacles are too thin it might happen that at one simulation step the
       particle is located above the obstacle and in the next simulation step it is located below, i.e. from the
       perspective of the simulation it was never *inside* the obstacle and hence will not be detected/invalid.
       Therefore it is the responsibility of the user to ensure that the specified time step size for the simulation
       is appropriately chosen in order to prevent such situations. To be on the safe side, the time step size ``dt``
       should obey ``dt < dx/c`` where ``dx`` is the thinnest part of the obstacle(s) and ``c`` is the speed of light.

    .. note::
       The correct global positioning of obstacles inside STL files must be ensured by the user. The simulation does
       not change any properties of the specified geometries.

    .. note::
       The detectors and obstacles should not overlap; if they do, it is undefined whether a particle will be
       ``DETECTED`` or ``INVALID``.

    .. note::
       The implementation uses the ``trimesh`` package [1]_ so in fact any file type that is compatible with
       ``trimesh.load_mesh`` should work (compatible in a sense that it returns a ``Trimesh`` object).
       File types other than STL are however untested.

    References
    ----------
    .. [1] Dawson-Haggerty et al., `trimesh <https://trimsh.org/>`__, https://trimsh.org/
    """

    obstacles: list[tuple[Callable, obstacles.Obstacle]]

    def __init__(self):
        super().__init__()

        if obstacles is None:
            raise MissingOptionalDependencyError(
                'Please install the missing dependencies via `python -m pip install Virtual-IPM[Obstacles]`'
            )

        self.obstacles = []
        for path in self._obstacles:
            self.obstacles.append((self.invalidate, self.create_multilayer_obstacle_from_stl_path(path=path)))
        for path in self._detectors:
            self.obstacles.append((self.detect, self.create_multilayer_obstacle_from_stl_path(path=path)))

    @property
    def x_boundaries(self):
        return np.array([-np.inf, np.inf])

    @property
    def y_boundaries(self):
        return np.array([-np.inf, np.inf])

    def scan_particles(self, particles, progress):
        for method, obstacle in self.obstacles:
            mask = obstacle.collide(particles.position)
            method(particles[mask], progress)

    @classmethod
    def create_multilayer_obstacle_from_stl_path(cls, path: Path) -> obstacles.Obstacle:
        stl_obstacle = obstacles.STLObstacle(str(path))
        bounding_box = cls.create_bounding_box_from_stl_obstacle(stl_obstacle)
        return obstacles.MultilayerObstacle([bounding_box, stl_obstacle])

    @classmethod
    def create_bounding_box_from_stl_obstacle(cls, stl_obstacle: obstacles.STLObstacle) -> obstacles.Box:
        center = stl_obstacle.corners.mean(axis=0)
        size = stl_obstacle.sides
        return obstacles.Box(center=center, size=size)
