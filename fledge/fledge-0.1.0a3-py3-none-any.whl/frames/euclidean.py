"""Simple coordinate frames which could contain points or vectors."""
from ..core import Frame
from ..core import S_co
from ..spaces.euclidean import Euclidean1d
from ..spaces.euclidean import Euclidean2d
from ..spaces.euclidean import Euclidean3d


class EuclideanFrame(Frame[S_co]):
    """A base class for Euclidan frames."""

    @property
    def dim(self):
        """TODO."""
        return self.space.dim


class Cartesian1d(EuclideanFrame[Euclidean1d]):
    """TODO."""

    space_type_bound = Euclidean1d


class Cartesian2d(EuclideanFrame[Euclidean2d]):
    """Cartesian plane with (x,y) references."""

    space_type_bound = Euclidean2d


class Cartesian3d(EuclideanFrame[Euclidean3d]):
    """TODO."""

    space_type_bound = Euclidean3d


class Polar(EuclideanFrame[Euclidean2d]):
    """Polar coordinate frame with (r, phi)."""

    space_type_bound = Euclidean2d


class Spherical(EuclideanFrame[Euclidean3d]):
    """Spherical coordinate frame with (r, theta, phi).

    As defined [here](https://en.wikipedia.org/wiki/Spherical_coordinate_system).

    """

    space_type_bound = Euclidean3d


class Cylindrical(EuclideanFrame[Euclidean3d]):
    """Cylindrical coordinate system with (r, phi, z) coordinates."""

    space_type_bound = Euclidean3d


class HomogeneousCoordinateFrame(EuclideanFrame[S_co]):
    """A base class for homogeneous frames."""

    pass


class HFrame1d(HomogeneousCoordinateFrame[Euclidean1d]):
    """TODO."""

    space_type_bound = Euclidean1d


class HFrame2d(HomogeneousCoordinateFrame[Euclidean2d]):
    """TODO."""

    space_type_bound = Euclidean2d


class HFrame3d(HomogeneousCoordinateFrame[Euclidean3d]):
    """TODO."""

    space_type_bound = Euclidean3d


HFrame = HFrame3d
