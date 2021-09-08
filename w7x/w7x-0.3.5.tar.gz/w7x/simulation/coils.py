"""
Bozhenkovs Field Line Tracer Code with abstract backend.
"""
from abc import abstractmethod
import typing

import tfields
import w7x
import w7x.plotting.poincare
from w7x.core import Code, Backend


class CoilsBackend(Backend):
    """
    Backend base class to be subclassed for implementations of the Coils db code
    """

    @staticmethod
    @abstractmethod
    def _get_filaments(
        coil_or_id: typing.Union[int, w7x.model.Coil]
    ) -> tfields.Points3D:
        """
        Get the filaments of a coil as point cloud
        """


# pylint:disable=protected-access
class Coils(Code):  # pylint: disable=abstract-method
    """
    High level Field Line Tracer object.
    """

    STRATEGY_TYPE = CoilsBackend
    STRATEGY_DEFAULT = "web_service"
